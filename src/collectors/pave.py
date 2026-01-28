"""
Pave webinar collector using Playwright.
Source: https://www.pave.com/insights/events-and-webinars

Air dates are in format: "Aired on: Month Day, Year" spread across child elements.
"""
from typing import List
import re
from playwright.sync_api import Page
from .base import BaseCollector


class PaveCollector(BaseCollector):
    """Collector for Pave webinars using Playwright."""
    
    SOURCE_NAME = "Pave"
    URL = "https://www.pave.com/insights/events-and-webinars"
    
    def collect(self, page: Page) -> List[dict]:
        """Collect webinars from Pave."""
        webinars = []
        
        page.goto(self.URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        
        # Find all webinar cards (links to explore.pave.com)
        cards = page.query_selector_all("a[href*='explore.pave.com']")
        
        self.logger.info(f"Found {len(cards)} webinar cards")
        
        seen_urls = set()
        
        for card in cards:
            try:
                link = card.get_attribute("href")
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)
                
                # Get full text to extract title and date
                full_text = card.inner_text()
                
                # Skip if too short or looks like a CTA button
                if len(full_text) < 20:
                    continue
                
                # Title is usually the first significant line or in h1/h3
                title_elem = card.query_selector("h1, h3, .heading-style-h5, .heading-style-h3")
                if title_elem:
                    title = title_elem.inner_text().strip()
                else:
                    # Take first line as title
                    title = full_text.split('\n')[0].strip()
                
                if not title or len(title) < 10:
                    continue
                
                # Extract air date - look for "Aired on:" pattern in text
                air_date = None
                
                # The text contains date parts separated by newlines like:
                # "Aired on:\nNovember\n \n20\n, \n2025"
                # Let's normalize and extract
                text_clean = ' '.join(full_text.split())  # Normalize whitespace
                
                # Look for "Aired on:" followed by date parts
                aired_match = re.search(r'Aired on:\s*(\w+)\s+(\d{1,2})\s*,\s*(\d{4})', text_clean)
                if aired_match:
                    month, day, year = aired_match.groups()
                    air_date = f"{month} {day}, {year}"
                else:
                    # Try another pattern - date might be formatted differently
                    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})\s*,?\s*(\d{4})', text_clean)
                    if date_match:
                        month, day, year = date_match.groups()
                        air_date = f"{month} {day}, {year}"
                
                webinars.append({
                    "source": self.SOURCE_NAME,
                    "title": title[:200],
                    "air_date": air_date,
                    "link": link
                })
                
            except Exception as e:
                self.logger.debug(f"Error parsing card: {e}")
                continue
        
        return webinars
