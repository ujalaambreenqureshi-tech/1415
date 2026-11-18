"""
Jumma Couture by Noman - Main Flask Application
Complete worldwide e-commerce storefront integrated with Shopify.
Strict 100% full advance payment via Visa, Mastercard, JazzCash, Easypaisa.
"""
import os
import json
import random
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from dotenv import load_dotenv

from shopify_client import shopify_client
from payment_gateway import payment_gateway, PaymentProcessingError, load_payment_config, save_payment_config
from database import get_connection, hash_password, init_db, update_order_status, VALID_ORDER_STATUSES
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "jumma_couture_secret_key_2026_stag")

# Initialize database schema
init_db()

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

@app.context_processor
def inject_global_data():
    return {
        "current_user": get_current_user(),
        "staging_mode": True,
        "store_currency": session.get("currency", "PKR")
    }

# 1. Home Page
@app.route("/")
def home():
    products = shopify_client.fetch_products()
    featured = [p for p in products if p.get("is_featured")] or products[:4]
    return render_template(
        "index.html",
        featured_products=featured,
        active_page="home"
    )

# 2. Shop / All Products Page
@app.route("/shop")
def shop():
    category = request.args.get("category")
    occasion = request.args.get("occasion")
    sort_by = request.args.get("sort", "featured")

    products = shopify_client.fetch_products()

    if category:
        if category.lower() in ["party", "party wear"]:
            products = [p for p in products if p.get("category", "").lower() in ["party", "party wear"] or p.get("occasion", "").lower() in ["party", "party wear"]]
        else:
            products = [p for p in products if p.get("category", "").lower() == category.lower()]
    if occasion:
        if occasion.lower() == "bridal":
            products = [p for p in products if p.get("is_bridal") or p.get("occasion", "").lower() in ["bridal", "wedding"]]
        elif occasion.lower() in ["party", "party wear"]:
            products = [p for p in products if p.get("occasion", "").lower() in ["party", "party wear"] or p.get("category", "").lower() in ["party wear", "party"]]
        else:
            products = [p for p in products if p.get("occasion", "").lower() == occasion.lower()]

    if sort_by == "price_asc":
        products = sorted(products, key=lambda x: x["sale_price_pkr"])
    elif sort_by == "price_desc":
        products = sorted(products, key=lambda x: x["sale_price_pkr"], reverse=True)
    elif sort_by == "newest":
        products = sorted(products, key=lambda x: x.get("is_new", False), reverse=True)

    return render_template(
        "shop.html",
        products=products,
        active_category=category,
        active_occasion=occasion,
        active_page="shop"
    )

@app.route("/bridal")
def bridal_section():
    return redirect(url_for("shop", occasion="Bridal"))

@app.route("/party")
def party_section():
    return redirect(url_for("shop", occasion="Party"))

# 3. Product Details Page
@app.route("/product/<slug>")
def product_detail(slug):
    products = shopify_client.fetch_products()
    product = next((p for p in products if p["slug"] == slug or (slug in ["luxury-deep-teal-lehenga", "zari-embroidered-lehenga"] and p["slug"] in ["luxury-deep-teal-lehenga", "zari-embroidered-lehenga"])), None)
    if not product:
        return redirect(url_for("shop"))

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reviews WHERE product_slug = ?", (slug,))
    reviews = c.fetchall()
    conn.close()

    related = [p for p in products if p["slug"] != slug and p["category"] == product["category"]][:4]

    return render_template(
        "product.html",
        product=product,
        reviews=reviews,
        related_products=related,
        active_category=product.get("category")
    )

# 4. Product Categories Page
@app.route("/categories")
def categories():
    return render_template("categories.html", active_page="categories")

# 5. Search Results Page
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    products = shopify_client.fetch_products()
    results = []
    if query:
        q_lower = query.lower()
        results = [
            p for p in products
            if q_lower in p["title"].lower()
            or q_lower in p["description"].lower()
            or q_lower in p["category"].lower()
            or q_lower in p.get("occasion", "").lower()
        ]
    return render_template("search.html", query=query, results=results)

