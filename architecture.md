# Architecture — B2B SaaS LTD Niche Price Directory

**Date:** 2026-03-19
**Author:** Forge
**Status:** Day 1 — Foundation

---

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Static site generator | Hugo v0.123.7 (extended) | Fast builds, excellent SEO, Go templating |
| Scrapers | Playwright (headless Chromium) + BeautifulSoup4 | JS-heavy sources (AppSumo) + HTML parsing |
| Database | SQLite3 | Single-file, zero-config, sufficient for single-niche |
| Deployment | Netlify (static hosting, free tier) | CI/CD on git push, CDN, automatic HTTPS |
| Cron/rebuild | GitHub Actions (nightly) | Free, reliable, triggers Hugo rebuild from fresh DB |
| Language | Python 3.12 (scrapers), Go templates (Hugo) | Already installed, mature ecosystem |

---

## Data Model

### `products` table (SQLite)

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    tagline TEXT,
    description TEXT,
    price_current REAL,
    price_original REAL,
    price_currency TEXT DEFAULT 'USD',
    discount_pct INTEGER,
    source TEXT NOT NULL,          -- 'appsumo', 'stacksocial', 'pitchground'
    source_url TEXT NOT NULL,
    affiliate_url TEXT,
    category TEXT,
    subcategory TEXT,
    rating REAL,
    review_count INTEGER,
    image_url TEXT,
    deal_active INTEGER DEFAULT 1, -- boolean
    plans TEXT,                    -- JSON: tier details
    features TEXT,                 -- JSON: feature list
    last_scraped TEXT NOT NULL,    -- ISO timestamp
    first_seen TEXT NOT NULL,      -- ISO timestamp
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_products_source ON products(source);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_deal_active ON products(deal_active);
```

### `scrape_runs` table (audit trail)

```sql
CREATE TABLE scrape_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    products_found INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_new INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running', -- 'running', 'completed', 'failed'
    error_message TEXT
);
```

---

## Scraper Targets

| Source | URL | Method | Priority |
|--------|-----|--------|----------|
| AppSumo | https://appsumo.com/browse/ | Playwright (JS-rendered) | P0 |
| StackSocial | https://stacksocial.com/collections/apps | Requests + BS4 | P1 |
| PitchGround | https://pitchground.com/marketplace | Playwright | P1 |

### Scraper Architecture

```
scrapers/
├── base.py           # BaseScraper ABC — common interface
├── appsumo.py        # AppSumo scraper (Playwright)
├── stacksocial.py    # StackSocial scraper
├── pitchground.py    # PitchGround scraper
├── db.py             # SQLite helper (upsert, query)
├── run_all.py        # Orchestrator — runs all scrapers, logs to scrape_runs
└── utils.py          # Slugify, URL sanitization, retry logic
```

Each scraper:
1. Inherits `BaseScraper`
2. Implements `scrape() -> List[Product]`
3. Returns normalized `Product` dataclass
4. Handles its own pagination
5. Logs to `scrape_runs` table

---

## URL Structure (SEO)

| Pattern | Example | Content |
|---------|---------|---------|
| `/deals/{product-slug}/` | `/deals/writesonic-lifetime-deal/` | Product detail page |
| `/category/{category}/` | `/category/email-marketing/` | Category listing |
| `/compare/{product-vs-product}/` | `/compare/writesonic-vs-jasper/` | Comparison page |
| `/source/{source}/` | `/source/appsumo/` | Source-specific listing |
| `/` | `/` | Homepage — featured deals, categories |
| `/all/` | `/all/` | Full deal directory |

Slugs are lowercase, hyphenated, derived from product name + "-lifetime-deal" suffix for SEO.

---

## Affiliate Link Parameterization

All affiliate links go through a redirect layer for tracking:

```
/go/{product-slug}/ → actual affiliate URL with parameters
```

Parameters by network:

| Network | Parameter | Example |
|---------|-----------|---------|
| AppSumo (Impact) | `irclickid`, `irgwc` | Auto-set by Impact tracking pixel |
| PartnerStack | `ps_partner_key`, `ps_xid` | `?ps_partner_key=PLACEHOLDER&ps_xid={slug}` |
| Direct | `ref`, `utm_source` | `?ref=saasltddir&utm_source=saasltddir` |

In code, affiliate URLs are constructed via `build_affiliate_url(product, network, partner_id)`.
Partner IDs stored in `.env` / environment variables — never hardcoded.

**Placeholder values for pre-approval:**
- `APPSUMO_IMPACT_ID=placeholder_impact_id`
- `PARTNERSTACK_KEY=placeholder_ps_key`
- `DEFAULT_REF=saasltddir`

---

## Hugo Site Structure

```
site/
├── config.toml              # Hugo config (baseURL, theme, taxonomies)
├── content/
│   ├── deals/               # Auto-generated from SQLite (one .md per product)
│   ├── category/            # Auto-generated category pages
│   └── compare/             # Auto-generated comparison pages
├── layouts/
│   ├── _default/
│   │   ├── baseof.html      # Base template
│   │   ├── list.html        # List pages
│   │   └── single.html      # Single product page
│   ├── deals/
│   │   └── single.html      # Product detail template
│   ├── category/
│   │   └── list.html        # Category listing template
│   ├── compare/
│   │   └── single.html      # Comparison template
│   └── partials/
│       ├── head.html        # SEO meta tags, schema markup
│       ├── product-card.html # Reusable product card
│       ├── affiliate-btn.html # CTA button with affiliate link
│       └── footer.html
├── static/
│   ├── css/
│   └── images/
├── data/                    # JSON data files generated from SQLite
└── themes/                  # Minimal custom theme (no heavy dependency)
```

---

## GitHub Repo Structure

```
saas-ltd-directory/
├── README.md
├── .github/
│   └── workflows/
│       └── nightly-rebuild.yml  # Cron: scrape → generate → deploy
├── scrapers/                    # Python scraper code
│   ├── requirements.txt
│   ├── base.py
│   ├── appsumo.py
│   ├── stacksocial.py
│   ├── pitchground.py
│   ├── db.py
│   ├── run_all.py
│   └── utils.py
├── generator/                   # Python script: SQLite → Hugo content files
│   └── generate.py
├── site/                        # Hugo site
│   ├── config.toml
│   ├── content/
│   ├── layouts/
│   ├── static/
│   └── data/
├── data/
│   └── saas_deals.db           # SQLite database (gitignored in prod, checked in for dev)
├── .env.example
├── .gitignore
└── Makefile                    # scrape, generate, build, deploy targets
```

---

## Build Pipeline (nightly)

```
1. scrapers/run_all.py    → Scrape all sources → Update SQLite
2. generator/generate.py  → Read SQLite → Write Hugo content/*.md files
3. hugo --minify          → Build static site
4. netlify deploy         → Push to CDN
```

Each step logs success/failure. GitHub Actions workflow runs this sequence nightly at 02:00 UTC.

---

## Day 1 Deliverables Checklist

- [x] Architecture doc (this file)
- [x] SQLite schema created (data/saas_deals.db)
- [x] Scraper framework (base class + db + utils)
- [x] AppSumo scraper pulling REAL data (60 products, 100% data quality)
- [x] Hugo site initialized (116 pages generated, full SEO)
- [x] Affiliate status documented (affiliate-status.md)
- [x] Standup posted (2026-03-19.jsonl)
- [x] GitHub Actions nightly workflow (.github/workflows/)
- [x] CSS/styling complete
- [x] Makefile for build pipeline
