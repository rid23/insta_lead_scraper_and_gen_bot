"""
Instagram Discovery Bot - Advanced Playwright Automation & Scraping Tool

This bot automates Google search queries and scrapes Instagram profile data
including follower counts, posts, and user interaction metrics.

Author: AI Automation Bot
Dependencies: playwright, playwright-stealth, beautifulsoup4, pandas, python-dotenv
"""

import os
import json
import time
import re
import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright, BrowserContext, Page, Browser
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


@dataclass
class InstagramProfile:
    """Data class for Instagram profile information"""

    username: str
    full_name: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts: int = 0
    profile_url: str = ""
    profile_image_url: str = ""
    is_verified: bool = False
    is_private: bool = False
    last_4_posts: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.last_4_posts is None:
            self.last_4_posts = []


class InstagramDiscoveryBot:
    """Main bot class for Instagram discovery and scraping"""

    def __init__(self, user_data_dir: str = "browser_data"):
        self.user_data_dir = user_data_dir
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.scraped_profiles: List[InstagramProfile] = []

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
        ]

        # Ensure user data directory exists
        os.makedirs(user_data_dir, exist_ok=True)

    async def init_browser(self) -> None:
        """Initialize Playwright browser with enhanced stealth features"""
        self.playwright = await async_playwright().start()

        # Enhanced browser arguments for stealth
        browser_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-extensions-except",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",  # Optional: disable images for faster loading
            "--disable-javascript-harmony-shipping",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-ipc-flooding-protection",
            "--disable-sync",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-logging",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-features=TranslateUI",
            "--disable-features=VizDisplayCompositor",
            "--window-size=1366,768",
            "--test-type",
        ]

        # Launch browser with stealth
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for production
            args=browser_args,
        )

        # Create persistent context with enhanced stealth settings
        storage_state = f"{self.user_data_dir}/state.json"
        if not os.path.exists(storage_state):
            storage_state = None

        # Random viewport sizes for variety
        viewport_sizes = [
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720},
        ]
        selected_viewport = random.choice(viewport_sizes)

        # Random user agent
        selected_user_agent = random.choice(self.user_agents)

        self.context = await self.browser.new_context(
            viewport=selected_viewport,
            user_agent=selected_user_agent,
            storage_state=storage_state,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            ignore_https_errors=True,
            # Enhanced device emulation
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            # Extra stealth options
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            },
        )

        self.page = await self.context.new_page()

        # Apply stealth to avoid detection
        stealth_obj = Stealth()
        await stealth_obj.apply_stealth_async(self.page)

        # Additional stealth scripts
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }
                ],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
            });

            // Override getBoundingClientRect
            const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = function() {
                const result = originalGetBoundingClientRect.call(this);
                // Add small random variations
                result.x += Math.random() * 0.1 - 0.05;
                result.y += Math.random() * 0.1 - 0.05;
                return result;
            };
        """)

    async def close_browser(self) -> None:
        """Close browser and save state"""
        if self.context:
            await self.context.storage_state(path=f"{self.user_data_dir}/state.json")
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()

    async def search_google(self, query: str) -> List[str]:
        """Search Google for Instagram profiles based on query"""
        instagram_links = []

        try:
            # Navigate to Google
            await self.page.goto("https://www.google.com", wait_until="networkidle")
            await asyncio.sleep(2)

            # Accept cookies if present
            try:
                await self.page.click('button:has-text("Accept all")', timeout=5000)
            except:
                pass

            # Search for the query
            search_box = await self.page.wait_for_selector(
                'textarea[name="q"]', timeout=10000
            )
            await search_box.fill(query)
            await search_box.press("Enter")
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)

            # Extract Instagram links from search results
            search_results = await self.page.query_selector_all("div.g")

            for result in search_results[:10]:  # Limit to first 10 results
                try:
                    link_element = await result.query_selector(
                        'a[href*="instagram.com"]'
                    )
                    if link_element:
                        href = await link_element.get_attribute("href")
                        if href and "instagram.com" in href:
                            # Clean the URL
                            clean_url = href.split("&")[0] if "&" in href else href
                            if clean_url not in instagram_links:
                                instagram_links.append(clean_url)
                except:
                    continue

        except Exception as e:
            print(f"Error searching Google for query '{query}': {e}")

        return instagram_links

    def extract_username_from_url(self, url: str) -> str:
        """Extract Instagram username from URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip("/").split("/")
            if (
                path_parts
                and path_parts[0]
                and not path_parts[0] in ["p", "explore", "accounts", "direct"]
            ):
                return path_parts[0]
        except:
            pass
        return ""

    async def scrape_instagram_profile(
        self, profile_url: str
    ) -> Optional[InstagramProfile]:
        """Scrape Instagram profile data"""
        try:
            print(f"Scraping profile: {profile_url}")

            # Navigate to profile
            await self.page.goto(profile_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)

            # Check if login required or page exists
            if await self.page.query_selector('button:has-text("Log in")'):
                print(f"Login required for {profile_url}")
                return None

            # Extract username
            username = self.extract_username_from_url(profile_url)
            if not username:
                return None

            profile = InstagramProfile(username=username, profile_url=profile_url)

            # Wait for profile data to load
            await self.page.wait_for_selector("header", timeout=10000)

            # Extract profile information using JavaScript
            profile_data = await self.page.evaluate("""
                () => {
                    const data = {};
                    
                    // Full name
                    const nameEl = document.querySelector('h1');
                    data.full_name = nameEl ? nameEl.textContent.trim() : '';
                    
                    // Bio
                    const bioEl = document.querySelector('div.-vDIg span');
                    data.bio = bioEl ? bioEl.textContent.trim() : '';
                    
                    // Stats (followers, following, posts)
                    const stats = document.querySelectorAll('a[href*="/"] span');
                    const statValues = [];
                    stats.forEach(stat => {
                        const text = stat.textContent.trim();
                        if (text.match(/[0-9]+[km]?/)) {
                            statValues.push(text);
                        }
                    });
                    
                    data.followers = statValues[0] || '0';
                    data.following = statValues[1] || '0';
                    data.posts = statValues[2] || '0';
                    
                    // Profile image
                    const imgEl = document.querySelector('img[data-testid="user-avatar"]');
                    data.profile_image_url = imgEl ? imgEl.src : '';
                    
                    // Verification and private status
                    data.is_verified = !!document.querySelector('[data-testid="verified-icon"]');
                    data.is_private = !!document.querySelector('header h2');
                    
                    return data;
                }
            """)

            # Update profile with extracted data
            profile.full_name = profile_data.get("full_name", "")
            profile.bio = profile_data.get("bio", "")
            profile.profile_image_url = profile_data.get("profile_image_url", "")
            profile.is_verified = profile_data.get("is_verified", False)
            profile.is_private = profile_data.get("is_private", False)

            # Parse follower/following/post counts
            profile.followers = self.parse_count(profile_data.get("followers", "0"))
            profile.following = self.parse_count(profile_data.get("following", "0"))
            profile.posts = self.parse_count(profile_data.get("posts", "0"))

            # Extract recent posts data
            await self.extract_recent_posts(profile)

            print(
                f"Successfully scraped {username}: {profile.followers} followers, {profile.posts} posts"
            )
            return profile

        except Exception as e:
            print(f"Error scraping profile {profile_url}: {e}")
            return None

    def parse_count(self, count_str: str) -> int:
        """Convert count string (e.g., '1.2k', '500') to integer"""
        try:
            count_str = count_str.lower().replace(",", "").replace(" ", "")
            if "k" in count_str:
                return int(float(count_str.replace("k", "")) * 1000)
            elif "m" in count_str:
                return int(float(count_str.replace("m", "")) * 1000000)
            else:
                return int(count_str)
        except:
            return 0

    async def extract_recent_posts(self, profile: InstagramProfile) -> None:
        """Extract interaction data from last 4-5 posts"""
        try:
            # Scroll to load posts
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Get post elements
            post_links = await self.page.query_selector_all('a[href*="/p/"]')

            for i, post_link in enumerate(post_links[:5]):  # Limit to 5 posts
                try:
                    post_href = await post_link.get_attribute("href")
                    if post_href:
                        full_post_url = f"https://www.instagram.com{post_href}"

                        # Get post preview data without leaving profile page
                        post_data = await self.extract_post_preview(post_link)
                        if post_data:
                            profile.last_4_posts.append(post_data)

                except Exception as e:
                    print(f"Error extracting post {i}: {e}")
                    continue

        except Exception as e:
            print(f"Error extracting recent posts for {profile.username}: {e}")

    async def extract_post_preview(self, post_element) -> Optional[Dict[str, Any]]:
        """Extract preview data from post element"""
        try:
            post_data = await post_element.evaluate("""
                (element) => {
                    const data = {};
                    
                    // Get like count from aria-label or other attributes
                    const likeEl = element.querySelector('[aria-label*="like"], [aria-label*="likes"]');
                    data.likes = '0';
                    if (likeEl) {
                        const label = likeEl.getAttribute('aria-label') || '';
                        const match = label.match(/([0-9,]+)/);
                        if (match) data.likes = match[1];
                    }
                    
                    // Get comment count
                    const commentEl = element.querySelector('[aria-label*="comment"], [aria-label*="comments"]');
                    data.comments = '0';
                    if (commentEl) {
                        const label = commentEl.getAttribute('aria-label') || '';
                        const match = label.match(/([0-9,]+)/);
                        if (match) data.comments = match[1];
                    }
                    
                    // Get post URL
                    const linkEl = element.closest('a');
                    data.url = linkEl ? linkEl.href : '';
                    
                    return data;
                }
            """)

            if post_data.get("url"):
                post_data["likes"] = self.parse_count(post_data.get("likes", "0"))
                post_data["comments"] = self.parse_count(post_data.get("comments", "0"))
                return post_data

        except Exception as e:
            print(f"Error extracting post preview: {e}")

        return None

    async def run_discovery(self, search_queries: List[str]) -> None:
        """Main discovery process"""
        await self.init_browser()

        try:
            all_instagram_links = []

            # Search each query and collect Instagram links
            for query in search_queries:
                print(f"\nSearching for: {query}")
                links = await self.search_google(query)
                all_instagram_links.extend(links)
                print(f"Found {len(links)} Instagram links for query: {query}")

                # Add delay between searches to avoid rate limiting
                await asyncio.sleep(2)

            # Remove duplicates
            unique_links = list(set(all_instagram_links))
            print(f"\nTotal unique Instagram profiles to scrape: {len(unique_links)}")

            # Scrape each profile
            for i, profile_url in enumerate(unique_links, 1):
                print(f"\n[{i}/{len(unique_links)}] Processing: {profile_url}")

                profile = await self.scrape_instagram_profile(profile_url)
                if profile:
                    self.scraped_profiles.append(profile)

                # Add delay between profile scraping
                await asyncio.sleep(3)

            # Save results
            await self.save_results()

        except Exception as e:
            print(f"Error in discovery process: {e}")
        finally:
            await self.close_browser()

    async def save_results(self) -> None:
        """Save scraped data to JSON and CSV files"""
        if not self.scraped_profiles:
            print("No profiles scraped to save.")
            return

        # Prepare data for JSON
        json_data = []
        for profile in self.scraped_profiles:
            profile_dict = {
                "username": profile.username,
                "full_name": profile.full_name,
                "bio": profile.bio,
                "followers": profile.followers,
                "following": profile.following,
                "posts": profile.posts,
                "profile_url": profile.profile_url,
                "profile_image_url": profile.profile_image_url,
                "is_verified": profile.is_verified,
                "is_private": profile.is_private,
                "recent_posts": profile.last_4_posts,
            }
            json_data.append(profile_dict)

        # Save to JSON
        with open("instagram_discovery_results.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        # Save to CSV (without nested post data for simplicity)
        csv_data = []
        for profile in self.scraped_profiles:
            csv_data.append(
                {
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "bio": profile.bio,
                    "followers": profile.followers,
                    "following": profile.following,
                    "posts": profile.posts,
                    "profile_url": profile.profile_url,
                    "profile_image_url": profile.profile_image_url,
                    "is_verified": profile.is_verified,
                    "is_private": profile.is_private,
                    "total_post_likes": sum(
                        post.get("likes", 0) for post in profile.last_4_posts
                    ),
                    "total_post_comments": sum(
                        post.get("comments", 0) for post in profile.last_4_posts
                    ),
                    "avg_post_likes": sum(
                        post.get("likes", 0) for post in profile.last_4_posts
                    )
                    / len(profile.last_4_posts)
                    if profile.last_4_posts
                    else 0,
                    "avg_post_comments": sum(
                        post.get("comments", 0) for post in profile.last_4_posts
                    )
                    / len(profile.last_4_posts)
                    if profile.last_4_posts
                    else 0,
                }
            )

        df = pd.DataFrame(csv_data)
        df.to_csv("instagram_discovery_results.csv", index=False, encoding="utf-8")

        print(f"\nResults saved:")
        print(f"- JSON: instagram_discovery_results.json ({len(json_data)} profiles)")
        print(f"- CSV: instagram_discovery_results.csv ({len(csv_data)} profiles)")


# Import the existing query generator
from insta_discovery import lead_search_query_generator


async def main():
    """Main function to run the Instagram discovery bot"""
    print("[BOT] Instagram Discovery Bot Starting...")

    # Get user input for search parameters
    platform = input("Enter platform (instagram): ").strip() or "instagram"
    niche = input("Enter niche (e.g., fitness, fashion, travel): ").strip()
    location = input("Enter location (e.g., delhi, kolkata) or leave blank: ").strip()
    keyword = input("Enter keyword (e.g., yoga, street style) or leave blank: ").strip()
    language = input("Enter language (e.g., English, Spanish) or leave blank: ").strip()

    # Generate search queries
    print("\n[SEARCH] Generating search queries...")
    try:
        queries = lead_search_query_generator(
            platform, niche, location, keyword, language
        )
        print(f"Generated {len(queries)} search queries:")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
    except Exception as e:
        print(f"Error generating queries: {e}")
        # Fallback to manual queries
        queries = [
            f"site:instagram.com {niche} {location} {keyword}".strip(),
            f'site:instagram.com "{niche} influencer" {location}'.strip(),
            f'site:instagram.com "{niche} blogger" {keyword}'.strip(),
        ]
        print(f"Using fallback queries: {queries}")

    # Run the discovery bot
    bot = InstagramDiscoveryBot()
    await bot.run_discovery(queries)

    print("\n[SUCCESS] Instagram Discovery Complete!")
    print(f"Total profiles scraped: {len(bot.scraped_profiles)}")


if __name__ == "__main__":
    asyncio.run(main())
