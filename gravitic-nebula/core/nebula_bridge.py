from typing import Optional, Dict

from core.config import Settings, get_settings
from core.entity_resolver.engine import HybridResolver
from core.persistence.engine import SignalStore, default_store
from core.scrapers.digital import DigitalScraper
from core.scrapers.hiring import HiringScraper
from core.scrapers.shipping import ShippingScraper
from core.scrapers.social import SocialScraper


class NebulaBridge:
    """
    Unified bridge for Nebula alternative-data signals.

    Provides a single entry point for calling the various scrapers and ensures
    they share configuration and persistence settings.
    """

    def __init__(
        self,
        resolver: Optional[HybridResolver] = None,
        config: Optional[Settings] = None,
        store: Optional[SignalStore] = None,
    ) -> None:
        self.config = config or get_settings()
        self.store = store or default_store
        self.resolver = resolver

        self.hiring = HiringScraper(config=self.config, store=self.store)
        self.shipping = ShippingScraper(resolver=self.resolver, config=self.config, store=self.store)
        self.digital = DigitalScraper(config=self.config, store=self.store)
        self.social = SocialScraper(config=self.config, store=self.store)

    def get_hiring_signal(self, ticker: str) -> Dict:
        return self.hiring.get_expansion_velocity(ticker)

    def get_shipping_signal(self, ticker: str, mmsi: Optional[str] = None) -> Dict:
        return self.shipping.nowcast_delivery(ticker, mmsi=mmsi)

    def get_digital_signal(self, ticker: str, app_id: str) -> Dict:
        return self.digital.get_digital_alpha(ticker, app_id)

    def get_social_signal(self, ticker: str, query: Optional[str] = None) -> Dict:
        return self.social.get_social_signal(ticker, query=query)
