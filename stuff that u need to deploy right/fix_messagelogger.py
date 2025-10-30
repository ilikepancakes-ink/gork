
"""
Quick fix script to help with MessageLogger cog loading issues
"""

def main():
    print("🔧 MessageLogger Cog Fix Guide")
    print("=" * 50)
    
    print("\n📋 **Issue Identified:**")
    print("The update cog was trying to reload 'MessageLogger' as 'cogs.messagelogger'")
    print("but the actual file is 'message_logger.py' (with underscore)")
    
    print("\n✅ **Fix Applied:**")
    print("- Updated cogs/update.py with proper cog name mapping")
    print("- Added mapping: 'MessageLogger' -> 'message_logger'")
    print("- Fixed new cog loading logic")
    
    print("\n🚀 **Next Steps:**")
    print("1. Restart your bot completely:")
    print("   python bot.py")
    print()
    print("2. Or try the update command again:")
    print("   /debug update")
    print()
    print("3. Check if MessageLogger loads properly:")
    print("   - Look for 'Loaded cog: message_logger.py' in console")
    print("   - Try the /logs command (if you have the right user ID)")
    print()
    
    print("📁 **File Structure Check:**")
    import os
    
    files_to_check = [
        "cogs/message_logger.py",
        "cogs/gork.py", 
        "cogs/update.py",
        "utils/database.py",
        "data/bot_messages.db"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    print("\n🔍 **Cog Name Mappings:**")
    mappings = {
        'MessageLogger': 'message_logger',
        'Gork': 'gork',
        'Status': 'status', 
        'Weather': 'weather',
        'HwInfo': 'hwinfo',
        'Update': 'update'
    }
    
    for cog_class, file_name in mappings.items():
        print(f"   {cog_class} -> cogs.{file_name}")
    
    print("\n💡 **Testing the Logs Command:**")
    print("Once MessageLogger is loaded, test with:")
    print("   /logs @username  (slash command)")
    print("   !logs @username  (regular command)")
    print("   (Only works for user ID: 1141746562922459136)")
    
    print("\n🎯 **Expected Behavior:**")
    print("- Bot should load all cogs without errors")
    print("- MessageLogger should appear in loaded cogs list")
    print("- Conversation context should work in Gork responses")
    print("- Logs command should be available")

if __name__ == "__main__":
    main()
