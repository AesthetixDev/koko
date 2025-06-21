"""Entry point for the Koko Discord bot."""

from __future__ import annotations

import asyncio
import json
import os

import discord
from discord.ext import commands

from .db import init_db


class KokoBot(discord.Bot):
    """Custom :class:`discord.Bot` implementation."""

    def __init__(self, *, config_path: str = "config.json") -> None:
        self.config = self._load_config(config_path)
        intents = discord.Intents.all()
        super().__init__(command_prefix=self.config.get("prefix", "!"), intents=intents)
        self.db_path = self.config.get("db_path", "data/koko.db")

    @staticmethod
    def _load_config(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    async def setup_hook(self) -> None:
        """Async initialization tasks when the bot starts."""
        await init_db(self.db_path)
        await self.load_extension("koko.cogs.general")
        await self.load_extension("koko.cogs.moderation")
        await self.load_extension("koko.cogs.automod")


async def main() -> None:
    """Main entry point to run the bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set")

    bot = KokoBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
