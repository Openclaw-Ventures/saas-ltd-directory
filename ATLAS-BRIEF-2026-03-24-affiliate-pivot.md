# Atlas Brief — Affiliate Pivot: Direct Programs (PartnerStack Rejected)

**From:** Atlas
**Date:** 2026-03-24
**Priority:** P0 — blocks monetisation
**Context:** PartnerStack rejected application ("not a great fit" — profile too thin, no traffic yet). All PartnerStack-linked vendors need to be migrated to their direct affiliate programs.

---

## Decision

PartnerStack is dead for now. Reapply once saas-deals.com has measurable GSC traffic.

AppSumo Impact remains primary. Status: submitted 2026-03-24, awaiting approval (est. 3–7 business days).

---

## Task

**Replace all PartnerStack affiliate links/config with direct program equivalents.**

### Direct Program Targets

| Vendor | Direct Affiliate URL | Commission | Notes |
|--------|---------------------|------------|-------|
| monday.com | monday.com/affiliates | Up to 20% | Verify approval requirements |
| Brevo | brevo.com/partners | $100 per paying customer | Check if they accept new sites |
| Kit (ConvertKit) | partners.kit.com | 50% recurring yr 1 | Strong program |
| Apollo.io | apollo.io/affiliates (or via Impact) | Up to 20% | May be on Impact.com |
| Gorgias | gorgias.com/partners | 10% ongoing | Verify direct vs network |

Research each URL — some may have moved. Check if they require site traffic thresholds before applying.

---

## Deliverables

1. **Research doc** — for each vendor: direct affiliate URL, commission structure, traffic/approval requirements, estimated approval timeline. Save to `~/clawd-forge/active/saas-ltd-directory/direct-affiliate-research.md`

2. **Update `.env.example`** — add placeholder vars for each direct program (replacing PartnerStack vars):
   ```
   MONDAY_AFFILIATE_ID=placeholder
   BREVO_AFFILIATE_ID=placeholder
   KIT_AFFILIATE_ID=placeholder
   APOLLO_AFFILIATE_ID=placeholder
   GORGIAS_AFFILIATE_ID=placeholder
   ```

3. **Update affiliate link generation code** — ensure the site's link-building layer can swap in real IDs when Jaisev gets approvals. No broken links, no dead placeholders in prod.

4. **Update `affiliate-status.md`** — mark PartnerStack as REJECTED with date, add direct programs with status PENDING_APPLICATION.

5. **Flag any vendor that requires >5k monthly visits** to approve — those go to a "reapply later" list. Don't waste Jaisev's time on applications that will bounce.

---

## Out of Scope

- Do NOT redesign site pages for this task
- Do NOT change AppSumo Impact integration (leave as-is)
- Do NOT apply to any program on Jaisev's behalf — research + code only

---

## Quality Standard

Done means:
- All PartnerStack references replaced in code and config
- Direct program research doc complete with real URLs verified
- Jaisev can apply to each program in one sitting using the research doc
- Affiliate link swaps take under 10 minutes per vendor once IDs are received

---

## Deadline

Research + code changes: **2026-03-25 SGT** (tomorrow)

---

## Output

Progress → `~/clawd-ventures/standups/2026-03-25.jsonl`
Files → `~/clawd-forge/active/saas-ltd-directory/`
Escalate to Atlas if: any vendor has a hard traffic gate (>10k visits required)
