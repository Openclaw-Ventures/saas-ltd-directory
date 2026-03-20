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
    
    partner_ids: dict of network -> partner_id
    Returns source_url with affiliate params appended.
    """
    import os
    if partner_ids is None:
        partner_ids = {
            "appsumo": os.environ.get("APPSUMO_IMPACT_ID", "placeholder_impact_id"),
            "partnerstack": os.environ.get("PARTNERSTACK_KEY", "placeholder_ps_key"),
            "default_ref": os.environ.get("DEFAULT_REF", "saasltddir"),
        }

    separator = "&" if "?" in source_url else "?"

    if source == "appsumo":
        # Impact.com handles tracking via their pixel, but we add a ref param
        return f"{source_url}{separator}ref={partner_ids.get('default_ref', 'saasltddir')}"
    elif source == "partnerstack":
        return f"{source_url}{separator}ps_partner_key={partner_ids.get('partnerstack', '')}&ps_xid=saasltddir"
    else:
        return f"{source_url}{separator}ref={partner_ids.get('default_ref', 'saasltddir')}"
