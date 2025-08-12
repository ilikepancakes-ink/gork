# Web Search Setup for Gork Bot

Gork now supports web search functionality using SearchAPI.io! Users can ask for information and Gork will automatically search the web when needed.

## Setup Instructions

### 1. Get SearchAPI.io API Key

1. Go to [SearchAPI.io](https://www.searchapi.io/)
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key from the dashboard

### 2. Configure Environment Variables

Add this line to your `ai.env` file:

```
SEARCHAPI_KEY="your_searchapi_key_here"
```

Replace the placeholder value with your actual SearchAPI.io API key.

### 3. Restart the Bot

Restart your bot to load the new configuration.

## Usage

Once configured, users can ask Gork questions that require web search:

- "What's the weather in New York?"
- "Latest news about AI"
- "How to install Python on Windows?"
- "Current Bitcoin price"
- "What happened in the news today?"

Gork will automatically detect when a web search is needed and provide relevant results.

## Features

- Automatic search detection
- Up to 10 search results per query
- Formatted results with titles, descriptions, and links
- Search statistics (total results, search time)
- Fallback to regular AI responses if search is not configured
- Uses Google search engine through SearchAPI.io

## Troubleshooting

- **"Web Search is not configured"**: Make sure `SEARCHAPI_KEY` is set in your `ai.env` file
- **API errors**: Check that your SearchAPI.io API key is valid and active
- **No results**: The search query might be too specific or there might be no relevant results

## API Limits

SearchAPI.io has generous usage limits:
- Free tier: 100 searches per month
- Paid tiers: Up to 100,000+ searches per month depending on plan

Monitor your usage in the SearchAPI.io dashboard.

## Why SearchAPI.io?

- **Easier setup**: Just one API key needed (vs Google's API key + Custom Search Engine ID)
- **Better free tier**: 100 searches/month vs Google's 100 searches/day
- **More reliable**: Dedicated search API service
- **Better results**: Direct access to Google search results without configuration complexity

## Example Interactions

**User:** "What's the current weather in Tokyo?"

**Gork:** *Automatically detects need for current information and searches*
🔍 **Web Search Results for:** weather Tokyo today
📊 Found 1,234,567 results in 0.45 seconds

**1. Tokyo Weather - Current Conditions**
Partly cloudy, 22°C (72°F). Humidity 65%. Wind 10 km/h from the east...
🔗 https://weather.com/tokyo

**User:** "Latest news about SpaceX"

**Gork:** *Searches for recent SpaceX news*
🔍 **Web Search Results for:** SpaceX latest news
📊 Found 2,345,678 results in 0.52 seconds

**1. SpaceX Successfully Launches Starship Mission**
SpaceX completed another successful test flight of its Starship vehicle...
🔗 https://spacenews.com/spacex-starship-latest
