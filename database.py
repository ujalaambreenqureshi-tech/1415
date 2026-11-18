"""
Database management for Jumma Couture By Noman Store
Manages SQLite store data: Customer accounts, Orders, Wishlists, Reviews, and Manual Payment Auditing
"""
import os
import sqlite3
import json
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heritage.db")

VALID_ORDER_STATUSES = ["Pending", "Payment Verification Pending", "Paid", "Failed", "Refunded"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        postal_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Orders table (Manual Payment with Verification Workflow)
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_email TEXT,
        customer_phone TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT,
        address TEXT NOT NULL,
        postal_code TEXT,
        delivery_instructions TEXT,
        items_json TEXT NOT NULL,
        subtotal REAL NOT NULL,
        shipping_fee REAL NOT NULL,
        tax_amount REAL NOT NULL,
        total_amount REAL NOT NULL,
        currency TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'Payment Verification Pending',
        transaction_id TEXT NOT NULL,
        receipt_path TEXT,
        shopify_order_id TEXT,
        shopify_sync_status TEXT NOT NULL,
        tracking_status TEXT NOT NULL,
        tracking_number TEXT,
        carrier TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check and migrate columns if needed
    c.execute("PRAGMA table_info(orders)")
    columns = [row["name"] for row in c.fetchall()]
    if "receipt_path" not in columns:
        try:
            c.execute("ALTER TABLE orders ADD COLUMN receipt_path TEXT")
        except Exception:
            pass
    if "delivery_instructions" not in columns:
        try:
            c.execute("ALTER TABLE orders ADD COLUMN delivery_instructions TEXT")
        except Exception:
            pass

    # Wishlist table
    c.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        product_slug TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(session_id, product_slug)
    )
    """)

    # Reviews table
    c.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_slug TEXT NOT NULL,
        author TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        verified_purchase INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Newsletter subscribers
    c.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Seed demo reviews if empty
    c.execute("SELECT COUNT(*) as count FROM reviews")
    if c.fetchone()["count"] == 0:
        seed_reviews = [
            ("zari-embroidered-lehenga", "Zainab Al-Mansoor (Dubai, UAE)", 5, "Breathtaking craftsmanship! The deep maroon velvet paired with golden zardozi exceeded my couture expectations. Paid via Bank Transfer and verified smoothly.", 1),
            ("zari-embroidered-lehenga", "Ayesha Malik (London, UK)", 5, "Ordered for my sister's wedding in Mayfair. Arrived in 4 days via DHL Express. Stitching fits like a glove!", 1),
            ("embellished-organza-saree", "Fatima Khan (Lahore, PK)", 5, "The dusty mauve tone and subtle gold foil are mesmerizing. Paid via Easypaisa and receipt was verified quickly.", 1),
            ("embellished-organza-saree", "Sana Mir (Toronto, Canada)", 5, "The organza drape is so graceful and lightweight. Jumma Couture is our new family favorite for festive collections.", 1),
            ("handwoven-silk-kurta-set", "Rabia Tariq (Karachi, PK)", 5, "Silk quality is 100% authentic pure Chanderi. Paid via JazzCash and verified within minutes.", 1),
            ("anarkali-suit-set", "Mariam Siddiqui (Riyadh, KSA)", 5, "The flare on this 24-kali gown is breathtaking. Royal yellow shade is exactly as pictured in the catalog.", 1)
        ]
        c.executemany("INSERT INTO reviews (product_slug, author, rating, comment, verified_purchase) VALUES (?, ?, ?, ?, ?)", seed_reviews)
        conn.commit()

    # Seed demo owner/client user
    c.execute("SELECT COUNT(*) as count FROM users WHERE email = 'owner@jummacouturebynoman.com'")
    if c.fetchone()["count"] == 0:
        c.execute("""
        INSERT INTO users (name, email, password_hash, phone, address, city, country, postal_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Muhammad Jumma (Owner)",
            "owner@jummacouturebynoman.com",
            hash_password("JummaOwner2026!"),
            "+92 308 1755403",
            "Jumma Couture Studio, Gulberg III",
            "Lahore",
            "Pakistan",
            "54000"
        ))
        conn.commit()

    conn.close()


def update_order_status(order_number: str, new_status: str, tracking_status: str = None):
    """Updates order payment status and tracking status"""
    if new_status not in VALID_ORDER_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {VALID_ORDER_STATUSES}")

    conn = get_connection()
    c = conn.cursor()
    if tracking_status:
        c.execute("UPDATE orders SET payment_status = ?, tracking_status = ? WHERE order_number = ?", (new_status, tracking_status, order_number))
    else:
        c.execute("UPDATE orders SET payment_status = ? WHERE order_number = ?", (new_status, order_number))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
