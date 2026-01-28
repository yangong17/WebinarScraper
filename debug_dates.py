"""
Debug script to inspect WorldatWork and Syndio for air dates.
"""
from playwright.sync_api import sync_playwright
import re

def inspect_worldatwork():
    """Inspect WorldatWork page structure."""
    print("\n" + "="*60)
    print("INSPECTING WORLDATWORK FOR LINKS")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://worldatwork.org/webinars?delivery=ondemand", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Get all links on the page
        all_links = page.query_selector_all("a[href*='/webinars/']")
        print(f"\nFound {len(all_links)} links containing '/webinars/'")
        
        for i, link in enumerate(all_links[:10]):
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            print(f"  {i+1}. {text[:50]} -> {href}")
        
        # Now visit the first webinar detail page
        if all_links:
            first_link = all_links[0].get_attribute("href")
            if not first_link.startswith("http"):
                first_link = f"https://worldatwork.org{first_link}"
            print(f"\n\nVisiting detail page: {first_link}")
            page.goto(first_link, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
            # Look for "On Demand until" text
            page_text = page.inner_text("body")
            match = re.search(r'On Demand until\s+(\w+\s+\d{1,2},?\s+\d{4})', page_text)
            if match:
                print(f"Found date: {match.group(1)}")
            else:
                # Print lines that might contain date info
                for line in page_text.split('\n'):
                    if 'demand' in line.lower() or 'until' in line.lower():
                        print(f"  Line: {line[:100]}")
        
        browser.close()

def inspect_syndio():
    """Inspect Syndio detail page for "Aired on" text."""
    print("\n" + "="*60)
    print("INSPECTING SYNDIO DETAIL PAGE FOR DATES")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # First get a webinar link
        page.goto("https://synd.io/resources/?_type=webinar", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Get first webinar link
        link_elem = page.query_selector("article a[href], [class*='card'] a[href]")
        if link_elem:
            link = link_elem.get_attribute("href")
            if not link.startswith("http"):
                link = f"https://synd.io{link}"
            
            print(f"Visiting: {link}")
            page.goto(link, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
            # Search for "Aired on" in the page text
            page_text = page.inner_text("body")
            
            # Look for Aired on pattern
            match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', page_text)
            if match:
                print(f"Found date: {match.group(1)}")
            else:
                # Print lines that might contain date info
                print("\nSearching for date-related text:")
                for line in page_text.split('\n'):
                    if 'aired' in line.lower() or 'date' in line.lower():
                        print(f"  Line: {line[:100]}")
            
            # Also try the user's XPath
            date_elem = page.locator("xpath=/html/body/div[9]/section/div/div[1]/div[5]/div/div[2]/div/div/div/div/div/div[1]/div[2]/div/div[6]/div[2]")
            if date_elem.count() > 0:
                print(f"\nUser XPath found: {date_elem.inner_text()}")
            else:
                print("\nUser XPath not found")
                
                # Try variations
                for xpath in [
                    "/html/body/div[9]//div[contains(text(),'Aired')]",
                    "//div[contains(text(),'Aired on')]",
                    "//span[contains(text(),'Aired on')]",
                ]:
                    elem = page.locator(f"xpath={xpath}")
                    if elem.count() > 0:
                        print(f"Found with xpath {xpath}: {elem.first.inner_text()}")
        
        browser.close()

if __name__ == "__main__":
    try:
        inspect_worldatwork()
    except Exception as e:
        print(f"WorldatWork error: {e}")
    
    try:
        inspect_syndio()
    except Exception as e:
        print(f"Syndio error: {e}")
