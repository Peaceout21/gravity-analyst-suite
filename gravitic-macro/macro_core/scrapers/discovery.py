"""
DiscoveryEngine: Maps Tickers to Polymarket Themes and performs Local Search.
"""
from typing import List, Dict, Optional
from macro_core.models_index import MarketMetadata
from macro_core.persistence.index import MarketIndex

TICKER_THEME_MAP = {
    "NVDA": {
        "sector": "AI/Chips",
        "keywords": ["NVDA", "Nvidia", "AI", "Chips", "Semiconductors", "TSMC", "Blackwell", "Jensen Huang"]
    },
    "MSFT": {
        "sector": "Software/Cloud",
        "keywords": ["MSFT", "Microsoft", "OpenAI", "Azure", "Cloud", "SaaS"]
    },
    "AAPL": {
        "sector": "Consumer Tech",
        "keywords": ["AAPL", "Apple", "iPhone", "China Sales", "App Store"]
    },
    "TSLA": {
        "sector": "Auto/Energy",
        "keywords": ["TSLA", "Tesla", "Musk", "EV", "Electric Vehicles", "Charging"]
    },
    "META": {
        "sector": "Ad/Social",
        "keywords": ["META", "Facebook", "Zuckerberg", "Ads", "Instagram", "Threads"]
    },
    "GOOGL": {
        "sector": "Ad/Search",
        "keywords": ["GOOGL", "Google", "Search", "Gemini", "YouTube", "Antitrust"]
    },
    "AMZN": {
        "sector": "Retail/Cloud",
        "keywords": ["AMZN", "Amazon", "AWS", "Retail", "Prime"]
    }
}

MACRO_THEMES = {
    "Macro": ["Fed", "Rates", "Interest Rate", "Inflation", "CPI", "GDP", "Recession", "Jerome Powell"],
    "Politics": ["Election", "Trump", "Biden", "Harris", "Cabinet", "Democrat", "Republican"],
    "Geopolitics": ["War", "Conflict", "China", "Ukraine", "Israel", "Taiwan"]
}

class DiscoveryEngine:
    """
    Orchestrates the discovery of Polymarket signals based on Ticker context.
    Uses Local Market Index for reliable search.
    Auto-triggers ingestion if index is empty or stale.
    """
    
    def __init__(self, auto_ingest: bool = True, max_stale_hours: int = 6):
        self.index = MarketIndex()
        self.auto_ingest = auto_ingest
        self.max_stale_hours = max_stale_hours
        
        # Auto-ingest if enabled and index is empty or stale
        if self.auto_ingest and (self.index.is_empty() or self.index.is_stale(self.max_stale_hours)):
            self._trigger_ingestion()

    def _trigger_ingestion(self, max_pages: int = 20):
        """
        Triggers a background ingestion of active markets.
        Limited to top 20 pages (~2000 events) for speed.
        
        NOTE: Uses raw API calls to avoid circular dependency with PolymarketScraper.
        """
        import requests
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔄 Auto-ingestion triggered: Local index is empty or stale.")
        
        all_metadata = []
        offset = 0
        url = "https://gamma-api.polymarket.com/events"
        session = requests.Session()
        session.headers.update({"Accept": "application/json"})
        
        for i in range(max_pages):
            try:
                params = {
                    "closed": "false",
                    "limit": 100,
                    "offset": offset,
                    "order": "volume",
                    "ascending": "false"
                }
                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for item in data:
                    markets = item.get("markets", [])
                    mkt_id = markets[0].get("id") if markets else None
                    tags = item.get("tags", [])
                    tag_str = ", ".join([t.get("label", "") for t in tags]) if tags else ""
                    vol = float(item.get("volume", 0) or 0)
                    
                    meta = MarketMetadata(
                        event_id=str(item.get("id")),
                        market_id=mkt_id or "",
                        title=item.get("title", "Unknown"),
                        description=item.get("description", ""),
                        slug=item.get("slug", ""),
                        tags=tag_str,
                        volume_usd=vol,
                        end_date=None
                    )
                    all_metadata.append(meta)
                
                offset += 100
                logger.info(f"Page {i+1}: Fetched {len(data)} events (Total: {len(all_metadata)})")
                
            except requests.RequestException as e:
                logger.error(f"Ingestion failed at page {i}: {e}")
                break
        
        count = self.index.upsert_markets(all_metadata)
        logger.info(f"✅ Auto-ingestion complete: {count} markets indexed.")

    def search_ticker(self, ticker: str, limit: int = 10) -> List[MarketMetadata]:
        """
        Deep search for a ticker using aliases and related keywords against local index.
        """
        keywords = self.get_keywords_for_ticker(ticker)
        results = []
        seen_ids = set()
        
        # Search for each keyword
        for kw in keywords:
            matches = self.index.search(kw, limit=limit)
            for m in matches:
                if m.event_id not in seen_ids:
                    results.append(m)
                    seen_ids.add(m.event_id)
        
        # Rank by volume logic could go here
        results.sort(key=lambda x: x.volume_usd, reverse=True)
        return results[:limit]
    
    @staticmethod
    def get_keywords_for_ticker(ticker: str) -> List[str]:
        """Returns relevant keywords for a given ticker."""
        mapping = TICKER_THEME_MAP.get(ticker.upper(), {})
        return mapping.get("keywords", [ticker.upper()])

    @staticmethod
    def get_sector_for_ticker(ticker: str) -> str:
        """Returns the sector label for a given ticker."""
        mapping = TICKER_THEME_MAP.get(ticker.upper(), {})
        return mapping.get("sector", "Other")

    @staticmethod
    def get_all_macro_keywords() -> List[str]:
        """Returns all basic macro keywords."""
        all_kw = []
        for kw_list in MACRO_THEMES.values():
            all_kw.extend(kw_list)
        return all_kw
