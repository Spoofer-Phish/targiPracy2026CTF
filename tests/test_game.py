"""Automated checks: full playthrough, level gating, injection/XSS/CSRF defences and assets.

Run:  py -m unittest discover -s tests -v
"""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Use a throw-away database and known secrets *before* the app is imported.
_tmp = tempfile.mkdtemp(prefix="kraknautica-test-")
os.environ["CTF_DATA_DIR"] = _tmp
os.environ["CTF_ADMIN_PASSWORD"] = "test-admin-pass"
os.environ["CTF_SECRET_KEY"] = "test-secret-key"

import app as app_module  # noqa: E402
import content  # noqa: E402
import terminal  # noqa: E402
from i18n import STRINGS  # noqa: E402

app = app_module.app
app.config["TESTING"] = True

CSRF_RE = re.compile(r'name="csrf-token" content="([^"]+)"')


class Client:
    """A browser-like wrapper that keeps cookies and sends the CSRF token."""

    def __init__(self):
        self.c = app.test_client()
        self.token = None

    def refresh_token(self, path="/"):
        html = self.c.get(path, follow_redirects=True).get_data(as_text=True)
        found = CSRF_RE.search(html)
        if found:
            self.token = found.group(1)
        return html

    def post_json(self, path, body=None, token=True):
        headers = {"X-CSRF-Token": self.token} if token and self.token else {}
        return self.c.post(path, json=body or {}, headers=headers)

    def register(self, nick):
        self.refresh_token()
        resp = self.c.post(
            "/register", data={"nickname": nick, "csrf_token": self.token}, follow_redirects=False
        )
        self.refresh_token("/play")
        return resp

    def player_id(self):
        with self.c.session_transaction() as sess:
            return sess.get("pid")

    def stage(self):
        with app.app_context():
            import db
            conn = db.connect()
            row = db.get_player(conn, self.player_id())
            conn.close()
            return row["stage"] if row else None


def solve_variant_order(client):
    """Reads the player's variant from the DB and returns the winning key order."""
    import db
    conn = db.connect()
    row = db.get_player(conn, client.player_id())
    conn.close()
    return list(content.L1_SOLUTIONS[row["variant"]]), row["variant"]


