# Instagram Discovery Bot

🤖 An advanced Playwright automation bot for discovering and scraping Instagram profiles based on custom search queries.

## Features

- **Automated Google Search**: Searches Google using custom queries to find Instagram profiles
- **Profile Data Extraction**: Scrapes comprehensive Instagram profile data including:
  - Username and full name
  - Bio/description
  - Follower, following, and post counts
  - Verification status
  - Private/public status
  - Profile image URL
- **Recent Posts Analysis**: Extracts interaction data from last 4-5 posts (likes, comments)
- **Persistent Browser Context**: Stores browser cache and session data for efficiency
- **Anti-Detection**: Uses stealth techniques to avoid bot detection
- **Multiple Export Formats**: Saves data in both JSON and CSV formats

## Installation

1. Install dependencies:
```bash
pip install -r bot_requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Set up environment variables in `.env` file (if using Google GenAI for query generation):
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

### Basic Usage

Run the bot and follow the prompts:
```bash
python instagram_discovery_bot.py
```

The bot will ask for:
- Platform (default: instagram)
- Niche (e.g., fitness, fashion, travel)
- Location (optional)
- Keywords (optional)
- Language (optional)

### Example Input
```
Platform: instagram
Niche: fitness
Location: new york
Keyword: yoga
Language: english
```

### Test the Bot

Run the test script to verify functionality:
```bash
python test_bot.py
```

## Output Files

The bot generates two output files:

1. **`instagram_discovery_results.json`** - Complete data with nested post information
2. **`instagram_discovery_results.csv`** - Flattened data for easy analysis

### Data Structure

Each profile contains:
```json
{
  "username": "fitness_guru",
  "full_name": "John Doe",
  "bio": "Fitness enthusiast | Yoga instructor",
  "followers": 125000,
  "following": 850,
  "posts": 342,
  "profile_url": "https://www.instagram.com/fitness_guru",
  "profile_image_url": "https://...",
  "is_verified": true,
  "is_private": false,
  "recent_posts": [
    {
      "url": "https://www.instagram.com/p/ABC123/",
      "likes": 2500,
      "comments": 120
    }
  ]
}
```

## Browser Data

The bot uses a persistent browser context stored in:
- `browser_data/` directory
- `browser_data/state.json` - Session state and cookies

This allows for:
- Faster subsequent runs
- Maintained login sessions
- Cached resources

## Configuration

### Custom Search Queries

The bot integrates with `insta_discovery.py` to generate optimized search queries using Google GenAI. You can also provide custom queries directly.

### Browser Settings

Modify the `init_browser()` method in `InstagramDiscoveryBot` class to adjust:
- Headless mode (set `headless=True` for production)
- Viewport size
- User agent
- Geolocation
- Permissions

## Error Handling

The bot includes comprehensive error handling for:
- Network timeouts
- Rate limiting
- Login requirements
- Profile access restrictions
- Missing elements

## Rate Limiting

To avoid detection and rate limiting:
- Built-in delays between searches (2 seconds)
- Built-in delays between profile scraping (3 seconds)
- Random user agent rotation
- Stealth techniques

## Troubleshooting

### Common Issues

1. **Login Required**: Some profiles require login to access
   - Solution: Log in manually once, the session will be saved

2. **Rate Limited**: Too many requests in short time
   - Solution: Increase delays in the code

3. **Element Not Found**: Instagram changed their HTML structure
   - Solution: Update selectors in the scraping methods

4. **Browser Not Installed**: Playwright browsers missing
   - Solution: Run `playwright install chromium`

### Debug Mode

Set `headless=False` in the browser initialization to watch the bot in action.

## Dependencies

- `playwright` - Browser automation
- `playwright-stealth` - Anti-detection techniques
- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation and CSV export
- `python-dotenv` - Environment variable management
- `lxml` - XML/HTML parser

## Security & Ethics

⚠️ **Important**: This tool is for educational and research purposes only. Always:
- Respect Instagram's Terms of Service
- Don't use for spam or harassment
- Comply with data privacy laws
- Use reasonable rate limits

## License

This project is for educational use. Please ensure compliance with all applicable laws and platform terms of service.