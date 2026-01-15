from macro_core.scrapers.polymarket import PolymarketScraper
from macro_core.scrapers.filter import LLMFilter
import logging
import json

# Setup
logging.basicConfig(level=logging.INFO)
scraper = PolymarketScraper(use_llm_filter=False)

print("=== 🧪 Testing Improvements ===\n")

# 1. Test Slug Fetching
print("--- 🐌 Testing Slug Fetching ---")
slug = "tesla-launches-unsupervised-full-self-driving-fsd-by"
print(f"Fetching slug: {slug}...")
event = scraper.get_event_by_slug(slug)
if event:
    print(f"✅ Success! Found: {event.title}")
    print(f"   Prob: {event.probability_yes:.1%}")
else:
    print("❌ Failed to fetch slug (Check if slug is valid/active)")

# 2. Test LLM Filter (Mocking output logic check)
print("\n--- 🧠 Testing LLM Filter Prompt ---")
filterer = LLMFilter()
test_titles = [
    "Will the Fed raise rates in March?",
    "Will Taylor Swift release a new album?",
    "Bitcoin hits $100k by December"
]
print(f"Input: {test_titles}")
# Note: This requires API key. If not present, it skips.
try:
    if filterer.client:
        approved = filterer.filter_events(json.dumps(test_titles))
        print(f"Approved: {approved}")
        if "Will Taylor Swift release a new album?" not in approved:
            print("✅ Filter successfully removed noise.")
        else:
            print("⚠️ Filter approved noise (check prompt).")
    else:
        print("⚠️ No API Key - Skipping live LLM test.")
except Exception as e:
    print(f"❌ Filter Error: {e}")

print("\n=== Test Complete ===")