class PlaythroughTest(unittest.TestCase):
    def play_all(self, lang, nick_suffix=""):
        cl = Client()
        cl.c.set_cookie("lang", lang)
        nick = f"Tester {lang} {nick_suffix}".strip()
        resp = cl.register(nick)
        self.assertEqual(resp.status_code, 302)
        cl.refresh_token("/play")

        # level 1
        self.assertIn("/level/1", cl.c.get("/play").headers["Location"])
        html = cl.c.get("/level/1").get_data(as_text=True)
        self.assertIn("BREACH PROTOCOL", html)
        order, variant = solve_variant_order(cl)
        bad = order[::-1] if order[::-1] != order else order[1:] + order[:1]
        self.assertFalse(cl.post_json("/api/l1/sequence", {"seq": bad}).get_json()["ok"])
        good = cl.post_json("/api/l1/sequence", {"seq": order}).get_json()
        self.assertTrue(good["ok"])
        self.assertEqual(good["passphrase"], content.l1_passphrase(variant))
        vault = cl.post_json("/api/l1/vault", {"passphrase": good["passphrase"]}).get_json()
        self.assertEqual(vault["flag"], content.FLAGS["l1"])
        self.assertFalse(cl.post_json("/api/flag", {"flag": "SPOOF{nope}"}).get_json()["ok"])
        r = cl.post_json("/api/flag", {"flag": "  spoof{AIRLOCK_open} "}).get_json()
        self.assertTrue(r["ok"])

        # level 2, part A
        self.assertEqual(cl.stage(), "l2a")
        html = cl.c.get("/level/2").get_data(as_text=True)
        self.assertIn(content.CAESAR_CIPHER, html)
        self.assertNotIn(content.MAINFRAME_PASSWORD, html)
        self.assertFalse(cl.post_json("/api/l2/login", {"password": "nope"}).get_json()["ok"])
        self.assertEqual(cl.post_json("/api/l2/term", {"cmd": "ls"}).status_code, 409)
        self.assertTrue(
            cl.post_json("/api/l2/login", {"password": "trident42"}).get_json()["ok"]
        )
        # part B
        t = cl.post_json("/api/l2/term", {"cmd": "cd /reactor", "cwd": "/home/captain"}).get_json()
        self.assertEqual(t["cwd"], "/reactor")
        t = cl.post_json("/api/l2/term", {"cmd": "cat core_access.txt", "cwd": "/reactor"}).get_json()
        self.assertIn(content.FLAGS["l2b"], t["output"])
        self.assertTrue(cl.post_json("/api/flag", {"flag": content.FLAGS["l2b"]}).get_json()["ok"])

        # level 3: IDOR then login
        self.assertEqual(cl.stage(), "l3a")
        html = cl.c.get("/level/3", follow_redirects=True).get_data(as_text=True)
        self.assertIn("Bubbles", html)
        self.assertNotIn("admin-form", html)
        self.assertEqual(cl.post_json("/api/l3/login", {"user": "admin", "password": "x"}).status_code, 409)
        html = cl.c.get("/level/3?id=1").get_data(as_text=True)
        self.assertIn("Octavius", html)
        self.assertEqual(cl.stage(), "l3b")
        self.assertIn("admin-form", html)
        self.assertFalse(
            cl.post_json("/api/l3/login", {"user": "admin", "password": "wrong"}).get_json()["ok"]
        )
        self.assertTrue(
            cl.post_json(
                "/api/l3/login", {"user": "Admin", "password": content.ADMIN_PASS}
            ).get_json()["ok"]
        )
        memo = cl.c.get("/memo").get_data(as_text=True)
        self.assertIn(content.FLAGS["l3b"], memo)
        self.assertIn(content.MEMO_PHRASE, memo)
        self.assertTrue(cl.post_json("/api/flag", {"flag": content.FLAGS["l3b"]}).get_json()["ok"])

        # level 4
        self.assertEqual(cl.stage(), "l4a")
        wrong = cl.post_json("/api/l4/report", {"id": "e1"}).get_json()
        self.assertFalse(wrong["correct"])
        self.assertEqual(cl.c.get("/private/sonar_scan.png").status_code, 404)
        self.assertTrue(cl.post_json("/api/l4/report", {"id": content.PHISH_ID}).get_json()["correct"])
        self.assertEqual(cl.c.get("/private/sonar_scan.png").status_code, 404)
        bad_send = cl.post_json("/api/l4/send", {"id": "p1"}).get_json()
        self.assertFalse(bad_send["correct"])
        self.assertTrue(
            cl.post_json("/api/l4/send", {"id": content.CORRECT_PHRASE_ID}).get_json()["correct"]
        )
        img = cl.c.get("/private/sonar_scan.png")
        self.assertEqual(img.status_code, 200)
        self.assertEqual(img.mimetype, "image/png")
        self.assertTrue(cl.post_json("/api/flag", {"flag": content.FLAGS["l4c"]}).get_json()["ok"])

        # prize screen
        self.assertEqual(cl.stage(), "done")
        done = cl.c.get("/done")
        self.assertEqual(done.status_code, 200)
        return cl

    def test_full_game_polish(self):
        self.play_all("pl")

    def test_full_game_english(self):
        self.play_all("en")

    def test_hints_are_three_per_part_and_stage_bound(self):
        cl = Client()
        cl.register("HintMaster")
        cl.refresh_token("/play")
        seen = []
        for _ in range(5):
            r = cl.post_json("/api/hint").get_json()
            seen.append(r["count"])
        self.assertEqual(seen, [1, 2, 3, 3, 3])
        for part in content.PARTS:
            for lang in ("pl", "en"):
                hints = content.get_hints(part, 0, lang)
                self.assertEqual(len(hints), 3, (part, lang))
                self.assertTrue(all(h.strip() for h in hints))


