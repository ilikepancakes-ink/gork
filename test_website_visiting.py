#!/usr/bin/env python3
"""
Test script for the website visiting functionality
This script tests the visit_website method independently
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
import re
import json

async def visit_website(url: str) -> str:
    """Visit a website and extract its content - standalone version for testing"""
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL to check if it's valid
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            return f"❌ Invalid URL format: {url}"
        
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'text/html' in content_type:
                        # Get HTML content
                        html_content = await response.text()
                        
                        # Parse HTML with BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        # Get page title
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else "No title"
                        
                        # Get main content
                        # Try to find main content areas
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I)) or soup.find('body')
                        
                        if main_content:
                            # Extract text content
                            text_content = main_content.get_text(separator='\n', strip=True)
                        else:
                            text_content = soup.get_text(separator='\n', strip=True)
                        
                        # Clean up the text
                        lines = text_content.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            line = line.strip()
                            if line and len(line) > 3:  # Filter out very short lines
                                cleaned_lines.append(line)
                        
                        cleaned_text = '\n'.join(cleaned_lines)
                        
                        # Limit content length to prevent overwhelming Discord/AI
                        max_length = 4000  # Reasonable limit for Discord and AI processing
                        if len(cleaned_text) > max_length:
                            cleaned_text = cleaned_text[:max_length] + "\n\n... (content truncated due to length)"
                        
                        # Format the response
                        formatted_response = f"🌐 **Website Content from:** {url}\n"
                        formatted_response += f"📄 **Title:** {title_text}\n\n"
                        formatted_response += f"**Content:**\n{cleaned_text}"
                        
                        return formatted_response
                        
                    elif 'application/json' in content_type:
                        # Handle JSON content
                        json_content = await response.json()
                        json_str = json.dumps(json_content, indent=2)
                        
                        # Limit JSON length
                        if len(json_str) > 3000:
                            json_str = json_str[:3000] + "\n... (JSON truncated due to length)"
                        
                        return f"🌐 **JSON Content from:** {url}\n```json\n{json_str}\n```"
                        
                    elif 'text/plain' in content_type:
                        # Handle plain text
                        text_content = await response.text()
                        
                        # Limit text length
                        if len(text_content) > 4000:
                            text_content = text_content[:4000] + "\n... (content truncated due to length)"
                        
                        return f"🌐 **Text Content from:** {url}\n```\n{text_content}\n```"
                        
                    else:
                        return f"🌐 **Website:** {url}\n❌ Unsupported content type: {content_type}\nThis appears to be a binary file or unsupported format."
                
                elif response.status == 403:
                    return f"🌐 **Website:** {url}\n❌ Access forbidden (403). The website blocks automated access."
                elif response.status == 404:
                    return f"🌐 **Website:** {url}\n❌ Page not found (404)."
                elif response.status == 429:
                    return f"🌐 **Website:** {url}\n❌ Too many requests (429). The website is rate limiting."
                else:
                    return f"🌐 **Website:** {url}\n❌ HTTP Error {response.status}: {response.reason}"
                    
    except asyncio.TimeoutError:
        return f"🌐 **Website:** {url}\n❌ Request timed out after 30 seconds."
    except aiohttp.ClientError as e:
        return f"🌐 **Website:** {url}\n❌ Connection error: {str(e)}"
    except Exception as e:
        return f"🌐 **Website:** {url}\n❌ Error visiting website: {str(e)}"

async def test_website_visiting():
    """Test the website visiting functionality with various URLs"""
    test_urls = [
        "https://httpbin.org/json",  # JSON API
        "https://httpbin.org/html",  # HTML page
        "https://example.com",       # Simple HTML
        "invalid-url",               # Invalid URL test
        "https://httpbin.org/status/404",  # 404 test
    ]
    
    print("Testing Website Visiting Functionality")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 30)
        result = await visit_website(url)
        print(result[:500] + "..." if len(result) > 500 else result)
        print()

if __name__ == "__main__":
    # Check if required dependencies are available
    try:
        import aiohttp
        import bs4
        print("✅ All required dependencies are available")
        print("Running website visiting tests...\n")
        asyncio.run(test_website_visiting())
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install aiohttp beautifulsoup4")
