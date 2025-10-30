
"""
Arch Linux setup script for gorkdb.ilikepancakes.gay
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_root():
    """Check if running as root"""
    return os.geteuid() == 0

def install_php():
    """Install PHP on Arch Linux"""
    print("📦 Installing PHP...")
    success, stdout, stderr = run_command("pacman -S --noconfirm php")
    if success:
        print("✅ PHP installed successfully")
        return True
    else:
        print(f"❌ Failed to install PHP: {stderr}")
        return False

def setup_firewall():
    """Setup firewall rules for port 80"""
    print("🔥 Configuring firewall...")
    
    
    success, _, _ = run_command("which ufw", check=False)
    if success:
        print("Using ufw...")
        run_command("ufw allow 80/tcp")
        run_command("ufw --force enable")
        print("✅ Firewall configured with ufw")
        return True
    
    
    success, _, _ = run_command("which iptables", check=False)
    if success:
        print("Using iptables...")
        run_command("iptables -A INPUT -p tcp --dport 80 -j ACCEPT")
        run_command("iptables-save > /etc/iptables/iptables.rules")
        print("✅ Firewall configured with iptables")
        return True
    
    print("⚠️  No firewall tool found. Please manually allow port 80")
    return False

def setup_systemd_service():
    """Setup systemd service"""
    print("⚙️  Setting up systemd service...")
    
    current_dir = Path.cwd().absolute()
    service_content = f"""[Unit]
Description=GorkDB Admin Server for gorkdb.ilikepancakes.gay
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory={current_dir}
ExecStart=/usr/bin/python {current_dir}/db_admin_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal


NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={current_dir}/data
ReadWritePaths={current_dir}/web_admin

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path("/etc/systemd/system/gorkdb.service")
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        
        run_command("systemctl daemon-reload")
        run_command("systemctl enable gorkdb.service")
        
        print("✅ Systemd service created and enabled")
        print("   Start with: sudo systemctl start gorkdb")
        print("   Stop with: sudo systemctl stop gorkdb")
        print("   Status: sudo systemctl status gorkdb")
        return True
    except Exception as e:
        print(f"❌ Failed to create systemd service: {e}")
        return False

def main():
    print("🏗️  Arch Linux Setup for gorkdb.ilikepancakes.gay")
    print("=" * 60)
    
    if not check_root():
        print("❌ This script must be run as root")
        print("Run with: sudo python setup_arch.py")
        return 1
    
    
    success, _, _ = run_command("which php", check=False)
    if not success:
        if not install_php():
            return 1
    else:
        print("✅ PHP is already installed")
    
    
    if not Path("data/bot_messages.db").exists():
        print("🗄️  Setting up database...")
        success, stdout, stderr = run_command("python setup_database.py")
        if success:
            print("✅ Database setup complete")
        else:
            print(f"❌ Database setup failed: {stderr}")
            return 1
    else:
        print("✅ Database already exists")
    
    
    setup_firewall()
    
    
    setup_systemd_service()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Configure DNS: Point gorkdb.ilikepancakes.gay to this server's IP")
    print("2. Update admin credentials in ai.env (change from default admin/admin123)")
    print("3. Start the service: sudo systemctl start gorkdb")
    print("4. Check status: sudo systemctl status gorkdb")
    print("5. View logs: sudo journalctl -u gorkdb -f")
    print("\n🌐 The site will be available at: http://gorkdb.ilikepancakes.gay")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
