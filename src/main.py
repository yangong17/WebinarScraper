"""
Main entry point for the Webinar Aggregation Agent.
Simplified version: On-demand webinars only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.syndio import SyndioCollector
from src.collectors.worldatwork import WorldatWorkCollector
from src.collectors.pave import PaveCollector
from src.database.db_manager import DatabaseManager
from src.database.models import Webinar


def main():
    """Run all collectors and update the database."""
    print("=" * 60)
    print("Webinar Aggregation Agent")
    print("=" * 60)
    
    db = DatabaseManager()
    
    total_inserted = 0
    total_updated = 0
    
    # Syndio - pass existing links to skip duplicates
    print(f"\n{'─' * 40}")
    print(f"Running Syndio...")
    syndio_existing = db.get_existing_links("Syndio")
    print(f"  (Found {len(syndio_existing)} existing entries in DB)")
    syndio_collector = SyndioCollector(existing_links=syndio_existing)
    syndio_results = syndio_collector.run()
    
    if syndio_results:
        for r in syndio_results:
            webinar = Webinar(source=r["source"], title=r["title"], air_date=r.get("air_date"), link=r["link"])
            if db.upsert_webinar(webinar):
                total_inserted += 1
            else:
                total_updated += 1
        print(f"  ✓ Collected {len(syndio_results)} webinars")
    else:
        print(f"  ✗ No new webinars found")
    
    # WorldatWork - pass existing links to skip duplicates
    print(f"\n{'─' * 40}")
    print(f"Running WorldatWork...")
    waw_existing = db.get_existing_links("WorldatWork")
    print(f"  (Found {len(waw_existing)} existing entries in DB)")
    waw_collector = WorldatWorkCollector(existing_links=waw_existing)
    waw_results = waw_collector.run()
    
    if waw_results:
        for r in waw_results:
            webinar = Webinar(source=r["source"], title=r["title"], air_date=r.get("air_date"), link=r["link"])
            if db.upsert_webinar(webinar):
                total_inserted += 1
            else:
                total_updated += 1
        print(f"  ✓ Collected {len(waw_results)} webinars")
    else:
        print(f"  ✗ No new webinars found")
    
    # Pave - doesn't need detail page visits, dates are on listing
    print(f"\n{'─' * 40}")
    print(f"Running Pave...")
    pave_collector = PaveCollector()
    pave_results = pave_collector.run()
    
    if pave_results:
        for r in pave_results:
            webinar = Webinar(source=r["source"], title=r["title"], air_date=r.get("air_date"), link=r["link"])
            if db.upsert_webinar(webinar):
                total_inserted += 1
            else:
                total_updated += 1
        print(f"  ✓ Collected {len(pave_results)} webinars")
    else:
        print(f"  ✗ No webinars found")
    
    print(f"\n{'=' * 60}")
    print(f"Complete! Inserted: {total_inserted}, Updated: {total_updated}")
    print("=" * 60)
    
    # Show database contents
    print("\nDatabase Contents:")
    print("-" * 100)
    print(f"{'SOURCE':12} | {'AIR DATE':20} | TITLE")
    print("-" * 100)
    
    for w in db.get_all():
        date = w["air_date"][:20] if w["air_date"] else "N/A"
        print(f"{w['source']:12} | {date:20} | {w['title'][:50]}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
