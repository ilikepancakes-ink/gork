#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
from pathlib import Path
import socket
from dotenv import load_dotenv

class DatabaseAdminServer:
    def __init__(self, port=80, host="0.0.0.0", domain="gorkdb.ilikepancakes.gay"):
        self.port = port
        self.host = host
        self.domain = domain
        self.php_process = None
        self.server_root = Path(__file__).parent / "web_admin"

        load_dotenv("ai.env")
        self.db_user = os.getenv("DB_USER", "admin")
        self.db_pass = os.getenv("DB_PASS", "admin123")
        
    def check_php_installed(self):
        try:
            result = subprocess.run(["php", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ PHP is installed: {result.stdout.split()[0]} {result.stdout.split()[1]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ PHP is not installed or not in PATH")
            print("Please install PHP from https://www.php.net/downloads.php")
            return False
    
    def find_available_port(self, start_port=80):
        port = start_port
        while port < start_port + 100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                port += 1
        raise RuntimeError("Could not find an available port")
    
    def setup_web_files(self):
        self.server_root.mkdir(exist_ok=True)

        db_path = Path("data/bot_messages.db").absolute()
        
        print(f"🔧 Setting up web files in {self.server_root}")
        print(f"📁 Database path: {db_path}")
        
        db_path_php = str(db_path).replace('\\', '/')

        config_content = f"""<?php
define('DB_PATH', '{db_path_php}');
define('ADMIN_USER', '{self.db_user}');
define('ADMIN_PASS', '{self.db_pass}');

session_start();

function isLoggedIn() {{
    return isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true;
}}

function requireLogin() {{
    if (!isLoggedIn()) {{
        header('Location: login.php');
        exit;
    }}
}}
?>"""
        
        with open(self.server_root / "config.php", "w") as f:
            f.write(config_content)
        
        print("✅ Created config.php")
        return True
    
    def start_server(self):
        if not self.check_php_installed():
            return False
        
        if not self.setup_web_files():
            return False

        try:
            self.port = self.find_available_port(self.port)
        except RuntimeError as e:
            print(f"❌ {e}")
            return False
        
        print(f"🚀 Starting PHP server on port {self.port}")
        print(f"📁 Server root: {self.server_root}")
        
        try:
            cmd = [
                "php", "-S", f"{self.host}:{self.port}",
                "-t", str(self.server_root)
            ]
            
            self.php_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            time.sleep(2)

            if self.php_process.poll() is None:
                url = f"http://{self.domain}"
                if self.port != 80:
                    url += f":{self.port}"

                print(f"✅ Server started successfully!")
                print(f"🌐 Access the admin panel at: {url}")
                print(f"🌐 Server is listening on {self.host}:{self.port}")
                print(f"👤 Login credentials:")
                print(f"   Username: {self.db_user}")
                print(f"   Password: {self.db_pass}")
                print("\n🔧 Press Ctrl+C to stop the server")
                print(f"\n⚠️  Note: Make sure {self.domain} points to this server's IP address")

                print("🌐 Navigate to the URL manually in your browser")
                
                return True
            else:
                stdout, stderr = self.php_process.communicate()
                print(f"❌ Server failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        if self.php_process and self.php_process.poll() is None:
            print("\n🛑 Stopping server...")
            self.php_process.terminate()
            try:
                self.php_process.wait(timeout=5)
                print("✅ Server stopped successfully")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing server...")
                self.php_process.kill()
                self.php_process.wait()
                print("✅ Server force stopped")
    
    def run(self):
        try:
            if self.start_server():
                while True:
                    if self.php_process.poll() is not None:
                        print("❌ Server process died unexpectedly")
                        break
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_server()

def main():
    print("🔧 Database Admin Server - gorkdb.ilikepancakes.gay")
    print("=" * 60)

    db_path = Path("data/bot_messages.db")
    if not db_path.exists():
        print("⚠️  Database not found. Running setup...")
        try:
            subprocess.run([sys.executable, "setup_database.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to setup database. Please run setup_database.py first.")
            return 1

    server = DatabaseAdminServer(port=8080, host="0.0.0.0", domain="gorkdb.ilikepancakes.gay")

    print("\n🌐 Server Configuration:")
    print(f"   Domain: {server.domain}")
    print(f"   Host: {server.host}")
    print(f"   Port: {server.port}")
    print("\n⚠️  Important DNS Setup:")
    print(f"   Make sure {server.domain} points to this server's public IP address")
    print("   You may need to configure your router/firewall to allow incoming connections on port 80")
    print("\n🔒 Security Note:")
    print("   The server will be accessible from the internet. Ensure you have strong admin credentials!")

    server.run()
    return 0

if __name__ == "__main__":
    sys.exit(main())
