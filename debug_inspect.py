"""
Debug script to inspect actual page structure and find air date elements.
"""
from playwright.sync_api import sync_playwright

def inspect_worldatwork():
    """Inspect WorldatWork page structure."""
    print("\n" + "="*60)
    print("INSPECTING WORLDATWORK")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://worldatwork.org/webinars?delivery=ondemand", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Find all webinar items and print their structure
        items = page.query_selector_all("[class*='card'], article, [class*='item']")
        print(f"\nFound {len(items)} potential items")
        
        for i, item in enumerate(items[:5]):  # First 5 only
            print(f"\n--- Item {i+1} ---")
            print(f"Outer HTML (first 500 chars):")
            html = item.evaluate("el => el.outerHTML")
            print(html[:500])
            
            # Look for text that might be dates
            text = item.inner_text()
            print(f"\nInner text:")
            print(text[:300] if len(text) > 300 else text)
        
        browser.close()

def inspect_pave():
    """Inspect Pave page structure."""
    print("\n" + "="*60)
    print("INSPECTING PAVE")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.pave.com/insights/events-and-webinars", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        
        # Find webinar cards
        cards = page.query_selector_all("a[href*='explore.pave.com']")
        print(f"\nFound {len(cards)} webinar links")
        
        for i, card in enumerate(cards[:5]):  # First 5 only
            print(f"\n--- Card {i+1} ---")
            
            # Get parent container
            parent = card.evaluate("el => el.closest('div')?.outerHTML || el.outerHTML")
            print(f"Parent HTML (first 800 chars):")
            print(parent[:800])
            
            # Get full text
            text = card.inner_text()
            print(f"\nCard text:")
            print(text[:300] if len(text) > 300 else text)
        
        browser.close()

if __name__ == "__main__":
    try:
        inspect_worldatwork()
    except Exception as e:
        print(f"WorldatWork error: {e}")
    
    try:
        inspect_pave()
    except Exception as e:
        print(f"Pave error: {e}")
