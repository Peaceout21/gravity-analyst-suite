import logging
import sys
import os

# Ensure core is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scrapers.social import SocialScraper
from core.scrapers.hiring import HiringScraper
from core.scrapers.digital import DigitalScraper

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Ticker to AppID mapping for DigitalScraper
TICKER_MAP = {
    "TSLA": "361309727",  # Tesla App
    "NVDA": "1515949117", # NVIDIA App
    "META": "284815983",  # Facebook
    "AAPL": "284035628",  # Apple (iTunes Store)
}

def sync_ticker(ticker: str):
    logger.info(f"=== 🚁 Syncing Alpha Signals for {ticker} ===")
    
    # 1. Social
    try:
        social = SocialScraper()
        social.get_social_signal(ticker)
        logger.info(f"✅ Social Synced for {ticker}")
    except Exception as e:
        logger.error(f"❌ Social Sync failed for {ticker}: {e}")

    # 2. Hiring
    try:
        hiring = HiringScraper()
        hiring.get_hiring_signal(ticker)
        logger.info(f"✅ Hiring Synced for {ticker}")
    except Exception as e:
        logger.error(f"❌ Hiring Sync failed for {ticker}: {e}")

    # 3. Digital (if app_id known)
    if ticker in TICKER_MAP:
        try:
            digital = DigitalScraper()
            digital.get_digital_alpha(ticker, TICKER_MAP[ticker])
            logger.info(f"✅ Digital Synced for {ticker}")
        except Exception as e:
            logger.error(f"❌ Digital Sync failed for {ticker}: {e}")

def main():
    tickers = ["TSLA", "NVDA", "AAPL"] # Default set
    if len(sys.argv) > 1:
        tickers = sys.argv[1].upper().split(",")
    
    for ticker in tickers:
        sync_ticker(ticker)
    
    logger.info("\n✨ SOTA Sync Complete. Check Celestial Dashboard (Nebula Alpha Tab).")

if __name__ == "__main__":
    main()
