"""Administrator settings commands for Koko."""

from __future__ import annotations

import json
from pathlib import Path

import discord
from discord.ext import commands

from ..bot import KokoBot, FEATURE_COGS


class Settings(commands.Cog):
    """Commands to manage bot features and filters."""

    def __init__(self, bot: KokoBot) -> None:
        self.bot = bot
        self.settings_path = Path(bot.settings_path)
        self.bad_words_path = Path("data/automod.json")

    # Slash command group
    settings = commands.SlashCommandGroup("settings", "Manage bot settings")

    async def _set_feature(self, feature: str, enabled: bool) -> None:
        self.bot.settings.setdefault("enabled_cogs", {})[feature] = enabled
        self.settings_path.write_text(json.dumps(self.bot.settings, indent=2))
        ext = FEATURE_COGS[feature]
        if enabled and ext not in self.bot.extensions:
            await self.bot.load_extension(ext)
        elif not enabled and ext in self.bot.extensions:
            await self.bot.unload_extension(ext)
        await self.bot.log(f"Feature {feature} set to {enabled}")

    @settings.command(name="enable", description="Enable a bot feature.")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx: discord.ApplicationContext, feature: discord.Option(str, choices=list(FEATURE_COGS.keys()))) -> None:
        """Enable a bot feature."""
        await self._set_feature(feature, True)
        embed = discord.Embed(title="Feature Enabled", description=f"Enabled {feature}.")
        await ctx.respond(embed=embed, ephemeral=True)

    @settings.command(name="disable", description="Disable a bot feature.")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx: discord.ApplicationContext, feature: discord.Option(str, choices=list(FEATURE_COGS.keys()))) -> None:
        """Disable a bot feature."""
        await self._set_feature(feature, False)
        embed = discord.Embed(title="Feature Disabled", description=f"Disabled {feature}.")
        await ctx.respond(embed=embed, ephemeral=True)

    def _load_bad_words(self) -> dict:
        return json.loads(self.bad_words_path.read_text())

    def _save_bad_words(self, data: dict) -> None:
        self.bad_words_path.write_text(json.dumps(data, indent=2))

    @settings.command(name="add_bad_word", description="Add a word to the language filter.")
    @commands.has_permissions(administrator=True)
    async def add_bad_word(self, ctx: discord.ApplicationContext, word: str) -> None:
        """Add a banned word to the automod filter."""
        config = self._load_bad_words()
        words = config.setdefault("banned_words", [])
        if word.lower() not in words:
            words.append(word.lower())
            self._save_bad_words(config)
            automod = self.bot.get_cog("AutoMod")
            if automod:
                automod.reload_config()
            embed = discord.Embed(title="Word Added", description=f"Added `{word}` to filter.")
        else:
            embed = discord.Embed(title="Word Exists", description=f"`{word}` is already banned.")
        await ctx.respond(embed=embed, ephemeral=True)

    @settings.command(name="remove_bad_word", description="Remove a word from the language filter.")
    @commands.has_permissions(administrator=True)
    async def remove_bad_word(self, ctx: discord.ApplicationContext, word: str) -> None:
        """Remove a banned word from the automod filter."""
        config = self._load_bad_words()
        words = config.setdefault("banned_words", [])
        if word.lower() in words:
            words.remove(word.lower())
            self._save_bad_words(config)
            automod = self.bot.get_cog("AutoMod")
            if automod:
                automod.reload_config()
            embed = discord.Embed(title="Word Removed", description=f"Removed `{word}` from filter.")
        else:
            embed = discord.Embed(title="Not Found", description=f"`{word}` is not in the filter.")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    bot.add_cog(Settings(bot))
