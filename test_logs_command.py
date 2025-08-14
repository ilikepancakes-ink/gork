#!/usr/bin/env python3
"""
Test script to verify the logs command functionality
"""
import asyncio
import os
from datetime import datetime
from utils.database import MessageDatabase

async def test_logs_functionality():
    """Test the logs command database functionality"""
    print("🧪 Testing logs command database functionality...")
    
    # Create a test database
    db = MessageDatabase("test_logs.db")
    
    try:
        # Initialize database
        await db.initialize()
        print("✅ Database initialized successfully")
        
        # Test user ID
        test_user_id = "987654321"
        
        # Add comprehensive test conversation data
        print("\n📝 Adding comprehensive test conversation data...")
        
        conversations = [
            {
                "user_msg": "Hello bot, how are you?",
                "bot_response": "Hello! I'm doing great, thank you for asking. How can I help you today?",
                "has_attachments": False
            },
            {
                "user_msg": "Can you help me with Python programming?",
                "bot_response": "Absolutely! I'd be happy to help you with Python programming. What specific topic or problem would you like assistance with?",
                "has_attachments": False
            },
            {
                "user_msg": "Here's my code that's not working",
                "bot_response": "I can see you've shared some code. Let me analyze it for you and help identify any issues.",
                "has_attachments": True
            },
            {
                "user_msg": "Thanks! That fixed it. Can you explain how loops work?",
                "bot_response": "Great! I'm glad that helped. Loops in Python are used to repeat code. There are two main types: 'for' loops and 'while' loops...",
                "has_attachments": False
            },
            {
                "user_msg": "What about error handling?",
                "bot_response": "Error handling in Python is done using try-except blocks. This allows you to catch and handle exceptions gracefully...",
                "has_attachments": False
            }
        ]
        
        # Add all conversations to database
        for i, conv in enumerate(conversations, 1):
            # Add user message
            await db.log_user_message(
                user_id=test_user_id,
                username="testuser",
                user_display_name="Test User",
                channel_id="123456789",
                channel_name="general",
                guild_id="111222333",
                guild_name="Test Server",
                message_id=f"msg_{i:03d}",
                message_content=conv["user_msg"],
                has_attachments=conv["has_attachments"],
                attachment_info={"count": 1, "files": [{"filename": "code.py", "size": 1024}]} if conv["has_attachments"] else None,
                timestamp=datetime.utcnow()
            )
            
            # Add bot response
            await db.log_bot_response(
                original_message_id=f"msg_{i:03d}",
                response_message_id=f"resp_{i:03d}",
                response_content=conv["bot_response"],
                processing_time_ms=200 + (i * 50),
                model_used="google/gemini-2.5-flash",
                timestamp=datetime.utcnow()
            )
        
        print(f"✅ Added {len(conversations)} conversation exchanges")
        
        # Test the conversation context retrieval (what the logs command uses)
        print("\n🔍 Testing conversation context retrieval...")
        
        conversation_context = await db.get_conversation_context(test_user_id, limit=100)
        
        print(f"📊 Retrieved {len(conversation_context)} context messages")
        
        # Simulate what the logs command would format
        print("\n📋 **Simulated Logs Output:**")
        print("=" * 60)
        
        log_content = f"📋 **Conversation Logs for Test User ({test_user_id})**\n"
        log_content += f"Total messages: {len(conversation_context)}\n"
        log_content += "=" * 50 + "\n\n"
        
        for i, msg in enumerate(conversation_context, 1):
            role = msg["role"]
            content = msg["content"]
            timestamp = msg["timestamp"]
            
            if role == "user":
                has_attachments = msg.get("has_attachments", False)
                attachment_note = " 📎" if has_attachments else ""
                print(f"**{i}. 👤 User{attachment_note}** ({timestamp}):")
                print(f"{content}\n")
            else:
                model = msg.get("model_used", "unknown")
                print(f"**{i}. 🤖 Bot** ({model}) ({timestamp}):")
                print(f"{content}\n")
        
        print("=" * 60)
        print(f"✅ **Log Export Complete**")
        print(f"Total messages: {len(conversation_context)}")
        
        # Test with different user (should return empty)
        print("\n🔍 Testing with non-existent user...")
        empty_context = await db.get_conversation_context("nonexistent_user", limit=100)
        print(f"📊 Retrieved {len(empty_context)} messages for non-existent user (should be 0)")
        
        print("\n✅ All logs command tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test database
        try:
            os.remove("test_logs.db")
            print("🧹 Cleaned up test database")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_logs_functionality())
