# Search Engine Submission Guide — SaaS LTD Directory

## Part 1: Google Search Console

### Step-by-step:

1. **Go to** https://search.google.com/search-console/welcome
2. **Choose** "URL prefix" method
3. **Enter** `https://saas-ltd-directory.netlify.app`
4. **Select verification method:** "HTML tag"
5. **Copy the verification code** — it looks like:
   ```
   <meta name="google-site-verification" content="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" />
   ```
   You only need the `content` value (the long string).

6. **Paste the code into Hugo config:**
   Open `site/hugo.toml` and find:
   ```toml
   [params]
     googleVerification = ""  # Paste your Google Search Console verification code here
   ```
   Paste the content value between the quotes:
   ```toml
   googleVerification = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   ```

7. **Rebuild and redeploy:**
   ```bash
   cd site/
   hugo --minify
   # Deploy to Netlify (push to git or manual deploy)
   ```

8. **Back in Search Console** → click "Verify"

9. **Once verified** → go to "Sitemaps" in the left sidebar
   - Enter: `https://saas-ltd-directory.netlify.app/sitemap.xml`
   - Click "Submit"

10. **Request indexing:**
    - Go to "URL Inspection" in the left sidebar
    - Enter the homepage URL: `https://saas-ltd-directory.netlify.app/`
    - Click "Request Indexing"
    - Repeat for a few key pages:
      - `https://saas-ltd-directory.netlify.app/deals/`
      - `https://saas-ltd-directory.netlify.app/categories/`
      - `https://saas-ltd-directory.netlify.app/compare/`

### What was already prepared in the codebase:

The Hugo template (`site/layouts/_default/baseof.html`) already has a conditional meta tag:
```html
{{ with .Site.Params.googleVerification }}
<meta name="google-site-verification" content="{{ . }}" />
{{ end }}
```

So all Jaisev needs to do is:
1. Paste the verification string into `hugo.toml`
2. Rebuild
3. Deploy
4. Click Verify in Search Console

No template editing needed.

---

## Part 2: Bing Webmaster Tools

### Step-by-step:

1. **Go to** https://www.bing.com/webmasters
2. **Sign in** with a Microsoft account
3. **Add site** → enter `https://saas-ltd-directory.netlify.app`
4. **Choose verification method:** "HTML Meta Tag"
5. **Copy the verification code** — it looks like:
   ```
   <meta name="msvalidate.01" content="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" />
   ```
   You only need the `content` value.

6. **Paste into Hugo config:**
   Open `site/hugo.toml` and find:
   ```toml
   bingVerification = ""    # Paste your Bing Webmaster Tools verification code here
   ```
   Paste the content value between the quotes.

7. **Rebuild and redeploy** (same as Google step 7)

8. **Back in Bing Webmaster Tools** → click "Verify"

9. **Submit sitemap:**
   - Go to "Sitemaps" in the dashboard
   - Enter: `https://saas-ltd-directory.netlify.app/sitemap.xml`
   - Click "Submit"

### Bing bonus: Import from Google Search Console
Bing offers an option to import your verified site directly from Google Search Console. If you've already verified with Google, this is the fastest path — just click "Import from GSC" on the Bing Webmaster Tools welcome page.

---

## Notes

- **Sitemap URL:** `https://saas-ltd-directory.netlify.app/sitemap.xml` (verified working, returns 200)
- **robots.txt:** Already configured to allow all crawlers including AI bots
- **llms.txt:** Already present with site description and content summary
- The sitemap currently references `saasltddeals.com` as the base URL (matching Hugo's `baseURL` config). When the custom domain is set up, URLs will automatically update.
