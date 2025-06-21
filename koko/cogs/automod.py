"""Automoderation features for the Koko bot."""

from __future__ import annotations

import json
from pathlib import Path

from discord.ext import commands


class AutoMod(commands.Cog):
    """Simple automoderation cog."""

    def __init__(self, bot: commands.Bot, config_path: str = "data/automod.json") -> None:
        self.bot = bot
        self.config = json.loads(Path(config_path).read_text())

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot:
            return
        content = message.content.lower()
        if any(word in content for word in self.config.get("banned_words", [])):
            await message.delete()
            await message.channel.send(f"{message.author.mention} watch your language!", delete_after=5)


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(AutoMod(bot))
