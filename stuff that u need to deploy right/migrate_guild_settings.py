#!/usr/bin/env python3
"""
Migration script to add guild_settings table to existing bot database
"""
import sqlite3
import os
import sys

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def migrate_guild_settings():
    """Add guild_settings table to existing database"""
    
    db_path = "data/bot_messages.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please run setup_database.py first to create the database")
        return False
    
    print(f"🔧 Migrating database at {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if guild_settings table already exists
        if check_table_exists(cursor, 'guild_settings'):
            print("ℹ️  guild_settings table already exists - no migration needed")
            conn.close()
            return True
        
        print("📝 Creating guild_settings table...")
        
        # Create guild_settings table
        cursor.execute("""
            CREATE TABLE guild_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL UNIQUE,
                guild_name TEXT,
                random_messages_enabled BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully created guild_settings table")
        print("\n📋 Migration complete!")
        print("\n🎯 Next steps:")
        print("1. Restart your bot to load the new server settings functionality")
        print("2. Server administrators can now use `/server randommessages enabled:True` to enable random messages")
        print("3. Use `/server_status` to view current server settings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def main():
    print("🚀 Guild Settings Migration Script")
    print("=" * 40)
    
    if not migrate_guild_settings():
        print("\n❌ Migration failed!")
        return 1
    
    print("\n🎉 Migration completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
