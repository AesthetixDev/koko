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

    @commands.slash_command(name="stats", description="Show server or user stats.")
    async def stats_slash(self, ctx: discord.ApplicationContext, member: discord.Member | None = None) -> None:
        """Display statistics for the server or a specific user via slash command."""
        if member and not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("You don't have permission to view others' stats.", ephemeral=True)
            return

        if member is None:
            guild = ctx.guild
            uptime = time.time() - self.bot.start_time
            embed = discord.Embed(title="Server & Bot Stats")
            embed.add_field(name="Members", value=str(guild.member_count), inline=False)
            embed.add_field(name="Channels", value=str(len(guild.channels)), inline=False)
            embed.add_field(name="Uptime", value=f"{uptime/3600:.2f} hours", inline=False)
            await ctx.respond(embed=embed)
        else:
            balance = await get_balance(self.bot.db_path, member.id)
            embed = discord.Embed(title=f"Stats for {member}")
            if member.joined_at:
                joined = discord.utils.format_dt(member.joined_at, 'F')
                embed.add_field(name="Joined", value=joined, inline=False)
            embed.add_field(name="Stars", value=str(balance), inline=False)
            await ctx.respond(embed=embed, ephemeral=True)



def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Stats(bot))
