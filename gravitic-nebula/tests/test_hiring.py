import pytest
import json
from core.scrapers.hiring import HiringScraper

def test_hiring_velocity_calculation():
    scraper = HiringScraper()
    ticker = "NVDA"
    
    report = scraper.get_expansion_velocity(ticker)
    
    assert report['ticker'] == ticker
    assert report['total_open_roles'] > 0
    assert "expansion_velocity" in report
    assert report['expansion_velocity'] >= 0.0
    
    print(f"\n💼 Hiring Signal for {ticker}:")
    print(f"   Velocity: {report['expansion_velocity']}")
    print(f"   Signal: {report['signal']}")

def test_role_classification_logic():
    scraper = HiringScraper()
    jobs = [
        {"title": "Staff AI Engineer", "department": "None"},
        {"title": "Inside Sales Rep", "department": "None"},
        {"title": "Office Admin", "department": "None"}
    ]
    
    classified = scraper.classify_roles(jobs)
    
    assert len(classified['RD']) == 1
    assert len(classified['Sales']) == 1
    assert len(classified['GA']) == 1
    assert "Engineer" in classified['RD'][0]['title']
