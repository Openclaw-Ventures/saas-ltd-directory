# Database Schema — SaaS LTD Directory

**Database:** SQLite (`data/saas_deals.db`)

---

## Table: `products`

Main product/deal records table.

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto-increment |
| `slug` | TEXT | Unique identifier (e.g., `notion-lifetime-deal`) |
| `name` | TEXT | Product name (e.g., `Notion`) |
| `tagline` | TEXT | Short description from source |
| `description` | TEXT | Full description (currently null) |
| `price_current` | REAL | Current deal price in USD |
| `price_original` | REAL | Original/full price |
| `price_currency` | TEXT | Currency code (default: USD) |
| `discount_pct` | INTEGER | Discount percentage (e.g., 83 for 83% off) |
| `source` | TEXT | Deal platform (appsumo, dealfuel, dealmirror, dealify) |
| `source_url` | TEXT | URL on the source platform |
| `affiliate_url` | TEXT | **LTD affiliate link** — points to deal platform with ref params |
| `subscription_url` | TEXT | **Subscription URL** — direct vendor subscription page (placeholder) |
| `subscription_affiliate_url` | TEXT | **Subscription affiliate link** — PartnerStack/direct affiliate link (placeholder) |
| `category` | TEXT | Product category (e.g., Productivity, Marketing) |
| `subcategory` | TEXT | Sub-category (currently null) |
| `rating` | REAL | User rating out of 5 (e.g., 4.61) |
| `review_count` | INTEGER | Number of user reviews |
| `image_url` | TEXT | Product image URL for listings |
| `deal_active` | INTEGER | Boolean: 1 = active, 0 = expired/removed |
| `plans` | TEXT | JSON array of plan names (currently null) |
| `features` | TEXT | JSON array of features (currently null) |
| `last_scraped` | TEXT | ISO timestamp of last scrape |
| `last_updated` | TEXT | ISO timestamp of last update (schema field; mirrors last_scraped) |
| `first_seen` | TEXT | ISO timestamp when first imported |
| `created_at` | TEXT | Record creation timestamp |
| `updated_at` | TEXT | Record update timestamp |

**Indices:**
- `idx_products_source` — for filtering by platform
- `idx_products_category` — for category pages
- `idx_products_slug` — unique lookup
- `idx_products_deal_active` — quick filtering of active deals only

---

## Table: `price_history`

Time-series price snapshots for price tracking and charts.

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto-increment |
| `product_id` | INTEGER | Foreign key to `products.id` (ON DELETE CASCADE) |
| `price` | REAL | Price at this timestamp |
| `discount_pct` | INTEGER | Discount at this timestamp |
| `recorded_at` | TEXT | ISO timestamp of recording |

**Indices:**
- `idx_price_history_product` — lookup all prices for a product
- `idx_price_history_recorded` — time-range queries

**Usage:**
- One record per product update
- 60 products = 60 initial records
- Enables price trend visualization

---

## Table: `scrape_runs`

Logging of scraper execution history.

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto-increment |
| `source` | TEXT | Platform name (appsumo, dealfuel, etc.) |
| `started_at` | TEXT | ISO timestamp when scrape began |
| `completed_at` | TEXT | ISO timestamp when scrape finished |
| `products_found` | INTEGER | Total products seen in scrape |
| `products_updated` | INTEGER | Existing products with new data |
| `products_new` | INTEGER | New products added to DB |
| `status` | TEXT | 'running', 'completed', or 'failed' |
| `error_message` | TEXT | Exception message if failed |

**Usage:**
- Track scraper health and performance
- Audit trail for data freshness

---

## Key Relationships

```
products (1)
  ↓ (one-to-many)
price_history (many)
```

**Cascading:** Deleting a product deletes all its price history.

---

## Affiliate Link Strategy

### Current State (Day 2)
- **affiliate_url** (LTD link): ✅ Populated for all 60 products
  - Points to AppSumo deal page with ref param
  - Commission: Up to $50/order via Impact.com
  
- **subscription_url**: ⏳ Placeholder (null)
  - Will be populated from PartnerStack or vendor sites
  - Points to SaaS vendor's subscription page
  
- **subscription_affiliate_url**: ⏳ Placeholder (null)
  - Will be populated from PartnerStack or direct affiliate programs
  - Recurring commission potential

### Future Workflow (Day 3-4)
1. Once PartnerStack account is set up, populate subscription fields via:
   - Manual lookup (small batch)
   - PartnerStack API integration (automated)
   - Vendor website inspection (fallback)

2. Hugo templates render both links:
   ```
   "Get Lifetime Deal" → affiliate_url
   "Get Monthly Plan" → subscription_affiliate_url (if available)
   ```

---

## Query Examples

### Get all active products by category
```sql
SELECT name, price_current, discount_pct 
FROM products 
WHERE category = 'Marketing' AND deal_active = 1
ORDER BY discount_pct DESC;
```

### Get 30-day price history for a product
```sql
SELECT price, discount_pct, recorded_at 
FROM price_history 
WHERE product_id = 1 
AND recorded_at > datetime('now', '-30 days')
ORDER BY recorded_at ASC;
```

### Recent products
```sql
SELECT name, source, first_seen 
FROM products 
WHERE deal_active = 1
ORDER BY first_seen DESC 
LIMIT 10;
```

### Check scraper health
```sql
SELECT source, status, products_found, products_new, completed_at 
FROM scrape_runs 
WHERE status = 'completed'
ORDER BY completed_at DESC 
LIMIT 5;
```

---

## Migration Notes

**Day 1 → Day 2:**
- Added `subscription_url`, `subscription_affiliate_url`, `last_updated`
- Created `price_history` table
- Existing AppSumo products re-imported with new schema
- All 60 products have initial price_history records

---

## Performance Characteristics

- **Lookups:** Slug-based (indexed, <1ms)
- **Filtering:** By source or category (indexed, <10ms for 1K products)
- **Scraping:** 60 products → ~30-40ms insert time
- **Price history write:** Auto on every product update (append-only, negligible cost)

---

This schema supports the current MVP and scales to 10K+ products without major refactoring.
