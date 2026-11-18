import os
import shutil
import zipfile
import sys
import traceback
import time

BASE_DIR = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce"
DIST_DIR = os.path.join(BASE_DIR, "dist")
ZIP_PATH = os.path.join(BASE_DIR, "googiehost-public_html.zip")

sys.path.append(BASE_DIR)

def run_build():
    t0 = time.time()
    print(">>> 1. Importing Flask app...", flush=True)
    import app
    from shopify_client import shopify_client
    client = app.app.test_client()

    print(">>> 2. Preparing dist directory...", flush=True)
    os.makedirs(DIST_DIR, exist_ok=True)

    routes = [
        ("/", "index.html"),
        ("/about", "about.html"),
        ("/cart", "cart.html"),
        ("/checkout", "checkout.html"),
        ("/categories", "categories.html"),
        ("/contact", "contact.html"),
        ("/faq", "faq.html"),
        ("/login", "login.html"),
        ("/register", "register.html"),
        ("/account", "account.html"),
        ("/track-order", "track-order.html"),
        ("/wishlist", "wishlist.html"),
        ("/shop", "shop.html"),
        ("/bridal", "bridal.html"),
        ("/party", "party.html"),
        ("/policies/privacy", "policies/privacy.html"),
        ("/policies/returns", "policies/returns.html"),
        ("/policies/shipping", "policies/shipping.html"),
        ("/policies/terms", "policies/terms.html"),
        ("/admin/orders", "admin/orders.html"),
    ]

    products = shopify_client.fetch_products()
    for p in products:
        slug = p["slug"]
        routes.append((f"/product/{slug}", f"product/{slug}.html"))

    filtered_shops = [
        ("/shop?occasion=Party", "shop/party.html"),
        ("/shop?occasion=Bridal", "shop/bridal.html"),
        ("/shop?category=Lehengas", "shop/lehengas.html"),
        ("/shop?category=Sarees", "shop/sarees.html"),
        ("/shop?category=Kurtas", "shop/kurtas.html"),
        ("/shop?category=Accessories", "shop/accessories.html"),
    ]
    routes.extend(filtered_shops)

    print(f">>> 3. Pre-rendering {len(routes)} pages...", flush=True)
    rendered_count = 0
    for route, dest_rel in routes:
        try:
            resp = client.get(route)
            if resp.status_code in [200, 302]:
                if resp.status_code == 302:
                    target = resp.headers.get("Location")
                    resp = client.get(target)

                html = resp.data.decode("utf-8")
                dest_file = os.path.join(DIST_DIR, dest_rel)
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                with open(dest_file, "w", encoding="utf-8") as f:
                    f.write(html)

                base_name, ext = os.path.splitext(dest_rel)
                if base_name != "index":
                    index_dest = os.path.join(DIST_DIR, base_name, "index.html")
                    os.makedirs(os.path.dirname(index_dest), exist_ok=True)
                    with open(index_dest, "w", encoding="utf-8") as f:
                        f.write(html)
                rendered_count += 1
        except Exception as e:
            print(f"Error rendering {route}: {e}", flush=True)

    print(f"Rendered {rendered_count} pages successfully.", flush=True)

    print(">>> 4. Copying static assets (css, js, images)...", flush=True)
    static_src = os.path.join(BASE_DIR, "static")
    static_dst = os.path.join(DIST_DIR, "static")
    shutil.copytree(static_src, static_dst, dirs_exist_ok=True)

    for sub in ["css", "js", "images"]:
        src_sub = os.path.join(static_src, sub)
        dst_sub = os.path.join(DIST_DIR, sub)
        if os.path.exists(src_sub):
            shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)

    print(">>> 5. Writing .htaccess...", flush=True)
    htaccess_content = r"""# GoogieHost / Apache Configuration
RewriteEngine On
RewriteBase /

# Explicit API Checkout routing to PHP handler
RewriteRule ^api/checkout/?$ api/checkout/index.php [L,QSA]

# Remove .html extension
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^([^.]+)$ $1.html [NC,L]

# Custom Error Document
ErrorDocument 404 /index.html
"""
    with open(os.path.join(DIST_DIR, ".htaccess"), "w", encoding="utf-8") as f:
        f.write(htaccess_content)

    print(">>> 6. Writing PHP API handler...", flush=True)
    api_dir = os.path.join(DIST_DIR, "api", "checkout")
    os.makedirs(api_dir, exist_ok=True)
    php_api_content = """<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$data = $_POST;
if (empty($data)) {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true) ?: [];
}

$method = isset($data['payment_method']) ? strtolower(trim($data['payment_method'])) : 'bank_transfer';
$tid = isset($data['transaction_id']) ? trim($data['transaction_id']) : '';

$accounts = [
    'bank_transfer' => [
        'title' => 'Bank Transfer (UBL)',
        'holder' => 'Muhammad Jumma',
        'account' => 'PK41UNIL0109000415148702',
        'instructions' => 'Transfer to Muhammad Jumma (IBAN: PK41UNIL0109000415148702). Verification within 2 hours.'
    ],
    'easypaisa' => [
        'title' => 'Easypaisa Mobile Wallet',
        'holder' => 'Muhammad Jumma',
        'account' => '03156045403',
        'instructions' => 'Send via Easypaisa App to Muhammad Jumma (03156045403). Enter 11-digit TID.'
    ],
    'jazzcash' => [
        'title' => 'JazzCash Mobile Wallet',
        'holder' => 'Muhammad Jumma',
        'account' => '03081755403',
        'instructions' => 'Send via JazzCash App to Muhammad Jumma (03081755403). Enter TID.'
    ]
];

$chosen = isset($accounts[$method]) ? $accounts[$method] : $accounts['bank_transfer'];
$order_number = 'JUM-2026-' . rand(1000, 9999);

$receipt_url = null;
if (isset($_FILES['receipt_file']) && $_FILES['receipt_file']['error'] === UPLOAD_ERR_OK) {
    $uploads_dir = __DIR__ . '/uploads';
    if (!file_exists($uploads_dir)) {
        @mkdir($uploads_dir, 0755, true);
    }
    $ext = pathinfo($_FILES['receipt_file']['name'], PATHINFO_EXTENSION);
    $fname = 'receipt_' . $order_number . '_' . time() . '.' . $ext;
    $target = $uploads_dir . '/' . $fname;
    if (@move_uploaded_file($_FILES['receipt_file']['tmp_name'], $target)) {
        $receipt_url = '/api/checkout/uploads/' . $fname;
    }
}

$response = [
    'success' => true,
    'order_number' => $order_number,
    'payment_status' => 'Payment Verification Pending',
    'tracking_status' => 'Awaiting Manual Payment Verification',
    'payment_method' => $chosen['title'],
    'transaction_id' => $tid,
    'receipt_url' => $receipt_url,
    'account_holder' => $chosen['holder'],
    'account_number' => $chosen['account'],
    'instructions' => $chosen['instructions'],
    'total_amount' => isset($data['total_amount']) ? floatval($data['total_amount']) : 0,
    'currency' => isset($data['currency']) ? $data['currency'] : 'PKR',
    'customer_name' => isset($data['customer_name']) ? $data['customer_name'] : '',
    'customer_phone' => isset($data['customer_phone']) ? $data['customer_phone'] : '',
    'delivery_address' => (isset($data['address']) ? $data['address'] : '') . ', ' . (isset($data['city']) ? $data['city'] : '') . ', Pakistan',
    'timestamp' => date('c'),
    'message' => 'Order submitted successfully. Your manual payment is queued for verification.'
];

$orders_file = __DIR__ . '/orders.json';
$existing_orders = [];
if (file_exists($orders_file)) {
    $existing_orders = json_decode(file_get_contents($orders_file), true) ?: [];
}
$existing_orders[] = $response;
@file_put_contents($orders_file, json_encode($existing_orders, JSON_PRETTY_PRINT));

echo json_encode($response);
?>
"""
    with open(os.path.join(api_dir, "index.php"), "w", encoding="utf-8") as f:
        f.write(php_api_content)

    print(">>> 7. Creating googiehost-public_html.zip...", flush=True)
    temp_zip = ZIP_PATH + ".tmp"
    if os.path.exists(temp_zip):
        os.remove(temp_zip)

    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zipf.write(full_path, rel_path)

    if os.path.exists(ZIP_PATH):
        try:
            os.remove(ZIP_PATH)
        except Exception:
            pass
    shutil.move(temp_zip, ZIP_PATH)

    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    dt = time.time() - t0
    print(f"\n==========================================", flush=True)
    print(f"PRODUCTION BUILD SUCCESSFUL in {dt:.1f}s!", flush=True)
    print(f"Package: {ZIP_PATH} ({size_mb:.2f} MB)", flush=True)
    print(f"==========================================", flush=True)

if __name__ == "__main__":
    try:
        run_build()
    except Exception as e:
        traceback.print_exc()
