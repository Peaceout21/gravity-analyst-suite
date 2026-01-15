from __future__ import annotations

from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field

# Load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    firecrawl_api_key: Optional[str] = Field(default=None, env="FIRECRAWL_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    ais_endpoint: Optional[str] = Field(default=None, env="AIS_ENDPOINT")
    bol_endpoint: Optional[str] = Field(default=None, env="BOL_ENDPOINT")
    app_rank_endpoint: Optional[str] = Field(default=None, env="APP_RANK_ENDPOINT")
    user_agent: Optional[str] = Field(default=None, env="USER_AGENT")
    hiring_model_name: Optional[str] = Field(default=None, env="HIRING_MODEL_NAME")
    digital_model_name: Optional[str] = Field(default=None, env="DIGITAL_MODEL_NAME")
    shipping_model_name: Optional[str] = Field(default=None, env="SHIPPING_MODEL_NAME")
    social_scraper_type: str = Field(default="modern", env="SOCIAL_SCRAPER_TYPE")
    use_live_requests: bool = Field(default=False, env="USE_LIVE_REQUESTS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
