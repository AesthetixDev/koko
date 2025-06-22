import os
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game("hello world"))
    print("Status set to 'hello world'")

@bot.hybrid_command(name="hello", with_app_command=True, description="Say hello")
async def hello(ctx: commands.Context):
    await ctx.send("Hello!")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable not set")
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
