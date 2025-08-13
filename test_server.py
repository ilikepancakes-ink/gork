#!/usr/bin/env python3
"""
Test script to verify the database admin server setup
"""
import os
import sys
from pathlib import Path
import subprocess

def test_php():
    """Test if PHP is available"""
    print("🔧 Testing PHP installation...")
    try:
        result = subprocess.run(["php", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ PHP is available: {result.stdout.split()[0]} {result.stdout.split()[1]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PHP is not installed or not in PATH")
        print("Please install PHP from https://www.php.net/downloads.php")
        return False

def test_database():
    """Test if database exists"""
    print("\n🗄️ Testing database...")
    db_path = Path("data/bot_messages.db")
    if db_path.exists():
        print(f"✅ Database found at: {db_path.absolute()}")
        print(f"   Size: {db_path.stat().st_size} bytes")
        return True
    else:
        print("❌ Database not found")
        print("Run: python setup_database.py")
        return False

def test_web_files():
    """Test if web files exist"""
    print("\n🌐 Testing web files...")
    web_dir = Path("web_admin")
    required_files = ["config.php", "login.php", "index.php", "messages.php", "responses.php", "users.php", "analytics.php"]
    
    if not web_dir.exists():
        print("❌ web_admin directory not found")
        return False
    
    missing_files = []
    for file in required_files:
        if not (web_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All web files present")
        return True

def test_env_file():
    """Test if environment file has required variables"""
    print("\n🔐 Testing environment configuration...")
    env_path = Path("ai.env")
    if not env_path.exists():
        print("❌ ai.env file not found")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if "DB_USER=" in content and "DB_PASS=" in content:
        print("✅ Database credentials configured")
        return True
    else:
        print("❌ DB_USER and DB_PASS not found in ai.env")
        return False

def main():
    print("🧪 Database Admin Server Test")
    print("=" * 40)
    
    tests = [
        ("PHP Installation", test_php),
        ("Database File", test_database),
        ("Web Files", test_web_files),
        ("Environment Config", test_env_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 40)
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Ready to start server.")
        print("\nTo start the server:")
        print("  python db_admin_server.py")
        print("\nThe server will be accessible at:")
        print("  http://gorkdb.ilikepancakes.gay")
        print("\n⚠️  Make sure the domain points to your server's IP!")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
