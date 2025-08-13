#!/usr/bin/env python3
"""
Test script for the enhanced update system with dependency checking.
This script tests the dependency checking functionality without requiring Discord.
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogs.update import Update
from unittest.mock import Mock

async def test_dependency_checking():
    """Test the dependency checking functionality"""
    print("🧪 Testing dependency checking functionality...\n")
    
    # Create a mock bot
    mock_bot = Mock()
    update_cog = Update(mock_bot)
    
    # Test 1: Check if requirements.txt exists
    print("📋 Test 1: Checking if requirements.txt exists...")
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt found")
        
        # Read and display current requirements
        with open("requirements.txt", 'r') as f:
            requirements = f.read().strip()
        print(f"📦 Current requirements:\n{requirements}\n")
    else:
        print("❌ requirements.txt not found")
        return
    
    # Test 2: Check for missing packages
    print("📋 Test 2: Checking for missing packages...")
    has_missing, message, missing_list = await update_cog.check_missing_packages()
    
    if has_missing:
        print(f"⚠️ {message}")
        print(f"📋 Missing packages: {missing_list}")
    else:
        print(f"✅ {message}")
    
    print()
    
    # Test 3: Check requirements changes (first run)
    print("📋 Test 3: Checking requirements changes...")
    changed, change_message = await update_cog.check_requirements_changes()
    print(f"📝 {change_message}")
    
    # Test 4: Check requirements changes again (should show no changes)
    print("\n📋 Test 4: Checking requirements changes again...")
    changed2, change_message2 = await update_cog.check_requirements_changes()
    print(f"📝 {change_message2}")
    
    print("\n🎉 Dependency checking tests completed!")
    
    # Clean up hash file
    if os.path.exists(".requirements_hash"):
        os.remove(".requirements_hash")
        print("🧹 Cleaned up test files")

async def test_requirements_parsing():
    """Test requirements.txt parsing with various formats"""
    print("\n🧪 Testing requirements.txt parsing...\n")
    
    # Create a temporary requirements file for testing
    test_requirements = """
# This is a comment
discord.py>=2.3.0
python-dotenv==1.0.0
psutil>=5.9.0,<6.0.0
aiohttp>3.8.0
# Another comment
GPUtil
beautifulsoup4>=4.12.0  # inline comment
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_requirements)
        temp_file = f.name
    
    try:
        # Create update cog with custom requirements file
        mock_bot = Mock()
        update_cog = Update(mock_bot)
        update_cog.requirements_file = temp_file
        
        has_missing, message, missing_list = await update_cog.check_missing_packages()
        
        print(f"📋 Test requirements parsing result:")
        print(f"   Has missing: {has_missing}")
        print(f"   Message: {message}")
        if missing_list:
            print(f"   Missing packages: {missing_list}")
        
    finally:
        # Clean up
        os.unlink(temp_file)
        print("🧹 Cleaned up temporary test file")

if __name__ == "__main__":
    print("🚀 Starting dependency checking tests...\n")
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the project root directory (where requirements.txt is located)")
        sys.exit(1)
    
    try:
        # Run the tests
        asyncio.run(test_dependency_checking())
        asyncio.run(test_requirements_parsing())
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
