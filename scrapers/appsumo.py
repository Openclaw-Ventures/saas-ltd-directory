"""AppSumo deal scraper using Playwright for JS-rendered content."""

import json
import re
from typing import List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from base import BaseScraper, Product
from utils import make_deal_slug, parse_price, random_delay, build_affiliate_url


class AppSumoScraper(BaseScraper):
    """Scrape active deals from AppSumo."""

    BASE_URL = "https://appsumo.com"
    BROWSE_URL = "https://appsumo.com/browse/?orderBy=most-recent"

    def __init__(self):
        super().__init__()
        self.source_name = "appsumo"

    def scrape(self) -> List[Product]:
        products = []
        seen_slugs = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            self.logger.info("Loading AppSumo browse page...")
            try:
                page.goto(self.BROWSE_URL, wait_until="networkidle", timeout=30000)
                random_delay(2, 3)

                # Infinite scroll — keep scrolling until no new products appear
                prev_count = 0
                stale_rounds = 0
                max_scroll_rounds = 30

                for scroll_round in range(max_scroll_rounds):
                    # Scroll to bottom
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)

                    # Check current product count
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    grid = soup.select_one("div.grid")
                    if not grid:
                        break
                    cards = grid.find_all("div", recursive=False)
                    current_count = len(cards)

                    if current_count > prev_count:
                        self.logger.info(f"Scroll round {scroll_round + 1}: {current_count} cards loaded")
                        prev_count = current_count
                        stale_rounds = 0
                    else:
                        stale_rounds += 1
                        if stale_rounds >= 3:
                            self.logger.info(f"No new content after 3 scroll rounds. Total: {current_count} cards")
                            break

                # Final parse
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                grid = soup.select_one("div.grid")
                if grid:
                    cards = grid.find_all("div", recursive=False)
                    self.logger.info(f"Final parse: {len(cards)} cards")

                    for card in cards:
                        product = self._parse_card(card)
                        if product and product.slug not in seen_slugs:
                            seen_slugs.add(product.slug)
                            products.append(product)

            except PlaywrightTimeout:
                self.logger.warning("Timeout loading AppSumo")
            except Exception as e:
                self.logger.error(f"Error scraping AppSumo: {e}")

            # Also scrape category pages for broader coverage
            category_urls = [
                "/browse/?collection=recently-launched",
                "/browse/?collection=best-sellers",
                "/browse/?orderBy=most-recent&maxPrice=49",
                "/browse/?orderBy=most-recent&maxPrice=99",
            ]

            for cat_url in category_urls:
                full_url = self.BASE_URL + cat_url
                self.logger.info(f"Scraping additional page: {cat_url}")
                try:
                    page.goto(full_url, wait_until="networkidle", timeout=30000)
                    random_delay(1, 2)

                    # Light scroll
                    for _ in range(8):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1500)

                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    grid = soup.select_one("div.grid")
                    if grid:
                        cards = grid.find_all("div", recursive=False)
                        new_on_page = 0
                        for card in cards:
                            product = self._parse_card(card)
                            if product and product.slug not in seen_slugs:
                                seen_slugs.add(product.slug)
                                products.append(product)
                                new_on_page += 1
                        self.logger.info(f"  → {new_on_page} new products from {cat_url}")
                except Exception as e:
                    self.logger.warning(f"Error on {cat_url}: {e}")

            browser.close()

        return products

    def _parse_card(self, card) -> Product:
        """Parse a product card from the AppSumo browse grid."""
        try:
            # Product link: <a href="/products/xxx/">
            link = card.select_one('a[href*="/products/"]')
            if not link or not link.get("href"):
                return None

            href = link["href"]
            if "#" in href:
                return None
            if not href.startswith("http"):
                href = self.BASE_URL + href

            # Name: <span class="...font-bold...">Name</span>
            name_el = card.select_one("span.font-bold")
            name = name_el.get_text(strip=True) if name_el else None
            if not name or len(name) < 2:
                sr = card.select_one("span.sr-only")
                name = sr.get_text(strip=True) if sr else None
            if not name or len(name) < 2:
                return None

            skip_names = {"Join AppSumo Plus", "AppSumo Plus", "Sign up"}
            if name in skip_names:
                return None

            # Category
            category = None
            cat_link = card.select_one('a[href*="/software/"]')
            if cat_link:
                category = cat_link.get_text(strip=True)

            # Tagline
            tagline = None
            tagline_el = card.select_one("div.line-clamp-3")
            if tagline_el:
                tagline = tagline_el.get_text(strip=True)

            # Rating from img alt
            rating = None
            rating_img = card.select_one('img[alt*="stars"]')
            if rating_img:
                m = re.search(r"([\d.]+)\s*stars?", rating_img.get("alt", ""))
                if m:
                    rating = float(m.group(1))

            # Review count
            review_count = None
            review_link = card.select_one('a[href*="#reviews"]')
            if review_link:
                m = re.search(r"(\d[\d,]*)", review_link.get_text(strip=True))
                if m:
                    review_count = int(m.group(1).replace(",", ""))

            # Price
            price_current = None
            price_el = card.select_one('[id="deal-price"]')
            if price_el:
                price_current = parse_price(price_el.get_text(strip=True))

            # Original price
            price_original = None
            orig_el = card.select_one('[id="deal-price-original"]')
            if orig_el:
                price_original = parse_price(orig_el.get_text(strip=True))

            # Image
            image_url = None
            img = card.select_one("img.aspect-sku-card")
            if img:
                image_url = img.get("src")

            # Discount
            discount_pct = None
            if price_current and price_original and price_original > price_current:
                discount_pct = int(round((1 - price_current / price_original) * 100))

            slug = make_deal_slug(name)
            affiliate_url = build_affiliate_url(href, "appsumo")
            
            # Placeholder for subscription URL (to be populated from vendor sites or PartnerStack later)
            subscription_url = None
            subscription_affiliate_url = None

            return Product(
                slug=slug,
                name=name,
                tagline=tagline,
                price_current=price_current,
                price_original=price_original,
                price_currency="USD",
                discount_pct=discount_pct,
                source="appsumo",
                source_url=href,
                affiliate_url=affiliate_url,
                subscription_url=subscription_url,
                subscription_affiliate_url=subscription_affiliate_url,
                category=category,
                rating=rating,
                review_count=review_count,
                image_url=image_url,
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse card: {e}")
            return None


if __name__ == "__main__":
    from db import upsert_product, start_scrape_run, complete_scrape_run, get_product_count, init_db

    init_db()
    scraper = AppSumoScraper()
    run_id = start_scrape_run("appsumo")

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
        print(f"\n=== AppSumo Scrape Complete ===")
        print(f"Found: {len(products)} | New: {new_count} | Updated: {updated_count}")
        print(f"Total products in DB: {total}")
    except Exception as e:
        complete_scrape_run(run_id, 0, 0, 0, status="failed", error=str(e))
        print(f"Scrape FAILED: {e}")
        raise
