"""
LLMFilter: Uses Gemini to filter for "Investment Grade" prediction market signals.
Discards jokes, pop culture, and sports bets.
"""
from google import genai
import os
import json
import logging
import re
import ast
from typing import List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class LLMFilter:
    """
    Filters Polymarket events to ensure they have financial or macro relevance.
    """
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No API key found for LLMFilter.")
        
        self.client = genai.Client(api_key=api_key) if api_key else None

    def filter_events(self, events_json: str) -> List[str]:
        """
        Takes a list of event titles and returns a list of only those that are 
        'Investment Grade'.
        """
        try:
            # Fallback if no client/key
            if not self.client:
                return ast.literal_eval(events_json)

            prompt = f"""
            You are a rigorous financial analyst. 
            Filter the following list of prediction market titles.
            
            CRITERIA:
            - KEEP: Macroeconomics (Fed, Rates, GDP), Geopolitics (War, Elections), Big Tech (Earnings, Product Launches), Crypto (Major tokens only).
            - DISCARD: Sports, Pop Culture, Celebrity Gossip, Niche crypto memecoins, Personal props.
            
            INPUT: {events_json}
            
            OUTPUT:
            Return strictly a valid JSON list of strings containing ONLY the approved titles.
            Do not include Markdown formatting (like ```json). Just the raw JSON list.
            """
            
            # Using basic generation
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            # Clean and parse
            text = response.text.replace("```json", "").replace("```", "").strip()
            
            try:
                approved = json.loads(text)
                return approved if isinstance(approved, list) else []
            except json.JSONDecodeError:
                # Fallback to regex if plain JSON fails
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    approved = json.loads(match.group(0))
                    return approved
                return []
        except Exception as e:
            logger.error(f"LLM Filter failed: {e}")
            try:
                return ast.literal_eval(events_json) # Final fallback to all
            except:
                return []

if __name__ == "__main__":
    # Test
    filterer = LLMFilter()
    test_json = json.dumps([
        "Will the Fed cut rates by 25bps in March?",
        "Will Taylor Swift get engaged in 2025?",
        "Will Nvidia beat Q3 revenue estimates?",
        "Will it rain in London tomorrow?"
    ])
    approved = filterer.filter_events(test_json)
    print(f"Approved: {approved}")
