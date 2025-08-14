"""General commands for the Koko bot."""

from __future__ import annotations

import discord
from discord.ext import commands


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping")
    async def ping_cmd(self, ctx: commands.Context) -> None:
        """Reply with bot latency using a prefixed command."""
        latency = self.bot.latency * 1000
        await ctx.send(f"Pong! {latency:.2f}ms")

    @commands.slash_command(name="ping", description="Reply with bot latency.")
    async def ping_slash(self, ctx: discord.ApplicationContext) -> None:
        """Reply with bot latency using a slash command."""
        latency = self.bot.latency * 1000
        await ctx.respond(f"Pong! {latency:.2f}ms")

    @discord.user_command(name="Greet")
    async def greet(self, ctx: discord.ApplicationContext, member: discord.Member) -> None:
        """Send a greeting from the invoker to ``member``."""
        await ctx.respond(f"{ctx.author.mention} says hello to {member.mention}!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Welcome a user that joins the guild."""
        try:
            await member.send("Welcome to the server!")
        except discord.HTTPException:
            pass



def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(General(bot))
