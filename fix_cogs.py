#!/usr/bin/env python3
"""
Quick fix script for cog loading issues
"""

def main():
    print("🔧 Cog Loading Fix Guide")
    print("=" * 50)
    
    print("\n📋 **Issues Identified:**")
    print("1. MessageLogger cog reload failing - extension not loaded")
    print("2. hwinfo and message_logger showing as 'already loaded' when trying to load new")
    print("3. Ping functionality may be broken due to cog loading issues")
    
    print("\n✅ **Fixes Applied:**")
    print("1. Updated cogs/update.py reload logic:")
    print("   - Better file existence checking")
    print("   - Improved error handling for 'already loaded' extensions")
    print("   - More robust cog discovery")
    
    print("\n🔍 **Cog Name Mappings (Class -> File):**")
    mappings = {
        'MessageLogger': 'message_logger.py',
        'Gork': 'gork.py',
        'Status': 'status.py', 
        'Weather': 'weather.py',
        'HwInfo': 'hwinfo.py',
        'Update': 'update.py'
    }
    
    for cog_class, file_name in mappings.items():
        print(f"   {cog_class} -> cogs/{file_name}")
    
    print("\n🚀 **Next Steps:**")
    print("1. Restart your bot to clear any stuck cog states")
    print("2. Try the /debug update command again")
    print("3. Test pinging the bot with @mention")
    
    print("\n🏓 **Testing Ping Functionality:**")
    print("- Make sure the bot has 'Message Content Intent' enabled")
    print("- Try mentioning the bot: @YourBot hello")
    print("- Check if the Gork cog is loaded properly")
    
    print("\n⚠️ **If Issues Persist:**")
    print("1. Check bot permissions in Discord Developer Portal")
    print("2. Verify all dependencies are installed (requirements.txt)")
    print("3. Check for any error messages in the bot console")
    print("4. Ensure the bot has proper intents enabled")
    
    print("\n📝 **Manual Reload Commands (if needed):**")
    print("In your bot console, you can try:")
    print("- Unload: await bot.unload_extension('cogs.message_logger')")
    print("- Load: await bot.load_extension('cogs.message_logger')")
    print("- Reload: await bot.reload_extension('cogs.message_logger')")

if __name__ == "__main__":
    main()
