"""
Syndio webinar collector using Playwright.
Source: https://synd.io/resources/?_type=webinar

Visits detail pages to extract "Aired on: [date]".
Skips entries that already exist in the database.
"""
from typing import List, Set
import re
from playwright.sync_api import Page
from .base import BaseCollector


class SyndioCollector(BaseCollector):
    """Collector for Syndio webinars."""
    
    SOURCE_NAME = "Syndio"
    URL = "https://synd.io/resources/?_type=webinar"
    
    def __init__(self, existing_links: Set[str] = None):
        super().__init__()
        self.existing_links = existing_links or set()
    
    def collect(self, page: Page) -> List[dict]:
        """Collect webinars from Syndio."""
        webinars = []
        webinar_links = []
        
        page.goto(self.URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        # Get all resource cards
        cards = page.query_selector_all("article, [class*='resource'], [class*='card']")
        
        self.logger.info(f"Found {len(cards)} potential cards")
        
        seen_urls = set()
        
        # First pass: collect all links and titles
        for card in cards:
            try:
                link_elem = card.query_selector("a[href]")
                if not link_elem:
                    continue
                
                link = link_elem.get_attribute("href")
                if not link or link in seen_urls:
                    continue
                
                seen_urls.add(link)
                
                if not link.startswith("http"):
                    link = f"https://synd.io{link}"
                
                # Get title
                title_elem = card.query_selector("h2, h3, h4, .title")
                title = title_elem.inner_text().strip() if title_elem else None
                
                if not title:
                    title = link_elem.inner_text().strip()
                
                if not title or len(title) < 5:
                    continue
                
                webinar_links.append({
                    "title": title[:200],
                    "link": link
                })
                
            except Exception as e:
                self.logger.debug(f"Error parsing card: {e}")
                continue
        
        self.logger.info(f"Collected {len(webinar_links)} webinar links, now fetching dates...")
        
        # Second pass: visit each detail page to get air date
        for i, webinar in enumerate(webinar_links):
            link = webinar["link"]
            
            # Skip if already in database
            if link in self.existing_links:
                self.logger.info(f"  [{i+1}/{len(webinar_links)}] Skipping (already in DB): {webinar['title'][:40]}...")
                continue
            
            self.logger.info(f"  [{i+1}/{len(webinar_links)}] Fetching date for: {webinar['title'][:40]}...")
            
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                
                air_date = None
                
                # Use the working XPath: //div[contains(text(),'Aired on')]
                date_elem = page.locator("xpath=//div[contains(text(),'Aired on')]")
                if date_elem.count() > 0:
                    date_text = date_elem.first.inner_text()
                    # Extract date from "Aired on: April 29, 2025"
                    match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', date_text)
                    if match:
                        air_date = match.group(1)
                
                # Fallback: search the whole page for "Aired on:" pattern
                if not air_date:
                    page_text = page.inner_text("body")
                    match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', page_text)
                    if match:
                        air_date = match.group(1)
                
                webinars.append({
                    "source": self.SOURCE_NAME,
                    "title": webinar["title"],
                    "air_date": air_date,
                    "link": link
                })
                
            except Exception as e:
                self.logger.debug(f"Error fetching detail page: {e}")
                webinars.append({
                    "source": self.SOURCE_NAME,
                    "title": webinar["title"],
                    "air_date": None,
                    "link": link
                })
        
        return webinars
