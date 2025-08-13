import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from dotenv import load_dotenv
import json
from typing import Optional

class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv("ai.env")
        self.weatherapi_key = os.getenv("WEATHERAPI_KEY")
        self.base_url = "http://api.weatherapi.com/v1"
    
    async def get_weather_data(self, location: str, days: int = 1) -> dict:
        """Get weather data from WeatherAPI"""
        if not self.weatherapi_key or self.weatherapi_key == "your_weatherapi_key_here":
            return {"error": "WeatherAPI key not configured. Please set WEATHERAPI_KEY in ai.env file."}
        
        # Use forecast endpoint for current + forecast data
        url = f"{self.base_url}/forecast.json"
        params = {
            "key": self.weatherapi_key,
            "q": location,
            "days": min(days, 10),  # API supports max 10 days
            "aqi": "yes",  # Include air quality data
            "alerts": "yes"  # Include weather alerts
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        return {"error": f"API Error {response.status}: {error_data.get('error', {}).get('message', 'Unknown error')}"}
        except Exception as e:
            return {"error": f"Failed to fetch weather data: {str(e)}"}
    
    async def format_weather_response(self, data: dict, location: str) -> str:
        """Format weather data into a readable response"""
        if "error" in data:
            return f"❌ {data['error']}"
        
        try:
            current = data["current"]
            location_info = data["location"]
            forecast = data["forecast"]["forecastday"]
            
            # Current weather
            response = f"🌤️ **Weather for {location_info['name']}, {location_info['region']}, {location_info['country']}**\n\n"
            response += f"**Current Conditions** ({location_info['localtime']})\n"
            response += f"🌡️ **Temperature:** {current['temp_c']}°C ({current['temp_f']}°F)\n"
            response += f"🌡️ **Feels like:** {current['feelslike_c']}°C ({current['feelslike_f']}°F)\n"
            response += f"☁️ **Condition:** {current['condition']['text']}\n"
            response += f"💨 **Wind:** {current['wind_kph']} km/h ({current['wind_mph']} mph) {current['wind_dir']}\n"
            response += f"💧 **Humidity:** {current['humidity']}%\n"
            response += f"👁️ **Visibility:** {current['vis_km']} km ({current['vis_miles']} miles)\n"
            response += f"🌡️ **UV Index:** {current['uv']}\n"
            
            # Air quality if available
            if "air_quality" in current:
                aqi = current["air_quality"]
                response += f"🌬️ **Air Quality:** CO: {aqi.get('co', 'N/A')}, NO2: {aqi.get('no2', 'N/A')}, O3: {aqi.get('o3', 'N/A')}\n"
            
            # Today's forecast
            if forecast:
                today = forecast[0]["day"]
                response += f"\n**Today's Forecast**\n"
                response += f"🌡️ **High/Low:** {today['maxtemp_c']}°C / {today['mintemp_c']}°C ({today['maxtemp_f']}°F / {today['mintemp_f']}°F)\n"
                response += f"☁️ **Condition:** {today['condition']['text']}\n"
                response += f"🌧️ **Chance of rain:** {today['daily_chance_of_rain']}%\n"
                response += f"❄️ **Chance of snow:** {today['daily_chance_of_snow']}%\n"
                
                # Sunrise/sunset
                astro = forecast[0]["astro"]
                response += f"🌅 **Sunrise:** {astro['sunrise']} | 🌇 **Sunset:** {astro['sunset']}\n"
            
            # Weather alerts
            if "alerts" in data and data["alerts"]["alert"]:
                response += f"\n⚠️ **Weather Alerts:**\n"
                for alert in data["alerts"]["alert"][:2]:  # Limit to 2 alerts
                    response += f"• {alert['headline']}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error formatting weather data: {str(e)}"
    
    async def format_forecast_response(self, data: dict, location: str, days: int) -> str:
        """Format forecast data into a readable response"""
        if "error" in data:
            return f"❌ {data['error']}"
        
        try:
            location_info = data["location"]
            forecast = data["forecast"]["forecastday"]
            
            response = f"📅 **{days}-Day Forecast for {location_info['name']}, {location_info['region']}, {location_info['country']}**\n\n"
            
            for day_data in forecast:
                date = day_data["date"]
                day = day_data["day"]
                
                response += f"**{date}**\n"
                response += f"🌡️ {day['mintemp_c']}°C - {day['maxtemp_c']}°C ({day['mintemp_f']}°F - {day['maxtemp_f']}°F)\n"
                response += f"☁️ {day['condition']['text']}\n"
                response += f"🌧️ Rain: {day['daily_chance_of_rain']}% | ❄️ Snow: {day['daily_chance_of_snow']}%\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error formatting forecast data: {str(e)}"
    
    @app_commands.command(name="weather", description="Get current weather for a location")
    @app_commands.describe(location="City name, coordinates, or location to get weather for")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def weather_command(self, interaction: discord.Interaction, location: str):
        """Get current weather for a location"""
        await interaction.response.defer()
        
        weather_data = await self.get_weather_data(location)
        response = await self.format_weather_response(weather_data, location)
        
        await interaction.followup.send(response)
    
    @app_commands.command(name="forecast", description="Get weather forecast for a location")
    @app_commands.describe(
        location="City name, coordinates, or location to get forecast for",
        days="Number of days to forecast (1-10, default: 3)"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def forecast_command(self, interaction: discord.Interaction, location: str, days: Optional[int] = 3):
        """Get weather forecast for a location"""
        await interaction.response.defer()
        
        # Validate days parameter
        if days < 1 or days > 10:
            await interaction.followup.send("❌ Days must be between 1 and 10.")
            return
        
        weather_data = await self.get_weather_data(location, days)
        response = await self.format_forecast_response(weather_data, location, days)
        
        await interaction.followup.send(response)
    
    async def search_weather(self, location: str) -> str:
        """Search weather for AI integration - returns formatted weather info"""
        weather_data = await self.get_weather_data(location)
        return await self.format_weather_response(weather_data, location)

async def setup(bot: commands.Bot):
    await bot.add_cog(Weather(bot))
