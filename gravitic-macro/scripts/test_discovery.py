#!/usr/bin/env python3
"""
Test script for Sector-Aware Discovery.
Fetches signals for NVDA and Macro themes.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
from macro_core.scrapers.polymarket import PolymarketScraper
from macro_core.scrapers.discovery import DiscoveryEngine
from macro_core.persistence.timeseries import TimeSeriesPersistence

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🔮 SECTOR-AWARE DISCOVERY TEST (NVDA)")
    print("=" * 60)

    # Initialize Discovery Engine (uses Local Index)
    discovery = DiscoveryEngine()
    
    print(f"\n📡 Discovering signals for Ticker: NVDA (Local Index)...")
    try:
        events = discovery.search_ticker("NVDA", limit=10)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        events = []
    
    if not events:
        print("❌ No sector signals found for NVDA.")
    else:
        print(f"\n✅ Found {len(events)} relevant AI/Chip events:")
        for i, m in enumerate(events, 1):
             print(f"{i}. [{m.volume_usd:,.0f}] {m.title}")
             print(f"   Slug: {m.slug}")
    
    # Also fetch broad macro using the same discovery engine (simple search)
    print(f"\n📡 Fetching Broad Macro Signals (Local Index)...")
    try:
        macro_events = discovery.search_ticker("Macro", limit=5)
    except Exception as e:
        logger.error(f"Macro search failed: {e}")
        macro_events = []
    
    
    # Consolidate and Hydrate
    # We need to fetch live probabilities for these search results
    print("\n💧 Hydrating events with live probabilities...")
    full_events = []
    
    # Initialize scraper for hydration
    scraper = PolymarketScraper()
    
    # Helper to hydrate
    def hydrate_and_append(metadata_list):
        for m in metadata_list:
            if not m.market_id:
                continue
            try:
                # Fetch live details
                live_event = scraper.get_event_by_id(m.market_id)
                if live_event:
                    # Inject sector/ticker context if known (naively for now)
                    if "NVDA" in m.title or "NVIDIA" in m.title:
                        live_event.sector = "AI/Chips"
                        live_event.related_ticker = "NVDA"
                    elif "Macro" in m.tags:
                        live_event.sector = "Macro"
                        
                    full_events.append(live_event)
            except Exception as e:
                logger.warning(f"Failed to hydrate {m.market_id}: {e}")

    hydrate_and_append(events)
    hydrate_and_append(macro_events)
    
    # Save to Time-Series DB
    print(f"\n💾 Saving {len(full_events)} hydrated snapshots to database...")
    db_path = "/Users/arjun/.gemini/antigravity/scratch/gravitic-macro/macro_signals.db"
    
    db = TimeSeriesPersistence(db_path=db_path)
    saved_count = db.save_batch(full_events)
    print(f"✅ Saved {saved_count} tagged snapshots.")
    
    # Verify latest
    print("\n📊 Latest Snapshots (With Tags):")
    latest = db.get_latest_probabilities(limit=5)
    for row in latest:
        ticker_tag = f"({row['related_ticker']})" if row['related_ticker'] else ""
        sector_tag = row['sector'] or "Unclassified"
        print(f"   - {sector_tag} {ticker_tag}: {row['event_title'][:40]} -> {row['probability_yes']:.1%}")

    print("\n" + "=" * 60)
    print("🏁 Discovery Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
