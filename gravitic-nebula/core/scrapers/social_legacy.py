import json
import logging
import importlib.util
from typing import Dict, Optional, List

from core.config import Settings, get_settings
from core.persistence.engine import SignalStore, default_store

logger = logging.getLogger(__name__)

def _safe_find_spec(module_name: str):
    try:
        return importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        return None


VADER_AVAILABLE = _safe_find_spec("vaderSentiment.vaderSentiment") is not None
if VADER_AVAILABLE:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
else:
    SentimentIntensityAnalyzer = None  # type: ignore

SNTWITTER_AVAILABLE = _safe_find_spec("snscrape.modules.twitter") is not None
if SNTWITTER_AVAILABLE:
    import snscrape.modules.twitter as sntwitter  # type: ignore
else:
    sntwitter = None  # type: ignore


class SocialScraperLegacy:
    """
    Social Sentiment Scraper (Legacy).

    Collects recent tweets about a company and derives a sentiment-based signal.
    Uses snscrape if installed. When live requests are disabled, it returns
    deterministic sample data for testing.
    """

    def __init__(self, config: Optional[Settings] = None, store: Optional[SignalStore] = None):
        self.config = config or get_settings()
        self.store = store or default_store
        self.sentiment_model = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer else None

    def _fetch_tweets(self, query: str, limit: int = 100) -> List[str]:
        """Fetch tweets matching a query using snscrape if available."""
        if sntwitter is None:
            raise ImportError(
                "snscrape is not installed. Install `snscrape` or set USE_LIVE_REQUESTS=False."
            )

        tweets: List[str] = []
        seen = set()
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            content = (tweet.content or "").strip()
            if not content or content.startswith("RT "):
                continue
            if content in seen:
                continue
            seen.add(content)
            tweets.append(content)
        return tweets

    def _analyze_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """Perform sentiment analysis using VADER."""
        if not self.sentiment_model:
            raise ImportError(
                "vaderSentiment is not installed. Install `vaderSentiment` or set USE_LIVE_REQUESTS=False."
            )

        total = len(texts)
        pos_count = 0
        neg_count = 0
        compound_total = 0.0
        for text in texts:
            scores = self.sentiment_model.polarity_scores(text)
            compound_total += scores["compound"]
            if scores["compound"] >= 0.05:
                pos_count += 1
            elif scores["compound"] <= -0.05:
                neg_count += 1

        positive_ratio = (pos_count / total) if total else 0.0
        negative_ratio = (neg_count / total) if total else 0.0
        avg_compound = (compound_total / total) if total else 0.0
        return {
            "total_tweets": total,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "positive_ratio": round(positive_ratio, 2),
            "negative_ratio": round(negative_ratio, 2),
            "avg_compound": round(avg_compound, 3),
        }

    def get_social_signal(self, ticker: str, query: Optional[str] = None) -> Dict:
        """
        Compute a tweet-based social sentiment signal for a given ticker.

        Checks the cache via SignalStore before performing a live scrape. If
        USE_LIVE_REQUESTS is False, returns deterministic sample data.
        """
        cached = self.store.get_latest_signal(ticker, "social")
        if cached:
            return cached

        query = query or ticker

        if not self.config.use_live_requests:
            logger.info("Using simulated social data (USE_LIVE_REQUESTS=False)")
            total = 50
            pos_count = 32
            neg_count = 18
            positive_ratio = pos_count / total
            negative_ratio = neg_count / total
            avg_compound = 0.18
            signal = (
                "Bullish" if positive_ratio > 0.6 else "Bearish" if positive_ratio < 0.4 else "Neutral"
            )
            interpretation = (
                f"Simulated social sentiment shows {positive_ratio*100:.0f}% positive mentions."
            )
            result = {
                "ticker": ticker,
                "metric": "Tweet Sentiment",
                "total_tweets": total,
                "positive_count": pos_count,
                "negative_count": neg_count,
                "positive_ratio": round(positive_ratio, 2),
                "negative_ratio": round(negative_ratio, 2),
                "avg_compound": avg_compound,
                "signal": signal,
                "interpretation": interpretation,
                "provider": "legacy"
            }
            self.store.save_signal(ticker, "social", result, signal_value=positive_ratio)
            return result

        try:
            tweets = self._fetch_tweets(query, limit=200)
            sentiment = self._analyze_sentiment(tweets)
            if sentiment["total_tweets"] == 0:
                result = {
                    "ticker": ticker,
                    "metric": "Tweet Sentiment",
                    "total_tweets": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "positive_ratio": 0.0,
                    "negative_ratio": 0.0,
                    "avg_compound": 0.0,
                    "signal": "Neutral",
                    "interpretation": "No social data available.",
                    "provider": "legacy"
                }
                self.store.save_signal(ticker, "social", result, signal_value=0.0)
                return result
            positive_ratio = sentiment["positive_ratio"]
            if positive_ratio > 0.6:
                signal = "Bullish"
            elif positive_ratio < 0.4:
                signal = "Bearish"
            else:
                signal = "Neutral"
            interpretation = (
                f"Out of {sentiment['total_tweets']} recent tweets, {sentiment['positive_count']} were positive "
                f"and {sentiment['negative_count']} were negative. Positive ratio: {positive_ratio*100:.0f}%."
            )
            result = {
                "ticker": ticker,
                "metric": "Tweet Sentiment",
                "total_tweets": sentiment["total_tweets"],
                "positive_count": sentiment["positive_count"],
                "negative_count": sentiment["negative_count"],
                "positive_ratio": sentiment["positive_ratio"],
                "negative_ratio": sentiment["negative_ratio"],
                "avg_compound": sentiment["avg_compound"],
                "signal": signal,
                "interpretation": interpretation,
                "provider": "legacy"
            }
            self.store.save_signal(ticker, "social", result, signal_value=positive_ratio)
            return result
        except Exception as exc:
            logger.error("Social scraping failed for query '%s': %s", query, exc)
            return {
                "ticker": ticker,
                "metric": "Tweet Sentiment",
                "total_tweets": 0,
                "positive_count": 0,
                "negative_count": 0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "avg_compound": 0.0,
                "signal": "Neutral",
                "interpretation": "No social data available.",
                "provider": "legacy"
            }
