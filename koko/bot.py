"""Entry point for the Koko Discord bot."""

from __future__ import annotations

import asyncio
import json
import os
import time

import discord
from discord.ext import commands

from .db import init_db

FEATURE_COGS: dict[str, str] = {
    "moderation": "koko.cogs.moderation",
    "automod": "koko.cogs.automod",
    "fun": "koko.cogs.fun",
    "stats": "koko.cogs.stats",
    "economy": "koko.cogs.economy",
}


class KokoBot(discord.Bot):
    """Custom :class:`discord.Bot` implementation."""

    def __init__(self, *, config_path: str = "config.json") -> None:
        self.config = self._load_config(config_path)
        intents = discord.Intents.all()
        super().__init__(command_prefix=self.config.get("prefix", "!"), intents=intents)
        self.db_path = self.config.get("db_path", "data/koko.db")
        self.logs_channel_id: int | None = self.config.get("logs_channel_id")
        self.settings_path = self.config.get("settings_path", "data/settings.json")
        self.settings = self._load_settings(self.settings_path)
        self.start_time = time.time()

    @staticmethod
    def _load_config(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    @staticmethod
    def _load_settings(path: str) -> dict:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fp:
                json.dump({"enabled_cogs": {k: True for k in FEATURE_COGS}}, fp, indent=2)
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    async def setup_hook(self) -> None:
        """Async initialization tasks when the bot starts."""
        await init_db(self.db_path)
        await self.load_extension("koko.cogs.general")
        for feature, ext in FEATURE_COGS.items():
            if self.settings.get("enabled_cogs", {}).get(feature, True):
                await self.load_extension(ext)
        await self.load_extension("koko.cogs.help")
        await self.load_extension("koko.cogs.settings")

    async def log(self, message: str) -> None:
        """Send a message to the configured logs channel."""
        if not self.logs_channel_id:
            return
        channel = self.get_channel(self.logs_channel_id)
        if channel:
            await channel.send(message)


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