# 6. Shopping Cart Page
@app.route("/cart")
def cart():
    return render_template("cart.html", active_page="cart")

# 7. Checkout Page (100% Full Advance Only)
@app.route("/checkout")
def checkout():
    user = get_current_user()
    return render_template("checkout.html", current_user=user, active_page="checkout")

# 8. Customer Login & Registration
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email, hash_password(password)))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            flash("Signed in successfully to Heritage.")
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password. Please check your credentials.")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        country = request.form.get("country", "Pakistan")
        password = request.form.get("password", "")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters.")

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""
            INSERT INTO users (name, email, password_hash, phone, country)
            VALUES (?, ?, ?, ?, ?)
            """, (name, email, hash_password(password), phone, country))
            conn.commit()
            user_id = c.lastrowid
            session["user_id"] = user_id
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception:
            conn.close()
            return render_template("register.html", error="An account with this email already exists.")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# 9. Customer Dashboard
@app.route("/account")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE customer_email = ? ORDER BY id DESC", (user["email"],))
    orders = c.fetchall()
    conn.close()

    return render_template("dashboard.html", current_user=user, orders=orders)

# 10. My Orders Page
@app.route("/account/orders")
def account_orders():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE customer_email = ? ORDER BY id DESC", (user["email"],))
    orders = c.fetchall()
    conn.close()

    return render_template("orders.html", orders=orders)

# 11. Order Tracking Page
@app.route("/track-order")
def track_order():
    order_num = request.args.get("order", "").strip()
    email = request.args.get("email", "").strip().lower()

    order = None
    items = []
    if order_num:
        conn = get_connection()
        c = conn.cursor()
        if email:
            c.execute("SELECT * FROM orders WHERE order_number = ? AND LOWER(customer_email) = ?", (order_num, email))
        else:
            c.execute("SELECT * FROM orders WHERE order_number = ?", (order_num,))
        order = c.fetchone()
        conn.close()

        if order:
            try:
                items = json.loads(order["items_json"])
            except Exception:
                items = []

    return render_template("track_order.html", order=order, items=items, order_number=order_num, email=email)

# 12. Wishlist Page
@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html", active_page="wishlist")

# 13. About Us Page
@app.route("/about")
def about():
    return render_template("about.html")

# 14. Contact Us Page
@app.route("/contact", methods=["GET", "POST"])
def contact():
    success = False
    if request.method == "POST":
        success = True
    return render_template("contact.html", success=success)

# 15. FAQ Page
@app.route("/faq")
def faq():
    return render_template("faq.html")

# 16-19. Policy Pages
@app.route("/policies/shipping")
def policy_shipping():
    return render_template("policies/shipping.html")

@app.route("/policies/returns")
def policy_returns():
    return render_template("policies/returns.html")

@app.route("/policies/privacy")
def policy_privacy():
    return render_template("policies/privacy.html")

@app.route("/policies/terms")
def policy_terms():
    return render_template("policies/terms.html")

# Newsletter subscription
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip().lower()
    if email:
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT OR IGNORE INTO subscribers (email) VALUES (?)", (email,))
            conn.commit()
        except Exception:
            pass
        conn.close()
    flash("Thank you for joining the Heritage circle.")
    return redirect(request.referrer or url_for("home"))

# =========================================================================
# API ENDPOINTS
# =========================================================================

@app.route("/api/products")
def api_products():
    products = shopify_client.fetch_products()
    return jsonify(products)

@app.route("/api/shopify/status")
def api_shopify_status():
    return jsonify(shopify_client.get_status())

# Configuration API Endpoint
@app.route("/api/payment-config", methods=["GET"])
def api_get_payment_config():
    """Returns the current business manual payment configuration"""
    return jsonify(load_payment_config())

@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    """
    MANUAL PAYMENT CHECKOUT ENDPOINT
    Supported Methods:
    1. Bank Transfer (Account: Muhammad Jumma, IBAN: PK41UNIL0109000415148702)
    2. Easypaisa (Account: Muhammad Jumma, Number: 03156045403)
    3. JazzCash (Account: Muhammad Jumma, Number: 03081755403)
    STRICT PROHIBITION: No COD, No Visa/Mastercard.
    Default status: 'Payment Verification Pending' (Never marked Paid until owner verifies).
    """
    # Support both multipart/form-data (for file upload) and json
    if request.is_json:
        data = request.get_json() or {}
        receipt_file = None
    else:
        data = request.form.to_dict()
        receipt_file = request.files.get("receipt_file")

        # Parse items if passed as json string in form-data
        if "items" in data and isinstance(data["items"], str):
            try:
                data["items"] = json.loads(data["items"])
            except Exception:
                data["items"] = []

    payment_method = data.get("payment_method", "").lower().strip()
    transaction_id = data.get("transaction_id", "").strip()
    total_amount = float(data.get("total_amount", 0))
    currency = data.get("currency", "PKR")
    items = data.get("items", [])
    country = data.get("country", "Pakistan")

    if not items:
        return jsonify({"success": False, "error": "Cart is empty. Please add items before checking out."}), 400

    # Handle receipt image upload
    receipt_filename = None
    if receipt_file and receipt_file.filename:
        upload_folder = os.path.join(app.root_path, "static", "uploads", "receipts")
        os.makedirs(upload_folder, exist_ok=True)
        ext = os.path.splitext(receipt_file.filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
            safe_name = f"receipt_{uuid.uuid4().hex[:8]}_{secure_filename(receipt_file.filename)}"
            receipt_path_on_disk = os.path.join(upload_folder, safe_name)
            receipt_file.save(receipt_path_on_disk)
            receipt_filename = f"/static/uploads/receipts/{safe_name}"

    # 1. Execute manual payment verification & validation
    try:
        payment_result = payment_gateway.process_order(
            method=payment_method,
            total_amount=total_amount,
            transaction_id=transaction_id,
            receipt_path=receipt_filename,
            currency=currency
        )
    except PaymentProcessingError as p_err:
        return jsonify({"success": False, "error": str(p_err)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Payment validation error: {str(e)}"}), 500

    # 2. Generate unique order number (e.g. JUM-2026-8349)
    order_num = f"JUM-2026-{random.randint(1000, 9999)}"

    # 3. Submit directly to Shopify Admin API / Staging pipeline
    order_payload = {
        "order_number": order_num,
        "customer_name": data.get("customer_name") or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "customer_email": data.get("customer_email", ""),
        "customer_phone": data.get("customer_phone", ""),
        "country": country,
        "city": data.get("city", ""),
        "state": data.get("state", ""),
        "address": data.get("address", ""),
        "postal_code": data.get("postal_code", ""),
        "delivery_instructions": data.get("delivery_instructions", ""),
        "items": items,
        "total_amount": total_amount,
        "currency": currency,
        "payment_method": payment_result["payment_method"],
        "transaction_id": transaction_id,
        "receipt_path": receipt_filename
    }

    shopify_result = shopify_client.create_shopify_order(order_payload)

    db_payment_status = "Payment Verification Pending"
    tracking_status = "Order Placed - Awaiting Payment Verification"

    # 4. Save to local SQLite database
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO orders (
        order_number, user_id, customer_name, customer_email, customer_phone,
        country, city, state, address, postal_code, delivery_instructions, items_json,
        subtotal, shipping_fee, tax_amount, total_amount, currency,
        payment_method, payment_status, transaction_id, receipt_path,
        shopify_order_id, shopify_sync_status, tracking_status, carrier
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_num,
        session.get("user_id"),
        order_payload["customer_name"],
        order_payload["customer_email"],
        order_payload["customer_phone"],
        order_payload["country"],
        order_payload["city"],
        order_payload["state"],
        order_payload["address"],
        order_payload["postal_code"],
        order_payload["delivery_instructions"],
        json.dumps(items),
        float(data.get("subtotal", 0)),
        float(data.get("shipping_fee", 0)),
        0.0,
        total_amount,
        currency,
        payment_result["payment_method"],
        db_payment_status,
        transaction_id,
        receipt_filename,
        shopify_result.get("shopify_order_id"),
        "Synced with Shopify" if shopify_result.get("success") else "Staging Synchronized",
        tracking_status,
        "Domestic Express Courier" if country == "Pakistan" else "DHL Express Priority"
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "order_number": order_num,
        "transaction_id": transaction_id,
        "payment_method": payment_result["payment_method"],
        "payment_status": db_payment_status,
        "receipt_uploaded": bool(receipt_filename),
        "receipt_path": receipt_filename,
        "instructions": payment_result.get("instructions", ""),
        "total_amount": total_amount,
        "currency": currency,
        "customer_name": order_payload["customer_name"],
        "customer_email": order_payload["customer_email"],
        "customer_phone": order_payload["customer_phone"],
        "delivery_address": f"{order_payload['address']}, {order_payload['city']}, {order_payload['country']}",
        "shopify_status": shopify_result,
        "message": "Order successfully submitted for manual payment verification."
    })

# -------------------------------------------------------------
# BUSINESS OWNER ADMIN ORDER MANAGEMENT
# -------------------------------------------------------------
@app.route("/admin")
@app.route("/admin/orders")
def admin_orders():
    """
    Order Management Dashboard for Business Owner (Muhammad Jumma)
    Allows reviewing all orders, viewing receipts, and updating statuses:
    Pending, Payment Verification Pending, Paid, Failed, Refunded.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders_raw = c.fetchall()
    conn.close()

    orders = []
    for o in orders_raw:
        od = dict(o)
        try:
            od["order_items"] = json.loads(od.get("items_json") or "[]")
        except Exception:
            od["order_items"] = []
        orders.append(od)

    payment_cfg = load_payment_config()

    return render_template(
        "admin_orders.html",
        orders=orders,
        payment_config=payment_cfg,
        valid_statuses=VALID_ORDER_STATUSES
    )

