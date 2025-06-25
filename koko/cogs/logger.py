"""Message logging cog for Koko."""

from __future__ import annotations

import datetime

import discord
from discord.ext import commands


class MessageLogger(commands.Cog):
    """Log all message events to the console."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Print a formatted line for each message received."""
        channel = message.channel
        if isinstance(channel, discord.abc.GuildChannel):
            channel_name = f"#{channel.name}"
        else:
            channel_name = "DM"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{channel_name}] ({ts}) {message.author}: {message.content}")


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(MessageLogger(bot))
