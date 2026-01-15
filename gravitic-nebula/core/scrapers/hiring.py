import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

from core.config import Settings, get_settings
from core.persistence.engine import SignalStore, default_store

logger = logging.getLogger(__name__)

import trafilatura
from firecrawl import Firecrawl
import google.generativeai as genai

logger = logging.getLogger(__name__)

class HiringScraper:
    """
    SOTA Hiring & Strategic Intent Scraper.
    Uses Firecrawl for extraction and Gemini for classification.
    """
    
    def __init__(self, config: Optional[Settings] = None, store: Optional[SignalStore] = None):
        self.config = config or get_settings()
        self.store = store or default_store
        self.firecrawl = Firecrawl(api_key=self.config.firecrawl_api_key)
        
        # Configure Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def scrape_jobs(self, company_name: str) -> Dict[str, any]:
        """
        SOTA Scrape-Parsing: Discovery -> Scrape -> Gemini.
        Returns both 'jobs' (sampled list) and 'total_count' (absolute metric).
        """
        logger.info(f"Scraping job postings for: {company_name}")
        
        if not self.config.use_live_requests:
            logger.info("Using simulated data (USE_LIVE_REQUESTS=False)")
            return {
                "jobs": [
                    {"title": "Senior AI Researcher", "department": "Engineering"},
                    {"title": "GPU Kernels Engineer", "department": "R&D"},
                    {"title": "Enterprise Account Executive", "department": "Sales"}
                ],
                "total_count": 1969
            }

        # 1. Discovery Search (0 Credits) - Prioritizing Deep Portal Links
        portal_url = None
        try:
            # SOTA: Query specifically for the "search results" or "portal" to skip landing pages
            search_query = f"{company_name} job openings portal results page"
            search_res = self.firecrawl.search(search_query) 
            
            # Priority 1: Deep links (Workday, etc.)
            deep_links = []
            generic_links = []
            
            for result in getattr(search_res, 'web', []):
                url = result.url.lower()
                # Prioritize known portal subdomains or paths
                if any(x in url for x in ['workday', 'eightfold', 'lever', 'greenhouse', 'smartrecruiters', 'successfactors', 'apply']):
                    deep_links.append(result.url)
                elif 'jobs' in url or 'openings' in url or 'careers' in url:
                    generic_links.append(result.url)
            
            if deep_links:
                portal_url = deep_links[0]
            elif generic_links:
                portal_url = generic_links[0]
                
            if not portal_url:
                portal_url = f"https://{company_name.lower().replace(' ', '')}.com/careers"
                
            logger.info(f"🎯 Discovered portal: {portal_url}")
        except Exception as e:
            logger.warning(f"Discovery search failed: {e}")
            portal_url = f"https://{company_name.lower().replace(' ', '')}.com/careers"

        # 2. Scrape & Handle Double-Hop
        try:
            data = self._scrape_and_parse(portal_url, company_name)
            
            # 3. Double-Hop Detection: Result is 0 but page has "Find Jobs" intent
            if data.get('total_count', 0) == 0 and data.get('portal_link'):
                new_url = data['portal_link']
                logger.info(f"🔄 Double-Hop detected. Transitioning to portal: {new_url}")
                data = self._scrape_and_parse(new_url, company_name)
                
            return data
            
        except Exception as e:
            logger.error(f"SOTA Scrape-Parsing failed: {e}")
            return {"jobs": [], "total_count": 0}

    def _scrape_and_parse(self, url: str, company_name: str) -> Dict[str, any]:
        """Internal helper for 1-credit scrape + Gemini synthesis."""
        logger.info(f"Scraping and parsing: {url}")
        scrape_res = self.firecrawl.scrape(
            url, 
            formats=['markdown'],
            wait_for=10000 # Increased wait for JS-heavy portals like MSFT
        )
        markdown_content = getattr(scrape_res, 'markdown', '')
        
        if not markdown_content or len(markdown_content) < 100:
            logger.warning(f"Sparse markdown for {url}")
            return {"jobs": [], "total_count": 0}

        # Local Gemini Synthesis (Robust Parsing)
        prompt = f"""
        Analyze this markdown from a {company_name} job portal.
        
        1. Extract 'total_count': The total number of open roles listed on this portal. 
           Look for text like "Showing 1-20 of 1969" or "Found 45 results".
        2. Extract 'jobs': A list of up to 20 individual job positions (titles and departments).
        3. Extract 'portal_link': If this page has NO jobs listed (0 results), identify the URL 
           for the actual "Search Jobs", "Explore Roles", or "Find Jobs" portal link. 
           Look for links containing 'apply', 'jobs', 'careers', 'search', or 'listings'.
        
        Output strictly valid JSON:
        {{ 
          "total_count": integer, 
          "jobs": [ {{ "title": "string", "department": "string" }} ],
          "portal_link": "string or null"
        }}
        
        Markdown:
        {markdown_content[:20000]}
        """
        response = self.model.generate_content(prompt)
        text = response.text
        
        try:
            # Robust JSON extraction
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                data = json.loads(text[start:end])
                
                # SOTA Fallback: If total_count is 0, manually hunt for portal candidates in markdown
                if data.get('total_count', 0) == 0 and not data.get('portal_link'):
                    import re
                    # Look for absolute apply/jobs links
                    candidates = re.findall(r'https?://[^\s\)\]]+(?:apply|jobs|careers|search)[^\s\)\]]+', markdown_content)
                    if candidates:
                        # Prioritize 'apply.' or 'jobs.' subdomains
                        prioritized = [c for c in candidates if 'apply.' in c or 'jobs.' in c]
                        data['portal_link'] = prioritized[0] if prioritized else candidates[0]
                        logger.info(f"🔍 Python-fallback found portal link: {data['portal_link']}")
                
                # Resolve relative links
                if data.get('portal_link') and data['portal_link'].startswith('/'):
                    from urllib.parse import urljoin
                    data['portal_link'] = urljoin(url, data['portal_link'])
                    
                return data
            else:
                raise ValueError("JSON braces not found")
        except Exception as e:
            logger.error(f"Failed to parse Gemini JSON for {url}: {e} | Text: {text[:100]}")
            return {"jobs": [], "total_count": 0}

    def classify_roles(self, jobs: List[Dict]) -> Dict:
        """
        Uses Gemini Flash to categorize jobs into Alpha-relevant categories.
        """
        if not jobs:
            return {"RD": [], "Sales": [], "GA": []}
            
        prompt = f"""
        Classify the following job titles into exactly three categories: 'RD', 'Sales', 'GA'.
        RD: Engineering, Research, Product, Design, R&D.
        Sales: Marketing, BD, Account Management, Growth.
        GA: Admin, HR, Legal, Ops, Finance.
        
        Jobs:
        {json.dumps([j['title'] for j in jobs])}
        
        Return ONLY a JSON object where keys are categories and values are list of titles.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find the JSON block in the response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            logger.warning(f"LMM classification failed, falling back to keyword logic: {e}")
            # Fallback keyword logic
            rd_roles = []
            sales_roles = []
            ga_roles = []
            for job in jobs:
                title = job['title'].lower()
                if any(kw in title for kw in ['researcher', 'engineer', 'product manager', 'initiatives', 'r&d', 'kernel']):
                    rd_roles.append(job)
                elif any(kw in title for kw in ['sales', 'account', 'growth', 'marketing']):
                    sales_roles.append(job)
                else:
                    ga_roles.append(job)
            return {"RD": rd_roles, "Sales": sales_roles, "GA": ga_roles}

    def get_expansion_velocity(self, ticker: str) -> Dict:
        """
        Calculate the 'Expansion Velocity' signal using Macro/Micro data.
        """
        # 1. Check Persistence Layer
        cached = self.store.get_latest_signal(ticker, "hiring")
        if cached:
            return cached

        # 2. Scrape & Process
        data = self.scrape_jobs(ticker)
        jobs = data.get('jobs', [])
        total_macro = data.get('total_count', len(jobs))
        
        # Micro-Analysis (Sample-based trend)
        classified = self.classify_roles(jobs)
        sample_count = len(jobs)
        rd_count = len(classified.get('RD', []))
        sales_count = len(classified.get('Sales', []))
        
        # Expansion velocity is calculated based on the sample trend
        expansion_count = rd_count + sales_count
        velocity = expansion_count / sample_count if sample_count > 0 else 0
        
        result = {
            "ticker": ticker,
            "total_open_roles_macro": total_macro,
            "sample_size_micro": sample_count,
            "rd_count_sample": rd_count,
            "sales_count_sample": sales_count,
            "expansion_velocity": round(velocity, 2),
            "signal": "High Expansion" if velocity > 0.7 else "Normal",
            "interpretation": f"Macro: {total_macro} jobs found. Micro-sample ({sample_count} roles) shows {velocity*100:.0f}% Growth/R&D focus."
        }

        # 3. Save to Persistence
        self.store.save_signal(ticker, "hiring", result, signal_value=velocity)
        
        return result

if __name__ == "__main__":
    scraper = HiringScraper()
    print(json.dumps(scraper.get_expansion_velocity("NVDA"), indent=2))
