# GEO Fixes — SaaS LTD Directory

**Source:** GEO Audit 2026-03-20  
**Report:** ~/clawd-atlas/research/2026-03-20-geo-audit-results.md  
**Priority:** 🔴 Critical → 🟡 Important → 🟢 Nice to Have

---

## 🔴 CRITICAL — Do First

### FIX-1: Remove Duplicate Canonical Tags

**File:** Hugo template that generates `<head>` (likely `layouts/partials/head.html` or `layouts/_default/baseof.html`)

**Problem:** Every page outputs TWO identical `<link rel="canonical">` tags.

**Fix:** Find the duplicate. One is probably in a partial and one in the base template. Remove one. Grep for `rel=canonical` across all templates.

```bash
grep -r "canonical" layouts/
```

Remove the duplicate. Keep one.

---

### FIX-2: Restructure Product Page Citability

**File:** `layouts/deals/single.html` (or equivalent product page template)

**Problem:** The most citable paragraph (`deal-intro`) appears AFTER CTAs and multiple sections. AI systems prioritize the first 200 words.

**Fix:** Move the intro paragraph to immediately after `<h1>`:

```html
<h1>{{ .Title }}</h1>

<!-- CITABILITY: AI-optimized first paragraph — must come first -->
<p class="deal-intro-top">
  {{ .Params.name }} is a {{ .Params.category }} tool available as a lifetime deal 
  on {{ .Params.platform }} for ${{ .Params.price }} (originally ${{ .Params.original_price }}/year, 
  {{ .Params.discount }}% off). It has {{ .Params.rating }}/5 stars from 
  {{ .Params.review_count }} verified reviews. {{ .Params.description }}
</p>

<!-- Quick Facts box (structured, semantic) -->
<dl class="quick-facts-top">
  <dt>Price</dt><dd>${{ .Params.price }} one-time</dd>
  <dt>Original</dt><dd>${{ .Params.original_price }}/year</dd>
  <dt>Savings</dt><dd>{{ .Params.discount }}%</dd>
  <dt>Rating</dt><dd>{{ .Params.rating }}/5 ({{ .Params.review_count }} reviews)</dd>
  <dt>Platform</dt><dd>{{ .Params.platform }}</dd>
  <dt>Category</dt><dd>{{ .Params.category }}</dd>
</dl>
```

