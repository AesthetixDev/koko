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
        await db.execute(
            """CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                stars INTEGER DEFAULT 0,
                last_daily REAL DEFAULT 0
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                logs_channel_id INTEGER,
                prefix TEXT DEFAULT '!'
            )"""
        )


async def _ensure_user(db: aiosqlite.Connection, user_id: int) -> None:
    """Ensure a row exists for a user in the economy table."""
    await db.execute(
        "INSERT OR IGNORE INTO economy (user_id) VALUES (?)",
        (user_id,),
    )


async def get_balance(path: str, user_id: int) -> int:
    """Return a user's star balance."""
    async with DBManager(path) as db:
        await _ensure_user(db, user_id)
        cursor = await db.execute(
            "SELECT stars FROM economy WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def update_balance(path: str, user_id: int, delta: int) -> None:
    """Modify a user's star balance by ``delta``."""
    async with DBManager(path) as db:
        await _ensure_user(db, user_id)
        await db.execute(
            "UPDATE economy SET stars = stars + ? WHERE user_id = ?",
            (delta, user_id),
        )


async def get_last_daily(path: str, user_id: int) -> float:
    """Return the timestamp of the user's last daily claim."""
    async with DBManager(path) as db:
        await _ensure_user(db, user_id)
        cursor = await db.execute(
            "SELECT last_daily FROM economy WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def set_last_daily(path: str, user_id: int, ts: float) -> None:
    """Update the last daily claim timestamp for a user."""
    async with DBManager(path) as db:
        await _ensure_user(db, user_id)
        await db.execute(
            "UPDATE economy SET last_daily = ? WHERE user_id = ?",
            (ts, user_id),
        )


async def _ensure_guild(db: aiosqlite.Connection, guild_id: int) -> None:
    """Ensure a row exists for a guild in the guild_settings table."""
    await db.execute(
        "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)",
        (guild_id,),
    )


async def get_guild_settings(path: str, guild_id: int) -> dict:
    """Return configuration for a guild."""
    async with DBManager(path) as db:
        await _ensure_guild(db, guild_id)
        cursor = await db.execute(
            "SELECT logs_channel_id, prefix FROM guild_settings WHERE guild_id = ?",
            (guild_id,),
        )
        row = await cursor.fetchone()
        return {
            "logs_channel_id": row[0],
            "prefix": row[1] or "!",
        }


async def set_guild_settings(
    path: str,
    guild_id: int,
    *,
    logs_channel_id: int | None = None,
    prefix: str | None = None,
) -> None:
    """Update configuration values for a guild."""
    async with DBManager(path) as db:
        await _ensure_guild(db, guild_id)
        if logs_channel_id is not None:
            await db.execute(
                "UPDATE guild_settings SET logs_channel_id = ? WHERE guild_id = ?",
                (logs_channel_id, guild_id),
            )
        if prefix is not None:
            await db.execute(
                "UPDATE guild_settings SET prefix = ? WHERE guild_id = ?",
                (prefix, guild_id),
            )

