# Affiliate Program Status — SaaS LTD Directory

**Last updated:** 2026-03-24

---

## Programs — Current Status

### 1. AppSumo via Impact.com (P0 — Primary Revenue)

- **Signup URL:** https://app.impact.com/campaign-promo-signup/AppSumo.brand?execution=e1s1
- **Commission:** Up to 100% ($50 max) on first purchase by referred new customer
- **Cookie:** Last-click via Impact
- **Payout:** 60 days after month-end, paid 10th of following month
- **Status:** ⏳ PENDING APPROVAL — submitted 2026-03-24

**Next step:** Jaisev checks Impact dashboard (est. 2–7 business days). Once approved: update `.env` with `APPSUMO_IMPACT_ID=<impact-id>`.

---

### 2. PartnerStack (REJECTED)

- **Status:** ❌ REJECTED — 2026-03-24 ("not a great fit" — profile too thin, no traffic)
- **Rejected vendors affected:** monday.com, Brevo, Kit, Apollo.io, Gorgias
- **Action taken:** Migrated all PartnerStack vendors to direct affiliate programs (see below)
- **Reapply trigger:** 10k monthly GSC visitors

---

## Direct Vendor Programs (PartnerStack Replacement)

### 3. monday.com Direct (P0)

- **Signup URL:** https://monday.com/affiliate-program
- **Commission:** Up to 100% first-year sales (tier model), base 25%
- **Payout:** Monthly via PayPal or Stripe
- **Traffic gate:** None disclosed
- **Env var:** `MONDAY_AFFILIATE_ID`
- **Status:** ⏳ PENDING APPLICATION — Jaisev to apply

### 4. Kit (ConvertKit) Direct (P0)

- **Signup URL:** https://kit.com/affiliate
- **Commission:** 50% recurring yr 1; 10–20% recurring lifetime after yr 1
- **Cookie:** 90 days
- **Traffic gate:** None disclosed
- **Env var:** `KIT_AFFILIATE_ID`
- **Status:** ⏳ PENDING APPLICATION — Jaisev to apply

### 5. Apollo.io Direct (P0)

- **Signup URL:** https://www.apollo.io/partners/affiliates
- **Commission:** 15% monthly / 20% annual, first 12 months. 4,000+ active partners.
- **Traffic gate:** None disclosed
- **Env var:** `APOLLO_AFFILIATE_ID`
- **Status:** ⏳ PENDING APPLICATION — Jaisev to apply

### 6. Brevo Direct (P0)

- **Signup URL:** https://www.brevo.com/partners/affiliates/
- **Commission:** $5/free signup + $100/paying customer
- **Payout:** PayPal or Stripe
- **Traffic gate:** None disclosed (apply directly to Brevo, NOT via PartnerStack marketplace)
- **Env var:** `BREVO_AFFILIATE_ID`
- **Note:** Brevo's backend uses PartnerStack but they manage approvals directly — the marketplace rejection does not apply here
- **Status:** ⏳ PENDING APPLICATION — Jaisev to apply

### 7. Gorgias Direct (DEFERRED)

- **Signup URL:** https://www.gorgias.com/partner-program
- **Commission:** Revenue share (agency-focused, % not publicly disclosed)
- **Traffic gate:** ⚠️ Agency/partner-focused program — low likelihood of approval for publisher without traffic
- **Env var:** `GORGIAS_AFFILIATE_ID`
- **Status:** ⏸ DEFERRED — revisit at 5k monthly GSC visitors

---

## Code Configuration

All affiliate links use env vars defined in `.env.example`. To activate any program:
1. Receive partner ID from the program dashboard
2. Set the env var in `.env` (or Netlify env vars dashboard)
3. Rebuild the Hugo site — links go live on next nightly cron run

**Swapping IDs takes under 10 minutes per vendor once approvals arrive.**

Current fallback: `?ref=saasltddir` appended to all untracked links (maintains basic analytics visibility).

---

## Timeline

| Date | Action |
|------|--------|
| 2026-03-19 | Code built with placeholder affiliate params |
| 2026-03-24 | AppSumo Impact submitted by Jaisev |
| 2026-03-24 | PartnerStack REJECTED — migrated to direct programs |
| 2026-03-24 | Direct program research + code changes complete (Forge) |
| 2026-03-24 | Jaisev to apply to Kit, monday.com, Apollo.io, Brevo (all same day) |
| 2026-03-26 | Expected: Kit + Apollo.io approvals (faster programs) |
| 2026-03-28 | Expected: AppSumo Impact + monday.com approvals |

---

## Revenue Potential

- AppSumo: Up to $50 per referred new customer (first purchase)
- monday.com: Up to 100% first-year commission at volume (base 25%)
- Kit: 50% recurring yr 1 = strong long-term value per subscriber
- Apollo.io: 15–20% for 12 months per B2B referral
- Brevo: $100 per paying customer activation
- Target: $800–$3,000/month at 30k monthly visitors
