"""Generate Hugo content files from SQLite database.

Day 3: Full content layer with original editorial content on every page:
- "Is it worth it?" verdict section
- "Who is this for?" section
- Price analysis blurb
- Related deals section
- Category landing pages with editorial content
- Comparison pages for top products
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from collections import defaultdict

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "saas_deals.db")
CONTENT_DIR = os.path.join(BASE_DIR, "site", "content")
DEALS_DIR = os.path.join(CONTENT_DIR, "deals")
CATEGORY_DIR = os.path.join(CONTENT_DIR, "categories")
COMPARE_DIR = os.path.join(CONTENT_DIR, "compare")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products WHERE deal_active = 1 ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_products_by_category():
    """Group products by category."""
    products = get_products()
    by_cat = defaultdict(list)
    for p in products:
        cat = p.get("category") or "Uncategorized"
        by_cat[cat].append(p)
    return by_cat


def generate_verdict(product):
    """Generate 'Is it worth it?' verdict based on rule-based logic."""
    rating = product.get("rating") or 0
    review_count = product.get("review_count") or 0
    discount_pct = product.get("discount_pct") or 0
    price = product.get("price_current")
    original = product.get("price_original")
    category = product.get("category") or "software"
    name = product.get("name", "This product")

    # Calculate discount if not stored
    if not discount_pct and price and original and original > price:
        discount_pct = int(round((1 - price / original) * 100))

    if rating >= 4.5 and review_count >= 100 and discount_pct >= 50:
        return (f"**Strong buy.** Highly rated by {review_count} users with a {rating}/5 star rating, "
                f"and you're getting {discount_pct}% off the original price. "
                f"This is one of the best-reviewed lifetime deals in the {category} category.")
    elif rating >= 4.0 and review_count >= 50:
        return (f"**Solid deal.** Well-reviewed with {review_count} ratings and a {rating}/5 star average. "
                f"Worth considering if you need {category.lower()} tools for your business.")
    elif rating >= 4.0 and review_count >= 20:
        return (f"**Decent option.** {name} has a {rating}/5 rating from {review_count} users. "
                f"If you're looking for {category.lower()} solutions, this is worth a closer look.")
    elif review_count >= 10 and rating >= 3.5:
        return (f"**Mixed reviews.** With a {rating}/5 rating from {review_count} users, "
                f"this deal shows promise but may not work for everyone. Read user reviews before committing.")
    elif discount_pct >= 70:
        return (f"**Deep discount ({discount_pct}% off), but limited reviews.** "
                f"The price is attractive, but with only {review_count} review{'s' if review_count != 1 else ''}, "
                f"it's harder to gauge long-term quality. Proceed with caution.")
    elif price and price <= 29:
        return (f"**Low-risk entry point.** At ${price:.0f}, the downside is limited even if the product "
                f"doesn't fully meet expectations. Worth trying if you need {category.lower()} tools.")
    else:
        return (f"**Proceed with caution.** Limited review data makes it difficult to fully assess quality. "
                f"Check the product's website for demos and detailed feature lists before purchasing.")


def generate_who_is_this_for(product):
    """Generate 'Who is this for?' section."""
    category = product.get("category") or "software"
    tagline = product.get("tagline") or ""
    name = product.get("name", "This product")

    # Map categories to user types
    category_users = {
        "productivity": "teams and professionals looking to streamline their workflows",
        "seo": "digital marketers and SEO professionals",
        "email marketing": "email marketers and newsletter operators",
        "crm": "sales teams and customer relationship managers",
        "project management": "project managers and distributed teams",
        "social media": "social media managers and content creators",
        "ecommerce": "online store owners and e-commerce entrepreneurs",
        "customer support": "support teams and customer success managers",
        "lead generation": "B2B marketers and sales development teams",
        "video": "video creators and marketing teams",
        "audio": "podcasters and audio content creators",
        "photo": "photographers and visual content creators",
        "web builders": "web developers and designers building sites",
        "content marketing": "content marketers and editorial teams",
        "marketing management": "marketing teams managing campaigns",
        "development tools": "software developers and dev teams",
        "sales & marketing": "sales and marketing professionals",
        "ai tools": "professionals leveraging AI for automation",
        "ai": "professionals leveraging AI for automation",
        "business": "business owners and entrepreneurs",
        "creative": "designers and creative professionals",
        "developer tools": "software developers and engineering teams",
        "web & hosting": "website owners and webmasters",
        "software": "businesses looking for specialized software tools",
        "plugins": "WordPress site owners and web developers",
    }

    cat_lower = category.lower().strip()
    user_type = category_users.get(cat_lower, f"{category.lower()} users")

    # Try to extract use case from tagline
    use_case = ""
    if tagline:
        # Use first meaningful phrase
        tagline_clean = tagline.split(".")[0].strip()
        if len(tagline_clean) > 15 and len(tagline_clean) < 150:
            use_case = f" — {tagline_clean.lower()}" if not tagline_clean[0].isupper() else f" — {tagline_clean}"

    return f"Best for {user_type} who need {name.lower()} capabilities{use_case}."


def generate_price_analysis(product):
    """Generate price analysis blurb."""
    price = product.get("price_current")
    original = product.get("price_original")
    discount_pct = product.get("discount_pct") or 0
    name = product.get("name", "this product")

    if not price:
        return ""

    parts = []

    if original and original > price:
        if not discount_pct:
            discount_pct = int(round((1 - price / original) * 100))
        
        savings = original - price
        parts.append(
            f"At **${price:.0f} one-time** vs ${original:.0f} regular price, "
            f"you're saving **{discount_pct}%** (${savings:.0f}) compared to buying at full price."
        )

        # Add context on annual savings
        if original >= 100:
            monthly_equiv = original / 12
            parts.append(
                f"That's equivalent to paying just {price / 12:.1f} months of the regular "
                f"${monthly_equiv:.0f}/month subscription — and keeping it forever."
            )
    elif price:
        parts.append(f"Available as a one-time purchase at **${price:.0f}** — no recurring fees.")

    return " ".join(parts)


def get_related_deals(product, all_products, count=3):
    """Find related deals in the same category."""
    category = product.get("category")
    slug = product.get("slug")

    if not category:
        return []

    # Find products in same category, excluding self
    same_cat = [p for p in all_products
                if p.get("category") == category and p.get("slug") != slug]

    # Sort by rating (desc), then review_count (desc)
    same_cat.sort(key=lambda p: (p.get("rating") or 0, p.get("review_count") or 0), reverse=True)

    return same_cat[:count]


def write_deal_page(product, all_products):
    """Generate a Hugo markdown file for a product deal with full content layer."""
    slug = product["slug"]
    filepath = os.path.join(DEALS_DIR, f"{slug}.md")

    is_expired = product.get("deal_active", 1) == 0

    # Build front matter
    fm = {
        "title": f"{product['name']} Lifetime Deal — ${product['price_current']:.0f}" if (not is_expired and product.get('price_current')) else (f"{product['name']} (Expired)" if is_expired else f"{product['name']} Lifetime Deal"),
        "description": product.get("tagline") or f"Get {product['name']} lifetime deal at a discounted price.",
        "date": product.get("first_seen", "2026-01-01"),
        "lastmod": product.get("last_updated") or product.get("last_scraped", "2026-01-01"),
        "product_name": product["name"],
        "slug": slug,
        "source": product["source"],
        "source_url": product["source_url"],
        "affiliate_url": product.get("affiliate_url", product["source_url"]),
        "subscription_url": product.get("subscription_url"),
        "subscription_affiliate_url": product.get("subscription_affiliate_url"),
        "price_current": product.get("price_current"),
        "price_original": product.get("price_original"),
        "price_currency": product.get("price_currency", "USD"),
        "discount_pct": product.get("discount_pct"),
        "rating": product.get("rating"),
        "review_count": product.get("review_count"),
        "image": product.get("image_url"),
        "deal_active": not is_expired,
        "last_scraped": product.get("last_scraped"),
        "last_updated": product.get("last_updated"),
    }

    # Categories for taxonomy
    if product.get("category"):
        fm["categories"] = [product["category"]]
    if product.get("source"):
        fm["sources"] = [product["source"]]

    # Build markdown content
    content_parts = []

    # Expired badge
    if is_expired:
        content_parts.append("🚫 **This deal is no longer available.** Check back for updates or browse other deals.\n")

    # Tagline / description
    if product.get("tagline"):
        content_parts.append(product["tagline"])
    if product.get("description"):
        content_parts.append(f"\n{product['description']}")

    # === ORIGINAL CONTENT LAYER ===

    # 1. "Is it worth it?" verdict
    verdict = generate_verdict(product)
    content_parts.append(f"\n## Is It Worth It?\n\n{verdict}\n")

    # 2. "Who is this for?"
    who_for = generate_who_is_this_for(product)
    content_parts.append(f"\n## Who Is This For?\n\n{who_for}\n")

    # 3. Price analysis
    price_analysis = generate_price_analysis(product)
    if price_analysis:
        content_parts.append(f"\n## Price Analysis\n\n{price_analysis}\n")

    # Last updated timestamp
    last_updated_str = "Unknown"
    if product.get("last_updated"):
        try:
            dt = datetime.fromisoformat(product["last_updated"])
            last_updated_str = dt.strftime("%Y-%m-%d %H:%M UTC")
        except:
            last_updated_str = product["last_updated"]

    content_parts.append(f"\n_Last updated: {last_updated_str}_\n")

    # Dual CTA section (only if not expired)
    if not is_expired:
        cta_section = "\n## Get This Deal\n"
        cta_section += '<div style="margin: 2rem 0; display: flex; gap: 1rem; flex-wrap: wrap;">\n'

        affiliate_url = product.get("affiliate_url") or product.get("source_url")
        cta_section += f'  <a href="{affiliate_url}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #2563eb; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get Lifetime Deal</a>\n'

        subscription_url = product.get("subscription_affiliate_url") or product.get("subscription_url")
        if subscription_url:
            cta_section += f'  <a href="{subscription_url}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #059669; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get Monthly Plan</a>\n'

        cta_section += '</div>\n'
        content_parts.append(cta_section)

    # 4. Related deals section
    related = get_related_deals(product, all_products)
    if related:
        content_parts.append("\n## Related Deals\n")
        content_parts.append("Looking for similar tools? Check out these deals:\n")
        for r in related:
            r_price = f"${r['price_current']:.0f}" if r.get('price_current') else "See pricing"
            r_discount = f" ({r['discount_pct']}% off)" if r.get('discount_pct') else ""
            content_parts.append(f"- [{r['name']}](/deals/{r['slug']}/) — {r_price}{r_discount}")
        content_parts.append("")

    # Write file
    content_body = "\n".join(content_parts)

    with open(filepath, "w") as f:
        f.write("---\n")
        for key, val in fm.items():
            if val is None:
                continue
            if isinstance(val, bool):
                f.write(f'{key}: {"true" if val else "false"}\n')
            elif isinstance(val, list):
                f.write(f"{key}:\n")
                for item in val:
                    f.write(f'  - "{item}"\n')
            elif isinstance(val, (int, float)):
                f.write(f"{key}: {val}\n")
            else:
                escaped = str(val).replace('"', '\\"')
                f.write(f'{key}: "{escaped}"\n')
        f.write("---\n\n")
        f.write(content_body)


def write_deals_index():
    """Write _index.md for /deals/ section."""
    filepath = os.path.join(DEALS_DIR, "_index.md")
    with open(filepath, "w") as f:
        f.write("---\n")
        f.write('title: "All SaaS Lifetime Deals"\n')
        f.write('description: "Browse all active SaaS lifetime deals across AppSumo, DealFuel, DealMirror, and Dealify. Updated daily with real pricing data."\n')
        f.write("---\n\n")
        f.write("# All SaaS Lifetime Deals\n\n")
        f.write("Browse our complete directory of lifetime software deals. Every price is verified daily across AppSumo, DealFuel, DealMirror, and Dealify.\n")


def write_category_pages(products_by_cat):
    """Generate category landing pages with editorial content."""
    # Category intro templates
    category_intros = {
        "productivity": "Looking for productivity lifetime deals? Here are the best one-time payment tools to boost your team's output in 2026.",
        "seo": "Find the best SEO tool lifetime deals. Stop paying monthly for keyword research, backlink analysis, and rank tracking.",
        "email marketing": "Looking for email marketing lifetime deals? Here are the best one-time deals to grow your list and send campaigns without monthly fees.",
        "crm": "Compare CRM lifetime deals and stop paying per-seat monthly fees. One-time payment, lifetime access to customer management.",
        "project management": "Project management lifetime deals let your team collaborate without monthly per-user pricing. Find the best PM tools here.",
        "social media": "Social media management lifetime deals — schedule, analyze, and grow across platforms without recurring subscription costs.",
        "ai tools": "AI tool lifetime deals are the smartest investment in 2026. Get lifetime access to AI-powered productivity, content, and automation tools.",
        "ai": "AI tool lifetime deals are the smartest investment in 2026. Get lifetime access to AI-powered productivity, content, and automation tools.",
        "business": "Business tool lifetime deals for entrepreneurs and small teams. CRM, invoicing, analytics, and more — one-time payment.",
        "creative": "Creative tool lifetime deals for designers, video editors, and content creators. Professional tools without monthly subscriptions.",
        "developer tools": "Developer tool lifetime deals for building, deploying, and monitoring software. Save thousands vs annual subscriptions.",
        "web & hosting": "Web hosting and website tool lifetime deals. Build, host, and manage your online presence with one-time payments.",
        "sales & marketing": "Sales and marketing lifetime deals to grow your business. Lead generation, email outreach, analytics, and more.",
        "software": "Software lifetime deals across every category. Find the best one-time payment tools curated from top deal platforms.",
        "plugins": "WordPress plugin lifetime deals. Extend your site's functionality without annual renewal fees.",
    }

    why_buy_templates = {
        "productivity": "Why buy a productivity LTD? Monthly subscriptions add up fast — a $20/month tool costs $240/year. A lifetime deal at $49-99 pays for itself in months and keeps working forever.",
        "seo": "Why buy an SEO LTD? Professional SEO tools like Ahrefs and SEMrush cost $100-400/month. Lifetime deal alternatives give you 80% of the features at a fraction of the long-term cost.",
        "email marketing": "Why buy an email marketing LTD? Email platforms charge based on subscriber count, and costs grow as your list grows. A lifetime deal locks in your price regardless of list size.",
        "ai tools": "Why buy an AI tool LTD? AI subscriptions are expensive and multiplying fast. A lifetime deal locks in today's price for tools that will only become more valuable.",
        "ai": "Why buy an AI tool LTD? AI subscriptions are expensive and multiplying fast. A lifetime deal locks in today's price for tools that will only become more valuable.",
        "business": "Why buy a business tool LTD? As your team grows, per-seat pricing on monthly tools scales your costs. Lifetime deals often include generous seat limits at a fixed price.",
        "creative": "Why buy a creative tool LTD? Design and video software subscriptions are a constant overhead. Lifetime deals let you invest once and create forever.",
        "software": "Why buy a software LTD? Lifetime deals give you permanent access at a fraction of the annual subscription cost. Most pay for themselves within 3-6 months.",
    }

    for category, products in sorted(products_by_cat.items()):
        if not category or category == "Uncategorized":
            continue

        # Create category slug
        cat_slug = category.lower().strip()
        cat_slug = cat_slug.replace(" ", "-").replace("&", "and").replace("/", "-")
        cat_slug = "".join(c for c in cat_slug if c.isalnum() or c == "-")
        cat_slug = "-".join(part for part in cat_slug.split("-") if part)

        cat_dir = os.path.join(CATEGORY_DIR, cat_slug)
        os.makedirs(cat_dir, exist_ok=True)

        filepath = os.path.join(cat_dir, "_index.md")

        # Sort by rating, then review count
        sorted_products = sorted(products, key=lambda p: (p.get("rating") or 0, p.get("review_count") or 0), reverse=True)

        # Get intro and why-buy
        cat_lower = category.lower().strip()
        intro = category_intros.get(cat_lower,
            f"Looking for {category.lower()} lifetime deals? Here are the best one-time deals available in 2026, "
            f"updated daily from AppSumo, DealFuel, DealMirror, and Dealify.")
        why_buy = why_buy_templates.get(cat_lower,
            f"Why buy a {category.lower()} LTD? Monthly subscriptions add up. A lifetime deal gives you permanent access "
            f"at a fraction of the annual cost — most pay for themselves within a few months.")

        # Top 3 featured deals
        top_deals = sorted_products[:3]

        with open(filepath, "w") as f:
            f.write("---\n")
            f.write(f'title: "Best {category} Lifetime Deals (2026)"\n')
            f.write(f'description: "{intro[:155]}"\n')
            f.write(f'category: "{category}"\n')
            f.write(f'deal_count: {len(products)}\n')
            f.write("---\n\n")

            f.write(f"# Best {category} Lifetime Deals\n\n")
            f.write(f"{intro}\n\n")
            f.write(f"**{len(products)} deals found** across AppSumo, DealFuel, DealMirror, and Dealify.\n\n")

            # Top picks
            if top_deals:
                f.write("## ⭐ Top Picks\n\n")
                for i, deal in enumerate(top_deals, 1):
                    price_str = f"${deal['price_current']:.0f}" if deal.get('price_current') else "See pricing"
                    rating_str = f" — {deal['rating']}/5 ({deal['review_count']} reviews)" if deal.get('rating') else ""
                    discount_str = f" ({deal['discount_pct']}% off)" if deal.get('discount_pct') else ""
                    f.write(f"{i}. **[{deal['name']}](/deals/{deal['slug']}/)** — {price_str}{discount_str}{rating_str}\n")
                f.write("\n")

            # All deals
            f.write("## All Deals\n\n")
            f.write("| Deal | Price | Discount | Platform |\n")
            f.write("|------|-------|----------|----------|\n")
            for deal in sorted_products:
                price = f"${deal['price_current']:.0f}" if deal.get('price_current') else "N/A"
                discount = f"{deal['discount_pct']}% off" if deal.get('discount_pct') else "—"
                source = deal.get('source', 'Unknown').title()
                f.write(f"| [{deal['name']}](/deals/{deal['slug']}/) | {price} | {discount} | {source} |\n")

            f.write(f"\n## {why_buy.split('?')[0]}?\n\n{why_buy}\n")


def write_comparison_pages(products):
    """Generate comparison pages for top products vs category competitors."""
    # Get top products by review count
    reviewed = [p for p in products if (p.get("review_count") or 0) > 0]
    reviewed.sort(key=lambda p: p.get("review_count", 0), reverse=True)
    top_products = reviewed[:20]

    if not top_products:
        # If no reviews, use products with highest discount
        discounted = [p for p in products if (p.get("discount_pct") or 0) > 0]
        discounted.sort(key=lambda p: p.get("discount_pct", 0), reverse=True)
        top_products = discounted[:20]

    # Group by category for finding competitors
    by_cat = defaultdict(list)
    for p in products:
        cat = p.get("category") or "Uncategorized"
        by_cat[cat].append(p)

    comparisons_made = set()
    comparison_count = 0

    for product in top_products:
        cat = product.get("category") or "Uncategorized"
        competitors = [p for p in by_cat[cat]
                      if p["slug"] != product["slug"]]

        if not competitors:
            continue

        # Pick closest competitor (by price similarity)
        if product.get("price_current"):
            competitors.sort(key=lambda p: abs((p.get("price_current") or 0) - product["price_current"]))
        competitor = competitors[0]

        # Avoid duplicate comparisons
        pair_key = tuple(sorted([product["slug"], competitor["slug"]]))
        if pair_key in comparisons_made:
            continue
        comparisons_made.add(pair_key)

        write_comparison_page(product, competitor)
        comparison_count += 1

        if comparison_count >= 20:
            break

    print(f"Generated {comparison_count} comparison pages")


def write_comparison_page(product_a, product_b):
    """Write a single comparison page."""
    slug_a = product_a["slug"].replace("-lifetime-deal", "")
    slug_b = product_b["slug"].replace("-lifetime-deal", "")
    comp_slug = f"{slug_a}-vs-{slug_b}"

    comp_dir = os.path.join(COMPARE_DIR, comp_slug)
    os.makedirs(comp_dir, exist_ok=True)
    filepath = os.path.join(comp_dir, "index.md")

    name_a = product_a["name"]
    name_b = product_b["name"]
    category = product_a.get("category") or "Software"

    # Generate verdict
    def score_product(p):
        s = 0
        if p.get("rating"): s += p["rating"] * 10
        if p.get("review_count"): s += min(p["review_count"], 100) * 0.1
        if p.get("discount_pct"): s += p["discount_pct"] * 0.2
        if p.get("price_current") and p["price_current"] < 100: s += 5
        return s

    score_a = score_product(product_a)
    score_b = score_product(product_b)

    if score_a > score_b * 1.2:
        verdict = f"**{name_a} edges ahead** with better ratings and value. However, {name_b} may suit different use cases — check the feature comparison below."
    elif score_b > score_a * 1.2:
        verdict = f"**{name_b} has the edge** in our comparison. That said, {name_a} offers unique strengths that may better fit your specific needs."
    else:
        verdict = f"**It's a close call.** Both {name_a} and {name_b} offer competitive lifetime deals. Your choice depends on which features matter most for your workflow."

    def fmt_price(p):
        return f"${p['price_current']:.0f}" if p.get('price_current') else "N/A"

    def fmt_orig(p):
        return f"${p['price_original']:.0f}" if p.get('price_original') else "N/A"

    def fmt_rating(p):
        if p.get('rating'):
            return f"{p['rating']}/5" + (f" ({p['review_count']} reviews)" if p.get('review_count') else "")
        return "No ratings yet"

    def fmt_discount(p):
        return f"{p['discount_pct']}%" if p.get('discount_pct') else "N/A"

    with open(filepath, "w") as f:
        f.write("---\n")
        f.write(f'title: "{name_a} vs {name_b} — Lifetime Deal Comparison (2026)"\n')
        f.write(f'description: "Compare {name_a} and {name_b} lifetime deals side by side. Price, features, ratings, and which is the better buy."\n')
        f.write(f'date: "2026-03-19"\n')
        f.write(f'comparison: true\n')
        f.write(f'product_a: "{name_a}"\n')
        f.write(f'product_b: "{name_b}"\n')
        f.write(f'category: "{category}"\n')
        f.write("---\n\n")

        f.write(f"# {name_a} vs {name_b}: Which Lifetime Deal Is Better?\n\n")
        f.write(f"Comparing two {category.lower()} lifetime deals to help you make the right choice.\n\n")

        # Side-by-side table
        f.write("## Side-by-Side Comparison\n\n")
        f.write(f"| Feature | {name_a} | {name_b} |\n")
        f.write("|---------|---------|----------|\n")
        f.write(f"| **LTD Price** | {fmt_price(product_a)} | {fmt_price(product_b)} |\n")
        f.write(f"| **Regular Price** | {fmt_orig(product_a)} | {fmt_orig(product_b)} |\n")
        f.write(f"| **Discount** | {fmt_discount(product_a)} | {fmt_discount(product_b)} |\n")
        f.write(f"| **Rating** | {fmt_rating(product_a)} | {fmt_rating(product_b)} |\n")
        f.write(f"| **Platform** | {product_a.get('source', 'N/A').title()} | {product_b.get('source', 'N/A').title()} |\n")
        f.write(f"| **Category** | {product_a.get('category', 'N/A')} | {product_b.get('category', 'N/A')} |\n")
        f.write("\n")

        # Verdict
        f.write(f"## Our Verdict\n\n{verdict}\n\n")

        # CTA buttons
        aff_a = product_a.get("affiliate_url") or product_a.get("source_url", "#")
        aff_b = product_b.get("affiliate_url") or product_b.get("source_url", "#")

        f.write("## Get These Deals\n\n")
        f.write(f'<div style="margin: 2rem 0; display: flex; gap: 1rem; flex-wrap: wrap;">\n')
        f.write(f'  <a href="{aff_a}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #2563eb; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get {name_a} Deal</a>\n')
        f.write(f'  <a href="{aff_b}" target="_blank" rel="nofollow sponsored" style="padding: 0.75rem 1.5rem; background-color: #059669; color: white; border-radius: 0.5rem; text-decoration: none; font-weight: bold;">Get {name_b} Deal</a>\n')
        f.write('</div>\n\n')

        # Links to individual pages
        f.write(f"📖 Read full review: [{name_a}](/deals/{product_a['slug']}/) | [{name_b}](/deals/{product_b['slug']}/)\n")


def write_homepage(products):
    """Write the homepage content."""
    filepath = os.path.join(CONTENT_DIR, "_index.md")

    # Get stats
    total = len(products)
    sources = set(p.get("source") for p in products if p.get("source"))
    categories = set(p.get("category") for p in products if p.get("category"))

    # Get newest deals
    newest = sorted(products, key=lambda p: p.get("first_seen", ""), reverse=True)[:5]

    with open(filepath, "w") as f:
        f.write("---\n")
        f.write('title: "SaaS LTD Deals — Best Lifetime Software Deals Directory"\n')
        f.write('description: "Auto-updated directory of the best SaaS lifetime deals across AppSumo, DealFuel, DealMirror, and Dealify. Updated daily."\n')
        f.write("---\n\n")
        f.write(f"# Best SaaS Lifetime Deals Directory\n\n")
        f.write(f"**{total} active deals** across {len(sources)} platforms, updated daily. "
                f"Browse {len(categories)} categories of lifetime software deals.\n\n")

        if newest:
            f.write("## 🆕 Newest Deals\n\n")
            for deal in newest:
                price_str = f"${deal['price_current']:.0f}" if deal.get('price_current') else "See pricing"
                f.write(f"- [{deal['name']}](/deals/{deal['slug']}/) — {price_str} on {deal.get('source','').title()}\n")
            f.write("\n")

        f.write("[Browse all deals →](/deals/)\n")


def main():
    os.makedirs(DEALS_DIR, exist_ok=True)
    os.makedirs(CATEGORY_DIR, exist_ok=True)
    os.makedirs(COMPARE_DIR, exist_ok=True)

    # Clean existing deal pages
    for f in os.listdir(DEALS_DIR):
        if f.endswith(".md") and f != "_index.md":
            os.remove(os.path.join(DEALS_DIR, f))

    products = get_products()
    print(f"Generating pages for {len(products)} products...")

    # Generate deal pages with content layer
    for product in products:
        write_deal_page(product, products)

    # Generate index pages
    write_deals_index()
    write_homepage(products)

    # Generate category pages with editorial content
    products_by_cat = defaultdict(list)
    for p in products:
        cat = p.get("category") or "Uncategorized"
        products_by_cat[cat].append(p)

    write_category_pages(products_by_cat)

    # Generate comparison pages
    write_comparison_pages(products)

    # Summary
    categories = set(p.get("category") for p in products if p.get("category"))
    sources = set(p.get("source") for p in products if p.get("source"))
    print(f"Generated {len(products)} deal pages with full content layer")
    print(f"Categories: {len(categories)}")
    print(f"Sources: {', '.join(sorted(sources))}")
    print("Done.")


if __name__ == "__main__":
    main()
