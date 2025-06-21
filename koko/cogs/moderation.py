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
    async def kick_slash(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str | None = None) -> None:
        """Kick a member from the server via slash command."""
        await ctx.guild.kick(member, reason=reason)
        await ctx.respond(f"Kicked {member} for {reason or 'No reason'}")

    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick")
    async def kick_prefix(self, ctx: commands.Context, member: discord.Member, *, reason: str | None = None) -> None:
        """Kick a member using the prefix command."""
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"Kicked {member} for {reason or 'No reason'}")

    @commands.has_permissions(ban_members=True)
    @commands.slash_command(name="ban", description="Ban a member from the server.")
    async def ban_slash(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str | None = None) -> None:
        """Ban a member from the server via slash command."""
        await ctx.guild.ban(member, reason=reason)
        await ctx.respond(f"Banned {member} for {reason or 'No reason'}")

    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban")
    async def ban_prefix(self, ctx: commands.Context, member: discord.Member, *, reason: str | None = None) -> None:
        """Ban a member from the server using the prefix command."""
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"Banned {member} for {reason or 'No reason'}")


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Moderation(bot))