class GatingTest(unittest.TestCase):
    def test_anonymous_is_redirected(self):
        c = app.test_client()
        self.assertEqual(c.get("/level/1").status_code, 302)
        self.assertEqual(c.get("/play").status_code, 302)
        self.assertEqual(c.get("/memo").status_code, 302)
        self.assertEqual(c.get("/done").status_code, 302)
        self.assertEqual(c.get("/private/sonar_scan.png").status_code, 404)

    def test_cannot_skip_levels(self):
        cl = Client()
        cl.register("Skipper")
        cl.refresh_token("/play")
        for n in (2, 3, 4):
            resp = cl.c.get(f"/level/{n}")
            self.assertEqual(resp.status_code, 302)
            self.assertIn("/level/1", resp.headers["Location"])
        self.assertEqual(cl.c.get("/done").status_code, 302)
        self.assertEqual(cl.c.get("/memo").status_code, 302)
        self.assertEqual(cl.c.get("/level/3?id=1").status_code, 302)
        for path in ("/api/l2/login", "/api/l3/login", "/api/l4/report", "/api/l4/send", "/api/l2/term"):
            self.assertEqual(cl.post_json(path, {"password": "x", "id": "e3"}).status_code, 409, path)
        # flags of later levels are rejected at level 1
        r = cl.post_json("/api/flag", {"flag": content.FLAGS["l4c"]}).get_json()
        self.assertFalse(r["ok"])
        self.assertEqual(cl.stage(), "l1")


