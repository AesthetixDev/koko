"""Entry point for the Koko Discord bot."""

from __future__ import annotations

import asyncio
import json
import os
import time

import discord
from discord.ext import commands

from .db import init_db, get_guild_settings

FEATURE_COGS: dict[str, str] = {
    "moderation": "koko.cogs.moderation",
    "automod": "koko.cogs.automod",
    "fun": "koko.cogs.fun",
    "stats": "koko.cogs.stats",
    "economy": "koko.cogs.economy",
}


class KokoBot(commands.Bot):
    """Custom :class:`commands.Bot` implementation supporting slash and prefix commands."""

    def __init__(self, *, config_path: str = "config.json") -> None:
        self.config = self._load_config(config_path)
        intents = discord.Intents.all()
        super().__init__(command_prefix=self._get_prefix, intents=intents)
        self.db_path = self.config.get("db_path", "data/koko.db")
        self.settings_path = self.config.get("settings_path", "data/settings.json")
        self.settings = self._load_settings(self.settings_path)
        self.start_time = time.time()

    async def _get_prefix(self, bot: commands.Bot, message: discord.Message) -> str:
        """Return the command prefix for ``message`` guild."""
        if message.guild is None:
            return "!"
        settings = await get_guild_settings(self.db_path, message.guild.id)
        return settings.get("prefix", "!")

    async def on_ready(self) -> None:
        """Log a message when the bot is ready."""
        print(f"Koko has been initialized as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        """Print a documentation snippet for each received message."""
        if message.author == self.user:
            return
        print(
            "There are 3 ways to register an event, the first way is through the"
            " use of Client.event(). The second way is through subclassing Client"
            " and overriding the specific events. The third way is through the use"
            " of Client.listen(), which can be used to assign multiple event"
            " handlers instead of only one like in Client.event()."
        )

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
        await self.load_extension("koko.cogs.logger")
        for feature, ext in FEATURE_COGS.items():
            if self.settings.get("enabled_cogs", {}).get(feature, True):
                await self.load_extension(ext)
        await self.load_extension("koko.cogs.help")
        await self.load_extension("koko.cogs.settings")
        await self.load_extension("koko.cogs.setup")
        # ensure slash commands are registered
        await self.sync_commands()

    async def log(self, guild: discord.Guild | None, message: str) -> None:
        """Send ``message`` to the guild's configured logs channel."""
        if not guild:
            return
        settings = await get_guild_settings(self.db_path, guild.id)
        channel_id = settings.get("logs_channel_id")
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(message)


async def main() -> None:
    """Main entry point to run the bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set")

    bot = KokoBot()
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
