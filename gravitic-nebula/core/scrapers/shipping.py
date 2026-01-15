import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from core.entity_resolver.engine import HybridResolver
from core.config import Settings, get_settings
from core.persistence.engine import SignalStore, default_store

logger = logging.getLogger(__name__)

import trafilatura
from firecrawl import Firecrawl
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ShippingScraper:
    """
    SOTA Shipping & Supply Chain Scraper.
    Targets BoL (Bill of Lading) and AIS Vessel Tracking.
    """
    
    def __init__(self, resolver: Optional[HybridResolver] = None, config: Optional[Settings] = None, store: Optional[SignalStore] = None):
        self.config = config or get_settings()
        self.store = store or default_store
        self.resolver = resolver
        self.firecrawl = Firecrawl(api_key=self.config.firecrawl_api_key)
        
        # Configure Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def fetch_vessel_status(self, mmsi: str) -> Dict:
        """
        Fetch real-time location via AIS (simulation).
        """
        logger.info(f"Fetching AIS status for MMSI: {mmsi}")
        return {
            "mmsi": mmsi,
            "status": "In Transit",
            "last_seen": datetime.now().isoformat(),
            "destination": "Savannah, USA",
            "eta": "2025-10-25T14:00:00",
            "lat": 32.12,
            "lng": -81.08
        }

    def scrape_manifests(self, consignee: str) -> List[Dict]:
        """
        SOTA Scrape-Parsing: Fetch BoL data efficiently (1 Credit).
        """
        logger.info(f"Scraping manifests for: {consignee}")
        
        if not self.config.use_live_requests:
            logger.info("Using simulated data (USE_LIVE_REQUESTS=False)")
            return [
                {
                    "date": "2025-10-10",
                    "shipper": "Hon Hai Precision",
                    "consignee": consignee,
                    "description": "Electronic components - Model X12",
                    "weight_kg": 45000,
                    "teu": 4
                }
            ]

        # 1. High-Efficiency Scrape (1 Credit)
        url = f"https://www.importyeti.com/search?q={consignee.replace(' ', '+')}"
        try:
            # Correcting for Firecrawl V2 SDK: wait_for instead of waitFor, scrape instead of scrape_url
            scrape_res = self.firecrawl.scrape(
                url, 
                formats=['html', 'markdown'],
                only_main_content=True,
                wait_for=3000
            )
            html_content = getattr(scrape_res, 'html', '')
            markdown_content = getattr(scrape_res, 'markdown', '')
            
            # 2. Trafilatura Pre-processing
            cleaned_text = trafilatura.extract(html_content, include_links=True)
            if not cleaned_text or len(cleaned_text) < 100:
                cleaned_text = markdown_content

            # 3. Local Gemini Synthesis
            prompt = f"""
            Extract a valid JSON list of shipment records for {consignee} from the text below.
            Format: {{ "shipments": [ {{ "date": "YYYY-MM-DD", "shipper": "Name", "teu": number }} ] }}
            
            Only return the JSON.
            
            Text:
            {cleaned_text[:10000]}
            """
            response = self.model.generate_content(prompt)
            raw_json = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw_json)
            
            shipments = data.get('shipments', [])
            logger.info(f"✅ Extracted {len(shipments)} manifests via SOTA Scrape-Parsing from ImportYeti.")
            return shipments
            
        except Exception as e:
            logger.error(f"SOTA Shipping Scrape-Parsing failed: {e}")
            return []

    def nowcast_delivery(self, ticker: str, mmsi: Optional[str] = None) -> Dict:
        """
        Produce a shipping-based revenue nowcast (Checks SOTA Cache).
        """
        # 1. Check persistence
        cached = self.store.get_latest_signal(ticker, "shipping")
        if cached:
            return cached

        logger.info(f"Running Fusion Nowcast for {ticker}")
        
        # Use Resolver if available to get canonical name
        consignee_name = ticker
        if self.resolver:
            res = self.resolver.resolve(ticker)
            if res:
                consignee_name = res['canonical_name']

        manifests = self.scrape_manifests(consignee_name)
        total_teu = sum((m.get('teu') or 0) for m in manifests)
        
        status = "Unknown"
        if mmsi:
            vessel = self.fetch_vessel_status(mmsi)
            status = vessel['status']
            eta = vessel['eta']
        else:
            eta = "N/A"
            
        result = {
            "ticker": ticker,
            "consignee_name": consignee_name,
            "total_inventory_incoming_teu": total_teu,
            "vessel_status": status,
            "estimated_arrival": eta,
            "signal_strength": "High" if total_teu > 5 else "Low",
            "interpretation": f"Inventory flow detected for {consignee_name}. Volume: {total_teu} TEU."
        }

        # 2. Save result
        self.store.save_signal(ticker, "shipping", result, signal_value=float(total_teu), canonical_name=consignee_name)
        
        return result

if __name__ == "__main__":
    # Quick Demo
    scraper = ShippingScraper()
    signal = scraper.nowcast_delivery("AAPL", mmsi="367448370")
    print(json.dumps(signal, indent=2))
