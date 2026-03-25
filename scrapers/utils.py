"""Utility functions for scrapers."""

import re
import time
import random


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text


def make_deal_slug(name, source=None):
    """Create a product slug: name-lifetime-deal."""
    base = slugify(name)
    if not base.endswith("-lifetime-deal"):
        base = f"{base}-lifetime-deal"
    return base


def parse_price(price_str):
    """Extract numeric price from string like '$49' or '$49.00'."""
    if not price_str:
        return None
    match = re.search(r'[\$€£]?\s*([\d,]+\.?\d*)', str(price_str))
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def random_delay(min_sec=1, max_sec=3):
    """Random delay between requests to be polite."""
    time.sleep(random.uniform(min_sec, max_sec))


def build_affiliate_url(source_url, source, partner_ids=None):
    """Build affiliate URL with tracking parameters.

    Supported sources: appsumo, dealmirror, dealfuel, dealify,
    monday, brevo, kit, apollo, gorgias, default.

    partner_ids: dict of source -> partner_id (loaded from env if not provided).
    Returns source_url with affiliate params appended.

    NOTE: PartnerStack rejected 2026-03-24 — migrated to direct programs.
    To activate a direct program, set the corresponding env var once Jaisev
    receives approval and update the placeholder value below.
    """
    import os
    if partner_ids is None:
        partner_ids = {
            # Primary
            "appsumo": os.environ.get("APPSUMO_IMPACT_ID", "placeholder_impact_id"),
            # Direct vendor programs (replaces PartnerStack — see direct-affiliate-research.md)
            "monday": os.environ.get("MONDAY_AFFILIATE_ID", ""),
            "brevo": os.environ.get("BREVO_AFFILIATE_ID", ""),
            "kit": os.environ.get("KIT_AFFILIATE_ID", ""),
            "apollo": os.environ.get("APOLLO_AFFILIATE_ID", ""),
            "gorgias": os.environ.get("GORGIAS_AFFILIATE_ID", ""),  # deferred
            # Fallback
            "default_ref": os.environ.get("DEFAULT_REF", "saasltddir"),
        }

    separator = "&" if "?" in source_url else "?"
    ref = partner_ids.get("default_ref", "saasltddir")

    if source == "appsumo":
        # Impact.com tracking pixel handles attribution; ref param for fallback tracking
        return f"{source_url}{separator}ref={ref}"
    elif source == "monday":
        partner_id = partner_ids.get("monday", "")
        if partner_id:
            return f"{source_url}{separator}ref={partner_id}"
        return f"{source_url}{separator}ref={ref}"
    elif source == "brevo":
        partner_id = partner_ids.get("brevo", "")
        if partner_id:
            return f"{source_url}{separator}fpr={partner_id}"
        return f"{source_url}{separator}ref={ref}"
    elif source == "kit":
        partner_id = partner_ids.get("kit", "")
        if partner_id:
            return f"{source_url}{separator}lmref={partner_id}"
        return f"{source_url}{separator}ref={ref}"
    elif source == "apollo":
        partner_id = partner_ids.get("apollo", "")
        if partner_id:
            return f"{source_url}{separator}ref={partner_id}"
        return f"{source_url}{separator}ref={ref}"
    elif source == "gorgias":
        partner_id = partner_ids.get("gorgias", "")
        if partner_id:
            return f"{source_url}{separator}ref={partner_id}"
        return f"{source_url}{separator}ref={ref}"
    else:
        return f"{source_url}{separator}ref={ref}"
