import os
import shutil
import zipfile
import sys

BASE_DIR = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce"
DIST_DIR = os.path.join(BASE_DIR, "dist")
ZIP_PATH = os.path.join(BASE_DIR, "googiehost-public_html.zip")

sys.path.append(BASE_DIR)

def build():
    print("==================================================", flush=True)
    print("GENERATING PRODUCTION BUILD FOR GOOGIEHOST", flush=True)
    print("==================================================", flush=True)

    import app
    from shopify_client import shopify_client

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)
    client = app.app.test_client()

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

    print(f"1. Pre-rendering {len(routes)} pages to static HTML...", flush=True)
    for route, dest_rel in routes:
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
            print(f"  Rendered {route} -> {dest_rel}", flush=True)

    print("2. Copying static assets (css, js, images)...", flush=True)
    static_src = os.path.join(BASE_DIR, "static")
    static_dst = os.path.join(DIST_DIR, "static")
    shutil.copytree(static_src, static_dst, dirs_exist_ok=True)

    for sub in ["css", "js", "images"]:
        src_sub = os.path.join(static_src, sub)
        dst_sub = os.path.join(DIST_DIR, sub)
        if os.path.exists(src_sub):
            shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)

    print("3. Creating .htaccess for clean URLs...", flush=True)
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

    print("4. Creating PHP API Checkout fallback for shared hosting...", flush=True)
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

$input = file_get_contents('php://input');
$data = json_decode($input, true);
if (!$data && !empty($_POST)) {
    $data = $_POST;
}

$payment_method = isset($data['payment_method']) ? strtolower(trim($data['payment_method'])) : 'bank_transfer';
$transaction_id = isset($data['transaction_id']) ? trim($data['transaction_id']) : '';

// Strict rejection of COD or card payments
if ($payment_method === 'cod' || strpos($payment_method, 'delivery') !== false) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Cash on Delivery (COD) is strictly not supported.']);
    exit;
}

if (strpos($payment_method, 'visa') !== false || strpos($payment_method, 'mastercard') !== false) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Card payments are not supported. Please choose Bank Transfer, Easypaisa, or JazzCash.']);
    exit;
}

$order_number = 'JUM-2026-' . rand(1000, 9999);

$method_names = [
    'bank_transfer' => 'Bank Transfer (UBL)',
    'easypaisa' => 'Easypaisa Mobile Wallet',
    'jazzcash' => 'JazzCash Mobile Account'
];

$method_label = isset($method_names[$payment_method]) ? $method_names[$payment_method] : 'Bank Transfer';

$payment_status = 'Payment Verification Pending';
$instructions = 'Your order and payment reference have been received. Our concierge team will manually verify the funds in our business account before order dispatch.';

$response = [
    'success' => true,
    'order_number' => $order_number,
    'payment_method' => $method_label,
    'payment_status' => $payment_status,
    'transaction_id' => $transaction_id,
    'instructions' => $instructions,
    'total_amount' => isset($data['total_amount']) ? floatval($data['total_amount']) : 0,
    'currency' => isset($data['currency']) ? $data['currency'] : 'PKR',
    'customer_name' => isset($data['customer_name']) ? $data['customer_name'] : ((isset($data['first_name']) ? $data['first_name'] : '') . ' ' . (isset($data['last_name']) ? $data['last_name'] : '')),
    'customer_phone' => isset($data['customer_phone']) ? $data['customer_phone'] : '',
    'delivery_address' => (isset($data['address']) ? $data['address'] : '') . ', ' . (isset($data['city']) ? $data['city'] : '') . ', Pakistan',
    'timestamp' => date('c'),
    'message' => 'Order submitted successfully for manual verification.'
];

// Save order to orders.json for shared hosting log
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

    print("5. Packaging ready-to-upload ZIP for DirectAdmin File Manager...", flush=True)
    if os.path.exists(ZIP_PATH):
        try:
            os.remove(ZIP_PATH)
        except Exception:
            pass

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zipf.write(full_path, rel_path)

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"Generated: {ZIP_PATH} ({zip_size_mb:.2f} MB)", flush=True)
    print("BUILD COMPLETE!", flush=True)

if __name__ == "__main__":
    build()
