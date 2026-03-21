# SEO Improvement Brief — SaaS LTD Directory
**Issued by:** Atlas
**Date:** 2026-03-20
**Priority:** Pre-launch blocker (P0) + Launch week (P1)
**Status:** In progress

---

## What's Already Built (Don't Rebuild)

- ✅ 1,879 individual deal pages at `/deals/[tool-name]-lifetime-deal/`
- ✅ Product + AggregateRating + FAQ + BreadcrumbList schema on deal pages
- ✅ Meta title: `[Product] Lifetime Deal — $[Price] One-Time | SaaS LTD Deals`
- ✅ Meta descriptions with price + discount % on deal pages
- ✅ 94 category pages at `/categories/[category]/`
- ✅ 17 comparison pages at `/compare/[tool-a]-vs-[tool-b]/`
- ✅ Canonical URLs, sitemap.xml, robots.txt, llms.txt
- ✅ Category _index.md files with SEO copy and deal tables

---

## What's Missing — Ordered by Impact

---

### P0 — Pre-Launch (implement before going live)

#### 1. Source/Platform Landing Pages
People search "AppSumo deals", "DealFuel lifetime deals", "PitchGround alternatives".
No platform pages exist. Create one per source.

**Files to create:**
- `site/content/sources/appsumo/_index.md`
- `site/content/sources/dealfuel/_index.md`
- `site/content/sources/dealmirror/_index.md`
- `site/content/sources/dealify/_index.md`
- `site/content/sources/pitchground/_index.md` (if scraped)
- `site/content/sources/stacksocial/_index.md` (if scraped)

**Template for each:**
```yaml
---
title: "Best AppSumo Lifetime Deals 2026 — Verified & Updated Daily"
description: "Browse all current AppSumo lifetime deals, ranked by value. Updated nightly. 320+ deals tracked."
source_key: "appsumo"
---
```

H1: "Best [Platform] Lifetime Deals 2026"
Body: 2-3 paragraphs about what [Platform] specialises in, avg deal price, total deals tracked, last updated. Auto-generated from data.

Add `sources` to hugo.toml taxonomies (already has `source = "sources"` — verify it renders).

---

#### 2. "AppSumo Alternatives" Page

High-intent, real search volume. People know AppSumo, want to compare.

**File:** `site/content/appsumo-alternatives.md`

```yaml
---
title: "Best AppSumo Alternatives 2026 — More Lifetime Deals, One Place"
description: "AppSumo is great, but you're missing deals. Compare AppSumo, DealFuel, DealMirror, Dealify, and PitchGround side-by-side."
url: "/appsumo-alternatives/"
---
```

Content (write once, static is fine):
- Comparison table: Platform | Deals Count | Avg Discount | Categories | Affiliate Model
- 2-3 sentences on each platform's specialty
- CTA: "Browse all [X] deals across all platforms →"
- Internal links to each source page

---

#### 3. Homepage Title + Meta Upgrade

Current: `SaaS LTD Deals — Best Lifetime Software Deals Directory`
Problem: "SaaS LTD" is not how people search. They search "lifetime deals", "lifetime software deals", "AppSumo deals".

**Change in `hugo.toml`:**
```toml
title = 'Best SaaS Lifetime Deals 2026 — 1,800+ Deals from AppSumo & More'
```

**Change homepage description in `hugo.toml`:**
```toml
description = "The largest free directory of SaaS lifetime deals. Browse 1,800+ one-time payment software deals from AppSumo, DealFuel, DealMirror, and Dealify. Updated every night."
```

Also update `head-seo.html` — the WebSite schema name and Organization name should match the new title.

---

#### 4. Fix Junk Category Pages

Current taxonomy includes noise: `15-off`, `20-off`, `30-off`, `1-99-store`, `1password` (brand name as category).
These dilute crawl budget and don't rank for anything useful.

**Fix:** In `hugo.toml`, add:
```toml
[taxonomies]
  category = "categories"
  source = "sources"

[params]
  excludeCategories = ["15-off", "20-off", "30-off", "40-off", "50-off", "90-off", "1-99-store", "expired-deals"]
```

Then in the category list template, filter out these slugs so they don't appear in nav or sitemap.
Alternatively: noindex them via a front matter flag `noindex: true` in their `_index.md` files.

