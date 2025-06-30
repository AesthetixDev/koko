import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Show this message")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here is a list of available commands",
            color=discord.Color.blurple(),
        )
        for command in self.bot.walk_commands():
            if command.parent is None:
                embed.add_field(
                    name=command.qualified_name,
                    value=command.help or "No description provided.",
                    inline=False,
                )
        await ctx.respond(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
