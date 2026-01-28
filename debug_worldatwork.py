"""
Debug script to inspect WorldatWork page structure for dates.
"""
from playwright.sync_api import sync_playwright

def inspect_worldatwork():
    """Inspect WorldatWork page structure for dates."""
    print("\n" + "="*60)
    print("INSPECTING WORLDATWORK FOR DATES")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://worldatwork.org/webinars?delivery=ondemand", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Use the user-provided XPath structure to find webinar items
        # XPath: /html/body/div[3]/div[6]/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/span[1]
        # This suggests the structure is: div[2] > div[1] > div[2] > div[2] > div[1] > span[1] for title
        
        # Let's look at the parent container
        container = page.locator("xpath=/html/body/div[3]/div[6]/div/div/div/div/div[2]")
        if container.count() > 0:
            print("\nFound main container")
            
            # Get all child divs that look like webinar items
            items = container.locator("div[class*='']").all()
            print(f"Found {len(items)} direct children")
        
        # Let's try to find webinar cards more specifically
        # Look for the list items that contain webinar info
        webinar_items = page.query_selector_all("div[class*='row'], div[class*='webinar'], div[class*='card']")
        print(f"\nFound {len(webinar_items)} potential webinar items")
        
        for i, item in enumerate(webinar_items[:10]):
            html = item.evaluate("el => el.outerHTML")
            if 'webinar' in html.lower() or 'register' in html.lower():
                print(f"\n--- Item {i+1} ---")
                text = item.inner_text()
                print(f"Text (first 400 chars):\n{text[:400]}")
        
        # Let's also try the specific XPath the user gave
        title_xpath = "/html/body/div[3]/div[6]/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/span[1]"
        title_elem = page.locator(f"xpath={title_xpath}")
        if title_elem.count() > 0:
            print(f"\n\nUser XPath found: {title_elem.inner_text()}")
        
        browser.close()

if __name__ == "__main__":
    inspect_worldatwork()
