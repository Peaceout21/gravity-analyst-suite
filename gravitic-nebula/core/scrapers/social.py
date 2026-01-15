import logging
from typing import Dict, Optional

from core.config import Settings, get_settings
from core.persistence.engine import SignalStore, default_store
from core.scrapers.social_modern import SocialScraperModern
from core.scrapers.social_legacy import SocialScraperLegacy

logger = logging.getLogger(__name__)

class SocialScraper:
    """
    Social Sentiment Scraper (Router).
    Delegates to either SocialScraperModern (Firecrawl + Gemini) 
    or SocialScraperLegacy (snscrape + VADER) based on configuration.
    """
    
    def __init__(self, config: Optional[Settings] = None, store: Optional[SignalStore] = None):
        self.config = config or get_settings()
        self.store = store or default_store
        
        # Initialize providers
        self.modern = SocialScraperModern(self.config, self.store)
        self.legacy = SocialScraperLegacy(self.config, self.store)

    def get_social_signal(self, ticker: str, query: Optional[str] = None) -> Dict:
        """
        Routes the request to the configured or default social scraper.
        """
        # Default to modern if not specified
        provider_type = getattr(self.config, "social_scraper_type", "modern").lower()
        
        if provider_type == "legacy":
            logger.info(f"Using Legacy Social Scraper (snscrape) for {ticker}")
            return self.legacy.get_social_signal(ticker, query)
        else:
            logger.info(f"Using Modern Social Scraper (Firecrawl + Gemini) for {ticker}")
            return self.modern.get_social_signal(ticker, query)

if __name__ == "__main__":
    # Test router
    scraper = SocialScraper()
    print(scraper.get_social_signal("TSLA"))
