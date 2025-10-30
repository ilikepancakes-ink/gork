
"""
Domain Setup Helper for gorkdb.ilikepancakes.gay
Helps configure the server for public domain access
"""
import socket
import subprocess
import sys
import requests
from pathlib import Path

def get_public_ip():
    """Get the public IP address of this server"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except:
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            return response.json()['origin']
        except:
            return None

def get_local_ip():
    """Get the local IP address"""
    try:
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def check_port_availability(port=80):
    """Check if port 80 is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            return True
    except OSError:
        return False

def check_dns_resolution():
    """Check if the domain resolves to this server"""
    domain = "gorkdb.ilikepancakes.gay"
    try:
        resolved_ip = socket.gethostbyname(domain)
        return resolved_ip
    except socket.gaierror:
        return None

def main():
    print("🌐 Domain Setup Helper for gorkdb.ilikepancakes.gay")
    print("=" * 60)
    
    
    print("\n📡 Network Information:")
    local_ip = get_local_ip()
    print(f"   Local IP: {local_ip}")
    
    public_ip = get_public_ip()
    if public_ip:
        print(f"   Public IP: {public_ip}")
    else:
        print("   Public IP: Could not determine (check internet connection)")
    
    
    print("\n🔌 Port Check:")
    if check_port_availability(80):
        print("   ✅ Port 80 is available")
    else:
        print("   ❌ Port 80 is in use or requires admin privileges")
        print("   💡 Try running as administrator/sudo, or use a different port")
    
    
    print("\n🌍 DNS Check:")
    resolved_ip = check_dns_resolution()
    if resolved_ip:
        print(f"   Domain resolves to: {resolved_ip}")
        if public_ip and resolved_ip == public_ip:
            print("   ✅ DNS is correctly configured!")
        else:
            print("   ⚠️  DNS points to different IP than your public IP")
    else:
        print("   ❌ Domain does not resolve")
        print("   💡 You need to configure DNS records")
    
    print("\n🔧 Setup Instructions:")
    print("1. DNS Configuration:")
    print("   - Create an A record for 'gorkdb.ilikepancakes.gay'")
    if public_ip:
        print(f"   - Point it to your public IP: {public_ip}")
    else:
        print("   - Point it to your server's public IP address")
    
    print("\n2. Firewall Configuration:")
    print("   - Allow incoming connections on port 80")
    print("   - Configure your router to forward port 80 to this machine")
    if local_ip != "127.0.0.1":
        print(f"   - Forward to local IP: {local_ip}")
    
    print("\n3. Security Considerations:")
    print("   - Change default admin credentials in ai.env")
    print("   - Consider using HTTPS (requires SSL certificate)")
    print("   - Monitor access logs for security")
    
    print("\n4. Testing:")
    print("   - After DNS propagation (can take up to 48 hours)")
    print("   - Visit http://gorkdb.ilikepancakes.gay")
    print("   - Check from external network to verify accessibility")
    
    print("\n🚀 Ready to start server:")
    print("   python db_admin_server.py")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
