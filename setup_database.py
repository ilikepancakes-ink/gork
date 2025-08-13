#!/usr/bin/env python3
"""
Setup script for the message logging database
"""
import os
import asyncio
from utils.database import MessageDatabase

async def setup_database():
    """Initialize the database and create necessary directories"""
    print("🔧 Setting up message logging database...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    print("✅ Created data directory")
    
    # Initialize the database
    db = MessageDatabase("data/bot_messages.db")
    await db.initialize()
    
    print("✅ Database setup complete!")
    print(f"📁 Database location: {os.path.abspath(db.db_path)}")
    
    # Test the database with some sample operations
    print("\n🧪 Testing database operations...")
    
    # Test getting stats (should be empty initially)
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
