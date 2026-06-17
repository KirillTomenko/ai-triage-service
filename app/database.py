import aiosqlite
from pathlib import Path

DB_PATH = Path("data/tickets.db")


async def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                client_id   TEXT NOT NULL,
                channel     TEXT NOT NULL,
                text        TEXT NOT NULL,
                category    TEXT,
                confidence  TEXT,
                escalate    INTEGER,
                draft_reply TEXT,
                error       TEXT
            )
        """)
        await db.commit()


async def save_ticket(
    client_id: str,
    channel: str,
    text: str,
    category: str | None,
    confidence: str | None,
    escalate: bool,
    draft_reply: str,
    error: str | None = None,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO tickets
                (client_id, channel, text, category, confidence, escalate, draft_reply, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, channel, text, category, confidence, int(escalate), draft_reply, error),
        )
        await db.commit()
        return cursor.lastrowid
