# GorkAI Discord Bot

GorkAI is a powerful, feature-rich Discord bot with advanced AI capabilities, multimedia processing, and extensive integration options.

##  Features

###  AI Chat
- **Intelligent Conversations**: Powered by Google's Gemini 2.5-flash via OpenRouter API
- **Context-Aware**: Maintains conversation history and user profiles
- **Slash Commands**: `/gork`, `/gork_status`, `/gork_commands`
- **Direct Mentions**: Mention the bot in any channel or DM

###  Message Logging & Analytics
- **Comprehensive Logging**: Tracks all user messages and bot responses
- **User Statistics**: `/message_stats` to view your messaging activity
- **Message History**: `/message_history` to view recent conversations
- **Automatic Cleanup**: Maintains database size (90-day retention)
- **Web Admin Panel**: Web interface for administrators to view logs and statistics

###  Multimedia Processing
- **Image Analysis**: Reads and analyzes JPG, PNG, GIF, and other image formats
- **Audio Transcription**: Transcribes MP3, WAV, and MP4 audio files using Whisper AI
- **File Reading**: Processes text files, code files, and documents
- **Video Processing**: Handles video files with audio extraction

###  System Commands
- **Safe System Queries**: Execute safe commands like `fastfetch`, `uptime`, `sensors`
- **Hardware Monitoring**: `/system check` for detailed hardware info
- **Temperature Monitoring**: `/system temps` via sensors command

###  External Integrations
- **Weather Information**: Current and forecast data via WeatherAPI
- **Steam Integration**: Game search, owned games, profile linking
- **Spotify Search**: Song and artist information with preview links
- **Web Search**: Real-time web search using SearchAPI
- **YouTube Transcript**: Summarize videos by pasting YouTube URLs with "summarize"
- **Website Content**: Read and summarize web page content

###  User Management
- **Profiles**: `/profile` to view user information
- **Settings**: `/my_settings` to manage personal preferences
- **Content Filtering**: Configure NSFW mode and content filters
- **Steam Linking**: `/link_steam` to connect Steam account for enhanced features
## Use the offical bot:
https://discord.com/oauth2/authorize?client_id=1404861614670352437
or...
## Self-Deployment

### Prerequisites
- Python 3.8+
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Optional API Keys for full features:
  - OpenRouter API Key (for AI chat)
  - SearchAPI Key (for web search)
  - WeatherAPI Key (for weather)
  - Spotify Client ID & Secret (for music search)
  - Steam Web API Key (for Steam integration)

### 1. Clone and Setup
```bash
git clone https://github.com/ilikepancakes-ink/gork.git
cd gork

# Install Python dependencies
pip install -r requirements.txt

# Setup database
python setup_database.py
```

### 2. Configuration
Copy the example environment file and configure:
```bash
cp templates/ai.env.example ai.env
```

Edit `ai.env` with your API keys:
```env
DISCORD_TOKEN=your_discord_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional (remove lines if not using)
SEARCHAPI_KEY=your_searchapi_key_here
WEATHERAPI_KEY=your_weatherapi_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
DB_USER=admin
DB_PASS=secure_password_123
```

### 3. Deploy the Bot
```bash
python gork.py
```

### 4. (Optional) Admin Web Interface
For advanced log viewing and administration:
```bash
python stuff\that\u\need\to\deploy\right/db_admin_server.py
```

Access via web browser with configured credentials from `ai.env`.

### 5. (Optional) System Service (Linux)
For production deployment on Arch Linux:
```bash
# Install PHP and configure firewall
python stuff/that/u/need/to/deploy/right/setup_arch.py

# Start service
sudo systemctl start gorkdb
```

##  Configuration Options

### Environment Variables
- `DISCORD_TOKEN`: **Required** - Your Discord bot token
- `OPENROUTER_API_KEY`: **Required** - For AI chat functionality
- `SEARCHAPI_KEY`: Optional - Enables web search
- `WEATHERAPI_KEY`: Optional - Enables weather features
- `SPOTIFY_CLIENT_ID`: Optional - Spotify integration
- `SPOTIFY_CLIENT_SECRET`: Optional - Spotify integration
- `DB_USER`: Default admin username for web panel
- `DB_PASS`: Default admin password (change from default!)

### Bot Commands
**Chat:**
- Mention bot or `@bot message` - AI conversation
- `/gork message:text` - Slash command chat

**System Info:**
- `/system check` - Hardware and system details
- `/system temps` - Sensor temperatures
- `/gork_commands` - List available system commands

**User Features:**
- `/profile [user]` - View user profile
- `/my_settings` - Personal settings
- `/nsfw_mode enabled:true/false` - Toggle NSFW content
- `/content_filter level:(strict/moderate/minimal)` - Content filtering

**Messaging:**
- `/message_stats [user]` - Message statistics
- `/message_history limit:10` - Recent messages

**External Services:**
- `/weather location:[city]` - Current weather
- `/forecast location:[city] days:3` - Weather forecast
- `/gork_status` - Bot status and capabilities

**Music & Games:**
- `/steam_search game_name:game` - Steam game search
- `/spotify_search query:song` - Spotify music search
- `/link_steam customurl:username` - Link Steam account

##  Architecture

### Directory Structure
```
gork/
├── gork.py                 # Main bot application
├── cogs/                   # Bot functionality modules
│   ├── gork.py            # AI chat and integration engine
│   ├── hwinfo.py          # Hardware monitoring commands
│   ├── weather.py         # Weather service integration
│   ├── message_logger.py  # Database logging system
│   ├── userprofile.py     # User profile commands
│   ├── usersettings.py    # User settings management
│   ├── steam_tool.py      # Steam API integration
│   └── ...
├── utils/                  # Utility functions
│   ├── database.py        # SQLite database operations
│   ├── content_filter.py  # Content filtering logic
│   └── ...
├── web_admin/             # Admin web interface (PHP)
├── data/                  # Bot data (created at runtime)
├── templates/             # Configuration templates
└── stuff that u need to deploy right/  # Deploy scripts
```

### Database Schema
- **Messages**: User messages, attachments, metadata
- **Responses**: Bot responses, processing times, AI model used
- **Users**: Profiles, settings, NSFW preferences
- **Guilds**: Server-specific settings

##  Security & Privacy

- **Self-Hosted**: Run your own instance, keep your data private
- **Content Filtering**: Configurable filtering levels per user
- **NSFW Controls**: User opt-in for mature content
- **Admin Controls**: Restricted admin commands and web access
- **Data Retention**: Automatic cleanup (90-day default)

##  Troubleshooting

### Bot Won't Start
- Verify `DISCORD_TOKEN` in `ai.env`
- Check Python version (3.8+)
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Database initialized: `python setup_database.py`

### Features Not Working
- Check optional API keys in `ai.env`
- Verify API service status
- Review console output for error messages

### Web Admin Not Loading
- Ensure PHP is installed
- Check port availability (default 8080)
- Verify DNS configuration if using custom domain
- Check login credentials from `ai.env`

##  Performance Notes

- **Database Growth**: Logs are automatically cleaned up (90 days)
- **Memory Usage**: Scales with user activity and conversation size
- **API Limits**: Respect external API rate limits
- **Disk Space**: Monitor database size for large deployments

##  Support

For issues, feature requests, or contributions:
- Check existing issues on GitHub
- Join our Discord server: [Add Discord link if available]
- Review documentation and examples

## License

This project is licensed under the terms specified in the LICENSE file.
