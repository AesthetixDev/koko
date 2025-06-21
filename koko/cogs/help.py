"""Help command for Koko bot."""

from __future__ import annotations

import discord
from discord.ext import commands


class Help(commands.Cog):
    """Provide a slash command listing available bot commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _format_usage(self, cmd: commands.ApplicationCommand) -> str:
        """Return a usage string for a command."""
        options = getattr(cmd, "options", [])
        params = " ".join(f"<{opt.name}>" for opt in options)
        return f"/{cmd.qualified_name} {params}".strip()

    @commands.slash_command(name="help", description="Show available commands.")
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """Send an ephemeral embed of commands the user can run."""
        categories: dict[str, list[str]] = {}
        for cmd in self.bot.walk_application_commands():
            if not isinstance(cmd, commands.InvokableApplicationCommand):
                continue
            try:
                if not await cmd._can_run(ctx):
                    continue
            except Exception:
                continue
            usage = f"{self._format_usage(cmd)} - {cmd.description}"
            cat = cmd.cog_name or "Other"
            categories.setdefault(cat, []).append(usage)
        embed = discord.Embed(title="Available Commands")
        for cat in sorted(categories):
            lines = sorted(categories[cat])
            embed.add_field(name=cat, value="\n".join(lines), inline=False)
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Help(bot))
