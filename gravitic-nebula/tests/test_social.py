from core.config import Settings
from core.scrapers.social import SocialScraper


def test_social_simulated_signal_has_compound():
    settings = Settings(use_live_requests=False)
    scraper = SocialScraper(config=settings)

    signal = scraper.get_social_signal("NVDA", query="NVDA OR Nvidia")

    assert signal["ticker"] == "NVDA"
    assert signal["metric"] == "Tweet Sentiment"
    assert signal["total_tweets"] == 50
    assert signal["avg_compound"] == 0.18
    assert signal["signal"] in {"Bullish", "Bearish", "Neutral"}
