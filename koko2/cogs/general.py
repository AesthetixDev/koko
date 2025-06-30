import random
import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx: commands.Context, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(str(left + right))

    @commands.command()
    async def roll(self, ctx: commands.Context, dice: str):
        """Rolls a die in NdN format."""
        try:
            rolls, limit = map(int, dice.split("d"))
        except ValueError:
            await ctx.send("Format has to be in NdN!")
            return
        result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
        await ctx.send(result)

    @commands.command(
        description="For when you wanna settle the score some other way"
    )
    async def choose(self, ctx: commands.Context, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @commands.command()
    async def repeat(
        self,
        ctx: commands.Context,
        times: int,
        *,
        content: str = "repeating...",
    ):
        """Repeats a message multiple times."""
        for _ in range(times):
            await ctx.send(content)

    @commands.command()
    async def joined(self, ctx: commands.Context, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(f"{member.name} joined in {member.joined_at}")

    @commands.group()
    async def cool(self, ctx: commands.Context):
        """Says if a user is cool."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No, {ctx.subcommand_passed} is not cool")

    @cool.command(name="bot")
    async def _bot(self, ctx: commands.Context):
        """Is the bot cool?"""
        await ctx.send("Yes, the bot is cool.")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
