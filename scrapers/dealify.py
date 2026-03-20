"""Dealify deal scraper - uses Shopify JSON API (no browser needed)."""

import json
import re
from typing import List
import requests

from base import BaseScraper, Product
from utils import make_deal_slug, parse_price, random_delay, build_affiliate_url


class DealifyScraper(BaseScraper):
    """Scrape active deals from Dealify via Shopify JSON API."""

    BASE_URL = "https://dealify.com"
    API_URL = "https://dealify.com/products.json"

    def __init__(self):
        super().__init__()
        self.source_name = "dealify"

    def scrape(self) -> List[Product]:
        products = []
        seen_slugs = set()
        page = 1
        per_page = 250  # Shopify max

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        while True:
            url = f"{self.API_URL}?limit={per_page}&page={page}"
            self.logger.info(f"Fetching Dealify page {page}...")

            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                page_products = data.get("products", [])

                if not page_products:
                    self.logger.info(f"No more products at page {page}")
                    break

                self.logger.info(f"Page {page}: {len(page_products)} products")

                for item in page_products:
                    product = self._parse_product(item)
                    if product and product.slug not in seen_slugs:
                        seen_slugs.add(product.slug)
                        products.append(product)

                # Shopify paginates; if less than per_page, we're done
                if len(page_products) < per_page:
                    break

                page += 1
                random_delay(1, 2)

            except Exception as e:
                self.logger.error(f"Error fetching Dealify page {page}: {e}")
                break

        return products

    def _parse_product(self, item) -> Product:
        """Parse a product from Shopify JSON API response."""
        try:
            name = item.get("title", "").strip()
            if not name or len(name) < 2:
                return None

            handle = item.get("handle", "")
            source_url = f"{self.BASE_URL}/products/{handle}"

            # Get price from first variant
            variants = item.get("variants", [])
            price_current = None
            price_original = None

            if variants:
                v = variants[0]
                price_str = v.get("price")
                compare_str = v.get("compare_at_price")

                if price_str:
                    price_current = float(price_str)
                if compare_str:
                    price_original = float(compare_str)

            # Category from product_type
            category = item.get("product_type") or None

            # Tagline from body_html (first sentence or first 200 chars)
            tagline = None
            body_html = item.get("body_html", "")
            if body_html:
                from bs4 import BeautifulSoup
                text = BeautifulSoup(body_html, "html.parser").get_text(strip=True)
                # First sentence or first 200 chars
                sentences = text.split(".")
                if sentences and len(sentences[0]) > 10:
                    tagline = sentences[0].strip()[:200]
                elif text:
                    tagline = text[:200]

            # Image
            image_url = None
            images = item.get("images", [])
            if images:
                image_url = images[0].get("src")

            # Tags
            tags = item.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            # Discount
            discount_pct = None
            if price_current and price_original and price_original > price_current:
                discount_pct = int(round((1 - price_current / price_original) * 100))

            slug = make_deal_slug(name)
            affiliate_url = build_affiliate_url(source_url, "dealify")

            return Product(
                slug=slug,
                name=name,
                tagline=tagline,
                price_current=price_current,
                price_original=price_original,
                price_currency="USD",
                discount_pct=discount_pct,
                source="dealify",
                source_url=source_url,
                affiliate_url=affiliate_url,
                category=category,
                image_url=image_url,
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse Dealify product: {e}")
            return None


if __name__ == "__main__":
    from db import upsert_product, start_scrape_run, complete_scrape_run, get_product_count, init_db

    init_db()
    scraper = DealifyScraper()
    run_id = start_scrape_run("dealify")

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
        print(f"\n=== Dealify Scrape Complete ===")
        print(f"Found: {len(products)} | New: {new_count} | Updated: {updated_count}")
        print(f"Total products in DB: {total}")
    except Exception as e:
        complete_scrape_run(run_id, 0, 0, 0, status="failed", error=str(e))
        print(f"Scrape FAILED: {e}")
        raise