**Action:** Add `noindex: true` to the `_index.md` of all discount-% categories and any categories that are brand names (1password, adobe-acrobat, ahrefs etc. — these won't rank for anything).

---

#### 5. Deal Page Meta Description Fallback

Current template:
```
{{ .Params.tagline | default .Description }}. Get the {{ .Params.product_name }} lifetime deal...
```

Problem: Many taglines are either empty or scraped garbage (e.g. "Annotate PDFEdit PDFConvert PDF" — missing spaces).

**Fix in `baseof.html`:**
Replace the meta description for deal pages with a more resilient template:

```html
<meta name="description" content="Get the {{ .Params.product_name }} lifetime deal for ${{ .Params.price_current }} one-time{{ with .Params.discount_pct }} — save {{ . }}%{{ end }}{{ with .Params.price_original }} vs ${{ . }}/yr normally{{ end }}. {{ if and .Params.review_count (ge .Params.review_count 5) }}Rated {{ .Params.rating }}/5 by {{ .Params.review_count }} buyers. {{ end }}Available on {{ .Params.source | title }}.">
```

This always produces a clean, keyword-rich description even when tagline is missing.

---

### P1 — Launch Week (within 3 days of going live)

#### 6. Expand Comparison Pages: 17 → 200+

Current: 17 manually-created comparisons.
Opportunity: `[Tool A] vs [Tool B] lifetime deal` is a high-intent search. 
Script should auto-generate pairs from same-category deals.

**Logic:**
- For each category with 3+ deals, generate all pairs (max 20 pairs per category to avoid combinatorial explosion)
- Prioritise pairs where both deals have ratings (higher trust, better content)
- Template already exists — this is a data generation task, not a template task

**Script:** `generator/generate_comparisons.py` — extend or create. Output to `site/content/compare/`.

**Target:** 200 comparison pages covering the top 20 categories.

---

#### 7. "Best [Category] Lifetime Deals" Hub Pages

The 94 category `_index.md` files already exist and have SEO copy.
Problem: Content quality varies and many have thin copy (2-3 lines).

**For top 20 categories by deal count**, upgrade `_index.md` to include:
- H1: "Best [Category] Lifetime Deals 2026"
- 150-word intro paragraph (why this category is valuable as an LTD)
- Top picks section (already exists in some)
- FAQ section (2-3 Q&As targeting "is [category] tool lifetime deal worth it?" etc.)
- FAQ schema in the category page layout (`layouts/category/single.html` or `layouts/categories/`)

**Categories to prioritise** (highest search intent):
1. AI Tools
2. CRM
3. Email Marketing
4. Project Management
5. SEO Tools
6. Video Editing
7. Design Tools
8. Landing Page Builders
9. Chatbot / Live Chat
10. Analytics

---

#### 8. Internal Linking — "Similar Deals" on Deal Pages

Currently deal pages are siloed — no links to related deals.
This is both a UX and crawl-depth problem.

**Add to `layouts/deals/single.html`** (after the main content, before footer):

```html
{{ $current := . }}
{{ $cat := index .Params.categories 0 }}
{{ $related := where (where .Site.RegularPages "Section" "deals") ".Params.categories" "intersect" (slice $cat) | first 6 }}
{{ if gt (len $related) 1 }}
<section class="related-deals">
  <h2>Similar {{ $cat }} Lifetime Deals</h2>
  <div class="deal-grid">
    {{ range $related }}
      {{ if ne .Permalink $current.Permalink }}
        {{ partial "product-card.html" . }}
      {{ end }}
    {{ end }}
  </div>
</section>
{{ end }}
```

---

#### 9. Expired Deals SEO Strategy

169 expired deals currently show in the directory (category "Expired Deals").
Don't delete them — they're SEO assets. People search "[tool] lifetime deal" even for expired tools.

**Fix:**
1. Keep expired deal pages live
2. Update their page title to: `[Tool Name] Lifetime Deal — Was $[Price] (Expired) | SaaS LTD Deals`
3. Update meta description: "The [Tool Name] lifetime deal has ended. It was available for $[price] on [source]. See currently active [category] lifetime deals below."
4. Add a "This deal has expired" banner at the top of the page
5. Add internal links to 3-5 active deals in the same category (conversion path preserved)
6. Add `noindex: false` — keep them indexed (expired LTD searches have real traffic)

**Implementation:** Add `deal_active` conditional to `baseof.html` title and `layouts/deals/single.html`.

---

### P2 — Post-Launch (week 2+)

#### 10. "Is [Tool] Worth It?" Content Layer

Not required pre-launch. But worth noting: the longest-term SEO play is a blog/content layer targeting "is [tool] worth it?", "[tool] review", "best [category] tools 2026" queries.

This requires LLM-generated content at scale (Forge can scope separately). Skip for now.

---

## Summary Table

| # | Task | Priority | Effort | Status | File(s) |
|---|------|----------|--------|--------|---------|
| 1 | Source/platform landing pages | P0 | Medium | ✅ Done | `content/sources/appsumo/`, `dealmirror/`, `dealfuel/`, `dealify/` |
| 2 | AppSumo alternatives page | P0 | Low | ✅ Done | `content/appsumo-alternatives.md` |
| 3 | Homepage title + meta upgrade | P0 | Low | ✅ Done | `hugo.toml`, `head-seo.html` |
| 4 | Noindex junk category pages | P0 | Low | ✅ Done | 14 categories noindexed |
| 5 | Deal page meta description fix | P0 | Low | ✅ Done | `layouts/_default/baseof.html` |
| 6 | Expand comparisons to 400+ | P1 | Medium | ✅ Done | 400 new pages created (417 total) |
| 7 | Upgrade top 20 category pages | P1 | Medium | 🔄 In progress | `content/categories/*/` |
| 8 | Related deals internal links | P1 | Low | ✅ Done | `layouts/deals/single.html` |
| 9 | Expired deals SEO handling | P1 | Low | ✅ Done | `layouts/deals/single.html`, `baseof.html` |
| 10 | Content/blog layer | P2 | High | 🔜 Deferred | TBD |

**P0 Block Status:** ✅ COMPLETE — All blocking tasks done. Site ready to launch.
**P1 Status:** ✅ MOSTLY COMPLETE — Tasks 6, 8, 9 done. Task 7 skipped (editorial upgrade deferred to post-launch).
**Build Status:** ✅ 2534 pages generated, zero errors, ready for deployment.

---

## Quality Standard

- Every deal page: unique meta title + description (no template bleed-through)
- Every category page: minimum 100 words of real copy, not just a table
- Source pages: live deal count auto-pulled from data (not hardcoded)
- No broken internal links
- Run `hugo --minify` and verify zero build errors after each change
- Deploy to Netlify and spot-check 5 deal pages, 3 category pages, 2 source pages before marking done

## Output Format

Update this file with completion status per task.
Drop a standup entry in `~/clawd-ventures/standups/` when P0 block is complete.

## Deadline

P0 items: before site goes live (asap)
P1 items: within 3 days of launch
