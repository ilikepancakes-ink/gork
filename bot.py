import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from discord import app_commands
import sys # Import sys
import os # Import os if not already imported

load_dotenv("ai.env")
discord_token = os.getenv("DISCORD_TOKEN")

# Add the current working directory to sys.path to ensure modules like 'utils.database' are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if not discord_token:
    raise ValueError("Missing DISCORD_TOKEN environment variable.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
async def load_cogs():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Commands synced successfully!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(discord_token)

if __name__ == "__main__":
    asyncio.run(main())
