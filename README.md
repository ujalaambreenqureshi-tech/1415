# Heritage — Ethnic Luxury E-Commerce Website

Complete, high-fashion worldwide e-commerce storefront integrated with Shopify. Tailored for patrons across Pakistan, United States, United Kingdom, Canada, UAE, Saudi Arabia, Australia, Europe, and global luxury markets.

---

## 🌟 Live Local Staging URL
**http://127.0.0.1:5000**

---

## 🎨 Visual Identity & Architecture (Matching Uploaded Design)
- **Brand Aesthetic:** Royal Maroon (`#4A0E17`), Antique Gold (`#C5A059`), Warm Cream / Ivory (`#FAF7F2`), Serif Headlines (*Playfair Display / Cinzel*).
- **Exact Layout Replicated from Reference:**
  1. Top Announcement Strip with Currency Switcher (PKR, USD, GBP, EUR, AED, SAR, CAD, AUD)
  2. Luxury Header with "Heritage ETHNIC LUXURY", Search Drawer, Wishlist Counter, Slide-out Bag
  3. Hero Banner: *"Timeless Traditions — Curated ethnic wear that celebrates your heritage"*
  4. Strict Advance Trust Strip (100% Advance Secure Checkout, Worldwide Express, Authentic Certified Quality, VIP Concierge)
  5. Shop by Occasion: Circular swatches with gold rims (Wedding, Festive, Party, Mehendi, Everyday, Accessories)
  6. Artisan Spotlight: *"Handcrafted by Jumma Couture By Noman — Meet Our Artisans"*
  7. Curated Collections: Tabs (*Best Sellers, New Arrivals, Ethnic Sets, Premium Edit*) with live color swatches
  8. Jewelry Collection Showcase
  9. *"Style It Your Way"* Lookbook Bundle Builder with 1-click bundle checkout
  10. Promotional Offers Banner (*Seasonal Flat 20%, Festive Extra 10% Code: FESTIVE10, New Patron 15%*)
  11. Footer with strictly authorized payment logos: **Visa, Mastercard, JazzCash, Easypaisa**

---

## 💳 STRICT PAYMENT POLICY — 100% FULL ADVANCE ONLY
- **Permitted Gateways (Only These Four):**
  1. **Visa** (3D-Secure 2.0 Tokenized Credit/Debit)
  2. **Mastercard** (Mastercard Identity Check Credit/Debit)
  3. **JazzCash** (Official Merchant Mobile Account & Instant Voucher)
  4. **Easypaisa** (Official Merchant Mobile Wallet & Tokenized Payment)
- **Strictly Blocked / Prohibited:**
  - Cash on Delivery (COD) is permanently disallowed
  - Partial payments and installments are blocked
  - PayPal, Apple Pay, Google Pay, Meezan Bank, UBL are removed

---

## 🌐 Complete 19 Pages Built & Connected
1. `GET /` — Home Page
2. `GET /shop` — All Products Catalog with category, occasion, price sorting
3. `GET /product/<slug>` — Product Details with interactive color swatches, size picker, live photo switching, quantity, "Add to Bag", and "Buy Now"
4. `GET /categories` — Occasions & Silhouettes Showcase
5. `GET /search` — Search Results
6. `GET /cart` — Shopping Bag & Price Breakdown
7. `GET /checkout` — 100% Advance Payment Checkout with international country selection
8. `GET/POST /login` & `/register` — Customer Authentication
9. `GET /account` — Customer VIP Dashboard
10. `GET /account/orders` — Orders History
11. `GET /track-order` — Real-Time Order Tracking & Shopify Sync Status
12. `GET /wishlist` — Wishlist with "Move to Bag"
13. `GET /about` — Brand Story & Artisan Heritage
14. `GET/POST /contact` — Customer Concierge Support
15. `GET /faq` — Detailed FAQ (100% Advance Payment, Shipping, Sizing)
16. `GET /policies/shipping` — Worldwide Shipping Policy
17. `GET /policies/returns` — Return & Refund Policy (7 Days)
18. `GET /policies/privacy` — Privacy & PCI-DSS Compliance
19. `GET /policies/terms` — Terms of Service

---

## 📁 Project Folder Structure
```
heritage-ecommerce/
│── app.py                    # Main Flask application & 19 routes + APIs
│── shopify_client.py         # Official Storefront & Admin API integration client
│── payment_gateway.py        # Strict 100% advance payment engine (Visa, MC, JazzCash, Easypaisa)
│── database.py               # SQLite database (Users, Orders, Reviews, Wishlist)
│── generate_assets.py        # Automated PIL asset generator for luxury color variants
│── heritage.db               # SQLite database file
│── .env.example              # Template for API keys & secrets
│── static/
│   ├── css/
│   │   └── style.css         # Master luxury CSS stylesheet
│   ├── js/
│   │   └── main.js           # Interactive client engine (color switcher, cart, currency)
│   └── images/               # Branded product photos, variants, banners & payment logos
└── templates/
    ├── base.html             # Common luxury layout, header, footer & cart drawer
    ├── index.html            # Exact uploaded design recreation
    ├── shop.html             # Catalog & filters
    ├── product.html          # PDP with color swatches & image switcher
    ├── categories.html       # Occasions
    ├── search.html           # Live search
    ├── cart.html             # Shopping bag
    ├── checkout.html         # 100% advance checkout
    ├── login.html            # Sign in
    ├── register.html         # Registration
    ├── dashboard.html        # Customer dashboard
    ├── orders.html           # My orders
    ├── track_order.html      # Order tracking with progress bar
    ├── wishlist.html         # Wishlist
    ├── about.html            # Brand story
    ├── contact.html          # Contact concierge
    ├── faq.html              # FAQ
    └── policies/
        ├── shipping.html     # Worldwide shipping policy
        ├── returns.html      # Return policy
        ├── privacy.html      # Privacy policy
        └── terms.html        # Terms & conditions
```

