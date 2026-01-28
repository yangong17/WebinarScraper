"""
Coda API integration for exporting webinar data.

Requires:
- CODA_API_TOKEN: Your Coda API token
- CODA_DOC_ID: The document ID from your Coda doc URL
- CODA_TABLE_ID: The table ID or table name
"""
import os
import requests
from typing import List, Dict


class CodaExporter:
    """Export webinar data to a Coda table."""
    
    BASE_URL = "https://coda.io/apis/v1"
    
    def __init__(self):
        self.api_token = os.environ.get("CODA_API_TOKEN")
        self.doc_id = os.environ.get("CODA_DOC_ID")
        self.table_id = os.environ.get("CODA_TABLE_ID")
        
        if not all([self.api_token, self.doc_id, self.table_id]):
            raise ValueError(
                "Missing required environment variables: "
                "CODA_API_TOKEN, CODA_DOC_ID, CODA_TABLE_ID"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def list_tables(self) -> List[Dict]:
        """List all tables in the doc to help find the correct table ID."""
        url = f"{self.BASE_URL}/docs/{self.doc_id}/tables"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tables = response.json().get("items", [])
            print(f"  Available tables in doc:")
            for t in tables:
                print(f"    - ID: {t.get('id')} | Name: {t.get('name')}")
            return tables
        except Exception as e:
            print(f"  Error listing tables: {e}")
            return []
    
    def get_existing_links(self) -> set:
        """Get existing webinar links from Coda table to avoid duplicates."""
        url = f"{self.BASE_URL}/docs/{self.doc_id}/tables/{self.table_id}/rows"
        existing_links = set()
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            rows = response.json().get("items", [])
            for row in rows:
                values = row.get("values", {})
                # Try common column names for link
                link = values.get("Link") or values.get("link") or values.get("URL") or values.get("url")
                if link:
                    existing_links.add(link)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  Table not found. Listing available tables...")
                self.list_tables()
            raise
        except Exception as e:
            print(f"Warning: Could not fetch existing rows: {e}")
        
        return existing_links
    
    def upsert_rows(self, webinars: List[Dict]) -> Dict:
        """
        Insert or update rows in the Coda table.
        
        Your Coda table should have columns:
        - Source
        - Title
        - Air Date
        - Link
        """
        url = f"{self.BASE_URL}/docs/{self.doc_id}/tables/{self.table_id}/rows"
        
        # First, verify we can access the table
        print(f"  Using Doc ID: {self.doc_id}")
        print(f"  Using Table ID: {self.table_id}")
        
        # Get existing links to determine what's new
        existing_links = self.get_existing_links()
        
        # Filter to only new webinars
        new_webinars = [w for w in webinars if w.get("link") not in existing_links]
        
        if not new_webinars:
            return {"inserted": 0, "message": "No new webinars to add"}
        
        # Format rows for Coda API
        rows = []
        for w in new_webinars:
            rows.append({
                "cells": [
                    {"column": "Source", "value": w.get("source", "")},
                    {"column": "Title", "value": w.get("title", "")},
                    {"column": "Air Date", "value": w.get("air_date") or ""},
                    {"column": "Link", "value": w.get("link", "")}
                ]
            })
        
        # Coda API allows up to 500 rows per request
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            payload = {"rows": batch}
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            total_inserted += len(batch)
            print(f"  Inserted batch of {len(batch)} rows")
        
        return {"inserted": total_inserted, "message": f"Added {total_inserted} new webinars"}


def export_to_coda(webinars: List[Dict]) -> Dict:
    """
    Export webinars to Coda.
    
    Args:
        webinars: List of webinar dicts with keys: source, title, air_date, link
    
    Returns:
        Result dict with insert count
    """
    exporter = CodaExporter()
    return exporter.upsert_rows(webinars)
