"""
Syndio webinar collector using Playwright.
Source: https://synd.io/resources/?_type=webinar

The listing page shows webinar cards with:
- Title
- "Aired on: [date]" text
- "Watch now" button
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
        """Collect webinars from Syndio listing page."""
        webinars = []
        
        page.goto(self.URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        # The page shows 71 webinars - need to scroll to load more or find all cards
        # First, let's scroll down a few times to load more content
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
        
        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        
        # Find all webinar cards - look for elements containing "WEBINAR" label and "Aired on"
        # Based on the screenshot, cards have: WEBINAR label, title, "Aired on: [date]", "Watch now" button
        
        # Try to find cards by looking for elements with "Watch now" buttons
        watch_buttons = page.query_selector_all("a:has-text('Watch now'), button:has-text('Watch now')")
        self.logger.info(f"Found {len(watch_buttons)} 'Watch now' buttons")
        
        seen_urls = set()
        
        for button in watch_buttons:
            try:
                # Get the link from the Watch now button or its parent
                link = None
                if button.get_attribute("href"):
                    link = button.get_attribute("href")
                else:
                    link_parent = button.evaluate("el => el.closest('a')?.href || ''")
                    if link_parent:
                        link = link_parent
                
                if not link:
                    # Try finding link in parent container
                    link = button.evaluate("""el => {
                        let p = el.parentElement;
                        for(let i=0; i<10; i++) {
                            if(p) {
                                let a = p.querySelector('a[href]');
                                if(a && a.href) return a.href;
                                p = p.parentElement;
                            }
                        }
                        return '';
                    }""")
                
                if not link or link in seen_urls:
                    continue
                    
                seen_urls.add(link)
                
                if not link.startswith("http"):
                    link = f"https://synd.io{link}"
                
                # Get the card container text to extract title and date
                card_text = button.evaluate("""el => {
                    let p = el.parentElement;
                    for(let i=0; i<10; i++) {
                        if(p && p.innerText && p.innerText.length > 100) {
                            return p.innerText;
                        }
                        if(p) p = p.parentElement;
                    }
                    return '';
                }""")
                
                # Extract title - it's usually after "WEBINAR" label
                title = None
                lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                
                for i, line in enumerate(lines):
                    if line.upper() == 'WEBINAR' and i + 1 < len(lines):
                        # Next line(s) should be the title
                        title = lines[i + 1]
                        break
                
                if not title:
                    # Fallback - find first substantial line that's not a known label
                    skip_words = ['WEBINAR', 'Watch now', 'Aired on']
                    for line in lines:
                        if len(line) > 20 and not any(sw in line for sw in skip_words):
                            title = line
                            break
                
                if not title:
                    continue
                
                # Extract "Aired on: [date]"
                air_date = None
                for line in lines:
                    match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', line)
                    if match:
                        air_date = match.group(1)
                        break
                
                # Also try in full text
                if not air_date:
                    match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', card_text)
                    if match:
                        air_date = match.group(1)
                
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
