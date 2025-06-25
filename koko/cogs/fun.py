"""Fun commands for the Koko bot."""

from __future__ import annotations

import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """Light-hearted entertainment commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="roll")
    async def roll_cmd(self, ctx: commands.Context) -> None:
        """Roll a six-sided die with a prefixed command."""
        result = random.randint(1, 6)
        await ctx.send(f"You rolled **{result}**")

    @commands.slash_command(name="roll", description="Roll a six-sided die.")
    async def roll_slash(self, ctx: discord.ApplicationContext) -> None:
        """Reply with a random number between 1 and 6 via slash command."""
        result = random.randint(1, 6)
        await ctx.respond(f"You rolled **{result}**")



def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Fun(bot))