class SecurityTest(unittest.TestCase):
    def test_nickname_rejects_markup_and_sql(self):
        for nick in ["<script>alert(1)</script>", "x' OR 1=1 --", "a\"b", "<b>", "'; DROP TABLE players;--",
                     "a", "x" * 40, "name;", "a&b", "{{7*7}}"]:
            cl = Client()
            resp = cl.register(nick)
            self.assertEqual(resp.status_code, 400, nick)

    def test_nickname_accepts_polish_letters(self):
        cl = Client()
        self.assertEqual(cl.register("Zażółć Gęślą").status_code, 302)

    def test_duplicate_nickname(self):
        Client().register("Dupe Nick")
        self.assertEqual(Client().register("dupe nick").status_code, 409)

    def test_csrf_required(self):
        cl = Client()
        cl.register("CsrfTest")
        cl.refresh_token("/play")
        self.assertEqual(cl.post_json("/api/hint", token=False).status_code, 403)
        self.assertEqual(cl.c.post("/logout").status_code, 403)
        self.assertEqual(cl.c.post("/register", data={"nickname": "NoToken"}).status_code, 403)

    def test_security_headers(self):
        resp = app.test_client().get("/")
        self.assertIn("default-src 'self'", resp.headers["Content-Security-Policy"])
        self.assertIn("script-src 'self'", resp.headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", resp.headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-eval", resp.headers["Content-Security-Policy"])
        self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(resp.headers["X-Frame-Options"], "DENY")
        self.assertTrue(resp.headers["Set-Cookie"].lower().count("httponly") >= 1)

    def test_no_inline_scripts_or_styles_in_pages(self):
        cl = Client()
        pages = [cl.refresh_token("/")]
        cl.register("InlineCheck")
        pages.append(cl.c.get("/level/1").get_data(as_text=True))
        for html in pages:
            self.assertNotRegex(html, r"<script(?![^>]*(src=|type=\"application/json\"))")
            self.assertNotRegex(html, r"\sstyle=")
            self.assertNotRegex(html, r"\son\w+=")

    def test_xss_in_idor_parameter_is_escaped(self):
        cl = Client()
        cl.register("XssTest")
        cl.refresh_token("/play")
        cl.post_json("/api/l1/sequence", {"seq": ["Y"]})
        # jump straight to level 3 through the DB, then probe the page with hostile ids
        import db
        conn = db.connect()
        pid = conn.execute("SELECT id FROM players WHERE nickname = 'XssTest'").fetchone()["id"]
        db.set_stage(conn, pid, "l3a")
        conn.close()
        for raw in ["<script>alert(1)</script>", "1' OR '1'='1", "../../etc/passwd", "1;DROP TABLE players", "-1", "99999999999"]:
            html = cl.c.get("/level/3", query_string={"id": raw}).get_data(as_text=True)
            self.assertNotIn("<script>alert", html)
            self.assertTrue("karta nurka" in html.lower() or "diver card" in html.lower())
        self.assertEqual(cl.stage(), "l3a")  # none of them counted as id=1

    def test_sql_injection_in_inputs_is_inert(self):
        cl = Client()
        cl.register("SqliTest")
        cl.refresh_token("/play")
        payloads = ["' OR 1=1 --", "\" OR \"\"=\"", "admin'--", "'; DROP TABLE players; --"]
        for p in payloads:
            self.assertFalse(cl.post_json("/api/flag", {"flag": p}).get_json()["ok"])
            self.assertFalse(cl.post_json("/api/l1/vault", {"passphrase": p}).get_json()["ok"])
        resume = Client()
        resume.refresh_token()
        for p in payloads:
            r = resume.c.post("/resume", data={"code": p, "csrf_token": resume.token})
            self.assertEqual(r.status_code, 404)
        # the table is still there and the player is still ours
        self.assertEqual(cl.stage(), "l1")

    def test_wrong_types_do_not_crash(self):
        cl = Client()
        cl.register("TypeTest")
        cl.refresh_token("/play")
        for body in [{"flag": 123}, {"flag": ["a"]}, {"flag": None}, {}, {"flag": {"a": 1}}]:
            self.assertIn(cl.post_json("/api/flag", body).status_code, (200, 400))
        for body in [{"seq": "YGRB"}, {"seq": [1, 2, 3, 4]}, {"seq": ["Y", "Y", "Y", "Y"]}, {"seq": None}]:
            self.assertEqual(cl.post_json("/api/l1/sequence", body).status_code, 400)

    def test_language_redirect_is_not_open(self):
        c = app.test_client()
        for target in ["https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)"]:
            resp = c.get("/lang/en", query_string={"next": target})
            self.assertEqual(resp.headers["Location"], "/")
        resp = c.get("/lang/en", query_string={"next": "/level/3?id=1"})
        self.assertEqual(resp.headers["Location"], "/level/3?id=1")
        self.assertEqual(c.get("/lang/xx").status_code, 404)

    def test_private_files_not_public(self):
        c = app.test_client()
        for path in ["/static/img/sonar_scan.png", "/private/sonar_scan.png", "/data/ctf.sqlite3",
                     "/static/../config.py", "/static/..%2fconfig.py", "/app.py", "/content.py",
                     "/media/fish.webp", "/data/secret.key"]:
            self.assertEqual(c.get(path).status_code, 404, path)

    def test_admin_requires_password(self):
        c = Client()
        c.refresh_token("/admin")
        self.assertEqual(c.c.get("/api/admin/state").status_code, 401)
        self.assertEqual(c.post_json("/api/admin/reset", {"confirm": "RESET"}).status_code, 401)
        bad = c.c.post("/admin/login", data={"password": "nope", "csrf_token": c.token})
        self.assertEqual(bad.status_code, 401)
        good = c.c.post("/admin/login", data={"password": "test-admin-pass", "csrf_token": c.token})
        self.assertEqual(good.status_code, 302)
        self.assertEqual(c.c.get("/api/admin/state").status_code, 200)

    def test_terminal_cannot_touch_real_files(self):
        for cmd in ["cat ../../../../etc/passwd", "cat /app.py", "cat C:\\Windows\\win.ini", "ls /",
                    "cat ..\\..\\config.py", "cat /home/captain/../../app.py", "; ls", "ls | cat app.py",
                    "cat $(whoami)", "cat `id`", "cd /etc", "ls /proc"]:
            out = terminal.run(cmd, "/home/captain", "en")["output"]
            self.assertNotIn("SECRET_KEY", out, cmd)
            self.assertNotIn("import ", out, cmd)
            self.assertNotIn("root:", out, cmd)
        self.assertEqual(terminal.valid_cwd("/etc/../../.."), "/")
        self.assertEqual(terminal.valid_cwd("/reactor/../tmp"), "/tmp")
        self.assertEqual(terminal.run("cd /nope", "/tmp", "en")["cwd"], "/tmp")
        self.assertEqual(terminal.run("sudo rm -rf /", "/tmp", "en")["output"], terminal.TEXT["sudo"]["en"])
        self.assertIn("SPOOF{this_is_a_decoy", terminal.run("cat passwords_DO_NOT_OPEN.txt", terminal.HOME, "en")["output"])
        self.assertNotIn(".bubble_notes", terminal.run("ls", terminal.HOME, "en")["output"])
        self.assertIn(".bubble_notes", terminal.run("ls -a", terminal.HOME, "en")["output"])


