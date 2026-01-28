"""Quick script to view the database contents."""
import sqlite3

conn = sqlite3.connect('data/webinars.db')
cursor = conn.cursor()

print("=" * 80)
print("WEBINAR DATABASE CONTENTS")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM webinars")
total = cursor.fetchone()[0]
print(f"Total webinars: {total}")
print()

cursor.execute("""
    SELECT provider, webinar_type, title, detail_link 
    FROM webinars 
    ORDER BY provider, title
""")

rows = cursor.fetchall()

print(f"{'PROVIDER':12} | {'TYPE':10} | TITLE")
print("-" * 80)

for provider, wtype, title, link in rows:
    print(f"{provider:12} | {wtype:10} | {title[:50]}")

conn.close()
