"""Moderation commands for the Koko bot."""

from __future__ import annotations

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Commands for server moderation."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.slash_command(name="kick", description="Kick a member from the server.")
    async def kick(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str | None = None) -> None:
        """Kick a member from the server."""
        await ctx.guild.kick(member, reason=reason)
        await ctx.respond(f"Kicked {member} for {reason or 'No reason'}")

    @commands.has_permissions(ban_members=True)
    @commands.slash_command(name="ban", description="Ban a member from the server.")
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str | None = None) -> None:
        """Ban a member from the server."""
        await ctx.guild.ban(member, reason=reason)
        await ctx.respond(f"Banned {member} for {reason or 'No reason'}")


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Moderation(bot))
