"""Base scraper class for SaaS LTD directory."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')


@dataclass
class Product:
    """Normalized product data from any source."""
    slug: str
    name: str
    source: str
    source_url: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    price_current: Optional[float] = None
    price_original: Optional[float] = None
    price_currency: str = "USD"
    discount_pct: Optional[int] = None
    affiliate_url: Optional[str] = None
    subscription_url: Optional[str] = None
    subscription_affiliate_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    deal_active: int = 1
    plans: Optional[str] = None  # JSON string
    features: Optional[str] = None  # JSON string

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


class BaseScraper(ABC):
    """Abstract base for all deal scrapers."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_name = "unknown"

    @abstractmethod
    def scrape(self) -> List[Product]:
        """Scrape deals and return normalized Product list."""
        pass

    def run(self) -> List[Product]:
        """Run scraper with logging."""
        self.logger.info(f"Starting scrape for {self.source_name}")
        try:
            products = self.scrape()
            self.logger.info(f"Scraped {len(products)} products from {self.source_name}")
            return products
        except Exception as e:
            self.logger.error(f"Scrape failed for {self.source_name}: {e}")
            raise
