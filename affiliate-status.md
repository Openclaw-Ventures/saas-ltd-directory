# Affiliate Program Status — SaaS LTD Directory

**Last updated:** 2026-03-19

---

## Programs to Apply To

### 1. AppSumo via Impact.com (P0 — Primary Revenue)

- **Signup URL:** https://app.impact.com/campaign-promo-signup/AppSumo.brand?execution=e1s1
- **Commission:** Up to 100% ($50 max) on first purchase by referred new customer
- **Cookie:** Last-click attribution via Impact
- **Payout:** 60 days after month-end, paid on 10th of following month
- **Approval time:** ~2 business days
- **Status:** ⏳ NOT YET APPLIED

**Steps for Jaisev:**
1. Go to https://app.impact.com/campaign-promo-signup/AppSumo.brand?execution=e1s1
2. Create an Impact.com account (or log in if existing)
3. Fill in website/promotional methods — list the directory URL
4. Submit application
5. Wait for approval (typically 2 business days)
6. Once approved: get the tracking parameters from Impact dashboard
7. Update `.env` with `APPSUMO_IMPACT_ID=<your-id>`

### 2. PartnerStack (P0 — Secondary Revenue)

- **Signup URL:** https://partnerstack.com/partnerstack-partner-program
- **Marketplace:** https://market.partnerstack.com/
- **Commission:** Varies by vendor (10%-50% recurring)
- **Status:** ⏳ NOT YET APPLIED

**Steps for Jaisev:**
1. Go to https://partnerstack.com/partnerstack-partner-program
2. Create a free PartnerStack account
3. Browse marketplace and apply to these high-priority vendor programs:
   - **Brevo** (email marketing) — $100 per paying customer
   - **monday.com** — up to 20% commission
   - **Kit (ConvertKit)** — 50% recurring for 1st year
   - **Apollo.io** — up to 20% commission
   - **Gorgias** — 10% commission indefinitely
4. Once approved: get `ps_partner_key` from dashboard
5. Update `.env` with `PARTNERSTACK_KEY=<your-key>`

### 3. Awin / ShareASale (P2 — Fallback)

- **Signup URL:** https://www.awin.com
- **Commission:** 4-50% depending on merchant
- **Min payout:** $50
- **Status:** ⏳ DEFERRED — apply after site is live with traffic

---

## Current Code Configuration

All affiliate links use **placeholder parameters** defined in `.env.example`:

```
APPSUMO_IMPACT_ID=placeholder_impact_id
PARTNERSTACK_KEY=placeholder_ps_key
DEFAULT_REF=saasltddir
```

The `?ref=saasltddir` parameter is appended to all AppSumo links now. This serves as a basic tracking parameter even before Impact approval. Once approved, we swap to proper Impact tracking.

---

## Timeline

| Date | Action |
|------|--------|
| 2026-03-19 | Code built with placeholder affiliate params |
| 2026-03-20 | Jaisev applies to Impact.com (AppSumo) + PartnerStack |
| 2026-03-22 | Expected Impact approval |
| 2026-03-23 | Swap placeholder IDs with real affiliate tracking |
| 2026-03-31 | Site live with real affiliate links |

---

## Revenue Potential (per pre-build gates report)

- AppSumo: Up to $50 per referred new customer
- PartnerStack vendors: 10-50% recurring commissions
- Target: $800-$3,000/month at 30k monthly visitors
