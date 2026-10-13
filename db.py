"""SQLite helpers. Every query uses ? placeholders: user input is never put into SQL text."""
import secrets
import sqlite3
import time

import config
import content

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname      TEXT NOT NULL,
    nickname_lc   TEXT NOT NULL UNIQUE,
    resume_code   TEXT NOT NULL UNIQUE,
    variant       INTEGER NOT NULL,
    stage         TEXT NOT NULL DEFAULT 'l1',
    admin_ok      INTEGER NOT NULL DEFAULT 0,
    created_at    REAL NOT NULL,
    finished_at   REAL,
    claim_code    TEXT UNIQUE,
    claimed_at    REAL
);
CREATE TABLE IF NOT EXISTS hints (
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    part      TEXT NOT NULL,
    n         INTEGER NOT NULL,
    PRIMARY KEY (player_id, part, n)
);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

RESUME_WORDS = [
    "KRAKEN", "MANTA", "CORAL", "TRITON", "REKIN", "MEDUZA", "ANCHOR", "SONAR",
    "KELP", "PERLA", "NAUTILUS", "ORKA", "KRYL", "SZTORM", "FALA", "RAFA",
]
# No 0/O/1/I so that a code read aloud or from a screen is hard to get wrong.
CLAIM_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    conn = connect()
    with conn:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('gadgets', ?)",
            (str(config.DEFAULT_GADGETS),),
        )
    conn.close()


# ------------------------------------------------------------------ players
def _new_resume_code(conn: sqlite3.Connection) -> str:
    while True:
        code = f"{secrets.choice(RESUME_WORDS)}-{secrets.randbelow(9000) + 1000}"
        if not conn.execute("SELECT 1 FROM players WHERE resume_code = ?", (code,)).fetchone():
            return code


def create_player(conn: sqlite3.Connection, nickname: str):
    """Returns the new player row, or None if the nickname is taken."""
    try:
        with conn:
            conn.execute(
                "INSERT INTO players (nickname, nickname_lc, resume_code, variant, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    nickname,
                    nickname.casefold(),
                    _new_resume_code(conn),
                    secrets.randbelow(len(content.L1_VARIANTS)),
                    time.time(),
                ),
            )
    except sqlite3.IntegrityError:
        return None
    return conn.execute(
        "SELECT * FROM players WHERE nickname_lc = ?", (nickname.casefold(),)
    ).fetchone()


def get_player(conn: sqlite3.Connection, player_id):
    return conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()


def find_by_resume_code(conn: sqlite3.Connection, code: str):
    return conn.execute(
        "SELECT * FROM players WHERE resume_code = ?", (code.strip().upper(),)
    ).fetchone()


def set_stage(conn: sqlite3.Connection, player_id: int, stage: str) -> None:
    with conn:
        if stage == "done":
            claim = _new_claim_code(conn)
            conn.execute(
                "UPDATE players SET stage = ?, finished_at = ?, claim_code = ? WHERE id = ?",
                (stage, time.time(), claim, player_id),
            )
        else:
            conn.execute("UPDATE players SET stage = ? WHERE id = ?", (stage, player_id))


def set_admin_ok(conn: sqlite3.Connection, player_id: int) -> None:
    with conn:
        conn.execute("UPDATE players SET admin_ok = 1 WHERE id = ?", (player_id,))


def _new_claim_code(conn: sqlite3.Connection) -> str:
    while True:
        code = "".join(secrets.choice(CLAIM_ALPHABET) for _ in range(6))
        if not conn.execute("SELECT 1 FROM players WHERE claim_code = ?", (code,)).fetchone():
            return code


def delete_player(conn: sqlite3.Connection, player_id: int) -> None:
    with conn:
        conn.execute("DELETE FROM players WHERE id = ?", (player_id,))


def reset_event(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("DELETE FROM players")


# ------------------------------------------------------------------ hints
def revealed_hints(conn: sqlite3.Connection, player_id: int, part: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM hints WHERE player_id = ? AND part = ?", (player_id, part)
    ).fetchone()
    return row["c"]


def reveal_next_hint(conn: sqlite3.Connection, player_id: int, part: str) -> int:
    """Reveals the next hint of a part (max 3). Returns how many are revealed now."""
    count = revealed_hints(conn, player_id, part)
    if count >= 3:
        return count
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO hints (player_id, part, n) VALUES (?, ?, ?)",
            (player_id, part, count + 1),
        )
    return count + 1


# ------------------------------------------------------------------ prizes / settings
def get_gadgets_left(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT value FROM settings WHERE key = 'gadgets'").fetchone()
    return int(row["value"]) if row else 0


def set_gadgets_left(conn: sqlite3.Connection, value: int) -> None:
    with conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('gadgets', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(max(0, value)),),
        )


def find_by_claim_code(conn: sqlite3.Connection, code: str):
    clean = "".join(ch for ch in code.upper() if ch.isalnum())
    return conn.execute("SELECT * FROM players WHERE claim_code = ?", (clean,)).fetchone()


def give_gadget(conn: sqlite3.Connection, player_id: int) -> bool:
    """Marks the prize as handed over and decreases the stock, atomically."""
    with conn:
        cur = conn.execute(
            "UPDATE players SET claimed_at = ? "
            "WHERE id = ? AND claim_code IS NOT NULL AND claimed_at IS NULL",
            (time.time(), player_id),
        )
        if cur.rowcount != 1:
            return False
        conn.execute(
            "UPDATE settings SET value = CAST(MAX(0, CAST(value AS INTEGER) - 1) AS TEXT) "
            "WHERE key = 'gadgets'"
        )
    return True


# ------------------------------------------------------------------ leaderboard
def leaderboard(conn: sqlite3.Connection) -> list:
    rows = conn.execute(
        "SELECT p.id, p.nickname, p.stage, p.created_at, p.finished_at, p.claimed_at, "
        "p.claim_code, (SELECT COUNT(*) FROM hints h WHERE h.player_id = p.id) AS hints "
        "FROM players p"
    ).fetchall()
    now = time.time()
    result = []
    for r in rows:
        finished = r["finished_at"] is not None
        end = r["finished_at"] if finished else now
        result.append(
            {
                "id": r["id"],
                "nickname": r["nickname"],
                "stage": r["stage"],
                "level": min(content.level_of(r["stage"]), 4),
                "done": finished,
                "seconds": int(end - r["created_at"]),
                "hints": r["hints"],
                "claimed": r["claimed_at"] is not None,
                "claim_code": r["claim_code"],
            }
        )
    # Finished players first (fastest first), then by progress.
    result.sort(
        key=lambda x: (0 if x["done"] else 1, x["seconds"] if x["done"] else -content.STAGES.index(x["stage"]), x["seconds"])
    )
    return result
