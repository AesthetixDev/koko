"""Database utility for asynchronous SQLite operations."""

import aiosqlite


class DBManager:
    """Asynchronous context manager for SQLite database."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def __aenter__(self) -> aiosqlite.Connection:
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.conn:
            await self.conn.commit()
            await self.conn.close()


async def init_db(path: str) -> None:
    """Initialize necessary tables in the database."""
    async with DBManager(path) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS infractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )

