"""KRAKNAUTICA 2099: a mini CTF for the KN SpooferPhish stand.

Run with:  py app.py        (see README.md for the full setup guide)
"""
import io
import re
import socket
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

from flask import (
    Flask, abort, g, jsonify, redirect, render_template, request, send_file, session, url_for,
)

import config
import content
import db
import security
import terminal
from i18n import STRINGS

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_NAME="kraknautica",
    PERMANENT_SESSION_LIFETIME=timedelta(days=2),
    MAX_CONTENT_LENGTH=8 * 1024,
)
app.after_request(security.add_security_headers)

db.init_db()


# ------------------------------------------------------------------ request setup
@app.before_request
def load_request_state():
    g.db = db.connect()
    g.lang = request.cookies.get("lang", "pl")
    if g.lang not in ("pl", "en"):
        g.lang = "pl"
    g.player = None
    pid = session.get("pid")
    if pid is not None:
        g.player = db.get_player(g.db, pid)
        if g.player is None:
            session.pop("pid", None)
    if request.method == "POST":
        security.check_csrf()


@app.teardown_request
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def t(key: str, **kwargs) -> str:
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry[g.lang]
    return text.format(**kwargs) if kwargs else text


@app.context_processor
def inject_globals():
    stage = g.player["stage"] if g.player else None
    return {
        "t": t,
        "lang": g.lang,
        "player": g.player,
        "stage": stage,
        "current_level": content.level_of(stage) if stage else None,
        "csrf_token": security.csrf_token(),
        "js_strings": {k[3:]: v[g.lang] for k, v in STRINGS.items() if k.startswith("js_")},
        "current_url": request.full_path.rstrip("?"),
    }


