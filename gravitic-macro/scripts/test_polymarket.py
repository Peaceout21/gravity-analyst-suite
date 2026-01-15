#!/usr/bin/env python3
"""
Test script for Polymarket Scraper.
Fetches live macro events and saves to time-series DB.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
from macro_core.scrapers.polymarket import PolymarketScraper
from macro_core.persistence.timeseries import TimeSeriesPersistence

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🔮 POLYMARKET MACRO RADAR - LIVE TEST")
    print("=" * 60)

    # Initialize scraper (min $50k volume for quality signals)
    scraper = PolymarketScraper(min_volume_usd=50000)
    
    # Target keywords for macro events
    keywords = ["Fed", "Trump", "Recession", "GDP", "Inflation", "Election"]
    
    print(f"\n📡 Fetching events with keywords: {keywords}")
    events = scraper.fetch_macro_events(keywords=keywords, limit=15)
    
    if not events:
        print("❌ No events found. API may be rate-limited or keywords too restrictive.")
        return
    
    print(f"\n✅ Found {len(events)} macro events:\n")
    for i, e in enumerate(events, 1):
        prob_fmt = f"{e.probability_yes:.1%}"
        vol_fmt = f"${e.volume_usd:,.0f}" if e.volume_usd else "N/A"
        print(f"{i:2}. [{prob_fmt:>6}] {e.title[:60]}... (Vol: {vol_fmt})")
    
    # Persist to time-series DB
    print("\n💾 Saving to time-series database...")
    db = TimeSeriesPersistence()
    saved_count = db.save_batch(events)
    print(f"✅ Saved {saved_count} event snapshots to macro_signals.db")
    
    # Show latest probabilities
    print("\n📊 Latest Probability Snapshots:")
    latest = db.get_latest_probabilities(limit=5)
    for row in latest:
        print(f"   - {row['event_title'][:50]}: {row['probability_yes']:.1%}")

    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
