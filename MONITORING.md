# Monitoring Setup — SaaS LTD Directory

## UptimeRobot (manual setup required)

1. Go to https://uptimerobot.com → Sign up (free)
2. Add New Monitor:
   - Monitor Type: HTTPS
   - Friendly Name: SaaS LTD Directory
   - URL: https://saas-ltd-directory.netlify.app
   - Monitoring Interval: 5 minutes
3. Alert Contact: Add Jaisev's email
4. Save

This is free and takes 2 minutes. Alerts on downtime via email.

## GitHub Actions — Nightly Rebuild

- Workflow: `Nightly Rebuild` in `Openclaw-Ventures/saas-ltd-directory`
- Trigger: Cron (nightly) + manual dispatch
- Check status: `gh run list --repo Openclaw-Ventures/saas-ltd-directory --limit 5`
- Manual trigger: `gh workflow run "Nightly Rebuild" --repo Openclaw-Ventures/saas-ltd-directory`

## Key URLs to Monitor

| URL | Expected | 
|-----|----------|
| https://saas-ltd-directory.netlify.app | 200, homepage with deal count |
| https://saas-ltd-directory.netlify.app/sitemap.xml | 200, valid XML sitemap |
| https://saas-ltd-directory.netlify.app/robots.txt | 200, allows all crawlers |
| https://saas-ltd-directory.netlify.app/llms.txt | 200, AI-readable summary |
| https://saas-ltd-directory.netlify.app/deals/ | 200, all deals listing |
| https://saas-ltd-directory.netlify.app/categories/ | 200, category index |

## Netlify Deploy

```bash
cd ~/clawd-forge/active/saas-ltd-directory
make build
NETLIFY_AUTH_TOKEN=nfp_DtoRudN9z3scPNd12wmxQ2PqsmCQGzQY2b08 netlify deploy --dir=site/public --prod --site=5f724959-cb60-4185-a45b-825f5c074d2f
```