@app.template_filter("clock")
def clock_filter(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# ------------------------------------------------------------------ helpers
def is_api() -> bool:
    return request.path.startswith("/api/")


def require_player():
    """Returns a redirect/JSON error if nobody is signed in, otherwise None."""
    if g.player is None:
        if is_api():
            return security.json_error("not signed in", 401)
        return redirect(url_for("index"))
    return None


def revealed_hint_texts(stage: str) -> list:
    if stage not in content.PARTS:
        return []
    count = db.revealed_hints(g.db, g.player["id"], stage)
    return content.get_hints(stage, g.player["variant"], g.lang)[:count]


def stage_url(stage: str) -> str:
    if stage == "done":
        return url_for("done")
    if stage == "l3a":
        return url_for("level", n=3, id=content.DEFAULT_CREW_ID)
    return url_for("level", n=content.level_of(stage))


def player_view(stage: str, **extra):
    """Common template data for a level page."""
    data = {
        "hints": revealed_hint_texts(stage),
        "hint_part": stage,
        "has_flag": stage in content.FLAGS,
    }
    data.update(extra)
    return data


# ------------------------------------------------------------------ public pages
@app.get("/")
def index():
    return render_template("index.html", error=None)


@app.post("/register")
def register():
    security.rate_limit("register", 20, 60)
    nick = security.clean_nickname(request.form.get("nickname", ""))
    if nick is None:
        return render_template("index.html", error="err_nick_invalid"), 400
    player = db.create_player(g.db, nick)
    if player is None:
        return render_template("index.html", error="err_nick_taken"), 409
    session.clear()
    session.permanent = True
    session["pid"] = player["id"]
    return redirect(url_for("play"))


@app.post("/resume")
def resume():
    security.rate_limit("resume", 10, 60)
    code = security.clean_text(request.form.get("code", ""), 30)
    player = db.find_by_resume_code(g.db, code) if code else None
    if player is None:
        return render_template("index.html", error="err_resume_bad"), 404
    session.clear()
    session.permanent = True
    session["pid"] = player["id"]
    return redirect(url_for("play"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/lang/<code>")
def set_language(code):
    if code not in ("pl", "en"):
        abort(404)
    target = request.args.get("next", "/")
    # Only local paths are allowed, so this can not be used as an open redirect.
    if not re.fullmatch(r"/[A-Za-z0-9_\-./?=&%]*", target) or target.startswith("//"):
        target = "/"
    response = redirect(target)
    response.set_cookie("lang", code, max_age=60 * 60 * 24 * 30, samesite="Lax")
    return response


@app.get("/board")
def board():
    return render_template("board.html")


@app.get("/api/board")
def api_board():
    security.rate_limit("board", 30, 10)
    rows = db.leaderboard(g.db)
    return jsonify(
        [
            {k: r[k] for k in ("nickname", "level", "done", "seconds", "hints")}
            for r in rows
        ]
    )


# ------------------------------------------------------------------ game flow
@app.get("/play")
def play():
    if (resp := require_player()) is not None:
        return resp
    return redirect(stage_url(g.player["stage"]))


@app.get("/level/<int:n>")
def level(n):
    if (resp := require_player()) is not None:
        return resp
    if n not in (1, 2, 3, 4):
        abort(404)
    stage = g.player["stage"]
    if content.level_of(stage) != n:
        return redirect(stage_url(stage))

    if n == 1:
        variant = g.player["variant"]
        keys = [
            {"id": k, "symbol": v["symbol"], "name": v[g.lang]} for k, v in content.KEYS.items()
        ]
        return render_template(
            "level1.html", **player_view(stage, clues=content.l1_clues(variant, g.lang), keys=keys)
        )

    if n == 2:
        return render_template("level2.html", **player_view(stage, cipher=content.CAESAR_CIPHER))

    if n == 3:
        if "id" not in request.args and stage == "l3a":
            return redirect(url_for("level", n=3, id=content.DEFAULT_CREW_ID))
        raw = request.args.get("id", str(content.DEFAULT_CREW_ID))
        crew_id = int(raw) if raw.isdigit() and len(raw) <= 6 else None
        card = content.CREW.get(crew_id) if crew_id is not None else None
        if crew_id == content.CAPTAIN_ID and stage == "l3a":
            db.set_stage(g.db, g.player["id"], "l3b")
            g.player = db.get_player(g.db, g.player["id"])
            stage = "l3b"
        return render_template(
            "level3.html", **player_view(stage, card=card, crew_id=crew_id, raw_id=raw[:6])
        )

    return render_template(
        "level4.html",
        **player_view(
            stage,
            emails=content.EMAILS,
            phrases=content.MEMO_PHRASES,
            nereus_address=content.NEREUS_ADDRESS,
            red_flags=content.PHISH_RED_FLAGS,
        ),
    )


@app.get("/memo")
def memo():
    if (resp := require_player()) is not None:
        return resp
    if not g.player["admin_ok"]:
        return redirect(url_for("play"))
    stage = g.player["stage"]
    return render_template(
        "memo.html",
        flag=content.FLAGS["l3b"] if stage == "l3b" else None,
        phrase=content.MEMO_PHRASE,
    )


@app.get("/done")
def done():
    if (resp := require_player()) is not None:
        return resp
    if g.player["stage"] != "done":
        return redirect(stage_url(g.player["stage"]))
    p = g.player
    total_hints = g.db.execute(
        "SELECT COUNT(*) AS c FROM hints WHERE player_id = ?", (p["id"],)
    ).fetchone()["c"]
    return render_template(
        "done.html",
        claim_code=f"{p['claim_code'][:3]}-{p['claim_code'][3:]}",
        seconds=int(p["finished_at"] - p["created_at"]),
        total_hints=total_hints,
        claimed=p["claimed_at"] is not None,
    )


@app.get("/private/sonar_scan.png")
def sonar_scan():
    """The level 4 image is served only after the rogue AI has 'leaked' it."""
    if g.player is None or g.player["stage"] not in ("l4c", "done"):
        abort(404)
    return send_file(BASE_DIR / "private" / "sonar_scan.png", mimetype="image/png")


# ------------------------------------------------------------------ player API
@app.post("/api/hint")
def api_hint():
    if (resp := require_player()) is not None:
        return resp
    security.rate_limit("hint", 10, 10, per_ip=False)
    stage = g.player["stage"]
    if stage not in content.PARTS:
        return security.json_error("no hints here")
    count = db.reveal_next_hint(g.db, g.player["id"], stage)
    texts = content.get_hints(stage, g.player["variant"], g.lang)[:count]
    return jsonify({"ok": True, "hints": texts, "count": count})


@app.post("/api/flag")
def api_flag():
    if (resp := require_player()) is not None:
        return resp
    security.rate_limit("flag", 8, 10, per_ip=False)
    stage = g.player["stage"]
    expected = content.FLAGS.get(stage)
    body = request.get_json(silent=True) or {}
    submitted = security.clean_text(body.get("flag"), 100)
    if expected is None or submitted is None:
        return security.json_error("bad request")
    if not security.safe_equal(
        content.normalise_flag(submitted), content.normalise_flag(expected)
    ):
        return jsonify({"ok": False, "error": "wrong_flag"})
    new_stage = content.next_stage(stage)
    db.set_stage(g.db, g.player["id"], new_stage)
    return jsonify({"ok": True, "next": stage_url(new_stage)})


# ---- level 1
def _require_stage(*allowed):
    """Returns an error response unless the player is in one of the given stages."""
    if (resp := require_player()) is not None:
        return resp
    if g.player["stage"] not in allowed:
        return security.json_error("wrong stage", 409)
    return None


@app.post("/api/l1/sequence")
def api_l1_sequence():
    if (resp := _require_stage("l1")) is not None:
        return resp
    security.rate_limit("l1seq", 40, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    seq = body.get("seq")
    valid = (
        isinstance(seq, list)
        and len(seq) == 4
        and all(isinstance(k, str) for k in seq)
        and sorted(seq) == sorted("YGRB")
    )
    if not valid:
        return security.json_error("bad sequence")
    variant = g.player["variant"]
    if content.l1_check(variant, seq):
        return jsonify({"ok": True, "passphrase": content.l1_passphrase(variant)})
    return jsonify({"ok": False})


@app.post("/api/l1/vault")
def api_l1_vault():
    if (resp := _require_stage("l1")) is not None:
        return resp
    security.rate_limit("l1vault", 10, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    phrase = security.clean_text(body.get("passphrase"), 40)
    if phrase is None:
        return security.json_error("bad request")
    expected = content.l1_passphrase(g.player["variant"])
    if security.safe_equal(phrase.strip().upper(), expected):
        return jsonify({"ok": True, "flag": content.FLAGS["l1"]})
    return jsonify({"ok": False})


# ---- level 2
@app.post("/api/l2/login")
def api_l2_login():
    if (resp := _require_stage("l2a")) is not None:
        return resp
    security.rate_limit("l2login", 10, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    pw = security.clean_text(body.get("password"), 40)
    if pw is None:
        return security.json_error("bad request")
    if security.safe_equal(pw.strip().upper(), content.MAINFRAME_PASSWORD):
        db.set_stage(g.db, g.player["id"], "l2b")
        return jsonify({"ok": True, "next": url_for("level", n=2)})
    return jsonify({"ok": False})


@app.post("/api/l2/term")
def api_l2_term():
    if (resp := _require_stage("l2b")) is not None:
        return resp
    security.rate_limit("term", 40, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    command = security.clean_text(body.get("cmd"), 200)
    cwd = body.get("cwd", terminal.HOME)
    if command is None:
        return security.json_error("bad request")
    result = terminal.run(command, cwd if isinstance(cwd, str) else terminal.HOME, g.lang)
    result["ok"] = True
    return jsonify(result)


# ---- level 3
@app.post("/api/l3/login")
def api_l3_login():
    if (resp := _require_stage("l3b")) is not None:
        return resp
    security.rate_limit("l3login", 10, 60, per_ip=False)
    body = request.get_json(silent=True) or {}
    user = security.clean_text(body.get("user"), 40)
    pw = security.clean_text(body.get("password"), 60)
    if user is None or pw is None:
        return security.json_error("bad request")
    # A plain comparison with fixed values. There is no database query to inject into.
    user_ok = security.safe_equal(user.strip().lower(), content.ADMIN_USER)
    pw_ok = security.safe_equal(pw.strip(), content.ADMIN_PASS)
    if user_ok and pw_ok:
        db.set_admin_ok(g.db, g.player["id"])
        return jsonify({"ok": True, "next": url_for("memo")})
    return jsonify({"ok": False})


# ---- level 4
@app.post("/api/l4/report")
def api_l4_report():
    if (resp := _require_stage("l4a")) is not None:
        return resp
    security.rate_limit("l4report", 20, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    email_id = security.clean_text(body.get("id"), 10)
    email = next((e for e in content.EMAILS if e["id"] == email_id), None)
    if email is None:
        return security.json_error("bad request")
    if not email["phish"]:
        return jsonify({"ok": True, "correct": False,
                        "message": content.WRONG_EMAIL_EXPLANATION[g.lang]})
    db.set_stage(g.db, g.player["id"], "l4b")
    return jsonify({"ok": True, "correct": True, "next": url_for("level", n=4)})


@app.post("/api/l4/send")
def api_l4_send():
    if (resp := _require_stage("l4b")) is not None:
        return resp
    security.rate_limit("l4send", 20, 10, per_ip=False)
    body = request.get_json(silent=True) or {}
    phrase_id = security.clean_text(body.get("id"), 10)
    ids = [p["id"] for p in content.MEMO_PHRASES]
    if phrase_id not in ids:
        return security.json_error("bad request")
    if phrase_id == content.CORRECT_PHRASE_ID:
        db.set_stage(g.db, g.player["id"], "l4c")
        return jsonify({"ok": True, "correct": True, "next": url_for("level", n=4)})
    reply = content.WRONG_PHRASE_REPLIES[ids.index(phrase_id)][g.lang]
    return jsonify({"ok": True, "correct": False, "message": reply})


# ------------------------------------------------------------------ admin
def admin_required():
    if not session.get("admin"):
        if is_api():
            return security.json_error("admin only", 401)
        return redirect(url_for("admin"))
    return None


@app.get("/admin")
def admin():
    if not session.get("admin"):
        return render_template("admin_login.html", error=False)
    return render_template("admin.html")


@app.post("/admin/login")
def admin_login():
    security.rate_limit("adminlogin", 6, 60)
    pw = security.clean_text(request.form.get("password", ""), 100)
    if pw is not None and security.safe_equal(pw, config.ADMIN_PASSWORD):
        session.permanent = True
        session["admin"] = True
        return redirect(url_for("admin"))
    return render_template("admin_login.html", error=True), 401


@app.post("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


def _admin_state() -> dict:
    rows = db.leaderboard(g.db)
    return {
        "ok": True,
        "gadgets": db.get_gadgets_left(g.db),
        "total": len(rows),
        "finished": sum(1 for r in rows if r["done"]),
        "claimed": sum(1 for r in rows if r["claimed"]),
        "players": rows,
    }


@app.get("/api/admin/state")
def api_admin_state():
    if (resp := admin_required()) is not None:
        return resp
    return jsonify(_admin_state())


def _claim_info(player) -> dict:
    return {
        "ok": True,
        "found": True,
        "nickname": player["nickname"],
        "claimed": player["claimed_at"] is not None,
        "id": player["id"],
    }


@app.post("/api/admin/claim/lookup")
def api_admin_lookup():
    if (resp := admin_required()) is not None:
        return resp
    security.rate_limit("claimlookup", 30, 60)
    body = request.get_json(silent=True) or {}
    code = security.clean_text(body.get("code"), 20)
    player = db.find_by_claim_code(g.db, code) if code else None
    if player is None:
        return jsonify({"ok": True, "found": False})
    return jsonify(_claim_info(player))


@app.post("/api/admin/claim/give")
def api_admin_give():
    if (resp := admin_required()) is not None:
        return resp
    body = request.get_json(silent=True) or {}
    code = security.clean_text(body.get("code"), 20)
    player = db.find_by_claim_code(g.db, code) if code else None
    if player is None:
        return security.json_error("unknown code", 404)
    if db.get_gadgets_left(g.db) <= 0:
        return security.json_error("out of stock", 409)
    if not db.give_gadget(g.db, player["id"]):
        return security.json_error("already claimed", 409)
    return jsonify(_admin_state())


@app.post("/api/admin/gadgets")
def api_admin_gadgets():
    if (resp := admin_required()) is not None:
        return resp
    body = request.get_json(silent=True) or {}
    value = body.get("value")
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100000:
        return security.json_error("bad request")
    db.set_gadgets_left(g.db, value)
    return jsonify(_admin_state())


@app.post("/api/admin/delete")
def api_admin_delete():
    if (resp := admin_required()) is not None:
        return resp
    body = request.get_json(silent=True) or {}
    player_id = body.get("id")
    if not isinstance(player_id, int) or isinstance(player_id, bool):
        return security.json_error("bad request")
    db.delete_player(g.db, player_id)
    return jsonify(_admin_state())


@app.post("/api/admin/reset")
def api_admin_reset():
    if (resp := admin_required()) is not None:
        return resp
    body = request.get_json(silent=True) or {}
    if body.get("confirm") != "RESET":
        return security.json_error("bad request")
    db.reset_event(g.db)
    return jsonify(_admin_state())


# ------------------------------------------------------------------ errors
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(413)
@app.errorhandler(429)
def http_error(err):
    code = getattr(err, "code", 500)
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": str(code)}), code
    return render_template("error.html", code=code), code


# ------------------------------------------------------------------ start-up
def lan_addresses() -> list:
    """Best-effort list of the laptop's IPv4 addresses (no internet needed)."""
    found = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in found:
                found.append(ip)
    except OSError:
        pass
    # Prefer typical hotspot / router ranges.
    found.sort(key=lambda ip: (not ip.startswith(("192.168.", "10.", "172.")), ip))
    return found


def print_banner() -> None:
    import qrcode

    addresses = lan_addresses() or ["127.0.0.1"]
    url = f"http://{addresses[0]}:{config.PORT}"
    print("\n" + "=" * 60)
    print("  KRAKNAUTICA 2099 is running")
    print("=" * 60)
    for ip in addresses:
        print(f"  Players:  http://{ip}:{config.PORT}")
    print(f"  Board:    {url}/board   (projector)")
    print(f"  Admin:    {url}/admin")
    if config.ADMIN_PASSWORD_GENERATED:
        print(f"  Admin password (random, set CTF_ADMIN_PASSWORD to choose): {config.ADMIN_PASSWORD}")
    print("=" * 60)
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    buf = io.StringIO()
    qr.print_ascii(out=buf, invert=True)
    print(buf.getvalue())
    print(f"  QR code above opens {url}\n")


if __name__ == "__main__":
    from waitress import serve

    print_banner()
    serve(app, host=config.HOST, port=config.PORT, threads=16)
