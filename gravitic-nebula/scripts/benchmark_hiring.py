import logging
import json
import os
from typing import List
from core.scrapers.hiring import HiringScraper
from core.config import get_settings

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("BENCHMARK")

def run_benchmarks():
    """
    Runs HiringScraper on a diverse set of companies to verify Macro/Micro metrics.
    """
    companies = [
        "Microsoft", # Big Tech (Large)
        "Apple",     # Big Tech (Large)
        "Appian",    # Mid-Cap (Greenhouse/Lever likely)
        "Fastly"     # Mid-Cap (Greenhouse/Lever likely)
    ]
    
    # Ensure live requests are enabled
    settings = get_settings()
    settings.use_live_requests = True
    
    scraper = HiringScraper(config=settings)
    
    print("\n" + "="*50)
    print("🚀 STARTING HIRING SIGNAL BENCHMARKS")
    print("="*50 + "\n")
    
    results = []
    for company in companies:
        try:
            print(f"📡 Processing {company}...")
            signal = scraper.get_expansion_velocity(company)
            results.append(signal)
            
            print(f"\n✅ Results for {company}:")
            print(json.dumps(signal, indent=2))
            print("-" * 30)
            
        except Exception as e:
            logger.error(f"Failed benchmark for {company}: {e}")
            results.append({"ticker": company, "error": str(e)})

    print("\n" + "="*50)
    print("📊 BENCHMARK SUMMARY")
    print("="*50)
    
    for res in results:
        if "error" in res:
            print(f"{res['ticker']}: ❌ FAILED - {res['error']}")
        else:
            print(f"{res['ticker']}: Macro {res.get('total_open_roles_macro')} | Velocity {res.get('expansion_velocity')} | Signal {res.get('signal')}")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    run_benchmarks()
