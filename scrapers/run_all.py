"""Run all scrapers and store results in SQLite."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import init_db, upsert_product, start_scrape_run, complete_scrape_run, get_product_count
from appsumo import AppSumoScraper
from dealfuel import DealFuelScraper
from dealmirror import DealMirrorScraper
from dealify import DealifyScraper

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger("run_all")


def run_scraper(scraper_cls):
    """Run a single scraper and persist results."""
    from db import mark_deals_expired
    
    scraper = scraper_cls()
    run_id = start_scrape_run(scraper.source_name)

    try:
        products = scraper.run()
        new_count = 0
        updated_count = 0
        found_slugs = set()
        
        for product in products:
            result = upsert_product(product.to_dict())
            found_slugs.add(product.slug)
            if result == "new":
                new_count += 1
            else:
                updated_count += 1

        # Mark deals as expired if they're no longer on the source platform
        mark_deals_expired(scraper.source_name, found_slugs)

        complete_scrape_run(run_id, len(products), updated_count, new_count)
        logger.info(f"{scraper.source_name}: Found={len(products)} New={new_count} Updated={updated_count}")
        return True
    except Exception as e:
        complete_scrape_run(run_id, 0, 0, 0, status="failed", error=str(e))
        logger.error(f"{scraper.source_name} FAILED: {e}")
        return False


def main():
    init_db()

    scrapers = [
        AppSumoScraper,
        DealFuelScraper,
        DealMirrorScraper,
        DealifyScraper,
    ]

    results = {}
    for cls in scrapers:
        success = run_scraper(cls)
        results[cls.__name__] = "OK" if success else "FAILED"

    total = get_product_count()
    print(f"\n=== Scrape Run Complete ===")
    for name, status in results.items():
        print(f"  {name}: {status}")
    print(f"Total active products in DB: {total}")

    return all(v == "OK" for v in results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
