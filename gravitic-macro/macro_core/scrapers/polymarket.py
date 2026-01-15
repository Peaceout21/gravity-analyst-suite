import requests
import logging
import re
import ast
from typing import List, Optional
from datetime import datetime

from macro_core.models import MacroEvent
from macro_core.models_index import MarketMetadata
from macro_core.scrapers.discovery import DiscoveryEngine
from macro_core.scrapers.filter import LLMFilter

logger = logging.getLogger(__name__)

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

class PolymarketScraper:
    """
    Scrapes prediction market data from Polymarket's Gamma API.
    """

    def __init__(self, min_volume_usd: float = 10000.0, use_llm_filter: bool = True):
        """
        Args:
            min_volume_usd: Minimum trading volume to filter noise.
            use_llm_filter: Whether to use Gemini to filter for investment-grade signals.
        """
        self.min_volume_usd = min_volume_usd
        self.use_llm_filter = use_llm_filter
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.llm_filter = LLMFilter() if use_llm_filter else None
        self.discovery = DiscoveryEngine()

    def search_events_by_text(self, query: str, limit: int = 50) -> List[dict]:
        """
        Searches Polymarket events using the API's title_contains filter.
        This is more efficient than fetching all and filtering client-side.
        """
        try:
            url = f"{GAMMA_API_BASE}/events"
            params = {
                "closed": "false", 
                "limit": limit,
                "title_contains": query
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Search for '{query}' returned {len(data)} events")
            return data
        except requests.RequestException as e:
            logger.error(f"Search API error: {e}")
            return []

    def fetch_macro_events(self, keywords: Optional[List[str]] = None, ticker: Optional[str] = None, limit: int = 50) -> List[MacroEvent]:
        """
        Fetches active prediction market events from Polymarket.
        
        ARCHITECTURE: Uses LOCAL INDEX as the primary search path.
        The broken Polymarket search API is bypassed entirely.
        
        Flow: Local Index Search -> Hydration via API -> Return MacroEvents

        Args:
            keywords: Optional list of keywords to filter events.
            ticker: Optional ticker symbol to auto-discover keywords.
            limit: Maximum number of events to return.

        Returns:
            List of MacroEvent objects with live probabilities.
        """
        try:
            # 1. Search local index (deterministic, fast)
            if ticker:
                metadata = self.discovery.search_ticker(ticker, limit=limit)
                sector = self.discovery.get_sector_for_ticker(ticker)
                related_ticker = ticker.upper()
            elif keywords:
                # Search for each keyword and de-duplicate
                metadata = []
                seen_ids = set()
                for kw in keywords[:5]:
                    matches = self.discovery.index.search(kw, limit=limit)
                    for m in matches:
                        if m.event_id not in seen_ids:
                            metadata.append(m)
                            seen_ids.add(m.event_id)
                sector = "Macro"
                related_ticker = None
            else:
                # Fallback: get top N by volume from index
                metadata = self.discovery.index.search("*", limit=limit)
                sector = "Macro"
                related_ticker = None
            
            if not metadata:
                logger.warning("No results from local index search.")
                return []
            
            logger.info(f"Found {len(metadata)} candidates in local index.")
            
            # 2. Hydrate with live probabilities
            events = self.hydrate_metadata(metadata)
            
            # 3. Attach sector/ticker context
            for event in events:
                event.sector = sector
                event.related_ticker = related_ticker
            
            # 4. Optional: LLM Filtering
            if self.use_llm_filter and events:
                titles = [e.title for e in events]
                approved_titles = self.llm_filter.filter_events(str(titles))
                events = [e for e in events if e.title in approved_titles]
            
            logger.info(f"Returning {len(events)} hydrated macro events.")
            return events[:limit]

        except Exception as e:
            logger.error(f"fetch_macro_events failed: {e}")
            return []

    def get_event_by_id(self, event_id: str) -> Optional[MacroEvent]:
        """Fetches a specific market by its ID (not condition ID, the actual market ID)."""
        try:
            url = f"{GAMMA_API_BASE}/markets/{event_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            market = response.json()
            return self._parse_single_market(market)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch event {event_id}: {e}")
            return None

    def get_event_by_slug(self, slug: str) -> Optional[MacroEvent]:
        """
        Fetches an event directly by its slug (e.g. 'will-nvda-hit-100').
        Useful for resolving direct URLs pasted by analysts.
        """
        try:
            url = f"{GAMMA_API_BASE}/events"
            params = {"slug": slug}
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning(f"No event found for slug: {slug}")
                return None
            
            # Use the first matching event
            item = data[0]
            markets = item.get("markets", [])
            if not markets:
                return None
                
            # We reuse the same parsing logic, but we need to check if we can reuse _parse_single_market
            # _parse_single_market expects a 'market' object, but here we have an 'event' object which contains markets.
            # Let's extract the primary market and parse it.
            return self.get_event_by_id(markets[0]["id"])
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch slug {slug}: {e}")
            return None

    def _parse_single_market(self, market: dict) -> MacroEvent:
        """Helper to parse a single market dict into a MacroEvent."""
        try:
            # Parse outcomes safely
            outcomes_data = []
            try:
                outcome_labels = ast.literal_eval(market.get("outcomes", "[]"))
                prices = ast.literal_eval(market.get("outcomePrices", "[]"))
                if outcome_labels and prices:
                    for label, price in zip(outcome_labels, prices):
                        outcomes_data.append({"label": label, "probability": float(price)})
                prob_yes = float(prices[0]) if prices else 0.5
            except:
                prob_yes = 0.5

            return MacroEvent(
                event_id=market.get("id", ""), # Market ID
                title=market.get("question", "Unknown"),
                probability_yes=prob_yes,
                outcomes=outcomes_data,
                volume_usd=float(market.get("volume", 0) or 0),
                source="polymarket"
            )
        except Exception as e:
            logger.error(f"Error parsing market: {e}")
            # Return a shell event on error
            return MacroEvent(event_id="", title="Error Parsing", probability_yes=0.0, volume_usd=0.0, source="error")

    def hydrate_metadata(self, metadata: List[MarketMetadata]) -> List[MacroEvent]:
        """
        Takes lightweight MarketMetadata (from local index) and 
        fetches real-time probabilities for all of them.
        """
        results = []
        for meta in metadata:
            if not meta.market_id:
                continue
            event = self.get_event_by_id(meta.market_id)
            if event:
                # Re-attach keywords/tags context if found
                results.append(event)
        return results

    def ingest_all_markets(self, limit_per_page: int = 100, max_pages: int = 50) -> List[MarketMetadata]:
        """
        Pages through ALL active markets to build a local index.
        Bypasses broken search API by fetching the entire corpus.
        """
        all_metadata = []
        offset = 0
        url = f"{GAMMA_API_BASE}/events"
        
        logger.info("Starting full market ingestion...")
        
        for i in range(max_pages):
            try:
                params = {
                    "closed": "false",
                    "limit": limit_per_page,
                    "offset": offset,
                    "order": "volume", # Prioritize high volume
                    "ascending": "false"
                }
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                batch = []
                for item in data:
                    # Extract Market ID (first market usually)
                    markets = item.get("markets", [])
                    mkt_id = markets[0].get("id") if markets else None
                    
                    # Extract Tags
                    tags = item.get("tags", [])
                    tag_str = ", ".join([t.get("label", "") for t in tags]) if tags else ""
                    
                    # Volume
                    vol = float(item.get("volume", 0) or 0)
                    
                    meta = MarketMetadata(
                        event_id=str(item.get("id")),
                        market_id=mkt_id or "",
                        title=item.get("title", "Unknown"),
                        description=item.get("description", ""),
                        slug=item.get("slug", ""),
                        tags=tag_str,
                        volume_usd=vol,
                        end_date=None # Parse if needed
                    )
                    batch.append(meta)
                
                all_metadata.extend(batch)
                logger.info(f"Page {i+1}: Fetched {len(batch)} events (Total: {len(all_metadata)})")
                
                offset += limit_per_page
                
            except requests.RequestException as e:
                logger.error(f"Ingestion failed at page {i}: {e}")
                break
                
        return all_metadata

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = PolymarketScraper(min_volume_usd=50000)
    
    # Test: Fetch Fed-related events
    events = scraper.fetch_macro_events(keywords=["Fed", "Trump", "Recession"], limit=10)
    for e in events:
        print(f"[{e.probability_yes:.1%}] {e.title} (Vol: ${e.volume_usd:,.0f})")
