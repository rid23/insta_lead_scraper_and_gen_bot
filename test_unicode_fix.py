"""
Test script to verify the Unicode fix in Instagram discovery bot
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the module and class explicitly
import instagram_discovery_bot

InstagramDiscoveryBot = instagram_discovery_bot.InstagramDiscoveryBot


async def test_bot():
    """Test the bot with hardcoded parameters"""
    print("[TEST] Testing Instagram Discovery Bot with Unicode fix...")

    # Test with hardcoded parameters
    bot = InstagramDiscoveryBot()

    # Test browser initialization
    try:
        await bot.init_browser()
        print("[SUCCESS] Browser initialized successfully")

        # Test a simple search
        test_queries = ["site:instagram.com fitness influencer"]

        # Test search functionality
        links = await bot.search_google(test_queries[0])
        print(f"[SUCCESS] Found {len(links)} Instagram links for test query")

        # Test profile scraping if links found
        if links:
            profile = await bot.scrape_instagram_profile(links[0])
            if profile:
                print(f"[SUCCESS] Successfully scraped profile: {profile.username}")
            else:
                print("[INFO] Could not scrape profile (login required or other issue)")

        await bot.close_browser()
        print("[SUCCESS] Test completed successfully")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        if bot.browser:
            await bot.close_browser()


if __name__ == "__main__":
    asyncio.run(test_bot())
