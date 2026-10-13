"""Security helpers: rate limiting, CSRF tokens, input validation and response headers."""
import hmac
import re
import secrets
import threading
import time
import unicodedata
from collections import defaultdict, deque

from flask import abort, jsonify, request, session

NICK_RE = re.compile(r"^\w[\w .\-]{0,15}$", re.UNICODE)


# ------------------------------------------------------------------ input validation
def clean_nickname(raw) -> str | None:
    """Allows letters (also Polish), digits, space, _ . - ; 2 to 16 characters.

    Anything else (< > " ' & ; etc.) is rejected, so a nickname can never carry markup.
    """
    if not isinstance(raw, str):
        return None
    nick = unicodedata.normalize("NFKC", raw)
    nick = " ".join(nick.split())
    if len(nick) < 2 or not NICK_RE.match(nick):
        return None
    return nick


def clean_text(raw, max_len: int):
    """Returns a short string, or None if the value is not a string or too long."""
    if not isinstance(raw, str) or len(raw) > max_len:
        return None
    return raw


# ------------------------------------------------------------------ rate limiting
class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window: float) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > window:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            if len(self._hits) > 5000:  # keep memory bounded
                for k in [k for k, v in self._hits.items() if not v or now - v[-1] > window]:
                    self._hits.pop(k, None)
            return True


limiter = RateLimiter()


def rate_limit(bucket: str, limit: int, window: float, per_ip: bool = True):
    """Aborts with 429 when too many requests arrive. Used as a plain function call."""
    from flask import current_app
    if current_app and current_app.config.get("TESTING"):
        return
    who = request.remote_addr if per_ip else str(session.get("pid"))
    if not limiter.allow(f"{bucket}:{who}", limit, window):
        abort(429)


# ------------------------------------------------------------------ CSRF
def csrf_token() -> str:
    token = session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(24)
        session["csrf"] = token
    return token


def check_csrf() -> None:
    """Every POST must carry the token from the session (header or form field)."""
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(str(sent), str(expected)):
        abort(403)


def safe_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# ------------------------------------------------------------------ headers
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data: blob:; "
    "connect-src 'self'; "
    "font-src 'self'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)


def add_security_headers(response):
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def json_error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status
