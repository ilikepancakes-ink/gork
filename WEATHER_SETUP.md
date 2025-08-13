# Weather Functionality Setup for Gork Bot

Gork now supports weather information using WeatherAPI! Users can ask for current weather conditions and forecasts for any location worldwide.

## Setup Instructions

### 1. Get WeatherAPI Key

1. Go to [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key from the dashboard

### 2. Configure Environment Variables

Add this line to your `ai.env` file:

```
WEATHERAPI_KEY="your_weatherapi_key_here"
```

Replace the placeholder value with your actual WeatherAPI key.

### 3. Restart the Bot

Restart your bot to load the new configuration.

## Features

### Automatic Weather Integration
- The AI automatically detects weather-related questions
- Provides current conditions, temperature, humidity, wind speed
- Includes 3-day forecast information
- Shows weather alerts when available
- Includes air quality data

### Manual Weather Commands
- `/weather <location>` - Get current weather for a location
- `/forecast <location> [days]` - Get weather forecast (1-10 days)

## Usage Examples

### AI Integration (Automatic)
Users can ask natural language questions and Gork will automatically fetch weather data:

```
User: "What's the weather like in Tokyo?"
Gork: **GET_WEATHER:** Tokyo
[Bot provides current weather and forecast for Tokyo]
```

```
User: "Is it going to rain in London tomorrow?"
Gork: **GET_WEATHER:** London
[Bot provides weather forecast including rain chances]
```

```
User: "How's the weather in New York City right now?"
Gork: **GET_WEATHER:** New York City
[Bot provides current weather conditions]
```

### Manual Commands
Users can also use dedicated weather commands:

```
/weather London
/forecast Paris 5
/weather 40.7128,-74.0060  (coordinates)
```

## Supported Location Formats

WeatherAPI supports various location formats:
- **City names**: "London", "New York", "Tokyo"
- **City, Country**: "London, UK", "Paris, France"
- **Coordinates**: "40.7128,-74.0060"
- **ZIP codes**: "10001" (US), "SW1A 1AA" (UK)
- **Airport codes**: "LAX", "JFK", "LHR"

## Weather Data Included

### Current Conditions
- Temperature (Celsius and Fahrenheit)
- "Feels like" temperature
- Weather condition description
- Wind speed and direction
- Humidity percentage
- Visibility
- UV index
- Air quality data (when available)

### Forecast Information
- Daily high/low temperatures
- Weather conditions
- Chance of rain/snow
- Sunrise/sunset times

### Additional Features
- Weather alerts and warnings
- Air quality index
- 3-day forecast by default
- Support for up to 10-day forecasts

## API Limits

WeatherAPI free tier includes:
- 1 million calls per month
- Current weather and 3-day forecast
- Historical weather (1 year)
- Weather alerts and air quality

## Troubleshooting

If weather functionality isn't working:

1. **Check API Key**: Ensure your WeatherAPI key is correctly set in `ai.env`
2. **Verify Location**: Try different location formats (city name, coordinates, etc.)
3. **Check Logs**: Look for weather-related error messages in bot logs
4. **Test Manually**: Use the `/weather` command to test functionality
5. **API Status**: Check [WeatherAPI status page](https://www.weatherapi.com/) for service issues

## Error Messages

- `❌ Weather functionality is not configured` - API key not set or invalid
- `❌ WeatherAPI Error 400: No matching location found` - Invalid location
- `❌ WeatherAPI Error 403: API key invalid` - Check your API key
- `❌ Error fetching weather data` - Network or API issue

## Integration with AI

The weather functionality is seamlessly integrated with Gork's AI capabilities:

1. **Natural Language Processing**: Users can ask weather questions in natural language
2. **Automatic Detection**: The AI automatically detects when weather information is needed
3. **Smart Responses**: The AI provides contextual responses based on weather data
4. **Fallback Options**: If weather API fails, the AI can fall back to web search

This makes weather information easily accessible through conversational interaction with the bot.
