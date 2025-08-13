# Website Visiting Feature for Gork Bot

Gork now supports visiting websites and extracting their content! Users can ask Gork to visit specific URLs and analyze the content of web pages.

## Features

### Website Content Extraction
- **HTML Pages**: Extracts title, main content, and readable text
- **JSON APIs**: Displays formatted JSON responses
- **Plain Text**: Shows text content from plain text URLs
- **Smart Content Filtering**: Removes navigation, scripts, styles, and other non-content elements
- **Content Length Management**: Automatically truncates long content to prevent Discord message limits

### Supported Content Types
- `text/html` - Web pages, blogs, news articles, documentation
- `application/json` - API endpoints, JSON data
- `text/plain` - Plain text files, logs, simple text content

### Error Handling
- **403 Forbidden**: Detects when websites block automated access
- **404 Not Found**: Handles missing pages gracefully
- **429 Rate Limited**: Recognizes rate limiting
- **Timeout Protection**: 30-second timeout to prevent hanging
- **Connection Errors**: Handles network issues gracefully

## Usage

Users can ask Gork to visit websites in natural language:

### Example Commands
- "Visit https://example.com and tell me what it says"
- "What's on this website: https://news.example.com"
- "Can you read this page for me? https://docs.example.com"
- "Check out this URL and summarize it"

### How It Works
1. User mentions a URL or asks Gork to visit a website
2. Gork automatically detects the request and responds with: `**VISIT_WEBSITE:** url`
3. The bot fetches the website content
4. Content is parsed and cleaned
5. Gork analyzes the content and provides a summary or answers questions about it

## Technical Details

### Content Processing
- Uses BeautifulSoup4 for HTML parsing
- Removes non-content elements (scripts, styles, navigation)
- Extracts main content areas (main, article, content divs)
- Cleans and formats text for readability
- Limits content to 4000 characters to prevent overwhelming Discord/AI

### Security Features
- URL validation and sanitization
- Timeout protection (30 seconds)
- User-Agent spoofing to appear as a regular browser
- Error handling for malicious or problematic sites

### Browser Simulation
- Uses realistic browser headers
- Supports gzip/deflate compression
- Handles redirects automatically
- Mimics Chrome browser behavior

## Installation

### 1. Install Dependencies

The website visiting feature requires BeautifulSoup4 for HTML parsing. Install it using:

```bash
pip install beautifulsoup4>=4.12.0
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Restart the Bot

No additional configuration is needed. The website visiting feature works out of the box once the dependencies are installed.

## Limitations

### Content Restrictions
- Some websites block automated access (403 Forbidden)
- Rate limiting may prevent frequent requests to the same site
- JavaScript-heavy sites may not display full content (only static HTML is processed)
- Login-protected content cannot be accessed

### Size Limits
- HTML content is limited to 4000 characters
- JSON content is limited to 3000 characters
- Very large pages will be truncated with a notice

### Supported Protocols
- Only HTTP and HTTPS are supported
- FTP, file://, and other protocols are not supported

## Privacy and Ethics

### Responsible Usage
- The bot respects robots.txt when possible
- Uses reasonable request timeouts
- Does not attempt to bypass security measures
- Identifies itself with a standard browser User-Agent

### Data Handling
- Website content is processed temporarily and not stored
- No cookies or session data is maintained
- Each request is independent

## Troubleshooting

### Common Issues

**"Access forbidden (403)"**
- The website blocks automated access
- Try visiting the site manually to confirm it's accessible
- Some sites require specific headers or authentication

**"Request timed out"**
- The website is slow to respond or unreachable
- Check if the URL is correct and the site is online
- Some sites may have geographic restrictions

**"Unsupported content type"**
- The URL points to a binary file (images, PDFs, etc.)
- Only text-based content can be processed
- Try finding a text-based version of the content

**"Invalid URL format"**
- Ensure the URL includes http:// or https://
- Check for typos in the URL
- The bot will automatically add https:// if missing

### Getting Help

If you encounter issues with the website visiting feature:

1. Check that the URL is accessible in a regular browser
2. Verify that beautifulsoup4 is installed
3. Check the bot logs for detailed error messages
4. Try with a different, simpler website to test functionality

## Examples

### News Article
```
User: "Visit https://example-news.com/article and summarize it"
Gork: **VISIT_WEBSITE:** https://example-news.com/article
[Bot fetches content and provides summary]
```

### Documentation
```
User: "What does this documentation say? https://docs.example.com/api"
Gork: **VISIT_WEBSITE:** https://docs.example.com/api
[Bot extracts and explains the documentation]
```

### JSON API
```
User: "Check this API endpoint: https://api.example.com/status"
Gork: **VISIT_WEBSITE:** https://api.example.com/status
[Bot displays formatted JSON response]
```

The website visiting feature makes Gork much more powerful by allowing it to access and analyze real-time web content, making it perfect for research, news analysis, documentation reading, and general web content exploration.
