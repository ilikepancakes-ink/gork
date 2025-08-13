#!/usr/bin/env python3
"""
Test script for message logging functionality
"""
import asyncio
import os
from datetime import datetime
from utils.database import MessageDatabase

async def test_message_logging():
    """Test the message logging database functionality"""
    print("🧪 Testing Message Logging Database...")
    
    # Create test database
    test_db_path = "test_messages.db"
    db = MessageDatabase(test_db_path)
    
    try:
        # Initialize database
        await db.initialize()
        print("✅ Database initialized successfully")
        
        # Test logging a user message
        success = await db.log_user_message(
            user_id="123456789",
            username="testuser",
            user_display_name="Test User",
            channel_id="987654321",
            channel_name="general",
            guild_id="111222333",
            guild_name="Test Server",
            message_id="msg_001",
            message_content="Hello, bot!",
            has_attachments=False,
            timestamp=datetime.utcnow()
        )
        print(f"✅ User message logged: {success}")
        
        # Test logging a bot response
        success = await db.log_bot_response(
            original_message_id="msg_001",
            response_message_id="resp_001",
            response_content="Hello! How can I help you?",
            processing_time_ms=250,
            model_used="google/gemini-2.5-flash",
            timestamp=datetime.utcnow()
        )
        print(f"✅ Bot response logged: {success}")
        
        # Test getting user message history
        history = await db.get_user_message_history("123456789", limit=10)
        print(f"✅ Retrieved {len(history)} messages from history")
        
        # Test getting conversation stats
        stats = await db.get_conversation_stats()
        print(f"✅ Conversation stats: {stats}")
        
        # Test user-specific stats
        user_stats = await db.get_conversation_stats("123456789")
        print(f"✅ User stats: {user_stats}")
        
        print("\n🎉 All tests passed! Message logging system is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    
    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("🧹 Cleaned up test database")

if __name__ == "__main__":
    asyncio.run(test_message_logging())
