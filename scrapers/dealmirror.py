"""DealMirror deal scraper - uses WooCommerce Store API (no browser needed)."""

import json
import re
from typing import List
import requests
from bs4 import BeautifulSoup

from base import BaseScraper, Product
from utils import make_deal_slug, parse_price, random_delay, build_affiliate_url


class DealMirrorScraper(BaseScraper):
    """Scrape active deals from DealMirror via WP Store API."""

    BASE_URL = "https://dealmirror.com"
    API_URL = "https://dealmirror.com/wp-json/wc/store/v1/products"

    def __init__(self):
        super().__init__()
        self.source_name = "dealmirror"

    def scrape(self) -> List[Product]:
        products = []
        seen_slugs = set()
        page = 1
        per_page = 100  # WP Store API max

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        max_pages = 15  # Cap at 1500 products to avoid excessive requests

        while page <= max_pages:
            url = f"{self.API_URL}?per_page={per_page}&page={page}"
            self.logger.info(f"Fetching DealMirror page {page}...")

            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                page_products = resp.json()

                if not page_products:
                    self.logger.info(f"No more products at page {page}")
                    break

                self.logger.info(f"Page {page}: {len(page_products)} products")

                for item in page_products:
                    product = self._parse_product(item)
                    if product and product.slug not in seen_slugs:
                        seen_slugs.add(product.slug)
                        products.append(product)

                # Check if more pages exist
                total_pages = int(resp.headers.get("X-WP-TotalPages", 0))
                if page >= total_pages or len(page_products) < per_page:
                    break

                page += 1
                random_delay(0.5, 1.5)

            except Exception as e:
                self.logger.error(f"Error fetching DealMirror page {page}: {e}")
                break

        return products

    def _parse_product(self, item) -> Product:
        """Parse a product from WP Store API response."""
        try:
            name = item.get("name", "").strip()
            if not name or len(name) < 2:
                return None

            source_url = item.get("permalink", "")
            if not source_url:
                slug = item.get("slug", "")
                source_url = f"{self.BASE_URL}/product/{slug}/"

            # Prices are in cents (currency_minor_unit: 2)
            prices = item.get("prices", {})
            minor_unit = prices.get("currency_minor_unit", 2)
            divisor = 10 ** minor_unit

            price_current = None
            price_original = None

            sale_price = prices.get("sale_price") or prices.get("price")
            regular_price = prices.get("regular_price")

            if sale_price:
                try:
                    price_current = float(sale_price) / divisor
                except (ValueError, TypeError):
                    pass

            if regular_price:
                try:
                    price_original = float(regular_price) / divisor
                except (ValueError, TypeError):
                    pass

            # Skip free products (likely teasers)
            if price_current is not None and price_current == 0 and (price_original is None or price_original == 0):
                return None

            # If sale_price is 0 but regular > 0, it's a freebie promo - keep it
            if price_current == 0 and price_original and price_original > 0:
                pass  # Keep — it's a genuine free deal

            # Category from categories array
            category = None
            categories = item.get("categories", [])
            # Filter out internal/pricing categories
            skip_cats = {"all in one template-woopricing", "10 percent off", "12 percent off", 
                        "30 percent off", "5 percent off", "Monthly 12% off"}
            for cat in categories:
                cat_name = cat.get("name", "")
                if cat_name and cat_name not in skip_cats and "percent off" not in cat_name.lower():
                    category = cat_name
                    break

            # Tagline from short_description
            tagline = None
            short_desc = item.get("short_description", "")
            if short_desc:
                text = BeautifulSoup(short_desc, "html.parser").get_text(strip=True)
                tagline = text[:200] if text else None

            # If no short_description, try description
            if not tagline:
                desc = item.get("description", "")
                if desc:
                    text = BeautifulSoup(desc, "html.parser").get_text(strip=True)
                    if text:
                        tagline = text[:200]

            # Image
            image_url = None
            images = item.get("images", [])
            if images:
                image_url = images[0].get("src")

            # Rating and reviews
            rating = None
            review_count = None
            avg_rating = item.get("average_rating")
            if avg_rating:
                try:
                    rating = float(avg_rating)
                except (ValueError, TypeError):
                    pass
            rev_count = item.get("review_count")
            if rev_count:
                try:
                    review_count = int(rev_count)
                except (ValueError, TypeError):
                    pass

            # Discount
            discount_pct = None
            if price_current is not None and price_original and price_original > price_current:
                discount_pct = int(round((1 - price_current / price_original) * 100))

            slug = make_deal_slug(name)
            affiliate_url = build_affiliate_url(source_url, "dealmirror")

            return Product(
                slug=slug,
                name=name,
                tagline=tagline,
                price_current=price_current,
                price_original=price_original,
                price_currency=prices.get("currency_code", "USD"),
                discount_pct=discount_pct,
                source="dealmirror",
                source_url=source_url,
                affiliate_url=affiliate_url,
                category=category,
                image_url=image_url,
                rating=rating,
                review_count=review_count,
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse DealMirror product: {e}")
            return None


if __name__ == "__main__":
    from db import upsert_product, start_scrape_run, complete_scrape_run, get_product_count, init_db

    init_db()
    scraper = DealMirrorScraper()
    run_id = start_scrape_run("dealmirror")

    try:
        products = scraper.run()
        new_count = 0
        updated_count = 0
        for product in products:
            result = upsert_product(product.to_dict())
            if result == "new":
                new_count += 1
            else:
                updated_count += 1

        complete_scrape_run(run_id, len(products), updated_count, new_count)
        total = get_product_count()
        print(f"\n=== DealMirror Scrape Complete ===")
        print(f"Found: {len(products)} | New: {new_count} | Updated: {updated_count}")
        print(f"Total products in DB: {total}")
    except Exception as e:
        complete_scrape_run(run_id, 0, 0, 0, status="failed", error=str(e))
        print(f"Scrape FAILED: {e}")
        raise
