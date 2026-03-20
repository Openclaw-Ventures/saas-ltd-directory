"""SQLite database helper for SaaS LTD directory."""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("SAAS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "saas_deals.db"))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            tagline TEXT,
            description TEXT,
            price_current REAL,
            price_original REAL,
            price_currency TEXT DEFAULT 'USD',
            discount_pct INTEGER,
            source TEXT NOT NULL,
            source_url TEXT NOT NULL,
            affiliate_url TEXT,
            subscription_url TEXT,
            subscription_affiliate_url TEXT,
            category TEXT,
            subcategory TEXT,
            rating REAL,
            review_count INTEGER,
            image_url TEXT,
            deal_active INTEGER DEFAULT 1,
            plans TEXT,
            features TEXT,
            last_scraped TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_updated TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_products_source ON products(source);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
        CREATE INDEX IF NOT EXISTS idx_products_deal_active ON products(deal_active);

        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            discount_pct INTEGER,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
        CREATE INDEX IF NOT EXISTS idx_price_history_recorded ON price_history(recorded_at);

        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            products_found INTEGER DEFAULT 0,
            products_updated INTEGER DEFAULT 0,
            products_new INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running',
            error_message TEXT
        );
    """)
    conn.commit()
    conn.close()


def upsert_product(product_dict):
    """Insert or update a product by slug. Also records price history."""
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    product_dict["last_scraped"] = now
    product_dict["last_updated"] = now
    product_dict.setdefault("first_seen", now)
    product_dict.setdefault("updated_at", now)

    existing = conn.execute("SELECT id, first_seen FROM products WHERE slug = ?", (product_dict["slug"],)).fetchone()

    if existing:
        product_dict["first_seen"] = existing["first_seen"]
        product_dict["updated_at"] = now
        cols = [k for k in product_dict if k not in ("id", "created_at")]
        set_clause = ", ".join(f"{c} = ?" for c in cols)
        vals = [product_dict[c] for c in cols]
        vals.append(product_dict["slug"])
        conn.execute(f"UPDATE products SET {set_clause} WHERE slug = ?", vals)
        
        # Record price history on update
        if product_dict.get("price_current"):
            conn.execute(
                "INSERT INTO price_history (product_id, price, discount_pct, recorded_at) VALUES (?, ?, ?, ?)",
                (existing["id"], product_dict["price_current"], product_dict.get("discount_pct"), now)
            )
        
        conn.commit()
        conn.close()
        return "updated"
    else:
        cols = [k for k in product_dict if k not in ("id", "created_at")]
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)
        vals = [product_dict[c] for c in cols]
        cursor = conn.execute(f"INSERT INTO products ({col_names}) VALUES ({placeholders})", vals)
        product_id = cursor.lastrowid
        
        # Record initial price history
        if product_dict.get("price_current"):
            conn.execute(
                "INSERT INTO price_history (product_id, price, discount_pct, recorded_at) VALUES (?, ?, ?, ?)",
                (product_id, product_dict["price_current"], product_dict.get("discount_pct"), now)
            )
        
        conn.commit()
        conn.close()
        return "new"


def start_scrape_run(source):
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO scrape_runs (source, started_at) VALUES (?, ?)",
        (source, now)
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def complete_scrape_run(run_id, found, updated, new, status="completed", error=None):
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE scrape_runs SET completed_at=?, products_found=?, products_updated=?, products_new=?, status=?, error_message=? WHERE id=?",
        (now, found, updated, new, status, error, run_id)
    )
    conn.commit()
    conn.close()


def get_all_products(active_only=True):
    conn = get_connection()
    if active_only:
        rows = conn.execute("SELECT * FROM products WHERE deal_active = 1 ORDER BY name").fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM products WHERE deal_active = 1").fetchone()[0]
    conn.close()
    return count


def record_price_history(product_id, price, discount_pct=None):
    """Record a price snapshot for history tracking."""
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO price_history (product_id, price, discount_pct, recorded_at) VALUES (?, ?, ?, ?)",
        (product_id, price, discount_pct, now)
    )
    conn.commit()
    conn.close()


def get_price_history(product_id, days=30):
    """Get price history for a product over N days."""
    conn = get_connection()
    now = datetime.now(timezone.utc)
    cutoff = (now.timestamp() - (days * 86400)) * 1000  # milliseconds
    
    rows = conn.execute(
        """SELECT price, discount_pct, recorded_at FROM price_history 
           WHERE product_id = ? AND recorded_at > datetime('now', ? || ' days')
           ORDER BY recorded_at ASC""",
        (product_id, -days)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_deals_expired(source, found_slugs):
    """Mark products from a source as expired if they weren't found in this scrape.
    
    Args:
        source: Platform name (e.g., 'appsumo')
        found_slugs: Set of product slugs found in this scrape
    """
    conn = get_connection()
    
    # Find products from this source that weren't in the scrape
    current = conn.execute(
        "SELECT id, slug FROM products WHERE source = ? AND deal_active = 1",
        (source,)
    ).fetchall()
    
    now = datetime.now(timezone.utc).isoformat()
    for row in current:
        if row["slug"] not in found_slugs:
            conn.execute(
                "UPDATE products SET deal_active = 0, updated_at = ? WHERE id = ?",
                (now, row["id"])
            )
    
    conn.commit()
    conn.close()


# Initialize on import
init_db()
