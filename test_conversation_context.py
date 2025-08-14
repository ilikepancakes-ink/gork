#!/usr/bin/env python3
"""
Test script for the new conversation context functionality
"""
import asyncio
import os
from datetime import datetime
from utils.database import MessageDatabase

async def test_conversation_context():
    """Test the conversation context functionality"""
    print("🧪 Testing conversation context functionality...")
    
    # Create a test database
    db = MessageDatabase("test_conversation.db")
    
    try:
        # Initialize database
        await db.initialize()
        print("✅ Database initialized successfully")
        
        # Test user ID
        test_user_id = "123456789"
        
        # Add some test conversation data
        print("\n📝 Adding test conversation data...")
        
        # User message 1
        await db.log_user_message(
            user_id=test_user_id,
            username="testuser",
            user_display_name="Test User",
            channel_id="987654321",
            channel_name="general",
            guild_id="111222333",
            guild_name="Test Server",
            message_id="msg_001",
            message_content="Hello, what's the weather like?",
            has_attachments=False,
            timestamp=datetime.utcnow()
        )
        
        # Bot response 1
        await db.log_bot_response(
            original_message_id="msg_001",
            response_message_id="resp_001",
            response_content="I can help you check the weather! What location would you like to know about?",
            processing_time_ms=250,
            model_used="google/gemini-2.5-flash",
            timestamp=datetime.utcnow()
        )
        
        # User message 2
        await db.log_user_message(
            user_id=test_user_id,
            username="testuser",
            user_display_name="Test User",
            channel_id="987654321",
            channel_name="general",
            guild_id="111222333",
            guild_name="Test Server",
            message_id="msg_002",
            message_content="New York City please",
            has_attachments=False,
            timestamp=datetime.utcnow()
        )
        
        # Bot response 2
        await db.log_bot_response(
            original_message_id="msg_002",
            response_message_id="resp_002",
            response_content="**GET_WEATHER:** New York City",
            processing_time_ms=180,
            model_used="google/gemini-2.5-flash",
            timestamp=datetime.utcnow()
        )
        
        # User message 3 with attachments
        await db.log_user_message(
            user_id=test_user_id,
            username="testuser",
            user_display_name="Test User",
            channel_id="987654321",
            channel_name="general",
            guild_id="111222333",
            guild_name="Test Server",
            message_id="msg_003",
            message_content="Can you analyze this image?",
            has_attachments=True,
            attachment_info={"count": 1, "files": [{"filename": "test.jpg", "size": 1024, "content_type": "image/jpeg"}]},
            timestamp=datetime.utcnow()
        )
        
        # Bot response 3
        await db.log_bot_response(
            original_message_id="msg_003",
            response_message_id="resp_003",
            response_content="I can see the image you've shared. It appears to be a photo of a sunset over a city skyline.",
            processing_time_ms=450,
            model_used="google/gemini-2.5-flash",
            timestamp=datetime.utcnow()
        )
        
        print("✅ Test data added successfully")
        
        # Test the conversation context retrieval
        print("\n🔍 Testing conversation context retrieval...")
        
        conversation_context = await db.get_conversation_context(test_user_id, limit=10)
        
        print(f"📊 Retrieved {len(conversation_context)} context messages")
        
        # Display the conversation context
        print("\n💬 Conversation Context:")
        for i, msg in enumerate(conversation_context, 1):
            role = msg["role"]
            content = msg["content"]
            timestamp = msg["timestamp"]
            
            if role == "user":
                has_attachments = msg.get("has_attachments", False)
                attachment_note = " [with attachments]" if has_attachments else ""
                print(f"  {i}. 👤 User{attachment_note}: {content}")
            else:
                model = msg.get("model_used", "unknown")
                print(f"  {i}. 🤖 Bot ({model}): {content}")
            
            print(f"      ⏰ {timestamp}")
            print()
        
        # Test with different limits
        print("🔍 Testing with limit=2...")
        limited_context = await db.get_conversation_context(test_user_id, limit=2)
        print(f"📊 Retrieved {len(limited_context)} context messages with limit=2")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test database
        try:
            os.remove("test_conversation.db")
            print("🧹 Cleaned up test database")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_conversation_context())
