import pytest
import json
from core.scrapers.shipping import ShippingScraper

def test_shipping_fusion_logic():
    scraper = ShippingScraper()
    
    # Test Nowcasting Fusion
    ticker = "NVDA"
    mmsi = "123456789"
    
    report = scraper.nowcast_delivery(ticker, mmsi)
    
    assert report['ticker'] == ticker
    assert "total_inventory_incoming_teu" in report
    assert report['total_inventory_incoming_teu'] > 0
    assert report['vessel_status'] == "In Transit"
    
    print(f"\n🚢 Shipping Signal for {ticker}:")
    print(f"   Interpretation: {report['interpretation']}")
    print(f"   Volume: {report['total_inventory_incoming_teu']} TEU")

def test_manifest_scraping_structure():
    scraper = ShippingScraper()
    manifests = scraper.scrape_manifests("Walmart")
    
    assert len(manifests) > 0
    assert "shipper" in manifests[0]
    assert "teu" in manifests[0]
