import sqlite3
import aiosqlite
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os

class MessageDatabase:
    """Database handler for storing bot messages and responses"""
    
    def __init__(self, db_path: str = "bot_messages.db"):
        self.db_path = db_path
        self.initialized = False
    
    async def initialize(self):
        """Initialize the database and create tables if they don't exist"""
        if self.initialized:
            return
            
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Create messages table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    user_display_name TEXT,
                    channel_id TEXT NOT NULL,
                    channel_name TEXT,
                    guild_id TEXT,
                    guild_name TEXT,
                    message_id TEXT NOT NULL UNIQUE,
                    message_content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'user',
                    has_attachments BOOLEAN DEFAULT FALSE,
                    attachment_info TEXT,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create responses table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_message_id TEXT NOT NULL,
                    response_message_id TEXT NOT NULL UNIQUE,
                    response_content TEXT NOT NULL,
                    response_chunks INTEGER DEFAULT 1,
                    chunk_number INTEGER DEFAULT 1,
                    processing_time_ms INTEGER,
                    model_used TEXT,
                    tokens_used INTEGER,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (original_message_id) REFERENCES messages (message_id)
                )
            """)
            
            # Create indexes for better performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages (user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_responses_original_message ON responses (original_message_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON responses (timestamp)")
            
            await db.commit()
        
        self.initialized = True
        print("✅ Message database initialized successfully")
    
    async def log_user_message(self, 
                              user_id: str,
                              username: str,
                              user_display_name: Optional[str],
                              channel_id: str,
                              channel_name: Optional[str],
                              guild_id: Optional[str],
                              guild_name: Optional[str],
                              message_id: str,
                              message_content: str,
                              has_attachments: bool = False,
                              attachment_info: Optional[Dict] = None,
                              timestamp: Optional[datetime] = None) -> bool:
        """Log a user message to the database"""
        if not self.initialized:
            await self.initialize()
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO messages 
                    (user_id, username, user_display_name, channel_id, channel_name, 
                     guild_id, guild_name, message_id, message_content, message_type,
                     has_attachments, attachment_info, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, username, user_display_name, channel_id, channel_name,
                    guild_id, guild_name, message_id, message_content, 'user',
                    has_attachments, json.dumps(attachment_info) if attachment_info else None,
                    timestamp
                ))
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ Error logging user message: {e}")
            return False
    
    async def log_bot_response(self,
                              original_message_id: str,
                              response_message_id: str,
                              response_content: str,
                              response_chunks: int = 1,
                              chunk_number: int = 1,
                              processing_time_ms: Optional[int] = None,
                              model_used: Optional[str] = None,
                              tokens_used: Optional[int] = None,
                              timestamp: Optional[datetime] = None) -> bool:
        """Log a bot response to the database"""
        if not self.initialized:
            await self.initialize()
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO responses 
                    (original_message_id, response_message_id, response_content,
                     response_chunks, chunk_number, processing_time_ms, model_used,
                     tokens_used, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    original_message_id, response_message_id, response_content,
                    response_chunks, chunk_number, processing_time_ms, model_used,
                    tokens_used, timestamp
                ))
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ Error logging bot response: {e}")
            return False
    
    async def get_user_message_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get message history for a specific user"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT m.*,
                           GROUP_CONCAT(r.response_content, ' ') as bot_responses,
                           COUNT(r.id) as response_count
                    FROM messages m
                    LEFT JOIN responses r ON m.message_id = r.original_message_id
                    WHERE m.user_id = ?
                    GROUP BY m.id
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Error getting user message history: {e}")
            return []

    async def get_conversation_context(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation context for a user (alternating user messages and bot responses)"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Get user messages and their corresponding bot responses
                async with db.execute("""
                    SELECT
                        m.message_content as user_message,
                        m.timestamp as user_timestamp,
                        m.has_attachments,
                        m.attachment_info,
                        r.response_content as bot_response,
                        r.timestamp as bot_timestamp,
                        r.model_used
                    FROM messages m
                    LEFT JOIN responses r ON m.message_id = r.original_message_id
                    WHERE m.user_id = ? AND m.message_type = 'user'
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()

                    # Convert to conversation format (most recent first, then reverse for chronological order)
                    conversation = []
                    for row in reversed(rows):  # Reverse to get chronological order
                        row_dict = dict(row)

                        # Add user message
                        user_msg = {
                            "role": "user",
                            "content": row_dict["user_message"],
                            "timestamp": row_dict["user_timestamp"],
                            "has_attachments": row_dict["has_attachments"]
                        }

                        # Parse attachment info if present
                        if row_dict["attachment_info"]:
                            try:
                                user_msg["attachment_info"] = json.loads(row_dict["attachment_info"])
                            except:
                                pass

                        conversation.append(user_msg)

                        # Add bot response if it exists
                        if row_dict["bot_response"]:
                            bot_msg = {
                                "role": "assistant",
                                "content": row_dict["bot_response"],
                                "timestamp": row_dict["bot_timestamp"],
                                "model_used": row_dict["model_used"]
                            }
                            conversation.append(bot_msg)

                    return conversation

        except Exception as e:
            print(f"❌ Error getting conversation context: {e}")
            return []
    
    async def get_conversation_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.initialized:
            await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Total messages
                if user_id:
                    cursor = await db.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
                    stats['total_messages'] = (await cursor.fetchone())[0]
                    
                    cursor = await db.execute("SELECT COUNT(*) FROM responses r JOIN messages m ON r.original_message_id = m.message_id WHERE m.user_id = ?", (user_id,))
                    stats['total_responses'] = (await cursor.fetchone())[0]
                else:
                    cursor = await db.execute("SELECT COUNT(*) FROM messages")
                    stats['total_messages'] = (await cursor.fetchone())[0]
                    
                    cursor = await db.execute("SELECT COUNT(*) FROM responses")
                    stats['total_responses'] = (await cursor.fetchone())[0]
                
                # Unique users (only if not filtering by user)
                if not user_id:
                    cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM messages")
                    stats['unique_users'] = (await cursor.fetchone())[0]
                
                return stats
        except Exception as e:
            print(f"❌ Error getting conversation stats: {e}")
            return {}
    
    async def cleanup_old_messages(self, days_to_keep: int = 30) -> int:
        """Clean up messages older than specified days"""
        if not self.initialized:
            await self.initialize()
        
        try:
            cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Delete old responses first (foreign key constraint)
                cursor = await db.execute("""
                    DELETE FROM responses 
                    WHERE original_message_id IN (
                        SELECT message_id FROM messages WHERE timestamp < ?
                    )
                """, (cutoff_date,))
                responses_deleted = cursor.rowcount
                
                # Delete old messages
                cursor = await db.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff_date,))
                messages_deleted = cursor.rowcount
                
                await db.commit()
                
                total_deleted = messages_deleted + responses_deleted
                print(f"🧹 Cleaned up {messages_deleted} messages and {responses_deleted} responses older than {days_to_keep} days")
                return total_deleted
        except Exception as e:
            print(f"❌ Error cleaning up old messages: {e}")
            return 0
