import pytest
from core.scrapers.digital import DigitalScraper

def test_digital_smoothing_and_viral_logic():
    scraper = DigitalScraper()
    ticker = "U" # Unity
    app_id = "com.unity.demo"
    
    alpha = scraper.get_digital_alpha(ticker, app_id)
    
    assert alpha['ticker'] == ticker
    assert alpha['current_value'] < 100 # Viral spike simulated
    assert alpha['signal'] == "Viral"
    assert "revenue surprise" in alpha['interpretation'].lower()
    
    print(f"\n📱 Digital Signal for {ticker}:")
    print(f"   Rank: {alpha['current_value']} (Smoothed: {alpha['smoothed_value']})")
    print(f"   Interpretation: {alpha['interpretation']}")

def test_moving_average_calculation():
    scraper = DigitalScraper()
    # Mock stable history
    history = [{"date": "2025-01-01", "rank": 100}] * 10
    signal = scraper.calculate_smoothed_signal(history)
    
    assert signal['7d_moving_average'] == 100.0
    assert not signal['is_viral_event']