The existing `deal-intro` paragraph at the bottom can be removed (it's now at the top in enriched form).

---

### FIX-3: Add About Page

**File:** Create `content/about.md`

```markdown
---
title: "About SaaS LTD Deals"
description: "SaaS LTD Deals is an independent, automated directory tracking lifetime software deals across AppSumo, DealFuel, DealMirror, and Dealify."
---

# About SaaS LTD Deals

SaaS LTD Deals is an independent directory that tracks lifetime software deals from the four major deal platforms: AppSumo, DealFuel, DealMirror, and Dealify.

## How It Works

- **Automated scraping** runs nightly to check all four platforms for new deals, price changes, and expired offers
- **1,878+ products** are currently tracked with real-time pricing
- **Ratings and reviews** are aggregated from the original platforms
- **Price history** is tracked to show deal value over time

## Editorial Standards

- We do not accept payment for listings — all deals are included automatically
- Affiliate links are clearly disclosed on every page
- Prices are verified daily and timestamped
- Expired deals are marked, not hidden

## Revenue Model

This site earns affiliate commissions when you purchase through our links, at no extra cost to you. This keeps the directory free and independently operated.

## Contact

[Add contact info or form]
```

Add to navigation in `layouts/partials/header.html`:
```html
<a href=/about/>About</a>
```

---

## 🟡 IMPORTANT — This Week

### FIX-4: Create llms-full.txt

**File:** Create a Hugo template or build script to generate `static/llms-full.txt`

This should be auto-generated from all deal data during build:

```
# SaaS LTD Deals — Full Product Listing
# Last updated: {{ now.Format "2006-01-02" }}
# Total products: {{ len (where .Site.RegularPages "Section" "deals") }}

## All Products

{{ range where .Site.RegularPages "Section" "deals" }}
### {{ .Params.name }}
- URL: https://saasltddeals.com{{ .RelPermalink }}
- Price: ${{ .Params.price }} one-time (was ${{ .Params.original_price }}/year)
- Discount: {{ .Params.discount }}%
- Rating: {{ .Params.rating }}/5 ({{ .Params.review_count }} reviews)
- Platform: {{ .Params.platform }}
- Category: {{ .Params.category }}
- Description: {{ .Params.description }}

{{ end }}
```

Also update `llms.txt` to reference it:
```
> Full product listing: https://saasltddeals.com/llms-full.txt
> Last updated: 2026-03-20
```

---

### FIX-5: Add Homepage Schema (WebSite + Organization)

**File:** `layouts/index.html` or `layouts/partials/head.html` (conditional on homepage)

Add to `<head>` on homepage only:

```html
{{ if .IsHome }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "SaaS LTD Deals",
  "url": "https://saasltddeals.com/",
  "description": "Auto-updated directory of the best SaaS lifetime deals across AppSumo, DealFuel, DealMirror, and Dealify.",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://saasltddeals.com/deals/?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "SaaS LTD Deals",
  "url": "https://saasltddeals.com/",
  "description": "Independent directory tracking lifetime software deals from AppSumo, DealFuel, DealMirror, and Dealify."
}
</script>
{{ end }}
```

---

### FIX-6: Add Homepage og:image

**File:** Head template (wherever OG tags are generated)

Add a default OG image for the homepage. Create a 1200x630 image for social sharing, then:

```html
{{ if .IsHome }}
<meta property="og:image" content="https://saasltddeals.com/images/og-default.png">
{{ end }}
```

Generate the image: a branded card saying "SaaS LTD Deals — 1878+ Lifetime Software Deals" with the site's visual identity.

---

### FIX-7: Add URLs and Timestamps to llms.txt

**File:** `static/llms.txt` (or the template that generates it)

Add at the top:
```
> Last updated: 2026-03-20
> Product pages: https://saasltddeals.com/deals/{product-slug}/
> Category pages: https://saasltddeals.com/categories/{category-slug}/
> Full listing: https://saasltddeals.com/llms-full.txt
```

In the "Best Deals by Category" section, add URLs:
```
### Productivity
- Shareables: $59 (AppSumo) — https://saasltddeals.com/deals/shareables-lifetime-deal/
- Documentation.AI: $69 (AppSumo) — https://saasltddeals.com/deals/documentation-ai-lifetime-deal/
```

---

### FIX-8: Add ItemList Schema to Category Pages

**File:** `layouts/categories/single.html` (or category template)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "{{ .Title }}",
  "description": "{{ .Params.description }}",
  "numberOfItems": {{ len .Pages }},
  "itemListElement": [
    {{ range $i, $p := .Pages }}
    {{ if $i }},{{ end }}
    {
      "@type": "ListItem",
      "position": {{ add $i 1 }},
      "url": "https://saasltddeals.com{{ $p.RelPermalink }}",
      "name": "{{ $p.Params.name }}"
    }
    {{ end }}
  ]
}
</script>
```

---

## 🟢 NICE TO HAVE — Next Sprint

### FIX-9: Enrich Product Descriptions

In the Hugo content generation script, replace the formulaic "Is It Worth It?" and "Who Is This For?" sections with data-driven content:

- "Is It Worth It?" → compare price to top 3 competitors in same category, note unique features
- "Who Is This For?" → list 3 specific personas with use cases (not generic)
- "About [Product]" → pull feature list from platform API if available

### FIX-10: Add FAQ Schema to Product Pages

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is the {{ .Params.name }} lifetime deal still available?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, as of {{ .Params.last_updated }}, {{ .Params.name }} is available for ${{ .Params.price }} on {{ .Params.platform }}."
      }
    },
    {
      "@type": "Question",
      "name": "How much does {{ .Params.name }} normally cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ .Params.name }} normally costs ${{ .Params.original_price }}/year. The lifetime deal saves you {{ .Params.discount }}%."
      }
    }
  ]
}
</script>
```

### FIX-11: Add Brand + Category to Product Schema

Update the Product JSON-LD template:

```json
"brand": {
  "@type": "Brand",
  "name": "{{ .Params.name }}"
},
"category": "{{ .Params.category }}"
```

### FIX-12: Add Favicon

Create a favicon and add to `<head>`:
```html
<link rel="icon" href="/favicon.ico" type="image/x-icon">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

### FIX-13: Reference llms.txt in robots.txt

```
# AI-readable site description
# See: https://saasltddeals.com/llms.txt
```

(Note: there's no formal standard for this yet, but it helps discoverability.)

### FIX-14: Add Bytespider to robots.txt

```
User-agent: Bytespider
Allow: /
```

### FIX-15: Fix HTML Entity Encoding

Product names with `&` are rendering as `&#038;` in some places. Check Hugo template escaping — likely need `{{ .Params.name | safeHTML }}` in appropriate contexts, or fix at data ingestion time.

---

## Implementation Order

1. FIX-1 (duplicate canonical) — 5 min
2. FIX-3 (About page) — 30 min
3. FIX-2 (citability restructure) — 1 hr
4. FIX-5 (homepage schema) — 15 min
5. FIX-6 (og:image) — 15 min + image creation
6. FIX-7 (llms.txt enrichment) — 30 min
7. FIX-4 (llms-full.txt) — 1 hr (auto-generation)
8. FIX-8 (category schema) — 30 min
9. FIX-12 (favicon) — 10 min
10. FIX-13 + FIX-14 (robots.txt updates) — 5 min
11. FIX-15 (entity encoding) — 30 min
12. FIX-11 (schema enrichment) — 15 min
13. FIX-10 (FAQ schema) — 1 hr
14. FIX-9 (content enrichment) — ongoing

**Estimated total: ~6 hours of Forge time**
