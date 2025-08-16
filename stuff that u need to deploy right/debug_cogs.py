#!/usr/bin/env python3
"""
Debug script to check cog loading status and fix issues
"""
import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

async def main():
    print("🔍 Discord Bot Cog Debug Tool")
    print("=" * 50)
    
    # Load environment
    load_dotenv("ai.env")
    discord_token = os.getenv("DISCORD_TOKEN")
    
    if not discord_token:
        print("❌ Missing DISCORD_TOKEN in ai.env")
        return
    
    # Check cog files
    print("\n📁 Available Cog Files:")
    cogs_dir = "cogs"
    if os.path.exists(cogs_dir):
        cog_files = [f for f in os.listdir(cogs_dir) if f.endswith('.py') and not f.startswith('__')]
        for cog_file in cog_files:
            print(f"   ✓ {cog_file}")
    else:
        print("   ❌ Cogs directory not found")
        return
    
    # Create bot instance
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"\n🤖 Bot logged in as: {bot.user}")
        
        print("\n📋 Currently Loaded Cogs:")
        for cog_name, cog in bot.cogs.items():
            print(f"   ✓ {cog_name} ({cog.__class__.__module__})")
        
        print("\n🔄 Testing Cog Reload...")
        
        # Test reloading each cog
        cog_file_mapping = {
            'MessageLogger': 'message_logger',
            'Gork': 'gork',
            'Status': 'status',
            'Weather': 'weather',
            'HwInfo': 'hwinfo',
            'Update': 'update'
        }
        
        for cog_name in list(bot.cogs.keys()):
            if cog_name.lower() == 'update':
                continue
                
            file_name = cog_file_mapping.get(cog_name, cog_name.lower())
            extension_name = f"cogs.{file_name}"
            
            try:
                await bot.reload_extension(extension_name)
                print(f"   ✅ Reloaded {cog_name} -> {extension_name}")
            except Exception as e:
                print(f"   ❌ Failed to reload {cog_name} -> {extension_name}: {e}")
        
        print("\n🔍 Testing MessageLogger Access:")
        message_logger = bot.get_cog('MessageLogger')
        if message_logger:
            print("   ✅ MessageLogger cog found and accessible")
        else:
            print("   ❌ MessageLogger cog not found")
            
        print("\n🏓 Testing Ping Functionality:")
        # Check if Gork cog has on_message listener
        gork_cog = bot.get_cog('Gork')
        if gork_cog:
            print("   ✅ Gork cog found")
            if hasattr(gork_cog, 'on_message'):
                print("   ✅ on_message listener found in Gork cog")
            else:
                print("   ❌ on_message listener not found in Gork cog")
        else:
            print("   ❌ Gork cog not found")
        
        await bot.close()
    
    # Load cogs
    print("\n🔄 Loading Cogs...")
    for cog_file in cog_files:
        try:
            await bot.load_extension(f"cogs.{cog_file[:-3]}")
            print(f"   ✅ Loaded {cog_file}")
        except Exception as e:
            print(f"   ❌ Failed to load {cog_file}: {e}")
    
    # Start bot (will trigger on_ready and then close)
    try:
        await bot.start(discord_token)
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
