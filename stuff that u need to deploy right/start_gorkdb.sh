#!/bin/bash
# Startup script for gorkdb.ilikepancakes.gay on Arch Linux

echo "🚀 Starting GorkDB Admin Server"
echo "================================"

# Check if running as root (needed for port 80)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Not running as root. Port 80 may not be available."
    echo "   Run with: sudo ./start_gorkdb.sh"
    echo "   Or the server will try to find an alternative port."
    echo ""
fi

# Check if PHP is installed
if ! command -v php &> /dev/null; then
    echo "❌ PHP is not installed"
    echo "Install with: sudo pacman -S php"
    exit 1
fi

# Check if Python dependencies are installed
if ! python -c "import dotenv" &> /dev/null; then
    echo "❌ Python dependencies missing"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi

# Check if database exists
if [ ! -f "data/bot_messages.db" ]; then
    echo "⚠️  Database not found. Setting up..."
    python setup_database.py
fi

# Check if ai.env has the required variables
if ! grep -q "DB_USER=" ai.env || ! grep -q "DB_PASS=" ai.env; then
    echo "❌ DB_USER and DB_PASS not found in ai.env"
    echo "Please add these variables to your ai.env file"
    exit 1
fi

echo "✅ All prerequisites met"
echo ""
echo "🌐 Starting server for gorkdb.ilikepancakes.gay"
echo "📡 Make sure the domain points to this server's IP address"
echo ""

# Start the server
python db_admin_server.py
