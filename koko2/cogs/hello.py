import discord
from discord.ext import commands


class Hello(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.command()
    async def hello(
        self, ctx: commands.Context, *, member: discord.Member = None
    ):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        self._last_member = member


async def setup(bot: commands.Bot):
    await bot.add_cog(Hello(bot))
