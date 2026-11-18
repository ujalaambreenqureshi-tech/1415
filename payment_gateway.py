"""
Manual Payment Gateway Engine for Jumma Couture By Noman Store
STRICT REQUIREMENT: ONLY 3 PAYMENT METHODS:
1. Bank Transfer
2. Easypaisa
3. JazzCash

STRICT PROHIBITION:
- NO Cash on Delivery (COD) anywhere.
- NO Visa or Mastercard payment claims.
- NO fake automated verification.
- Manual verification by business owner required for all orders.
"""
import os
import json
import logging

logger = logging.getLogger("ManualPaymentGateway")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payment_config.json")

DEFAULT_CONFIG = {
    "bank_transfer": {
        "enabled": True,
        "title": "Bank Transfer",
        "account_holder": "Muhammad Jumma",
        "iban": "PK41UNIL0109000415148702",
        "bank_name": "United Bank Limited (UBL)",
        "instructions": "Transfer the total order amount to our official business bank account. After payment, enter your Transaction ID (TID) below and upload your payment screenshot/receipt. Your order will be manually verified by our team before confirmation."
    },
    "easypaisa": {
        "enabled": True,
        "title": "Easypaisa",
        "account_holder": "Muhammad Jumma",
        "account_number": "03156045403",
        "instructions": "Send the total amount to our Easypaisa wallet via your Easypaisa Mobile App or OTC agent. Enter the 3737 SMS Transaction ID (TID) below and upload your payment screenshot. Our team will manually verify the payment to confirm your order."
    },
    "jazzcash": {
        "enabled": True,
        "title": "JazzCash",
        "account_holder": "Muhammad Jumma",
        "account_number": "03081755403",
        "instructions": "Send the total amount to our JazzCash account via your JazzCash App or retailer. Enter the 8558 SMS Transaction ID (TID) below and upload your payment screenshot. Payment will be manually verified by our team prior to order fulfillment."
    }
}


def load_payment_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading payment config: {e}")
    return DEFAULT_CONFIG


def save_payment_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving payment config: {e}")
        return False


class PaymentProcessingError(Exception):
    pass


class ManualPaymentGateway:
    ALLOWED_METHODS = ["bank_transfer", "easypaisa", "jazzcash"]

    def __init__(self):
        self.config = load_payment_config()

    def get_supported_methods(self):
        """Returns ONLY the 3 allowed manual payment options with current owner settings"""
        cfg = load_payment_config()
        return [
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "title": cfg.get("bank_transfer", {}).get("title", "Bank Transfer"),
                "account_holder": cfg.get("bank_transfer", {}).get("account_holder", "Muhammad Jumma"),
                "iban": cfg.get("bank_transfer", {}).get("iban", "PK41UNIL0109000415148702"),
                "bank_name": cfg.get("bank_transfer", {}).get("bank_name", "United Bank Limited (UBL)"),
                "instructions": cfg.get("bank_transfer", {}).get("instructions", ""),
                "badge": "Manual Verification Required",
                "icon": "🏦"
            },
            {
                "id": "easypaisa",
                "name": "Easypaisa",
                "title": cfg.get("easypaisa", {}).get("title", "Easypaisa Mobile Wallet"),
                "account_holder": cfg.get("easypaisa", {}).get("account_holder", "Muhammad Jumma"),
                "account_number": cfg.get("easypaisa", {}).get("account_number", "03156045403"),
                "instructions": cfg.get("easypaisa", {}).get("instructions", ""),
                "badge": "Manual Verification Required",
                "icon": "📱"
            },
            {
                "id": "jazzcash",
                "name": "JazzCash",
                "title": cfg.get("jazzcash", {}).get("title", "JazzCash Mobile Account"),
                "account_holder": cfg.get("jazzcash", {}).get("account_holder", "Muhammad Jumma"),
                "account_number": cfg.get("jazzcash", {}).get("account_number", "03081755403"),
                "instructions": cfg.get("jazzcash", {}).get("instructions", ""),
                "badge": "Manual Verification Required",
                "icon": "📱"
            }
        ]

    def validate_payment(self, method: str, total_amount: float, transaction_id: str, receipt_provided: bool = False):
        """Strict validation of manual payment details"""
        m = method.strip().lower()

        # Strict rejection of forbidden methods
        if m in ["cod", "cash_on_delivery", "cash on delivery"] or "delivery" in m:
            raise PaymentProcessingError("Cash on Delivery (COD) is strictly not supported by Jumma Couture by Noman.")

        if "visa" in m or "mastercard" in m or "card" in m:
            raise PaymentProcessingError("Direct card charging is not supported. Please select Bank Transfer, Easypaisa, or JazzCash.")

        if m not in self.ALLOWED_METHODS:
            raise PaymentProcessingError(f"Unsupported payment method. Please choose Bank Transfer, Easypaisa, or JazzCash.")

        if total_amount <= 0:
            raise PaymentProcessingError("Order total must be greater than zero.")

        if not transaction_id or len(transaction_id.strip()) < 4:
            raise PaymentProcessingError("Please provide your valid Transaction ID (TID / Reference Number) from your payment SMS or app.")

        return True

    def process_order(self, method: str, total_amount: float, transaction_id: str, receipt_path: str = None, currency: str = "PKR"):
        """
        Registers manual payment order.
        Orders are ALWAYS registered with status 'Payment Verification Pending'.
        Never marks orders as 'Paid' automatically.
        """
        self.validate_payment(method, total_amount, transaction_id, bool(receipt_path))
        cfg = load_payment_config()
        method_meta = cfg.get(method, {})
        method_title = method_meta.get("title", method.replace("_", " ").title())

        return {
            "status": "Payment Verification Pending",
            "payment_status": "Payment Verification Pending",
            "payment_method": method_title,
            "method_key": method,
            "transaction_id": transaction_id.strip(),
            "receipt_path": receipt_path,
            "amount": total_amount,
            "currency": currency,
            "instructions": "Your payment reference and receipt have been received. Our concierge team will manually verify the funds in our business account before confirming order dispatch."
        }


# Singleton instance
manual_payment_gateway = ManualPaymentGateway()
payment_gateway = manual_payment_gateway
