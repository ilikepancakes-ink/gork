# Message Logging System for Gork Bot

The bot now automatically saves all messages sent to it and its responses in a SQLite database, organized per user. This provides conversation history, analytics, and performance tracking.

## Features

### 🗄️ Database Storage
- **SQLite Database**: Lightweight, serverless database stored in `data/bot_messages.db`
- **User Messages**: Stores all messages sent to the bot (mentions, DMs, slash commands)
- **Bot Responses**: Stores all bot responses with metadata
- **Performance Metrics**: Tracks processing time for each response
- **Attachment Info**: Records information about files/images sent to the bot

### 📊 Data Tracked

#### User Messages
- User ID, username, and display name
- Channel and server information
- Message content and timestamp
- Attachment information (filenames, sizes, types)
- Message type (regular message vs slash command)

#### Bot Responses
- Response content and timestamp
- Processing time in milliseconds
- AI model used for the response
- Multi-chunk response handling
- Link to original user message

### 🎯 User Commands

#### `/message_stats [user]`
- View message statistics for yourself or another user
- Shows total messages sent and responses received
- Server owners can see overall bot statistics

#### `/message_history [limit]`
- View your recent message history (private/ephemeral)
- Shows up to 50 recent messages with timestamps
- Indicates which messages received bot responses

### 🔧 Admin Commands (Bot Owner Only)

#### `!cleanup_messages [days]`
- Manually clean up messages older than specified days (default: 30)
- Helps manage database size

#### `!db_stats`
- View detailed database statistics
- Shows total messages, responses, unique users, and database size

## Setup Instructions

### 1. Install Dependencies
The required dependency `aiosqlite` has been added to `requirements.txt`. Install it with:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
Run the setup script to create the database and data directory:
```bash
python setup_database.py
```

### 3. Restart the Bot
Restart your bot to load the new message logging functionality:
```bash
python bot.py
```

## Database Schema

### Messages Table
```sql
CREATE TABLE messages (
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
);
```

### Responses Table
```sql
CREATE TABLE responses (
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
);
```

## Automatic Features

### 🧹 Automatic Cleanup
- Runs daily to remove messages older than 90 days
- Prevents database from growing too large
- Configurable retention period

### 📈 Performance Tracking
- Measures response time for each AI interaction
- Helps identify performance issues
- Useful for optimization

### 🔒 Privacy Features
- Message history command is ephemeral (private)
- Users can only see their own message history
- Admin commands are restricted to bot owner

## File Structure

```
├── utils/
│   └── database.py          # Database utility class
├── cogs/
│   └── message_logger.py    # Message logging cog
├── data/
│   └── bot_messages.db      # SQLite database (created automatically)
├── setup_database.py        # Database setup script
└── MESSAGE_LOGGING_SETUP.md # This documentation
```

## Usage Examples

### For Users
```
# View your message statistics
/message_stats

# View your recent message history (last 10 messages)
/message_history 10

# View another user's stats (if you have permissions)
/message_stats @username
```

### For Bot Owners
```
# View database statistics
!db_stats

# Clean up messages older than 60 days
!cleanup_messages 60
```

## Technical Details

### Database Location
- Default: `data/bot_messages.db`
- Automatically created on first run
- Uses SQLite for maximum compatibility

### Performance
- Asynchronous database operations
- Indexed for fast queries
- Minimal impact on bot response time

### Error Handling
- Graceful degradation if database is unavailable
- Comprehensive error logging
- Non-blocking operations

## Troubleshooting

### Database Not Created
1. Ensure the `data/` directory exists
2. Check file permissions
3. Run `python setup_database.py`

### Commands Not Working
1. Restart the bot after setup
2. Check that the MessageLogger cog is loaded
3. Verify database file exists and is accessible

### Performance Issues
1. Run database cleanup: `!cleanup_messages`
2. Check database size with `!db_stats`
3. Consider reducing retention period

## Privacy and Data Protection

- All data is stored locally in SQLite
- No external services or cloud storage
- Users can request their data through message history
- Automatic cleanup prevents indefinite data retention
- Bot owner has full control over data retention policies

The message logging system is now fully integrated and will automatically start tracking conversations once the bot is restarted!
