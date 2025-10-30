
"""
Database migration script to add user_settings table for NSFW mode functionality.
This script safely adds the new table without affecting existing data.
"""

import os
import sqlite3
import sys
from datetime import datetime

def check_database_exists(db_path):
    """Check if the database file exists"""
    return os.path.exists(db_path)

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def backup_database(db_path):
    """Create a backup of the database before migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def migrate_database(db_path):
    """Perform the database migration"""
    print(f"🔄 Starting migration for database: {db_path}")
    
    
    if not check_database_exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ Migration aborted - could not create backup")
        return False
    
    try:
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        
        if check_table_exists(cursor, 'user_settings'):
            print("ℹ️  user_settings table already exists - no migration needed")
            conn.close()
            return True
        
        print("📝 Creating user_settings table...")
        
        
        cursor.execute("""
            CREATE TABLE user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                username TEXT,
                user_display_name TEXT,
                nsfw_mode BOOLEAN DEFAULT FALSE,
                content_filter_level TEXT DEFAULT 'strict',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE INDEX idx_user_settings_user_id ON user_settings (user_id)
        """)
        
        
        conn.commit()
        
        
        if check_table_exists(cursor, 'user_settings'):
            print("✅ user_settings table created successfully")
            
            
            cursor.execute("PRAGMA table_info(user_settings)")
            columns = cursor.fetchall()
            print(f"📋 Table structure verified - {len(columns)} columns created")
            
            conn.close()
            return True
        else:
            print("❌ Failed to create user_settings table")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            conn.close()
        except:
            pass
        return False

def main():
    """Main migration function"""
    print("🚀 NSFW Mode Database Migration")
    print("=" * 40)
    
    
    default_db_path = "data/bot_messages.db"
    
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = default_db_path
    
    print(f"📁 Database path: {db_path}")
    
    
    success = migrate_database(db_path)
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your bot to load the new user settings functionality")
        print("2. Users can now use the following commands:")
        print("   • /nsfw_mode - Enable/disable NSFW content")
        print("   • /content_filter - Set content filtering level")
        print("   • /my_settings - View current settings")
        print("\n⚠️  Important notes:")
        print("• NSFW mode is disabled by default for all users")
        print("• Users must explicitly enable NSFW mode to access mature content")
        print("• All settings are private and user-specific")
        print("• Content filtering respects Discord's Terms of Service")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        print("If the problem persists, please restore from backup and contact support.")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
