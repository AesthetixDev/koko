"""General commands for the Koko bot."""

from __future__ import annotations

import discord
from discord.ext import commands


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="ping", description="Reply with bot latency.")
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        """Reply with bot latency."""
        latency = self.bot.latency * 1000
        await ctx.respond(f"Pong! {latency:.2f}ms")


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(General(bot))
