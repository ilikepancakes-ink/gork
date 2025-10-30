import sqlite3
import aiosqlite
import asyncio
from datetime import datetime, timedelta
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
            
        
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            
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
            
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    username TEXT,
                    user_display_name TEXT,
                    nsfw_mode BOOLEAN DEFAULT FALSE,
                    content_filter_level TEXT DEFAULT 'strict',
                    steam_id TEXT,
                    steam_username TEXT,
                    steam_linked_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL UNIQUE,
                    guild_name TEXT,
                    random_messages_enabled BOOLEAN DEFAULT FALSE,
                    bot_reply_enabled BOOLEAN DEFAULT FALSE,
                    reply_all_enabled BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channel_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL UNIQUE,
                    guild_id TEXT NOT NULL,
                    reply_all_enabled BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    summary_text TEXT NOT NULL,
                    message_count_at_update INTEGER NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages (user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_responses_original_message ON responses (original_message_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON responses (timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings (user_id)")

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

                    
                    conversation = []
                    for row in reversed(rows):  
                        row_dict = dict(row)

                        
                        user_msg = {
                            "role": "user",
                            "content": row_dict["user_message"],
                            "timestamp": row_dict["user_timestamp"],
                            "has_attachments": row_dict["has_attachments"]
                        }

                        
                        if row_dict["attachment_info"]:
                            try:
                                user_msg["attachment_info"] = json.loads(row_dict["attachment_info"])
                            except:
                                pass

                        conversation.append(user_msg)

                        
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
            cutoff_date = cutoff_date - timedelta(days=days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("""
                    DELETE FROM responses 
                    WHERE original_message_id IN (
                        SELECT message_id FROM messages WHERE timestamp < ?
                    )
                """, (cutoff_date,))
                responses_deleted = cursor.rowcount
                
                
                cursor = await db.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff_date,))
                messages_deleted = cursor.rowcount
                
                await db.commit()
                
                total_deleted = messages_deleted + responses_deleted
                print(f"🧹 Cleaned up {messages_deleted} messages and {responses_deleted} responses older than {days_to_keep} days")
                return total_deleted
        except Exception as e:
            print(f"❌ Error cleaning up old messages: {e}")
            return 0

    async def get_user_settings(self, user_id: str) -> dict:
        """Get user settings, creating default settings if they don't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, username, user_display_name, nsfw_mode, content_filter_level,
                           steam_id, steam_username, steam_linked_at,
                           created_at, updated_at
                    FROM user_settings
                    WHERE user_id = ?
                """, (user_id,))

                result = await cursor.fetchone()

                if result:
                    return {
                        'user_id': result[0],
                        'username': result[1],
                        'user_display_name': result[2],
                        'nsfw_mode': bool(result[3]),
                        'content_filter_level': result[4],
                        'steam_id': result[5],
                        'steam_username': result[6],
                        'steam_linked_at': result[7],
                        'created_at': result[8],
                        'updated_at': result[9]
                    }
                else:
                    
                    default_settings = {
                        'user_id': user_id,
                        'username': None,
                        'user_display_name': None,
                        'nsfw_mode': False,
                        'content_filter_level': 'strict',
                        'steam_id': None,
                        'steam_username': None,
                        'steam_linked_at': None,
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    return default_settings

        except Exception as e:
            print(f"❌ Error getting user settings: {e}")
            
            return {
                'user_id': user_id,
                'username': None,
                'user_display_name': None,
                'nsfw_mode': False,
                'content_filter_level': 'strict',
                'steam_id': None,
                'steam_username': None,
                'steam_linked_at': None,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

    async def update_user_settings(self, user_id: str, username: str = None, user_display_name: str = None,
                                 nsfw_mode: bool = None, content_filter_level: str = None,
                                 steam_id: str = None, steam_username: str = None) -> bool:
        """Update user settings, creating the record if it doesn't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("SELECT user_id FROM user_settings WHERE user_id = ?", (user_id,))
                exists = await cursor.fetchone()

                current_time = datetime.utcnow().isoformat()

                if exists:
                    
                    update_fields = []
                    update_values = []

                    if username is not None:
                        update_fields.append("username = ?")
                        update_values.append(username)

                    if user_display_name is not None:
                        update_fields.append("user_display_name = ?")
                        update_values.append(user_display_name)

                    if nsfw_mode is not None:
                        update_fields.append("nsfw_mode = ?")
                        update_values.append(nsfw_mode)

                    if content_filter_level is not None:
                        update_fields.append("content_filter_level = ?")
                        update_values.append(content_filter_level)

                    if steam_id is not None:
                        update_fields.append("steam_id = ?")
                        update_values.append(steam_id)
                        
                        update_fields.append("steam_linked_at = ?")
                        update_values.append(current_time)

                    if steam_username is not None:
                        update_fields.append("steam_username = ?")
                        update_values.append(steam_username)

                    if update_fields:
                        update_fields.append("updated_at = ?")
                        update_values.append(current_time)
                        update_values.append(user_id)  

                        query = f"UPDATE user_settings SET {', '.join(update_fields)} WHERE user_id = ?"
                        await db.execute(query, update_values)
                else:
                    
                    await db.execute("""
                        INSERT INTO user_settings (user_id, username, user_display_name, nsfw_mode,
                                                 content_filter_level, steam_id, steam_username,
                                                 steam_linked_at, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, username, user_display_name,
                         nsfw_mode if nsfw_mode is not None else False,
                         content_filter_level if content_filter_level is not None else 'strict',
                         steam_id, steam_username,
                         current_time if steam_id else None,
                         current_time, current_time))

                await db.commit()
                return True

        except Exception as e:
            print(f"❌ Error updating user settings: {e}")
            return False

    async def get_guild_settings(self, guild_id: str) -> dict:
        """Get guild settings, creating default settings if they don't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT guild_id, guild_name, random_messages_enabled, bot_reply_enabled, reply_all_enabled, created_at, updated_at
                    FROM guild_settings
                    WHERE guild_id = ?
                """, (guild_id,))

                result = await cursor.fetchone()

                if result:
                    return {
                        'guild_id': result[0],
                        'guild_name': result[1],
                        'random_messages_enabled': bool(result[2]),
                        'bot_reply_enabled': bool(result[3]),
                        'reply_all_enabled': bool(result[4]),
                        'created_at': result[5],
                        'updated_at': result[6]
                    }
                else:
                    
                    default_settings = {
                        'guild_id': guild_id,
                        'guild_name': None,
                        'random_messages_enabled': False,
                        'bot_reply_enabled': False,
                        'reply_all_enabled': False,
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    return default_settings

        except Exception as e:
            print(f"❌ Error getting guild settings: {e}")
            
            return {
                'guild_id': guild_id,
                'guild_name': None,
                'random_messages_enabled': False,
                'bot_reply_enabled': False,
                'reply_all_enabled': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

    async def update_guild_settings(self, guild_id: str, guild_name: str = None,
                                  random_messages_enabled: bool = None,
                                  bot_reply_enabled: bool = None,
                                  reply_all_enabled: bool = None) -> bool:
        """Update guild settings, creating the record if it doesn't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            current_time = datetime.utcnow().isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("SELECT guild_id FROM guild_settings WHERE guild_id = ?", (guild_id,))
                exists = await cursor.fetchone()

                if exists:
                    
                    update_fields = []
                    update_values = []

                    if guild_name is not None:
                        update_fields.append("guild_name = ?")
                        update_values.append(guild_name)

                    if random_messages_enabled is not None:
                        update_fields.append("random_messages_enabled = ?")
                        update_values.append(random_messages_enabled)

                    if bot_reply_enabled is not None:
                        update_fields.append("bot_reply_enabled = ?")
                        update_values.append(bot_reply_enabled)

                    if reply_all_enabled is not None:
                        update_fields.append("reply_all_enabled = ?")
                        update_values.append(reply_all_enabled)

                    if update_fields:
                        update_fields.append("updated_at = ?")
                        update_values.append(current_time)
                        update_values.append(guild_id)  

                        query = f"UPDATE guild_settings SET {', '.join(update_fields)} WHERE guild_id = ?"
                        await db.execute(query, update_values)
                else:
                    
                    await db.execute("""
                        INSERT INTO guild_settings (guild_id, guild_name, random_messages_enabled,
                                                  bot_reply_enabled, reply_all_enabled,
                                                  created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (guild_id, guild_name,
                         random_messages_enabled if random_messages_enabled is not None else False,
                         bot_reply_enabled if bot_reply_enabled is not None else False,
                         reply_all_enabled if reply_all_enabled is not None else False,
                         current_time, current_time))

                await db.commit()
                return True

        except Exception as e:
            print(f"❌ Error updating guild settings: {e}")
            return False

    async def get_channel_settings(self, channel_id: str, guild_id: str) -> dict:
        """Get channel settings, creating default settings if they don't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT channel_id, guild_id, reply_all_enabled, created_at, updated_at
                    FROM channel_settings
                    WHERE channel_id = ?
                """, (channel_id,))

                result = await cursor.fetchone()

                if result:
                    return {
                        'channel_id': result[0],
                        'guild_id': result[1],
                        'reply_all_enabled': bool(result[2]),
                        'created_at': result[3],
                        'updated_at': result[4]
                    }
                else:
                    
                    default_settings = {
                        'channel_id': channel_id,
                        'guild_id': guild_id,
                        'reply_all_enabled': False,
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    return default_settings

        except Exception as e:
            print(f"❌ Error getting channel settings: {e}")
            
            return {
                'channel_id': channel_id,
                'guild_id': guild_id,
                'reply_all_enabled': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

    async def update_channel_settings(self, channel_id: str, guild_id: str,
                                  reply_all_enabled: bool = None) -> bool:
        """Update channel settings, creating the record if it doesn't exist"""
        if not self.initialized:
            await self.initialize()

        try:
            current_time = datetime.utcnow().isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("SELECT channel_id FROM channel_settings WHERE channel_id = ?", (channel_id,))
                exists = await cursor.fetchone()

                if exists:
                    
                    update_fields = []
                    update_values = []

                    if reply_all_enabled is not None:
                        update_fields.append("reply_all_enabled = ?")
                        update_values.append(reply_all_enabled)

                    if update_fields:
                        update_fields.append("updated_at = ?")
                        update_values.append(current_time)
                        update_values.append(channel_id)  

                        query = f"UPDATE channel_settings SET {', '.join(update_fields)} WHERE channel_id = ?"
                        await db.execute(query, update_values)
                else:
                    
                    await db.execute("""
                        INSERT INTO channel_settings (channel_id, guild_id, reply_all_enabled,
                                                  created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (channel_id, guild_id,
                         reply_all_enabled if reply_all_enabled is not None else False,
                         current_time, current_time))

                await db.commit()
                return True

        except Exception as e:
            print(f"❌ Error updating channel settings: {e}")
            return False

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> List[str]:
        """Get recent messages from a specific channel for random message generation"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT message_content
                    FROM messages
                    WHERE channel_id = ? AND message_type = 'user' AND message_content != ''
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (channel_id, limit))

                results = await cursor.fetchall()
                return [row[0] for row in results]

        except Exception as e:
            print(f"❌ Error getting channel messages: {e}")
            return []

    async def get_users_with_nsfw_enabled(self) -> list:
        """Get all users who have NSFW mode enabled"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, username, user_display_name, content_filter_level, updated_at
                    FROM user_settings
                    WHERE nsfw_mode = TRUE
                    ORDER BY updated_at DESC
                """)

                results = await cursor.fetchall()

                return [
                    {
                        'user_id': row[0],
                        'username': row[1],
                        'user_display_name': row[2],
                        'content_filter_level': row[3],
                        'updated_at': row[4]
                    }
                    for row in results
                ]

        except Exception as e:
            print(f"❌ Error getting users with NSFW enabled: {e}")
            return []

    async def delete_user_settings(self, user_id: str) -> bool:
        """Delete a user's settings from the database."""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ Error deleting user settings for {user_id}: {e}")
            return False

    async def validate_steam_id_link(self, steam_id: str, user_id: str) -> dict:
        """
        Validate Steam ID linking with checks for:
        1. Steam ID format
        2. Uniqueness across users
        3. Preventing multiple links to the same Steam ID

        Returns a dictionary with validation results
        """
        if not self.initialized:
            await self.initialize()

        try:
            
            if not steam_id or not steam_id.isdigit() or len(steam_id) != 17:
                return {
                    'valid': False,
                    'error': 'Invalid Steam ID format. Must be a 17-digit number.'
                }

            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("""
                    SELECT user_id FROM user_settings 
                    WHERE steam_id = ? AND user_id != ?
                """, (steam_id, user_id))
                existing_link = await cursor.fetchone()

                if existing_link:
                    return {
                        'valid': False,
                        'error': 'This Steam ID is already linked to another user.'
                    }

                
                cursor = await db.execute("""
                    SELECT steam_id FROM user_settings 
                    WHERE user_id = ? AND steam_id IS NOT NULL AND steam_id != ?
                """, (user_id, steam_id))
                current_steam_id = await cursor.fetchone()

                if current_steam_id and current_steam_id[0] != steam_id:
                    return {
                        'valid': False,
                        'error': 'User already has a different Steam ID linked.'
                    }

                
                return {
                    'valid': True,
                    'message': 'Steam ID is valid and can be linked.'
                }

        except Exception as e:
            print(f"❌ Error validating Steam ID: {e}")
            return {
                'valid': False,
                'error': 'An unexpected error occurred during Steam ID validation.'
            }

    async def get_user_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's summary if it exists"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, summary_text, message_count_at_update,
                           last_updated, created_at
                    FROM user_summaries
                    WHERE user_id = ?
                """, (user_id,))

                result = await cursor.fetchone()

                if result:
                    return {
                        'user_id': result[0],
                        'summary_text': result[1],
                        'message_count_at_update': result[2],
                        'last_updated': result[3],
                        'created_at': result[4]
                    }
                return None

        except Exception as e:
            print(f"❌ Error getting user summary: {e}")
            return None

    async def update_user_summary(self, user_id: str, summary_text: str, message_count: int) -> bool:
        """Update or create a user's summary"""
        if not self.initialized:
            await self.initialize()

        try:
            current_time = datetime.utcnow().isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                
                cursor = await db.execute("SELECT user_id FROM user_summaries WHERE user_id = ?", (user_id,))
                exists = await cursor.fetchone()

                if exists:
                    
                    await db.execute("""
                        UPDATE user_summaries
                        SET summary_text = ?, message_count_at_update = ?, last_updated = ?
                        WHERE user_id = ?
                    """, (summary_text, message_count, current_time, user_id))
                else:
                    
                    await db.execute("""
                        INSERT INTO user_summaries (user_id, summary_text, message_count_at_update,
                                                  last_updated, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, summary_text, message_count, current_time, current_time))

                await db.commit()
                return True

        except Exception as e:
            print(f"❌ Error updating user summary: {e}")
            return False

    async def get_message_count_for_user(self, user_id: str) -> int:
        """Get the total number of messages for a user"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"❌ Error getting message count for user: {e}")
            return 0

    async def get_recent_user_messages_for_summary(self, user_id: str, limit: int = 10) -> List[str]:
        """Get recent messages for a user to generate summary"""
        if not self.initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT message_content
                    FROM messages
                    WHERE user_id = ? AND message_type = 'user' AND message_content != ''
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))

                results = await cursor.fetchall()
                
                return [row[0] for row in reversed(results)]

        except Exception as e:
            print(f"❌ Error getting recent messages for summary: {e}")
            return []
