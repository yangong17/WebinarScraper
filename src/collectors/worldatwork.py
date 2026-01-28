"""
WorldatWork webinar collector using Playwright.
Source: https://worldatwork.org/webinars?delivery=ondemand

Uses Register button links which are /product/redirect/ URLs.
Visits each detail page to get "On Demand until [date]".
Skips entries that already exist in the database.
"""
from typing import List, Set
import re
from playwright.sync_api import Page
from .base import BaseCollector


class WorldatWorkCollector(BaseCollector):
    """Collector for WorldatWork on-demand webinars (public only)."""
    
    SOURCE_NAME = "WorldatWork"
    URL = "https://worldatwork.org/webinars?delivery=ondemand"
    
    def __init__(self, existing_links: Set[str] = None):
        super().__init__()
        self.existing_links = existing_links or set()
    
    def collect(self, page: Page) -> List[dict]:
        """Collect on-demand webinars from WorldatWork with pagination."""
        webinars = []
        webinar_links = []
        
        page.goto(self.URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        page_num = 1
        max_pages = 10
        
        # Collect all webinar links from listing pages
        while page_num <= max_pages:
            self.logger.info(f"Collecting links from page {page_num}")
            
            # Find all Register buttons (a tags with href=/product/redirect/)
            register_links = page.query_selector_all("a[href*='/product/redirect/']")
            
            found_on_page = 0
            for register_link in register_links:
                try:
                    href = register_link.get_attribute("href")
                    if not href:
                        continue
                    
                    if not href.startswith("http"):
                        href = f"https://worldatwork.org{href}"
                    
                    # Skip duplicates
                    if any(w['link'] == href for w in webinar_links):
                        continue
                    
                    # Get title - navigate up to find the card container and get title
                    # The structure has the title in a span above the register button
                    card_text = register_link.evaluate("""el => {
                        let p = el.parentElement;
                        for(let i=0; i<10; i++) {
                            if(p && p.innerText && p.innerText.length > 50) {
                                return p.innerText;
                            }
                            if(p) p = p.parentElement;
                        }
                        return '';
                    }""")
                    
                    # Extract title from card text
                    lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                    title = None
                    skip_keywords = ['Featured', 'On Demand', 'Gain Recertification Credits', 
                                   'Register', 'Member Only Access', 'Exclusive']
                    
                    for line in lines:
                        if (len(line) > 15 and 
                            line not in skip_keywords and
                            not line.startswith('On Demand')):
                            title = line
                            break
                    
                    if title:
                        webinar_links.append({
                            "title": title[:200],
                            "link": href
                        })
                        found_on_page += 1
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing item: {e}")
                    continue
            
            self.logger.info(f"Found {found_on_page} webinars on page {page_num} (total: {len(webinar_links)})")
            
            # Next page using user's XPath
            next_button = page.locator("xpath=/html/body/div[3]/div[6]/div/div/div/div/div[2]/div[3]/nav/ul/li[3]/button")
            if next_button.count() > 0 and next_button.is_enabled():
                try:
                    next_button.click()
                    page.wait_for_timeout(2000)
                    page_num += 1
                except:
                    break
            else:
                break
        
        self.logger.info(f"Collected {len(webinar_links)} webinar links, now fetching dates...")
        
        # Now visit each detail page to get the air date
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
                
                # Look for "On Demand until [date]" text
                air_date = None
                page_text = page.inner_text("body")
                
                # Pattern: "On Demand until December 31, 2025"
                match = re.search(r'On Demand until\s+(\w+\s+\d{1,2},?\s+\d{4})', page_text)
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
