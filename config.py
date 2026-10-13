"""Runtime settings. Everything can be overridden with environment variables."""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("CTF_DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

PORT = int(os.environ.get("CTF_PORT", "8080"))
HOST = os.environ.get("CTF_HOST", "0.0.0.0")
DB_PATH = Path(os.environ.get("CTF_DB", DATA_DIR / "ctf.sqlite3"))
DEFAULT_GADGETS = int(os.environ.get("CTF_GADGETS", "30"))


def _load_secret_key() -> str:
    """The signing key is stored on disk so that restarting the server keeps players logged in."""
    env = os.environ.get("CTF_SECRET_KEY")
    if env:
        return env
    key_file = DATA_DIR / "secret.key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_hex(32)
    key_file.write_text(key)
    return key


SECRET_KEY = _load_secret_key()

# Admin password: set CTF_ADMIN_PASSWORD, otherwise a random one is printed at startup.
ADMIN_PASSWORD_GENERATED = "CTF_ADMIN_PASSWORD" not in os.environ
ADMIN_PASSWORD = os.environ.get("CTF_ADMIN_PASSWORD") or secrets.token_urlsafe(6)
