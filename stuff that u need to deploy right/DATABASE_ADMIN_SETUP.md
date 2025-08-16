# Database Admin Web Interface

This setup provides a web-based administration interface for the bot's message database with secure login functionality, hosted on **gorkdb.ilikepancakes.gay**.

## Features

- 🔐 **Secure Login**: Uses credentials from `ai.env` file
- 🌐 **Custom Domain**: Hosted on gorkdb.ilikepancakes.gay
- 📊 **Dashboard**: Overview of database statistics
- 💬 **Message Management**: View, search, and delete messages
- 🤖 **Response Management**: View bot responses with processing times
- 👥 **User Management**: View user statistics and manage user data
- 📈 **Analytics**: Charts and insights about bot usage
- 🔍 **Search & Filter**: Advanced filtering options
- 📱 **Responsive Design**: Works on desktop and mobile
- 🌍 **Public Access**: Accessible from anywhere on the internet

## Prerequisites

1. **PHP**: You need PHP installed on your system
   - **Arch Linux**: `sudo pacman -S php`
   - **Other Linux**: `sudo apt install php` or `sudo yum install php`
   - **macOS**: `brew install php`
   - **Windows**: Download from https://www.php.net/downloads.php

2. **Python Dependencies**: Make sure you have the required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Network Configuration** (for public domain access):
   - Ensure port 80 is available
   - Configure firewall to allow incoming connections
   - Set up DNS records for gorkdb.ilikepancakes.gay

## Setup Instructions

### 1. Configure Admin Credentials

The admin credentials are stored in your `ai.env` file. The following variables have been added:

```env
# Database admin credentials for web interface
DB_USER="admin"
DB_PASS="admin123"
```

**⚠️ Important**: Change these default credentials to something secure!

### 2. Ensure Database Exists

If you haven't set up the database yet, run:

```bash
python setup_database.py
```

This will create the SQLite database at `data/bot_messages.db`.

### 3. Start the Admin Server

Run the Python script to start the web server:

```bash
python db_admin_server.py
```

The script will:
- Check if PHP is installed
- Find an available port (starting from 8080)
- Create the web interface files
- Start the PHP development server
- Automatically open your browser

### 4. Access the Web Interface

Once the server starts, you'll see output like:

```
✅ Server started successfully!
🌐 Access the admin panel at: http://gorkdb.ilikepancakes.gay
🌐 Server is listening on 0.0.0.0:80
👤 Login credentials:
   Username: admin
   Password: admin123

⚠️  Note: Make sure gorkdb.ilikepancakes.gay points to this server's IP address
```

## Arch Linux Specific Setup

### 1. Install PHP
```bash
sudo pacman -S php
```

### 2. Configure Firewall (if using ufw)
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

### 3. Run as Root (for port 80)
Since port 80 requires root privileges:
```bash
sudo python db_admin_server.py
```

### 4. Alternative: Use Higher Port
If you don't want to run as root, modify the script to use port 8080:
```python
server = DatabaseAdminServer(port=8080, host="0.0.0.0", domain="gorkdb.ilikepancakes.gay")
```

## Quick Arch Linux Setup

For a complete automated setup on Arch Linux:

```bash
# Run the automated setup (requires root)
sudo python setup_arch.py

# Or manual setup:
sudo pacman -S php
sudo ufw allow 80/tcp  # or configure iptables
sudo python db_admin_server.py
```

## Running as a Service

The setup script creates a systemd service for you:

```bash
# Start the service
sudo systemctl start gorkdb

# Enable auto-start on boot
sudo systemctl enable gorkdb

# Check status
sudo systemctl status gorkdb

# View logs
sudo journalctl -u gorkdb -f
```

## Usage

### Login Page
- Enter your DB_USER and DB_PASS credentials
- The system will authenticate against your `ai.env` file

### Dashboard
- View overall statistics (total messages, responses, users)
- Quick navigation to different sections
- Database file information

### Messages Section
- Browse all user messages with pagination
- Search messages by content or username
- Filter by specific users
- Delete individual messages (also removes associated responses)

### Responses Section
- View all bot responses
- See processing times and model usage
- Filter by AI model used
- Delete individual responses

### Users Section
- View all users who have interacted with the bot
- See message counts and activity patterns
- View user-specific message history
- Delete all data for a specific user

### Analytics Section
- Message activity charts (last 30 days)
- Top users by message count
- AI model usage statistics
- Processing time analytics
- Channel activity breakdown

## Security Notes

1. **Change Default Credentials**: The default admin/admin123 credentials should be changed immediately
2. **Local Access Only**: The PHP server only binds to localhost by default
3. **Session Management**: Uses PHP sessions for login state
4. **Input Sanitization**: All user inputs are properly sanitized

## Troubleshooting

### PHP Not Found
```
❌ PHP is not installed or not in PATH
```
**Solution**: Install PHP and ensure it's in your system PATH.

### Port Already in Use
The script automatically finds an available port. If you see port conflicts, the script will try the next available port.

### Database Not Found
```
⚠️ Database not found. Running setup...
```
**Solution**: The script will automatically run `setup_database.py` for you.

### Permission Errors
If you get permission errors accessing the database file, ensure the `data/` directory and `bot_messages.db` file have proper read/write permissions.

## File Structure

```
web_admin/
├── config.php          # Database and authentication configuration
├── login.php           # Login page
├── index.php           # Main dashboard
├── messages.php        # Message management
├── responses.php       # Response management
├── users.php           # User management
└── analytics.php       # Analytics and charts
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running. The script will gracefully shut down the PHP server.

## Advanced Configuration

### Custom Port
You can modify the `DatabaseAdminServer` class in `db_admin_server.py` to use a specific port:

```python
server = DatabaseAdminServer(port=9000)
```

### Custom Database Path
The database path is automatically detected from your bot's configuration. If you need to use a different database file, modify the `DB_PATH` in the generated `config.php` file.

## Support

If you encounter any issues:

1. Check that PHP is properly installed
2. Ensure the database file exists and is readable
3. Verify your `ai.env` file contains the DB_USER and DB_PASS variables
4. Check the terminal output for specific error messages

The web interface provides a clean, secure way to manage your bot's database without needing to use command-line database tools.
