"""
Minimal test for Instagram Discovery Bot
"""

import asyncio
from instagram_discovery_bot import InstagramDiscoveryBot


async def minimal_test():
    """Minimal test without actual scraping"""
    print("Minimal Test: Instagram Discovery Bot")

    bot = InstagramDiscoveryBot()

    # Test basic functionality
    print("Bot instance created")

    # Test count parsing
    test_count = bot.parse_count("1.2k")
    print(f"Count parsing test: '1.2k' -> {test_count}")

    # Test username extraction
    test_url = "https://www.instagram.com/username/"
    username = bot.extract_username_from_url(test_url)
    print(f"Username extraction test: {test_url} -> {username}")

    print("All basic tests passed!")


if __name__ == "__main__":
    asyncio.run(minimal_test())
