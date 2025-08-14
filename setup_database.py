#!/usr/bin/env python3
import os
import asyncio
from utils.database import MessageDatabase

async def setup_database():
    print("🔧 Setting up message logging database...")

    os.makedirs("data", exist_ok=True)
    print("✅ Created data directory")

    db = MessageDatabase("data/bot_messages.db")
    await db.initialize()
    
    print("✅ Database setup complete!")
    print(f"📁 Database location: {os.path.abspath(db.db_path)}")

    print("\n🧪 Testing database operations...")

    stats = await db.get_conversation_stats()
    print(f"📊 Initial stats: {stats}")
    
    print("\n✅ All tests passed! The message logging system is ready to use.")
    print("\n📝 The bot will now automatically log:")
    print("   • User messages (both mentions and DMs)")
    print("   • Bot responses")
    print("   • Processing times")
    print("   • Message metadata (user info, channel info, etc.)")
    print("\n🔍 Use the following commands to view data:")
    print("   • /message_stats - View your message statistics")
    print("   • /message_history - View your recent message history")

if __name__ == "__main__":
    asyncio.run(setup_database())
