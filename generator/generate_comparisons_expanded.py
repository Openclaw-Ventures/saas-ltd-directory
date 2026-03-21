"""
Expand comparison pages from 17 to 200+.
Generates same-category pairs, prioritising deals with ratings.
Max 20 pairs per category to avoid combinatorial explosion.
"""

import os
import sys
import sqlite3
from collections import defaultdict
from itertools import combinations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "saas_deals.db")
COMPARE_DIR = os.path.join(BASE_DIR, "site", "content", "compare")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_active_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE deal_active = 1 ORDER BY review_count DESC NULLS LAST"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def write_comparison_page(product_a, product_b):
    slug_a = (product_a.get("slug") or "").replace("-lifetime-deal", "")
    slug_b = (product_b.get("slug") or "").replace("-lifetime-deal", "")
    dir_slug = f"{slug_a}-vs-{slug_b}"
    out_dir = os.path.join(COMPARE_DIR, dir_slug)

    # Skip if already exists
    if os.path.exists(os.path.join(out_dir, "index.md")):
        return False

    os.makedirs(out_dir, exist_ok=True)

    name_a = product_a.get("name", "Product A")
    name_b = product_b.get("name", "Product B")
    price_a = product_a.get("price_current") or 0
    price_b = product_b.get("price_current") or 0
    discount_a = product_a.get("discount_pct") or 0
    discount_b = product_b.get("discount_pct") or 0
    rating_a = product_a.get("rating") or 0
    rating_b = product_b.get("rating") or 0
    review_a = product_a.get("review_count") or 0
    review_b = product_b.get("review_count") or 0
    source_a = (product_a.get("source") or "").title()
    source_b = (product_b.get("source") or "").title()
    category = product_a.get("category") or "Software"
    affiliate_a = product_a.get("affiliate_url") or product_a.get("source_url") or "#"
    affiliate_b = product_b.get("affiliate_url") or product_b.get("source_url") or "#"
    slug_full_a = product_a.get("slug") or slug_a
    slug_full_b = product_b.get("slug") or slug_b

    # Verdict logic
    score_a = (rating_a * 0.4) + (discount_a * 0.3) + (min(review_a, 200) / 200 * 0.3 * 10)
    score_b = (rating_b * 0.4) + (discount_b * 0.3) + (min(review_b, 200) / 200 * 0.3 * 10)

    if score_a >= score_b:
        verdict = f"**{name_a} edges ahead** on our scoring — better value or stronger social proof. That said, {name_b} may suit different use cases depending on your needs."
    else:
        verdict = f"**{name_b} has the edge** in our comparison. That said, {name_a} offers unique strengths — check the comparison below before deciding."

    rating_str_a = f"{rating_a}/5 ({review_a} reviews)" if review_a >= 5 else "New listing"
    rating_str_b = f"{rating_b}/5 ({review_b} reviews)" if review_b >= 5 else "New listing"
    price_orig_a = f"${product_a.get('price_original'):.0f}/yr" if product_a.get("price_original") else "N/A"
    price_orig_b = f"${product_b.get('price_original'):.0f}/yr" if product_b.get("price_original") else "N/A"

    content = f"""---
title: "{name_a} vs {name_b} — Lifetime Deal Comparison (2026)"
description: "Compare {name_a} and {name_b} lifetime deals side by side. Price, discount, ratings, and which is the better buy for {category} tools."
date: "2026-03-20"
comparison: true
product_a: "{name_a}"
product_b: "{name_b}"
category: "{category}"
---

# {name_a} vs {name_b}: Which Lifetime Deal Is Better?

Comparing two {category} lifetime deals to help you make the right choice.

## Side-by-Side Comparison

| Feature | {name_a} | {name_b} |
|---------|---------|----------|
| **LTD Price** | ${price_a:.0f} | ${price_b:.0f} |
| **Regular Price** | {price_orig_a} | {price_orig_b} |
| **Discount** | {discount_a}% off | {discount_b}% off |
| **Rating** | {rating_str_a} | {rating_str_b} |
| **Platform** | {source_a} | {source_b} |
| **Category** | {category} | {category} |

## Our Verdict

{verdict}

## Get These Deals

<div style="margin: 2rem 0; display: flex; gap: 1rem; flex-wrap: wrap;">
  <a href="{affiliate_a}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #2563eb; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get {name_a} — ${price_a:.0f}</a>
  <a href="{affiliate_b}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #059669; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get {name_b} — ${price_b:.0f}</a>
</div>

📖 Read full review: [{name_a}](/deals/{slug_full_a}/) | [{name_b}](/deals/{slug_full_b}/)

## Frequently Asked Questions

**Is the {name_a} lifetime deal worth it?**
At ${price_a:.0f} one-time vs {price_orig_a} regular price, {name_a} offers {discount_a}% savings. {rating_str_a if review_a >= 5 else "It's a newer listing with limited reviews."}

**Is the {name_b} lifetime deal worth it?**
At ${price_b:.0f} one-time vs {price_orig_b} regular price, {name_b} offers {discount_b}% savings. {rating_str_b if review_b >= 5 else "It's a newer listing with limited reviews."}

**Which {category} lifetime deal is cheaper?**
{"Both are the same price." if price_a == price_b else (f"{name_a} at ${price_a:.0f}" if price_a < price_b else f"{name_b} at ${price_b:.0f}") + " is the lower-priced option."}
"""

    with open(os.path.join(out_dir, "index.md"), "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    products = get_active_products()
    print(f"Loaded {len(products)} active products")

    # Group by category
    by_cat = defaultdict(list)
    for p in products:
        cat = p.get("category") or "Uncategorized"
        if cat and cat != "Uncategorized":
            by_cat[cat].append(p)

    # Top 20 categories by deal count
    top_cats = sorted(by_cat.items(), key=lambda x: len(x[1]), reverse=True)[:20]

    existing = set(os.listdir(COMPARE_DIR)) if os.path.exists(COMPARE_DIR) else set()
    print(f"Existing comparisons: {len(existing)}")

    total_new = 0
    for cat, deals in top_cats:
        if len(deals) < 2:
            continue

        # Prioritise deals with ratings, then by discount
        rated = [d for d in deals if (d.get("review_count") or 0) >= 5]
        unrated = [d for d in deals if (d.get("review_count") or 0) < 5]
        unrated.sort(key=lambda d: d.get("discount_pct") or 0, reverse=True)

        # Pool: rated first, then unrated (up to 15 total to generate ~20 pairs)
        pool = (rated + unrated)[:15]

        cat_new = 0
        for prod_a, prod_b in combinations(pool, 2):
            if cat_new >= 20:
                break
            created = write_comparison_page(prod_a, prod_b)
            if created:
                cat_new += 1
                total_new += 1

        print(f"  {cat}: +{cat_new} new comparisons")

    print(f"\nTotal new comparison pages created: {total_new}")
    print(f"Total comparisons now: {len(os.listdir(COMPARE_DIR))}")


if __name__ == "__main__":
    main()
