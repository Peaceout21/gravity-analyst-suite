import json
import logging
import pandas as pd
import trafilatura
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from core.config import Settings, get_settings
from core.persistence.engine import SignalStore, default_store
from firecrawl import Firecrawl
import google.generativeai as genai

logger = logging.getLogger(__name__)

class SocialScraperModern:
    """
    SOTA Social Sentiment Scraper (Modern).
    Uses Firecrawl and Gemini for nuanced signal detection (Twitter, Reddit, Web).
    """
    
    def __init__(self, config: Optional[Settings] = None, store: Optional[SignalStore] = None):
        self.config = config or get_settings()
        self.store = store or default_store
        
        # Initialize Firecrawl
        if self.config.firecrawl_api_key:
            self.firecrawl = Firecrawl(api_key=self.config.firecrawl_api_key)
        else:
            self.firecrawl = None
            
        # Configure Gemini
        if self.config.gemini_api_key:
            genai.configure(api_key=self.config.gemini_api_key)
            # Use same model version as DigitalScraper for consistency
            self.model = genai.GenerativeModel('gemini-3-flash-preview')
        else:
            self.model = None

    def get_social_signal(self, ticker: str, query: Optional[str] = None) -> Dict:
        """
        Compute a multi-source social sentiment signal for a given ticker.
        Checks SOTA persistence before fetching live.
        """
        # 1. Check persistence
        cached = self.store.get_latest_signal(ticker, "social")
        if cached:
            return cached

        # Construct a search query that targets social sentiment
        search_query = query or f"${ticker} stock sentiment reddit community posts"
        
        if not self.config.use_live_requests:
            logger.info("Using simulated social data (USE_LIVE_REQUESTS=False)")
            result = {
                "ticker": ticker,
                "metric": "Social Sentiment",
                "sentiment_score": 0.72,
                "signal": "Bullish",
                "interpretation": f"Simulated social data for {ticker} shows strong community growth and bullish sentiment on Reddit.",
                "provider": "modern"
            }
            self.store.save_signal(ticker, "social", result, signal_value=0.72)
            return result

        if not self.firecrawl or not self.model:
            logger.warning("Firecrawl or Gemini API keys missing. Falling back to Neutral.")
            return self._neutral_fallback(ticker)

        try:
            # 2. Firecrawl Scrape (High Efficiency)
            # We search for the ticker on social platforms via Google to get a snapshot of community sentiment
            search_url = f"https://www.google.com/search?q={search_query}"
            logger.info(f"🚀 SOTA Social Scrape initiating for {ticker}...")
            
            scrape_res = self.firecrawl.scrape(
                search_url,
                formats=['html', 'markdown'],
                only_main_content=True,
                wait_for=3000
            )
            
            html_content = getattr(scrape_res, 'html', '')
            markdown_content = getattr(scrape_res, 'markdown', '')
            
            # 3. Trafilatura Pre-processing
            cleaned_text = trafilatura.extract(html_content, include_links=False)
            if not cleaned_text or len(cleaned_text) < 100:
                cleaned_text = markdown_content

            # 4. Gemini Synthesis
            prompt = f"""
            Analyze the following social media/search results for the company with ticker ${ticker}.
            
            TASK:
            1. Extract the prevailing social sentiment (from Reddit, Twitter, and finance forums).
            2. Identify 2-3 key bullish or bearish arguments being discussed.
            3. Determine an 'Alpha Signal' (Bullish, Bearish, or Neutral).
            4. Assign a 'sentiment_score' from 0.0 (Extremely Negative) to 1.0 (Extremely Positive).
            
            Return ONLY a valid JSON object:
            {{
                "sentiment_score": float,
                "signal": "Bullish" | "Bearish" | "Neutral",
                "key_arguments": ["string"],
                "interpretation": "A 1-sentence analytical summary"
            }}
            
            SOURCE CONTENT:
            {cleaned_text[:6000]}
            """
            
            logger.info(f"🧠 Gemini synthesizing social alpha for {ticker}...")
            response = self.model.generate_content(prompt)
            data_str = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(data_str)
            
            result = {
                "ticker": ticker,
                "metric": "Social Sentiment",
                "sentiment_score": data.get("sentiment_score", 0.5),
                "signal": data.get("signal", "Neutral"),
                "interpretation": data.get("interpretation", "No clear signal."),
                "key_arguments": data.get("key_arguments", []),
                "provider": "modern"
            }
            
            # 5. Save result
            self.store.save_signal(ticker, "social", result, signal_value=float(result['sentiment_score']))
            logger.info(f"✅ Social Alpha stored for {ticker}: {result['signal']} ({result['sentiment_score']})")
            return result

        except Exception as e:
            logger.error(f"SOTA Social Scrape-Parsing failed: {e}")
            return self._neutral_fallback(ticker)

    def _neutral_fallback(self, ticker: str) -> Dict:
        return {
            "ticker": ticker,
            "metric": "Social Sentiment",
            "sentiment_score": 0.5,
            "signal": "Neutral",
            "interpretation": "Insufficient social data to derive a signal."
        }

if __name__ == "__main__":
    # Quick Test
    scraper = SocialScraper()
    print(json.dumps(scraper.get_social_signal("TSLA"), indent=2))
