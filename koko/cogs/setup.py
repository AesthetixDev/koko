"""Server setup workflow for Koko."""

from __future__ import annotations

import discord
from discord.ext import commands

from ..bot import KokoBot
from ..db import set_guild_settings


class Setup(commands.Cog):
    """Provide a setup command and welcome message on guild join."""

    def __init__(self, bot: KokoBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.sync_commands(guild_ids=[guild.id])
        channel = discord.utils.get(guild.text_channels, name="general")
        if not channel or not channel.permissions_for(guild.me).send_messages:
            channel = next(
                (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
                None,
            )
        message = (
            "Thanks for inviting me! Use `/setup` to configure logs and other settings."
        )
        if channel:
            await channel.send(message)
        else:
            try:
                await guild.owner.send(message)
            except Exception:
                pass

    @commands.has_permissions(administrator=True)
    @commands.command(name="setup")
    async def setup_cmd(self, ctx: commands.Context, logs_channel: discord.TextChannel | None = None, prefix: str | None = None) -> None:
        """Configure logs channel and command prefix via prefixed command."""
        await self._do_setup(ctx, logs_channel, prefix)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="setup", description="Configure Koko for this server.")
    async def setup_slash(self, ctx: discord.ApplicationContext, logs_channel: discord.TextChannel | None = None, prefix: str | None = None) -> None:
        """Configure logs channel and command prefix using a slash command."""
        await self._do_setup(ctx, logs_channel, prefix)

    async def _do_setup(
        self,
        ctx: discord.abc.Messageable,
        logs_channel: discord.TextChannel | None,
        prefix: str | None,
    ) -> None:
        """Shared setup implementation."""
        guild = ctx.guild
        assert guild
        if logs_channel is None:
            overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
            logs_channel = await guild.create_text_channel("koko-logs", overwrites=overwrites)
        await set_guild_settings(self.bot.db_path, guild.id, logs_channel_id=logs_channel.id, prefix=prefix)
        if isinstance(ctx, discord.ApplicationContext):
            await ctx.respond("Setup complete!", ephemeral=True)
        else:
            await ctx.send("Setup complete!")



def setup(bot: commands.Bot) -> None:
    bot.add_cog(Setup(bot))

