#!/usr/bin/env python3
"""
Test script for weather functionality
"""
import asyncio
import os
from dotenv import load_dotenv
import aiohttp

async def test_weather_api():
    """Test the WeatherAPI integration"""
    load_dotenv("ai.env")
    api_key = os.getenv("WEATHERAPI_KEY")
    
    if not api_key or api_key == "your_weatherapi_key_here":
        print("❌ WeatherAPI key not configured. Please set WEATHERAPI_KEY in ai.env file.")
        return
    
    print(f"✅ WeatherAPI key found: {api_key[:10]}...")
    
    # Test API call
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": "London",
        "days": 3,
        "aqi": "yes",
        "alerts": "yes"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ WeatherAPI test successful!")
                    print(f"📍 Location: {data['location']['name']}, {data['location']['country']}")
                    print(f"🌡️ Current temp: {data['current']['temp_c']}°C")
                    print(f"☁️ Condition: {data['current']['condition']['text']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ WeatherAPI Error {response.status}: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ Error testing WeatherAPI: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_weather_api())
