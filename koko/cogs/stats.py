"""Statistics commands for the Koko bot."""

from __future__ import annotations

import time

import discord
from discord.ext import commands

from ..db import get_balance
from ..bot import KokoBot


class Stats(commands.Cog):
    """Provide server and user statistics."""

    def __init__(self, bot: KokoBot) -> None:
        self.bot = bot

    @commands.command(name="stats")
    async def stats_cmd(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        """Display statistics for the server or a user via a prefixed command."""
        await self._stats(ctx.send, ctx.author, ctx.guild, member)

    @commands.slash_command(name="stats", description="Show server or user stats.")
    async def stats_slash(self, ctx: discord.ApplicationContext, member: discord.Member | None = None) -> None:
        """Display statistics for the server or a specific user via slash command."""
        await self._stats(ctx.respond, ctx.author, ctx.guild, member)

    async def _stats(
        self,
        responder: commands.Context.send | discord.ApplicationContext.respond,
        viewer: discord.Member,
        guild: discord.Guild | None,
        target: discord.Member | None,
    ) -> None:
        """Internal helper to build the stats embed."""
        target = target or viewer
        if target != viewer and not viewer.guild_permissions.manage_messages:
            await responder("You don't have permission to view others' stats.", ephemeral=True)
            return
        if target == guild.me:
            uptime = time.time() - self.bot.start_time
            embed = discord.Embed(title="Server & Bot Stats")
            embed.add_field(name="Members", value=str(guild.member_count), inline=False)
            embed.add_field(name="Channels", value=str(len(guild.channels)), inline=False)
            embed.add_field(name="Uptime", value=f"{uptime/3600:.2f} hours", inline=False)
            await responder(embed=embed)
        else:
            balance = await get_balance(self.bot.db_path, target.id)
            embed = discord.Embed(title=f"Stats for {target}")
            if target.joined_at:
                joined = discord.utils.format_dt(target.joined_at, 'F')
                embed.add_field(name="Joined", value=joined, inline=False)
            embed.add_field(name="Stars", value=str(balance), inline=False)
            await responder(embed=embed, ephemeral=True)



def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Stats(bot))