@app.route("/api/admin/orders/<order_number>/status", methods=["POST"])
def api_admin_update_order_status(order_number):
    """Allows business owner to manually update payment status and order fulfillment"""
    data = request.get_json() or {}
    new_status = data.get("status", "").strip()
    tracking_status = data.get("tracking_status", "").strip()

    if new_status not in VALID_ORDER_STATUSES:
        return jsonify({"success": False, "error": f"Invalid status. Must be one of: {VALID_ORDER_STATUSES}"}), 400

    try:
        if not tracking_status:
            if new_status == "Paid":
                tracking_status = "Payment Verified & Order in Production"
            elif new_status == "Payment Verification Pending":
                tracking_status = "Awaiting Owner Payment Verification"
            elif new_status == "Failed":
                tracking_status = "Payment Verification Failed"
            elif new_status == "Refunded":
                tracking_status = "Payment Refunded"
            else:
                tracking_status = "Order Pending"

        update_order_status(order_number, new_status, tracking_status)
        return jsonify({
            "success": True,
            "order_number": order_number,
            "new_status": new_status,
            "tracking_status": tracking_status,
            "message": f"Order {order_number} status updated to {new_status}."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/admin/payment-config", methods=["POST"])
def api_admin_update_payment_config():
    """Allows business owner to edit Bank, Easypaisa, and JazzCash account details"""
    data = request.get_json() or {}
    current = load_payment_config()

    for method in ["bank_transfer", "easypaisa", "jazzcash"]:
        if method in data:
            current[method].update(data[method])

    if save_payment_config(current):
        return jsonify({"success": True, "message": "Payment account details updated successfully.", "config": current})
    return jsonify({"success": False, "error": "Failed to save configuration."}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Jumma Couture by Noman Store on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

