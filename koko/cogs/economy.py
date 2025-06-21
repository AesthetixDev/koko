"""Economy system for the Koko bot."""

from __future__ import annotations

import time

import discord
from discord.ext import commands

from ..bot import KokoBot
from ..db import (
    DBManager,
    get_balance,
    update_balance,
    get_last_daily,
    set_last_daily,
)

DAILY_AMOUNT = 10
SHOP_ITEMS = {"cool_role": 100}


class Economy(commands.Cog):
    """Commands managing the Stars economy."""

    def __init__(self, bot: KokoBot) -> None:
        self.bot = bot

    @commands.slash_command(name="balance", description="Check your Stars balance.")
    async def balance(self, ctx: discord.ApplicationContext) -> None:
        """Show the user's current balance."""
        amount = await get_balance(self.bot.db_path, ctx.author.id)
        await ctx.respond(f"You have {amount} ✭", ephemeral=True)

    @commands.slash_command(name="daily", description="Claim daily Stars.")
    async def daily(self, ctx: discord.ApplicationContext) -> None:
        """Allow users to claim a daily reward."""
        last = await get_last_daily(self.bot.db_path, ctx.author.id)
        now = time.time()
        if now - last < 86400:
            remaining = int(86400 - (now - last))
            await ctx.respond(
                f"Come back in {remaining // 3600}h {(remaining % 3600) // 60}m to claim again.",
                ephemeral=True,
            )
            return
        await update_balance(self.bot.db_path, ctx.author.id, DAILY_AMOUNT)
        await set_last_daily(self.bot.db_path, ctx.author.id, now)
        await ctx.respond(f"You claimed {DAILY_AMOUNT} ✭!", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} claimed daily stars")

    @commands.slash_command(name="transfer", description="Transfer Stars to another user.")
    async def transfer(self, ctx: discord.ApplicationContext, member: discord.Member, amount: commands.Range[int, 1]) -> None:
        """Transfer Stars to another member."""
        sender_balance = await get_balance(self.bot.db_path, ctx.author.id)
        if sender_balance < amount:
            await ctx.respond("You don't have enough Stars.", ephemeral=True)
            return
        await update_balance(self.bot.db_path, ctx.author.id, -amount)
        await update_balance(self.bot.db_path, member.id, amount)
        await ctx.respond(f"Transferred {amount} ✭ to {member.display_name}.", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} sent {amount} stars to {member}")

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="addstars", description="Add Stars to a user.")
    async def addstars(self, ctx: discord.ApplicationContext, member: discord.Member, amount: int) -> None:
        """Manually add Stars to a user's balance."""
        await update_balance(self.bot.db_path, member.id, amount)
        await ctx.respond(f"Added {amount} ✭ to {member.display_name}.", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} added {amount} stars to {member}")

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="removestars", description="Remove Stars from a user.")
    async def removestars(self, ctx: discord.ApplicationContext, member: discord.Member, amount: int) -> None:
        """Manually remove Stars from a user's balance."""
        await update_balance(self.bot.db_path, member.id, -amount)
        await ctx.respond(f"Removed {amount} ✭ from {member.display_name}.", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} removed {amount} stars from {member}")

    @commands.slash_command(name="leaderboard", description="Top users by Stars.")
    async def leaderboard(self, ctx: discord.ApplicationContext) -> None:
        """Display the top 10 users by Stars."""
        async with DBManager(self.bot.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id, stars FROM economy ORDER BY stars DESC LIMIT 10"
            )
            rows = await cursor.fetchall()
        lines = []
        for index, (user_id, stars) in enumerate(rows, start=1):
            user = ctx.guild.get_member(user_id)
            name = user.display_name if user else f"User {user_id}"
            lines.append(f"{index}. {name} - {stars} ✭")
        description = "\n".join(lines) if lines else "No data."
        embed = discord.Embed(title="Stars Leaderboard", description=description)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="shop", description="View shop items.")
    async def shop(self, ctx: discord.ApplicationContext) -> None:
        """Display available shop items."""
        lines = [f"{name} - {price} ✭" for name, price in SHOP_ITEMS.items()]
        await ctx.respond("\n".join(lines), ephemeral=True)


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Economy(bot))
