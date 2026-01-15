#!/usr/bin/env python3
"""
Runs the Ingestion Engine to build the Local Market Index.
Then performs a local search for 'NVDA' to verify the fix.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
from macro_core.scrapers.polymarket import PolymarketScraper
from macro_core.persistence.index import MarketIndex

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🚜 POLYMARKET INGESTION & LOCAL INDEXING")
    print("=" * 60)

    # 1. Ingest
    scraper = PolymarketScraper()
    # Fetch 20 pages * 100 = 2000 top markets by volume
    # This should be enough to capture significant NVDA events
    markets = scraper.ingest_all_markets(max_pages=20) 
    
    # 2. Index
    print(f"\n💾 Indexing {len(markets)} markets into SQLite...")
    indexer = MarketIndex()
    count = indexer.upsert_markets(markets)
    print(f"✅ Indexed {count} documents.")
    
    # 3. Local Search Verification
    query = "NVDA"
    print(f"\n🔍 Executing LOCAL search for '{query}'...")
    results = indexer.search(query)
    
    if not results:
        print("❌ No matches found locally.")
    else:
        print(f"✅ Found {len(results)} matches:")
        for i, m in enumerate(results, 1):
            print(f"{i}. [{m.volume_usd:,.0f}] {m.title}")
            print(f"   Slug: {m.slug}")
            print(f"   Tags: {m.tags}")
            print("-" * 40)

if __name__ == "__main__":
    main()
