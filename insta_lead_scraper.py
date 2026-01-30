import os
import re
import time
import random
from typing import Optional
from playwright.sync_api import sync_playwright, Page
import pandas as pd
from urllib.parse import urlparse, parse_qs , urlencode

#this function deduplicates links and removes links with unwanted patters
def clean_links_list(links: list[str]) -> list[str]:
    blocked_patterns = [ 
    "https://www.instagram.com/p/",
    "https://www.instagram.com/reel/",
    "https://instagram.com/p/",
    "https://instagram.com/reel/",
    "https://www.instagram.com/tv/",
    "https://instagram.com/tv/",
    "https://www.instagram.com/explore/",
    "https://instagram.com/explore/",
    "https://www.instagram.com/stories/",
    "https://instagram.com/stories/",
    "https://www.instagram.com/accounts/",
    "https://instagram.com/accounts/",  
    "https://www.instagram.com/about/",
    "https://instagram.com/about/",
    "/search?",
    "/explore/"
    ]
    pattern = "|".join(map(re.escape, blocked_patterns))
    keyword = "instagram.com"

    cleaned = (
        pd.Series(links)
        .drop_duplicates()
         .loc[
        lambda s:
        s.str.contains(keyword, case=False, na=False)
        & ~s.str.contains(pattern, case=False, na=False)]
        .tolist()
    )
    return cleaned

#this function helps in converting google dork search queries into filesystem safe strings / filename
def query_to_filename(query, ext="csv"):
    # lowercase (optional)
    query = query.lower()

    # remove quotes
    query = query.replace('"', '')

    # replace logical operators with readable tokens
    query = re.sub(r"\s+or\s+", "_OR_", query, flags=re.I)
    query = re.sub(r"\s+and\s+", "_AND_", query, flags=re.I)

    # replace forbidden characters with underscores
    query = re.sub(r"[:/\\?*<>|()]", "_", query)

    # replace spaces with underscores
    query = re.sub(r"\s+", "_", query)

    # collapse multiple underscores
    query = re.sub(r"_+", "_", query).strip("_")

    return f"{query}.{ext}"


def open_google_and_type(query: str, profile_dir: str = "browser_data", headless: bool = False) -> Optional[Page]:
    """Launch Chrome via Playwright with a persistent profile and perform a Google search.

    - Stores session data in `profile_dir` for reuse.
    - Sets a human-like user agent that includes `HumanLiker/1.0`.
    - Types the query with slight delays to simulate human typing, presses Enter,
      waits for results and prints the top result links.

    Returns the Playwright `Page` when running non-headless (for interactive use).
    When running headless the function performs the search, prints links, and returns None.
    """
    os.makedirs(profile_dir, exist_ok=True)

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.5993.90 Safari/537.36 HumanLiker/1.0"
    )

    with sync_playwright() as p:
        browser_type = p.chromium
        context = browser_type.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="chrome",
            headless=headless,
            viewport={"width": 1280, "height": 800},
            user_agent=user_agent,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        try:
            page = context.new_page() if not context.pages else context.pages[0]

            number_pages_to_scrape = 10
            all_the_links= []
            for i in range(number_pages_to_scrape):
                encoded_query = urlencode({'q': query, 'start': i * 10})
                url = f"https://www.google.com/search?{encoded_query}"
                page.goto(url, timeout=30000)

                # Dismiss common cookie/consent dialogs if present
                try:
                    consent = page.query_selector(
                        'button:has-text("I agree"), button:has-text("Accept"), button:has-text("AGREE")'
                    )
                    if consent:
                        consent.click()
                except Exception:
                    pass
                '''
                # Wait for the main search input and type like a human
                page.wait_for_selector("xpath=//textarea[@title='Search']", timeout=10000)
                input_box = page.query_selector('textarea[title="Search"]')

                if input_box:
                    for char in query:
                        input_box.type(char)
                        time.sleep(random.uniform(0.05, 0.35))

                time.sleep(random.uniform(0.12, 0.20))
                input_box.press("Enter")
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(random.uniform(1.0, 2.0))  # small buffer after results load
                '''
                # Collect some top search-result links (best-effort selector)
                links = []
                try:
                    insta_lead_links = page.locator("xpath=//div[@id='search']//div[@class='MjjYud']//a[not(@aria-describedby) and @href][1]")
                    #count = min(insta_lead_links.count(), 10)
                    for i in range(insta_lead_links.count()):
                        href = insta_lead_links.nth(i).get_attribute("href")
                        if href and href not in links:
                            links.append(href)
                    #deduplicate and filter links
                    links = clean_links_list(links)
                    print(f"Found {len(links)} links on the search results page.")
                    print("="*40)
                    all_the_links.extend(links)
                    print("="*40)
                    print("total links scraped so far:", len(all_the_links))
                    print("-"*40)
                    for idx, href in enumerate(links, start=1):
                        print(f"{idx}: {href}")
                except Exception:
                    pass

            if headless:
                context.close()
                return None

            return all_the_links
        except Exception:
            if headless:
                try:
                    context.close()
                except Exception:
                    pass
            raise


if __name__ == "__main__":
    # Demo: launches Chrome with persistent profile and performs a search.
    query = input("Enter your Google search query for insta lead discovery: ")
    print(f"Opening Chrome and searching for: {query}")
    all_links = open_google_and_type(
        query,
        profile_dir=os.path.join(os.path.dirname(__file__), "browser_data"),
        headless=False,
    )

    if all_links:
        df = pd.DataFrame({"links": all_links})
        output_file = query_to_filename(query)
        print(f"Saving {len(df)} links to {output_file}")
        df.to_csv(output_file, index=False)