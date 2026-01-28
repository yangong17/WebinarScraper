"""
Debug script to check actual Syndio links and WorldatWork.
"""
from playwright.sync_api import sync_playwright
import re

def debug_syndio():
    """Debug Syndio links and dates."""
    print("\n" + "="*60)
    print("DEBUGGING SYNDIO")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://synd.io/resources/?_type=webinar", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        # Get all cards
        cards = page.query_selector_all("article, [class*='resource'], [class*='card']")
        print(f"Found {len(cards)} cards")
        
        links_found = []
        for card in cards:
            link_elem = card.query_selector("a[href]")
            if link_elem:
                href = link_elem.get_attribute("href")
                if href and href not in links_found:
                    links_found.append(href)
        
        print(f"Unique links: {len(links_found)}")
        for link in links_found[:5]:
            print(f"  - {link}")
        
        # Visit first actual webinar link and look for date
        if links_found:
            first_link = links_found[0]
            if not first_link.startswith("http"):
                first_link = f"https://synd.io{first_link}"
            
            print(f"\nVisiting: {first_link}")
            page.goto(first_link, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
            # Search for Aired on
            page_text = page.inner_text("body")
            match = re.search(r'Aired on:\s*(\w+\s+\d{1,2},?\s+\d{4})', page_text)
            if match:
                print(f"Found date (regex): {match.group(1)}")
            else:
                print("Regex didn't find date")
                # Print all text containing 'aired'
                for line in page_text.split('\n'):
                    if 'aired' in line.lower():
                        print(f"  Line with 'aired': {line[:100]}")
            
            # Try XPath
            date_elem = page.locator("xpath=//div[contains(text(),'Aired on')]")
            if date_elem.count() > 0:
                print(f"XPath found: {date_elem.first.inner_text()}")
            else:
                print("XPath //div[contains(text(),'Aired on')] not found")
        
        browser.close()

def debug_worldatwork():
    """Debug WorldatWork links."""
    print("\n" + "="*60)
    print("DEBUGGING WORLDATWORK")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://worldatwork.org/webinars?delivery=ondemand", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Get page HTML to see structure
        print("Looking for Register text on page...")
        
        # Find all elements with "Register" text
        register_elements = page.query_selector_all("text=Register")
        print(f"Found {len(register_elements)} elements with 'Register' text")
        
        for i, elem in enumerate(register_elements[:3]):
            tag = elem.evaluate("el => el.tagName")
            parent_html = elem.evaluate("el => el.parentElement?.outerHTML?.substring(0, 300) || ''")
            print(f"\n  {i+1}. Tag: {tag}")
            print(f"      Parent: {parent_html[:200]}")
        
        # Find all a tags  
        all_a = page.query_selector_all("a")
        webinar_links = []
        for a in all_a:
            href = a.get_attribute("href") or ""
            text = a.inner_text().strip()
            if "/webinars/" in href and len(text) > 0:
                webinar_links.append((href, text))
        
        print(f"\nFound {len(webinar_links)} links containing '/webinars/':")
        for href, text in webinar_links[:10]:
            print(f"  {text[:30]} -> {href}")
        
        # If we found webinar links, visit one to check for date
        if webinar_links:
            first_link = webinar_links[0][0]
            if not first_link.startswith("http"):
                first_link = f"https://worldatwork.org{first_link}"
            print(f"\nVisiting: {first_link}")
            page.goto(first_link, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
            page_text = page.inner_text("body")
            match = re.search(r'On Demand until\s+(\w+\s+\d{1,2},?\s+\d{4})', page_text)
            if match:
                print(f"Found date: {match.group(1)}")
            else:
                print("Date pattern not found")
                for line in page_text.split('\n'):
                    if 'demand' in line.lower():
                        print(f"  Line: {line[:100]}")
        
        browser.close()

if __name__ == "__main__":
    debug_syndio()
    debug_worldatwork()
