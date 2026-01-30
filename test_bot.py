"""
Test script for Instagram Discovery Bot
"""

import asyncio
from instagram_discovery_bot import InstagramDiscoveryBot


async def test_bot():
    """Test the bot with a single query"""
    print("🧪 Testing Instagram Discovery Bot...")

    # Test queries
    test_queries = [
        "site:instagram.com fitness influencer new york",
        "site:instagram.com fashion blogger london",
    ]

    bot = InstagramDiscoveryBot()

    try:
        await bot.init_browser()
        print("✅ Browser initialized successfully")

        # Test Google search
        links = await bot.search_google(test_queries[0])
        print(f"✅ Found {len(links)} Instagram links for test query")

        if links:
            # Test profile scraping
            profile = await bot.scrape_instagram_profile(links[0])
            if profile:
                print(f"✅ Successfully scraped profile: {profile.username}")
                print(f"   Followers: {profile.followers}")
                print(f"   Posts: {profile.posts}")
            else:
                print("⚠️ Profile scraping returned None (might require login)")

        await bot.close_browser()
        print("✅ Test completed successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        await bot.close_browser()


if __name__ == "__main__":
    asyncio.run(test_bot())
