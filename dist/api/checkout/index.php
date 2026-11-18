<?php
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