class PrizeDeskTest(unittest.TestCase):
    def test_claim_code_is_one_time(self):
        finished = PlaythroughTest().play_all("pl", nick_suffix="PD")
        page = finished.c.get("/done").get_data(as_text=True)
        code = re.search(r'class="bigcode claim">([A-Z0-9]{3}-[A-Z0-9]{3})<', page).group(1)

        admin = Client()
        admin.refresh_token("/admin")
        admin.c.post("/admin/login", data={"password": "test-admin-pass", "csrf_token": admin.token})
        admin.refresh_token("/admin")

        before = admin.c.get("/api/admin/state").get_json()["gadgets"]
        look = admin.post_json("/api/admin/claim/lookup", {"code": code.lower()}).get_json()
        self.assertTrue(look["found"])
        self.assertFalse(look["claimed"])
        self.assertFalse(admin.post_json("/api/admin/claim/lookup", {"code": "ZZZ-ZZZ"}).get_json()["found"])
        self.assertEqual(admin.post_json("/api/admin/claim/give", {"code": code}).status_code, 200)
        self.assertEqual(admin.post_json("/api/admin/claim/give", {"code": code}).status_code, 409)
        after = admin.c.get("/api/admin/state").get_json()["gadgets"]
        self.assertEqual(after, before - 1)
        # the player's screen shows it was collected
        self.assertIn("alert good", finished.c.get("/done").get_data(as_text=True))


class ContentTest(unittest.TestCase):
    def test_level1_variants_have_unique_solutions(self):
        self.assertEqual(len(content.L1_SOLUTIONS), len(content.L1_VARIANTS))
        self.assertEqual(len(set(content.L1_SOLUTIONS)), len(content.L1_SOLUTIONS))
        for v in range(len(content.L1_VARIANTS)):
            for lang in ("pl", "en"):
                self.assertEqual(len(content.l1_clues(v, lang)), 3)

    def test_caesar_roundtrip(self):
        self.assertEqual(content.caesar(content.CAESAR_CIPHER, -content.CAESAR_SHIFT), content.CAESAR_PLAIN)
        self.assertIn(content.MAINFRAME_PASSWORD, content.CAESAR_PLAIN)
        self.assertNotIn(content.MAINFRAME_PASSWORD, content.CAESAR_CIPHER)
        self.assertTrue(content.CAESAR_PLAIN.isascii())

    def test_all_template_and_js_keys_exist(self):
        keys = set()
        for path in (ROOT / "templates").glob("*.html"):
            for m in re.findall(r"""\bt\(\s*['"]([a-z0-9_]+)['"]""", path.read_text(encoding="utf-8")):
                if not m.endswith("_"):
                    keys.add(m)
        app_keys = set(re.findall(r"""error=['"]([a-z0-9_]+)['"]""", (ROOT / "app.py").read_text(encoding="utf-8")))
        for key in sorted(keys | app_keys):
            self.assertIn(key, STRINGS, f"missing translation key {key}")
        for path in (ROOT / "static" / "js").glob("*.js"):
            for name in re.findall(r"\bi18n\.([a-z0-9_]+)", path.read_text(encoding="utf-8")):
                self.assertIn("js_" + name, STRINGS, f"{path.name}: missing js_{name}")
        for key, value in STRINGS.items():
            self.assertEqual(set(value), {"pl", "en"}, key)
            self.assertTrue(value["pl"].strip() and value["en"].strip(), key)
        for code in (403, 404, 405, 413, 429):
            self.assertIn(f"error_{code}", STRINGS)

    def test_stego_image(self):
        from PIL import Image

        path = ROOT / "private" / "sonar_scan.png"
        with Image.open(path) as img:
            self.assertEqual(img.info.get("Comment"), content.FLAGS["l4c"])
            w, h = img.size
            strip = img.convert("RGB").crop((0, h - 100, w, h))
            greens = [p[1] for p in strip.getdata()]
            self.assertLessEqual(max(greens), 9)
            raw = sum(1 for g in greens if g > 40)
            boosted = sum(1 for g in greens if (g - 6) * 40 > 100)
            self.assertEqual(raw, 0)
            self.assertGreater(boosted, 500)


if __name__ == "__main__":
    unittest.main()
