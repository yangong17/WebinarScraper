"""
Base collector using Playwright for JavaScript-rendered pages.
"""
from abc import ABC, abstractmethod
from typing import List
from playwright.sync_api import sync_playwright, Page, Browser
import logging


class BaseCollector(ABC):
    """Abstract base class for Playwright-based collectors."""
    
    SOURCE_NAME: str = "Unknown"
    
    def __init__(self):
        self.logger = logging.getLogger(f"collector.{self.SOURCE_NAME.lower()}")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
            self.logger.addHandler(handler)
    
    @abstractmethod
    def collect(self, page: Page) -> List[dict]:
        """Collect webinars using the Playwright page. Returns list of dicts."""
        pass
    
    def run(self) -> List[dict]:
        """Run the collector with Playwright."""
        self.logger.info(f"Starting collection for {self.SOURCE_NAME}")
        webinars = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                webinars = self.collect(page)
                browser.close()
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
        
        self.logger.info(f"Collected {len(webinars)} webinars from {self.SOURCE_NAME}")
        return webinars
