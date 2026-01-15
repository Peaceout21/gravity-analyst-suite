import json
import logging
import sys
import os

# Ensure we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scrapers.social import SocialScraper
from core.config import get_settings

# Setup logging to see the SOTA output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_debug():
    print("=== 🛰️ Social Scraper Modernization - Debug Session ===\n")
    
    settings = get_settings()
    # Force live requests for this test
    os.environ["USE_LIVE_REQUESTS"] = "True"
    
    scraper = SocialScraper()
    
    ticker = "TSLA"
    print(f"Testing ticker: {ticker}")
    
    try:
        result = scraper.get_social_signal(ticker)
        print("\n--- 📊 Final Signal Output ---")
        print(json.dumps(result, indent=2))
        
        if result.get("signal") == "Neutral" and result.get("sentiment_score") == 0.5:
             print("\n⚠️ WARNING: Neutral fallback detected. Check API keys or Firecrawl connectivity.")
        else:
             print("\n✅ SUCCESS: Modernized social signal retrieved.")
             
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")

if __name__ == "__main__":
    run_debug()
