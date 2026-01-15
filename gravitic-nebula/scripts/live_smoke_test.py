import logging
import json
import os
from core.config import get_settings
from core.scrapers.hiring import HiringScraper
from core.scrapers.shipping import ShippingScraper
from core.scrapers.digital import DigitalScraper

# Setup verbose logging to see the API flow
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LIVE_SMOKE")

def run_live_smoke():
    settings = get_settings()
    # OVERRIDE to Live mode for this script
    settings.use_live_requests = True
    
    logger.info("🔥 Starting Live Smoke Test (SOTA APIs Enabled)")
    
    # 1. Hiring Smoke (Firecrawl + Gemini)
    hiring = HiringScraper(config=settings)
    logger.info("📡 Testing Hiring Signal (Live)...")
    hiring_signal = hiring.get_expansion_velocity("Nvidia")
    print(f"\n💼 Hiring Signal (Nvidia):\n{json.dumps(hiring_signal, indent=2)}")
    
    # 2. Shipping Smoke (Firecrawl Manifest Search)
    shipping = ShippingScraper(config=settings)
    logger.info("📡 Testing Shipping Manifests (Live)...")
    # Using 'Tesla' as they have high volume manifestations
    shipping_signal = shipping.nowcast_delivery("Tesla")
    print(f"\n🚢 Shipping Signal (Tesla):\n{json.dumps(shipping_signal, indent=2)}")
    
    # 3. Digital Smoke (Firecrawl + Gemini parse)
    digital = DigitalScraper(config=settings)
    logger.info("📡 Testing Digital Footprint (Live)...")
    digital_alpha = digital.get_digital_alpha("Unity", "Unity-3D")
    print(f"\n📱 Digital Alpha (Unity):\n{json.dumps(digital_alpha, indent=2)}")

if __name__ == "__main__":
    if not os.getenv("FIRECRAWL_API_KEY") and not get_settings().firecrawl_api_key:
        print("❌ Error: FIRECRAWL_API_KEY not found in .env")
    else:
        run_live_smoke()
