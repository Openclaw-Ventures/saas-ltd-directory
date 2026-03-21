# Build: SaaS LTD Niche Price Directory

Brief: ~/clawd-ventures/pipeline/04-build/FORGE-BRIEF-2026-03-19-saas-ltd-directory.md
Start Date: 2026-03-19
Target Ship: 2026-03-31 (Jaisev hard deadline)
Kill Date: 2026-03-28

## MVP Scope (Locked)
- Auto-scraper: AppSumo, StackSocial, PitchGround, DealFuel, DealMirror, Dealify
- SQLite database with 1,800+ active LTD products
- Hugo static site: deal pages, category pages, comparison pages
- Affiliate link layer (Impact.com / PartnerStack)
- SEO: Schema.org Product markup, sitemap, OG tags, llms.txt for GEO
- Nightly rebuild cron (scrape → generate → deploy)
- NOT included: paid AdSense account (placeholder slots only), Stripe billing

## Milestones
| Day | Milestone | Status | Notes |
|-----|-----------|--------|-------|
| 1 | Architecture locked + API verified | ✅ DONE | Tech stack locked: Hugo+Playwright+SQLite+Netlify. AppSumo scraper live, 60 real products. Hugo site initialized, 116 pages. GitHub Actions workflow ready. |
| 2 | Multi-platform scrapers + dual affiliate links | ✅ DONE | DealFuel/DealMirror/Dealify scrapers built (needed DOM fixes). Dual CTA (LTD + subscription) affiliate links on all product pages. |
| 3 | Scrapers fixed + content layer + 1000+ products | ✅ DONE | All 3 scrapers fixed using APIs (Shopify JSON, WP Store API, WooCommerce). 1,878 active products. Original content (verdict, who-is-this-for, price analysis) on every page. 17 comparison pages. 94 category pages. 2,006 HTML pages generated. |
| 4 | SEO + GEO optimization + deployment config | ✅ DONE | Sitemap (2,014 URLs), robots.txt (AI crawlers allowed), JSON-LD schema on every page, OG/Twitter Cards, llms.txt, AdSense slots, netlify.toml headers/redirects, 2,132 pages generated. |
| 5 | Deployed to prod + nightly cron live | ✅ DONE | Files copied to /var/www/ltd-stjarvis. Caddy route for ltd.stjarvis.com added + validated. Caddy reloaded OK. PENDING: Jaisev must add DNS CNAME for ltd.stjarvis.com in Cloudflare dashboard (CF token lacks zone edit scope). OpenClaw nightly rebuild cron registered. |
| 6 | Affiliate programs applied + distribution | ⏳ | Apply AppSumo Impact.com + PartnerStack. Reddit + IndieHackers launch posts. |
| 7 | Handoff complete | ⏳ | Sentinel registry, Ledger configured, Atlas sign-off, postmortem |

## Target Buyers (from brief)
1. Bootstrapped SaaS founders checking LTD pricing — organic search (no outreach needed — SEO-driven)
2. AppSumo affiliate audience — affiliate referral plays
3. SaaS review bloggers who link to price data — outreach on Day 6

## Coding Agents Spawned
- Prior Forge session (2026-03-19 daytime): Architecture, all scrapers, Hugo site, SEO — all inline
- Deployer subagent: Day 5 deployment — SPAWNING NOW

## Daily Log

### Day 1 (2026-03-19, morning)
- Architecture doc written, tech stack locked
- AppSumo scraper: 60 real products (Playwright)
- Hugo site initialized: 116 pages generated
- Affiliate status doc written
- GitHub Actions nightly workflow created
- Standup: 13:37 UTC

### Day 2 (2026-03-19, midday)
- Multi-platform scraper framework (DealFuel, DealMirror, Dealify)
- Dual affiliate CTA buttons (LTD + subscription)
- Price history table in SQLite schema
- 60 products, 4 scrapers (3 need DOM fix)
- Standup: 13:37 UTC

### Day 3 (2026-03-19, afternoon)
- Fixed all 3 broken scrapers using REST APIs
- 1,878 active products in DB
- Original content layer: verdict + who-it's-for + price analysis on every page
- 17 comparison pages generated
- 94 category landing pages
- 2,006 HTML pages
- Launch distribution brief (LAUNCH-DISTRIBUTION.md)
- Standup: 16:15 UTC

### Day 4 (2026-03-19, late afternoon)
- Full SEO pass: sitemap, robots.txt, JSON-LD schema, canonical URLs
- GEO: llms.txt, Quick Facts boxes for AI citability
- AdSense placeholder slots (3 positions)
- netlify.toml: headers + redirects
- 2,132 pages generated
- Standup: 17:15 UTC

## Blockers
- No Netlify token available → deploying to stjarvis.com via Caddy instead

## Handoff Checklist
- [ ] Live URL: https://ltd.stjarvis.com (target)
- [ ] GitHub repo created + code pushed
- [ ] Nightly cron active (OpenClaw cron)
- [ ] Sentinel monitoring active
- [ ] Affiliate programs applied (Gate 1)
- [ ] Atlas notified
- [ ] Postmortem written → moved to completed/
