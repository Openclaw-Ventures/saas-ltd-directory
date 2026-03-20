# Search Engine Indexing Steps

Follow these steps after the site is live on a public URL.

## 1. Google Search Console

1. Go to https://search.google.com/search-console
2. Click **Add Property** → choose **URL prefix**
3. Enter the live site URL (e.g., `https://saas-ltd-directory.netlify.app`)
4. Choose **HTML tag** verification method
5. Copy the meta tag Google gives you. It looks like:
   ```html
   <meta name="google-site-verification" content="XXXXXXXXXX" />
   ```
6. Add it to Hugo's head template. Edit `site/layouts/partials/head-seo.html` and add at the top:
   ```html
   <meta name="google-site-verification" content="PASTE_YOUR_CODE_HERE" />
   ```
7. Rebuild and redeploy: `cd site && hugo --minify && netlify deploy --dir=public --prod`
8. Go back to Google Search Console and click **Verify**
9. Once verified, go to **Sitemaps** → submit: `https://[your-domain]/sitemap.xml`
10. Go to **URL Inspection** → enter the homepage URL → click **Request Indexing**

## 2. Bing Webmaster Tools

1. Go to https://www.bing.com/webmasters
2. Sign in → **Add your site** → enter the live URL
3. Choose **HTML Meta Tag** verification
4. Add the Bing meta tag to the same `head-seo.html` partial:
   ```html
   <meta name="msvalidate.01" content="PASTE_BING_CODE_HERE" />
   ```
5. Rebuild and redeploy
6. Verify in Bing Webmaster Tools
7. Submit sitemap: `https://[your-domain]/sitemap.xml`

## 3. Google Indexing API (Optional — Faster Indexing)

For bulk URL submission:
1. Create a Google Cloud project
2. Enable the Indexing API
3. Create a service account
4. Add the service account as an owner in Search Console
5. Use the API to submit URLs programmatically

This is optional — the sitemap submission in step 1 is usually sufficient.

## 4. Social Signals (Free SEO Boost)

After indexing is submitted:
- Share the homepage on Twitter/X via @OpenClawV
- Post on relevant Reddit communities (r/SaaS, r/AppSumo, r/Entrepreneur)
- Submit to Product Hunt (if timing is right)
- Submit to directories: IndieHackers, AlternativeTo, etc.

## Timeline

- Day 0: Submit to Google + Bing
- Day 1-3: Homepage should appear in Google
- Week 1-2: Category pages indexed
- Week 2-4: Individual deal pages indexed
- Month 1: Full index expected for 2,000+ pages
