# SaaS LTD Directory — Deployment Status

**Date:** 2026-03-20
**Repo:** https://github.com/Openclaw-Ventures/saas-ltd-directory (transferred ✅)

---

## What's Done

1. **GitHub org transfer** — Repo successfully moved from `Jaisev-Sachdev/saas-ltd-directory` → `Openclaw-Ventures/saas-ltd-directory` ✅
2. **Git remote updated** — Local build dir points to new org URL ✅
3. **Nightly workflow committed locally** — `.github/workflows/nightly-rebuild.yml` is committed but **not pushed** (PAT missing `workflow` scope) ⚠️
4. **Deployment zip created** — `/tmp/saas-ltd-public.zip` (14MB) ready for Netlify Drop ✅

---

## What Jaisev Needs To Do

### 1. Push the workflow file (1 min)

Your GitHub PAT needs the `workflow` scope to push GitHub Actions files.

1. Go to https://github.com/settings/tokens
2. Edit your PAT → check the `workflow` scope → Save
3. Then run on the server:
   ```bash
   cd ~/clawd-forge/active/saas-ltd-directory
   git push origin master
   ```

### 2. Deploy to Netlify (1 min)

**Option A: Netlify Drop (fastest)**
1. Go to https://app.netlify.com/drop
2. Drag the `site/public/` folder (or download `/tmp/saas-ltd-public.zip`, unzip, drag `public/`)
3. You'll get a live URL in ~60 seconds

**Option B: Netlify CLI (if you set up auth)**
```bash
export NETLIFY_AUTH_TOKEN=<your-token>
cd ~/clawd-forge/active/saas-ltd-directory
npx netlify-cli deploy --dir=site/public --prod
```

### 3. Set GitHub Actions secrets (for nightly rebuild)

After the workflow is pushed, add these secrets at:
`https://github.com/Openclaw-Ventures/saas-ltd-directory/settings/secrets/actions`

- `NETLIFY_AUTH_TOKEN` — Your Netlify personal access token
- `NETLIFY_SITE_ID` — The site ID from your Netlify dashboard

---

## Site Stats

- **1,880+ deals** across 100+ categories
- **6 data sources** scraped and merged
- **Static Hugo site** — fast, SEO-friendly, zero hosting cost
- **14MB zipped** deployment package

---

## Architecture

```
Scrapers (Python) → JSON data → Hugo templates → Static HTML
                                                    ↓
                                              Netlify (CDN)
                                                    ↑
                                        GitHub Actions (nightly cron)
```
