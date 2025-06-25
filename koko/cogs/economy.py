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

    @commands.command(name="balance")
    async def balance_cmd(self, ctx: commands.Context) -> None:
        """Show the user's current balance via a prefixed command."""
        amount = await get_balance(self.bot.db_path, ctx.author.id)
        await ctx.send(f"You have {amount} \N{WHITE STAR}")

    @commands.slash_command(name="balance", description="Check your Stars balance.")
    async def balance_slash(self, ctx: discord.ApplicationContext) -> None:
        """Show the user's current balance via slash command."""
        amount = await get_balance(self.bot.db_path, ctx.author.id)
        await ctx.respond(f"You have {amount} \N{WHITE STAR}", ephemeral=True)


    @commands.command(name="daily")
    async def daily_cmd(self, ctx: commands.Context) -> None:
        """Allow users to claim a daily reward via a prefixed command."""
        await self._daily(ctx.send, ctx.author, ctx.guild)

    @commands.slash_command(name="daily", description="Claim daily Stars.")
    async def daily_slash(self, ctx: discord.ApplicationContext) -> None:
        """Allow users to claim a daily reward via slash command."""
        await self._daily(ctx.respond, ctx.author, ctx.guild)

    async def _daily(
        self,
        responder: commands.Context.send | discord.ApplicationContext.respond,
        user: discord.User,
        guild: discord.Guild | None,
    ) -> None:
        """Handle the daily reward logic."""
        last = await get_last_daily(self.bot.db_path, user.id)
        now = time.time()
        if now - last < 86400:
            remaining = int(86400 - (now - last))
            await responder(
                f"Come back in {remaining // 3600}h {(remaining % 3600) // 60}m to claim again.",
                ephemeral=True,
            )
            return
        await update_balance(self.bot.db_path, user.id, DAILY_AMOUNT)
        await set_last_daily(self.bot.db_path, user.id, now)
        await responder(f"You claimed {DAILY_AMOUNT} \N{WHITE STAR}!", ephemeral=True)
        await self.bot.log(guild, f"{user} claimed daily stars")


    @commands.command(name="transfer")
    async def transfer_cmd(self, ctx: commands.Context, member: discord.Member, amount: commands.Range[int, 1]) -> None:
        """Transfer Stars to another member via a prefixed command."""
        await self._transfer(ctx.send, ctx.author, member, amount, ctx.guild)

    @commands.slash_command(name="transfer", description="Transfer Stars to another user.")
    async def transfer_slash(self, ctx: discord.ApplicationContext, member: discord.Member, amount: commands.Range[int, 1]) -> None:
        """Transfer Stars to another member via slash command."""
        await self._transfer(ctx.respond, ctx.author, member, amount, ctx.guild)

    async def _transfer(
        self,
        responder: commands.Context.send | discord.ApplicationContext.respond,
        sender: discord.User,
        member: discord.Member,
        amount: int,
        guild: discord.Guild | None,
    ) -> None:
        """Handle star transfers between users."""
        sender_balance = await get_balance(self.bot.db_path, sender.id)
        if sender_balance < amount:
            await responder("You don't have enough Stars.", ephemeral=True)
            return
        await update_balance(self.bot.db_path, sender.id, -amount)
        await update_balance(self.bot.db_path, member.id, amount)
        await responder(f"Transferred {amount} \N{WHITE STAR} to {member.display_name}.", ephemeral=True)
        await self.bot.log(guild, f"{sender} sent {amount} stars to {member}")


    @commands.has_permissions(administrator=True)
    @commands.command(name="addstars")
    async def addstars_cmd(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        """Manually add Stars to a user's balance via a prefixed command."""
        await update_balance(self.bot.db_path, member.id, amount)
        await ctx.send(f"Added {amount} \N{WHITE STAR} to {member.display_name}.")
        await self.bot.log(ctx.guild, f"{ctx.author} added {amount} stars to {member}")

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="addstars", description="Add Stars to a user.")
    async def addstars_slash(self, ctx: discord.ApplicationContext, member: discord.Member, amount: int) -> None:
        """Manually add Stars to a user's balance via slash command."""
        await update_balance(self.bot.db_path, member.id, amount)
        await ctx.respond(f"Added {amount} \N{WHITE STAR} to {member.display_name}.", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} added {amount} stars to {member}")


    @commands.has_permissions(administrator=True)
    @commands.command(name="removestars")
    async def removestars_cmd(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        """Manually remove Stars from a user's balance via a prefixed command."""
        await update_balance(self.bot.db_path, member.id, -amount)
        await ctx.send(f"Removed {amount} \N{WHITE STAR} from {member.display_name}.")
        await self.bot.log(ctx.guild, f"{ctx.author} removed {amount} stars from {member}")

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="removestars", description="Remove Stars from a user.")
    async def removestars_slash(self, ctx: discord.ApplicationContext, member: discord.Member, amount: int) -> None:
        """Manually remove Stars from a user's balance via slash command."""
        await update_balance(self.bot.db_path, member.id, -amount)
        await ctx.respond(f"Removed {amount} \N{WHITE STAR} from {member.display_name}.", ephemeral=True)
        await self.bot.log(ctx.guild, f"{ctx.author} removed {amount} stars from {member}")


    @commands.command(name="leaderboard")
    async def leaderboard_cmd(self, ctx: commands.Context) -> None:
        """Display the top 10 users by Stars with a prefixed command."""
        await self._leaderboard(ctx)

    @commands.slash_command(name="leaderboard", description="Top users by Stars.")
    async def leaderboard_slash(self, ctx: discord.ApplicationContext) -> None:
        """Display the top 10 users by Stars via slash command."""
        await self._leaderboard(ctx)

    async def _leaderboard(self, ctx: discord.abc.Messageable) -> None:
        """Internal helper to display the leaderboard."""
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
        if isinstance(ctx, discord.ApplicationContext):
            await ctx.respond(embed=embed)
        else:
            await ctx.send(embed=embed)


    @commands.command(name="shop")
    async def shop_cmd(self, ctx: commands.Context) -> None:
        """Display available shop items with a prefixed command."""
        lines = [f"{name} - {price} \N{WHITE STAR}" for name, price in SHOP_ITEMS.items()]
        await ctx.send("\n".join(lines))

    @commands.slash_command(name="shop", description="View shop items.")
    async def shop_slash(self, ctx: discord.ApplicationContext) -> None:
        """Display available shop items via slash command."""
        lines = [f"{name} - {price} \N{WHITE STAR}" for name, price in SHOP_ITEMS.items()]
        await ctx.respond("\n".join(lines), ephemeral=True)



def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Economy(bot))
