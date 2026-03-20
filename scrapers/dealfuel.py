"""DealFuel deal scraper - WooCommerce HTML scraper with pagination."""

import json
import re
from typing import List
import requests
from bs4 import BeautifulSoup

from base import BaseScraper, Product
from utils import make_deal_slug, parse_price, random_delay, build_affiliate_url


class DealFuelScraper(BaseScraper):
    """Scrape active deals from DealFuel via WooCommerce HTML pages."""

    BASE_URL = "https://www.dealfuel.com"
    # Software category has the most relevant SaaS/tool deals
    CATEGORY_URLS = [
        ("https://www.dealfuel.com/product-category/software/", "Software"),
        ("https://www.dealfuel.com/product-category/plugins/", "Plugins"),
        ("https://www.dealfuel.com/product-category/seo-2/", "SEO"),
    ]

    def __init__(self):
        super().__init__()
        self.source_name = "dealfuel"

    def scrape(self) -> List[Product]:
        products = []
        seen_slugs = set()

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        for cat_url, cat_name in self.CATEGORY_URLS:
            self.logger.info(f"Scraping DealFuel category: {cat_name}")
            page = 1
            max_pages = 20  # Safety limit per category

            while page <= max_pages:
                url = f"{cat_url}page/{page}/" if page > 1 else cat_url
                self.logger.info(f"  Page {page}: {url}")

                try:
                    resp = requests.get(url, headers=headers, timeout=15)
                    if resp.status_code == 404:
                        self.logger.info(f"  No more pages at {page}")
                        break
                    resp.raise_for_status()

                    soup = BeautifulSoup(resp.text, "html.parser")
                    cards = soup.select("li.product")

                    if not cards:
                        self.logger.info(f"  No products found on page {page}")
                        break

                    self.logger.info(f"  Found {len(cards)} products")

                    for card in cards:
                        product = self._parse_card(card, cat_name)
                        if product and product.slug not in seen_slugs:
                            seen_slugs.add(product.slug)
                            products.append(product)

                    # Check if there's a next page
                    next_link = soup.select_one("a.next.page-numbers")
                    if not next_link:
                        break

                    page += 1
                    random_delay(0.5, 1.5)

                except Exception as e:
                    self.logger.error(f"Error on DealFuel page {page}: {e}")
                    break

        return products

    def _parse_card(self, card, default_category="Software") -> Product:
        """Parse a WooCommerce product card."""
        try:
            # Product link
            link = card.select_one("a.woocommerce-LoopProduct-link, a[href*='/seller/'], a[href*='/product/']")
            if not link:
                link = card.select_one("a")
            if not link or not link.get("href"):
                return None

            href = link["href"]
            if not href.startswith("http"):
                href = self.BASE_URL + href

            # Name
            name_el = card.select_one(".woocommerce-loop-product__title, h2.woocommerce-loop-product__title, h2")
            if not name_el:
                return None
            name = name_el.get_text(strip=True)
            if not name or len(name) < 2:
                return None

            # Skip non-deal items (categories, placeholder pages)
            classes = card.get("class", [])
            if "product-category" in classes:
                return None

            # Category from CSS classes
            category = default_category
            cat_classes = [c.replace("product_cat-", "") for c in classes if c.startswith("product_cat-")]
            # Prefer specific categories over generic ones
            skip_cats = {"all", "homepage", "uncategorized", "marketplace", "operating-system",
                        "deal-subscription", "instant-download-deals", "lifetime-deals"}
            for cc in cat_classes:
                if cc not in skip_cats:
                    category = cc.replace("-", " ").title()
                    break

            # Price parsing
            price_current = None
            price_original = None
            price_el = card.select_one(".price")

            if price_el:
                # Sale price (inside <ins>)
                ins = price_el.select_one("ins .woocommerce-Price-amount, ins .amount")
                if ins:
                    price_current = parse_price(ins.get_text(strip=True))

                # Original price (inside <del>)
                dele = price_el.select_one("del .woocommerce-Price-amount, del .amount")
                if dele:
                    price_original = parse_price(dele.get_text(strip=True))

                # If no sale markup, just a single price
                if price_current is None and price_original is None:
                    amount = price_el.select_one(".woocommerce-Price-amount, .amount")
                    if amount:
                        price_current = parse_price(amount.get_text(strip=True))

            # Image
            image_url = None
            img = card.select_one("img")
            if img:
                image_url = img.get("src") or img.get("data-src")
                # Skip placeholder images
                if image_url and "placeholder" in image_url:
                    image_url = None

            # Discount
            discount_pct = None
            if price_current and price_original and price_original > price_current:
                discount_pct = int(round((1 - price_current / price_original) * 100))

            slug = make_deal_slug(name)
            affiliate_url = build_affiliate_url(href, "dealfuel")

            return Product(
                slug=slug,
                name=name,
                tagline=None,  # Not available on listing page
                price_current=price_current,
                price_original=price_original,
                price_currency="USD",
                discount_pct=discount_pct,
                source="dealfuel",
                source_url=href,
                affiliate_url=affiliate_url,
                category=category,
                image_url=image_url,
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse DealFuel card: {e}")
            return None


if __name__ == "__main__":
    from db import upsert_product, start_scrape_run, complete_scrape_run, get_product_count, init_db

    init_db()
    scraper = DealFuelScraper()
    run_id = start_scrape_run("dealfuel")

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
        print(f"\n=== DealFuel Scrape Complete ===")
        print(f"Found: {len(products)} | New: {new_count} | Updated: {updated_count}")
        print(f"Total products in DB: {total}")
    except Exception as e:
        complete_scrape_run(run_id, 0, 0, 0, status="failed", error=str(e))
        print(f"Scrape FAILED: {e}")
        raise
