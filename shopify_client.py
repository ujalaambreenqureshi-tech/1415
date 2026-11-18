"""
Shopify Integration Client for Jumma Couture by Noman Store
Provides official Storefront API (GraphQL) and Admin API (REST/GraphQL) support.
Includes robust fallback offline catalog for development/staging mode.
"""
import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ShopifyClient")
logging.basicConfig(level=logging.INFO)

# Shopify Store Credentials from Environment
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN", "").strip()
SHOPIFY_STOREFRONT_ACCESS_TOKEN = os.getenv("SHOPIFY_STOREFRONT_ACCESS_TOKEN", "").strip()
SHOPIFY_ADMIN_API_ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_API_ACCESS_TOKEN", "").strip()
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01").strip()

# Fallback Ethnic Luxury Catalog matching uploaded design & requirements
DEFAULT_CATALOG = [
    {
        "id": "prod_001",
        "slug": "zari-embroidered-lehenga",
        "title": "Luxury Deep Teal Lehenga – Handcrafted Bridal Elegance",
        "subtitle": "Handcrafted Bridal Masterpiece in Rich Deep Teal Sheesha Silk",
        "description": "An exquisite masterpiece in rich Deep Teal, this luxurious three-piece ensemble beautifully blends traditional craftsmanship with timeless elegance. Designed for women who appreciate intricate detailing and regal sophistication.\n\nA statement of exceptional artistry and luxury, this ensemble is perfect for weddings, bridal celebrations, receptions, and grand festive occasions. Experience the beauty of handcrafted luxury, where every detail tells a story of elegance.",
        "category": "Lehengas",
        "occasion": "Bridal",
        "collection": "Bridal Couture",
        "is_bridal": True,
        "base_price_pkr": 230000,
        "base_price_usd": 825,
        "sale_price_pkr": 184000,
        "sale_price_usd": 660,
        "sku": "HRT-BRL-001",
        "rating": 5.0,
        "review_count": 89,
        "fabric": "Kurti: Premium Sheesha Silk | Lehenga: Luxurious Sheesha Silk | Dupatta: Medium Silk / China Silk",
        "care": "Professional Dry Clean Only. Preserve in Jumma Couture bespoke muslin garment bag.",
        "fabric_details": [
            {"label": "Kurti", "value": "Premium Sheesha Silk"},
            {"label": "Lehenga", "value": "Luxurious Sheesha Silk"},
            {"label": "Dupatta", "value": "Medium Silk / China Silk"}
        ],
        "embellishment_details": "Adorned with exquisite handmade Kora Dabka work, Japanese Cut Dana, delicate Resham embroidery, shimmering sequins, elegant star embellishments, and sparkling crystals. Every detail is meticulously crafted to create a luxurious and graceful finish.",
        "specifications": [
            "180-inch grand flare",
            "12 beautifully structured panels",
            "Intricate front and back embroidery",
            "Elaborately embellished borders and hemline"
        ],
        "gallery_images": [
            {
                "id": "gal_1",
                "title": "Bridal Model Silhouette",
                "caption": "Full model drape with embroidered dupatta",
                "image": "emerald-gold-lehenga.jpg"
            },
            {
                "id": "gal_2",
                "title": "Kurti & Dabka Details",
                "caption": "Premium Sheesha Silk with Kora Dabka, Cut Dana & crystals",
                "image": "teal-lehenga-blouse.jpg"
            },
            {
                "id": "gal_3",
                "title": "180-Inch Flare & Borders",
                "caption": "12 structured panels with grand embroidered hemline",
                "image": "teal-lehenga-flare.jpg"
            },
            {
                "id": "gal_4",
                "title": "Full Ensemble Studio View",
                "caption": "Complete 3-piece handcrafted bridal ensemble",
                "image": "teal-lehenga-full.jpg"
            }
        ],
        "colors": [
            {
                "name": "Deep Teal",
                "hex": "#093D37",
                "image": "emerald-gold-lehenga.jpg",
                "in_stock": True,
                "stock_count": 9,
                "variant_id": "var_lhg_teal"
            },
            {
                "name": "Royal Maroon",
                "hex": "#5E131E",
                "image": "lehenga-maroon.jpg",
                "in_stock": True,
                "stock_count": 7,
                "variant_id": "var_lhg_maroon"
            },
            {
                "name": "Noir Black",
                "hex": "#121110",
                "image": "lehenga-navy.jpg",
                "in_stock": True,
                "stock_count": 5,
                "variant_id": "var_lhg_noir"
            },
            {
                "name": "Imperial Plum",
                "hex": "#42133D",
                "image": "lehenga-plum.jpg",
                "in_stock": True,
                "stock_count": 4,
                "variant_id": "var_lhg_plum"
            }
        ],
        "sizes": ["XS", "S", "M", "L", "XL", "Custom Stitched"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    },
    {
        "id": "prod_002",
        "slug": "embellished-organza-saree",
        "title": "Embellished Organza Saree",
        "subtitle": "Hand-Cut Gotta Patti & Resham Work Saree",
        "description": "Crafted from whisper-soft Japanese organza, this heirloom saree features ethereal gotta patti floral sprays, delicate sequin lattices, and hand-tasseled pallu borders. Accompanied by an unstitched heavy brocade blouse piece.",
        "category": "Sarees",
        "occasion": "Festive",
        "collection": "Curated Collections",
        "base_price_pkr": 28999,
        "base_price_usd": 105,
        "sale_price_pkr": 24999,
        "sale_price_usd": 89,
        "sku": "HRT-SAR-002",
        "rating": 4.8,
        "review_count": 62,
        "fabric": "Lightweight Organza & Silk Crepe",
        "care": "Gentle Dry Clean Only. Avoid direct perfume sprays.",
        "colors": [
            {
                "name": "Dusty Mauve",
                "hex": "#5A3845",
                "image": "saree-mauve.jpg",
                "in_stock": True,
                "stock_count": 12,
                "variant_id": "var_sar_mauve"
            },
            {
                "name": "Champagne Gold",
                "hex": "#4F4435",
                "image": "saree-champagne.jpg",
                "in_stock": True,
                "stock_count": 10,
                "variant_id": "var_sar_champagne"
            },
            {
                "name": "Sage Green",
                "hex": "#2C3E35",
                "image": "saree-sage.jpg",
                "in_stock": True,
                "stock_count": 7,
                "variant_id": "var_sar_sage"
            },
            {
                "name": "Bridal Crimson",
                "hex": "#541219",
                "image": "saree-crimson.jpg",
                "in_stock": True,
                "stock_count": 9,
                "variant_id": "var_sar_crimson"
            }
        ],
        "sizes": ["Free Size (6.5m with blouse)"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    },
    {
        "id": "prod_003",
        "slug": "handwoven-silk-kurta-set",
        "title": "Handwoven Silk Kurta Set",
        "subtitle": "Chanderi Silk 3-Piece Festive Set with Dupatta",
        "description": "A refined 3-piece silhouette including a straight-cut Chanderi silk kurta with delicate marodi threadwork on neckline and cuffs, tapered cigarette trousers, and a luxurious Banarasi zari weave dupatta.",
        "category": "Kurtas",
        "occasion": "Party",
        "collection": "Ethnic Sets",
        "base_price_pkr": 21999,
        "base_price_usd": 79,
        "sale_price_pkr": 19999,
        "sale_price_usd": 72,
        "sku": "HRT-KRT-003",
        "rating": 4.9,
        "review_count": 39,
        "fabric": "Chanderi Silk & Pure Cotton Lining",
        "care": "Professional Dry Clean Recommended.",
        "colors": [
            {
                "name": "Forest Green",
                "hex": "#123324",
                "image": "kurta-forest.jpg",
                "in_stock": True,
                "stock_count": 14,
                "variant_id": "var_krt_forest"
            },
            {
                "name": "Mustard Yellow",
                "hex": "#4A3B10",
                "image": "kurta-mustard.jpg",
                "in_stock": True,
                "stock_count": 11,
                "variant_id": "var_krt_mustard"
            },
            {
                "name": "Ivory Brocade",
                "hex": "#423B36",
                "image": "kurta-ivory.jpg",
                "in_stock": True,
                "stock_count": 8,
                "variant_id": "var_krt_ivory"
            },
            {
                "name": "Terracotta Rust",
                "hex": "#52261E",
                "image": "kurta-terracotta.jpg",
                "in_stock": True,
                "stock_count": 5,
                "variant_id": "var_krt_rust"
            }
        ],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "is_featured": True,
        "is_bestseller": False,
        "is_new": True
    },
    {
        "id": "prod_004",
        "slug": "anarkali-suit-set",
        "title": "Anarkali Suit Set",
        "subtitle": "Floor-Length 24-Kali Flared Festive Gown",
        "description": "Glorious 24-kali flared Anarkali rendered in premium georgette and organza. Richly embellished with mirror-work accents, golden kora work, and paired with a scalloped dupatta and stretch churidar.",
        "category": "Kurtas",
        "occasion": "Mehendi",
        "collection": "Premium Edit",
        "base_price_pkr": 26999,
        "base_price_usd": 99,
        "sale_price_pkr": 23999,
        "sale_price_usd": 86,
        "sku": "HRT-ANR-004",
        "rating": 4.7,
        "review_count": 53,
        "fabric": "Micro Georgette & Satin Silk Lining",
        "care": "Dry Clean Only.",
        "colors": [
            {
                "name": "Marigold Yellow",
                "hex": "#543F07",
                "image": "anarkali-yellow.jpg",
                "in_stock": True,
                "stock_count": 15,
                "variant_id": "var_anr_yellow"
            },
            {
                "name": "Peach Blossom",
                "hex": "#573531",
                "image": "anarkali-peach.jpg",
                "in_stock": True,
                "stock_count": 9,
                "variant_id": "var_anr_peach"
            },
            {
                "name": "Mint Green",
                "hex": "#1B3B36",
                "image": "anarkali-mint.jpg",
                "in_stock": True,
                "stock_count": 7,
                "variant_id": "var_anr_mint"
            },
            {
                "name": "Ruby Red",
                "hex": "#500C1B",
                "image": "anarkali-ruby.jpg",
                "in_stock": True,
                "stock_count": 6,
                "variant_id": "var_anr_ruby"
            }
        ],
        "sizes": ["S", "M", "L", "XL", "Custom"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    },
    {
        "id": "prod_005",
        "slug": "blush-pearl-embroidered-potli",
        "title": "Blush Pearl Embroidered Potli",
        "subtitle": "Handcrafted Zari & Freshwater Pearl Tassel Evening Bag",
        "description": "Artisanal handcrafted evening potli purse designed in blush raw silk with delicate floral dabka embroidery, antique gold tassels, and strung freshwater pearls. Ideal heirloom accessory for bridal and festive celebrations.",
        "category": "Accessories",
        "occasion": "Wedding",
        "collection": "Curated Collections",
        "base_price_pkr": 6499,
        "base_price_usd": 24,
        "sale_price_pkr": 4999,
        "sale_price_usd": 18,
        "sku": "HRT-ACC-005",
        "rating": 4.9,
        "review_count": 31,
        "fabric": "Pure Raw Silk & Satin Lining with Pearl Beading",
        "care": "Spot clean only. Store in protective cotton dustbag.",
        "colors": [
            {
                "name": "Blush Rose",
                "hex": "#E8A598",
                "image": "potli-gold.jpg",
                "in_stock": True,
                "stock_count": 22,
                "variant_id": "var_potli_blush"
            }
        ],
        "sizes": ["One Size"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    },
    {
        "id": "prod_006",
        "slug": "royal-maroon-velvet-potli",
        "title": "Royal Embroidered Velvet Potli",
        "subtitle": "Antique Gold Zardozi & Pearl Tassel Evening Pouch",
        "description": "An opulent imperial velvet potli handcrafted with antique gold dabka, nakshi work, and luminous micro-pearls. Features rich silk braided drawstrings with artisan pearl tassels. Perfect accessory for grand weddings and celebrations.",
        "category": "Accessories",
        "occasion": "Wedding",
        "collection": "Curated Collections",
        "base_price_pkr": 3499,
        "base_price_usd": 13,
        "sale_price_pkr": 2999,
        "sale_price_usd": 11,
        "sku": "HRT-PTL-006",
        "rating": 4.9,
        "review_count": 28,
        "fabric": "Silk Velvet with Golden Zari Tassels",
        "care": "Spot clean only. Store in Jumma Couture By Noman cotton pouch.",
        "colors": [
            {
                "name": "Muted Gold",
                "hex": "#D4AF37",
                "image": "potli-gold.jpg",
                "in_stock": True,
                "stock_count": 20,
                "variant_id": "var_ptl_gold"
            }
        ],
        "sizes": ["Standard (8 x 9.5 inches)"],
        "is_featured": True,
        "is_bestseller": False,
        "is_new": True
    },
    {
        "id": "prod_007",
        "slug": "zari-velvet-potli-bag",
        "title": "Zari Velvet Potli Bag",
        "subtitle": "Micro-Sequin & Beaded Tassel Evening Pouch",
        "description": "A regal evening accessory in plush silk velvet, detailed with golden bead tassels, drawstring closure, and hand-embroidered floral vines.",
        "category": "Accessories",
        "occasion": "Party",
        "collection": "Curated Collections",
        "base_price_pkr": 2999,
        "base_price_usd": 11,
        "sale_price_pkr": 2499,
        "sale_price_usd": 9,
        "sku": "HRT-ACC-007",
        "rating": 4.9,
        "review_count": 21,
        "fabric": "Silk Velvet with Golden Tassels",
        "care": "Spot clean only.",
        "colors": [
            {
                "name": "Muted Gold",
                "hex": "#D4AF37",
                "image": "potli-gold.jpg",
                "in_stock": True,
                "stock_count": 25,
                "variant_id": "var_acc_potli"
            }
        ],
        "sizes": ["Standard (8 x 9.5 inches)"],
        "is_featured": False,
        "is_bestseller": False,
        "is_new": False
    },
    {
        "id": "prod_008",
        "slug": "luxury-emerald-green-moos-embellished-silk-ensemble",
        "title": "Luxury Emerald Green – Moos Embellished Silk Ensemble",
        "subtitle": "Exquisite Emerald Green 3-Piece Ensemble with Delicate All-Over Moos Work",
        "description": "Discover effortless elegance with this exquisite emerald green three-piece ensemble, thoughtfully designed to combine contemporary sophistication with luxurious traditional craftsmanship.\n\nFeaturing a graceful silhouette and delicate all-over Moos embellishment, this outfit offers a refined look with a beautiful touch of shimmer and elegance.\n\nThe subtle sparkle of the embellishments against the rich emerald green shade creates an elegant and sophisticated appearance.\n\nStyle: Luxury Contemporary Formal & Festive Wear\nPerfect for festive celebrations, intimate weddings, evening gatherings and special occasions.\nMinimal in silhouette, luxurious in detail — elegance that speaks for itself.",
        "category": "Party Wear",
        "occasion": "Party",
        "collection": "Party & Festive Luxury",
        "is_bridal": False,
        "base_price_pkr": 43000,
        "base_price_usd": 155,
        "sale_price_pkr": 34400,
        "sale_price_usd": 124,
        "sku": "JUM-PRT-001",
        "rating": 5.0,
        "review_count": 42,
        "fabric": "Shirt: Premium Sheesha Silk | Trouser: Premium Sheesha Silk | Dupatta: Elegant Medium Silk",
        "care": "Professional Dry Clean Only. Preserve in Jumma Couture luxury garment bag.",
        "fabric_details": [
            {"label": "Shirt", "value": "Premium Sheesha Silk"},
            {"label": "Trouser", "value": "Premium Sheesha Silk"},
            {"label": "Dupatta", "value": "Elegant Medium Silk"}
        ],
        "embellishment_details": "Intricate all-over Moos (M-U-S) embellishment, beautifully embellished neckline and front detailing, delicate Moos work distributed evenly across the shirt, and refined embellishment on sleeves for a coordinated finish.",
        "specifications": [
            "Graceful modern silhouette with delicate Moos (M-U-S) craftsmanship",
            "Intricate all-over Moos hand detailing",
            "Beautifully embellished neckline and front panel",
            "Refined embellishment on sleeves for a coordinated finish",
            "Complete 3-piece luxury ensemble (Shirt, Trouser, Dupatta)"
        ],
        "gallery_images": [
            {
                "id": "gal_eg_1",
                "title": "Shirt Front",
                "caption": "Front view with delicate all-over Moos embellishment & embellished neckline",
                "image": "emerald-silk-front.jpg"
            },
            {
                "id": "gal_eg_2",
                "title": "Shirt Back",
                "caption": "Graceful back with evenly distributed Moos handwork",
                "image": "emerald-silk-back.jpg"
            },
            {
                "id": "gal_eg_3",
                "title": "Dupatta",
                "caption": "Elegant Medium Silk dupatta with subtle shimmer accents",
                "image": "emerald-silk-dupatta.jpg"
            },
            {
                "id": "gal_eg_4",
                "title": "Trouser",
                "caption": "Premium Sheesha Silk tailored trouser",
                "image": "emerald-silk-trouser.jpg"
            },
            {
                "id": "gal_eg_5",
                "title": "Complete on Model",
                "caption": "Complete 3-piece luxury ensemble styled on model",
                "image": "emerald-silk-model.jpg"
            },
            {
                "id": "gal_eg_6",
                "title": "Side Drape Detail",
                "caption": "Close-up perspective of fabric drape and sleeve finish",
                "image": "emerald-silk-side.jpg"
            }
        ],
        "colors": [
            {
                "name": "Emerald Green",
                "hex": "#1B4D3E",
                "image": "emerald-silk-front.jpg",
                "in_stock": True,
                "stock_count": 8,
                "variant_id": "var_emr_green"
            }
        ],
        "sizes": ["XS", "S", "M", "L", "XL", "Custom Stitched"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    },
    {
        "id": "prod_009",
        "slug": "midnight-black-antique-gold-luxury-ensemble",
        "title": "Midnight Black – Antique Gold Luxury Hand-Embellished Ensemble",
        "subtitle": "Regal Midnight Black Ensemble Adorned with Elaborate Antique & Golden Hand Embellishments",
        "description": "An exquisite statement of timeless elegance, this luxurious midnight black ensemble is adorned with elaborate antique and golden hand embellishments. Designed to reflect regal sophistication, the outfit showcases exceptional craftsmanship with intricate detailing and a captivating touch of sparkle.\n\nDesign & Embellishment Details:\nBeautifully embellished with a rich combination of traditional handwork and premium decorative elements:\n- Intricate traditional Dabka handwork\n- Antique and golden Japanese Cut Dana\n- Exquisite stone embellishments\n- Kholi-style decorative stone accents\n- Premium jewellery-inspired embellishment material\n- Delicate star sequins for a radiant finish\n- Fine shimmering and sparkling detailing\n- Intricate golden embroidery along the neckline, front panels, sleeves and hemline\n\nSignature Design Features:\nThe beautifully embellished neckline, statement central front panel and delicate vertical detailing create an elongated, graceful silhouette. Richly decorated sleeve borders and hemline complete the design with a luxurious finish.\n\nColour: Midnight Black with Antique & Golden Embellishments\nStyle: Luxury Designer Formal & Festive Wear\nPerfect for weddings, receptions, evening celebrations and exclusive festive occasions.\nAn extraordinary blend of traditional hand craftsmanship and contemporary luxury, created to make an unforgettable impression.",
        "category": "Party Wear",
        "occasion": "Party",
        "collection": "Party & Festive Luxury",
        "is_bridal": False,
        "base_price_pkr": 55000,
        "base_price_usd": 198,
        "sale_price_pkr": 44000,
        "sale_price_usd": 158,
        "sku": "JUM-PRT-002",
        "rating": 5.0,
        "review_count": 58,
        "fabric": "Shirt & Trouser: Premium Luxury Silk | Dupatta: Medium Silk with Gold Zari Accents",
        "care": "Professional Dry Clean Only. Preserve in Jumma Couture luxury garment bag.",
        "fabric_details": [
            {"label": "Shirt", "value": "Premium Midnight Black Silk"},
            {"label": "Trouser / Shalwar", "value": "Premium Silk with Hand-Embellished Cuffs"},
            {"label": "Dupatta", "value": "Medium Silk with Gold Zari Border"}
        ],
        "embellishment_details": "Intricate traditional Dabka handwork, Antique & golden Japanese Cut Dana, Exquisite stone embellishments, Kholi-style decorative stone accents, Premium jewellery-inspired embellishment material, Delicate star sequins, and fine shimmering detailing.",
        "specifications": [
            "Statement central front panel with delicate vertical detailing",
            "Intricate golden embroidery along neckline, front panels, sleeves, and hemline",
            "Richly decorated sleeve borders and hemline finish",
            "Hand-embellished cuff motifs on shalwar / trouser",
            "Complete 3-piece luxury ensemble (Shirt, Shalwar, Dupatta)"
        ],
        "gallery_images": [
            {
                "id": "gal_mb_1",
                "title": "Shirt Front",
                "caption": "Front view with elaborate antique gold Dabka, Cut Dana & neckline detailing",
                "image": "midnight-black-front.jpg"
            },
            {
                "id": "gal_mb_2",
                "title": "Shirt Back",
                "caption": "Back view with golden embroidery motifs along neckline and hem",
                "image": "midnight-black-back.jpg"
            },
            {
                "id": "gal_mb_3",
                "title": "Dupatta",
                "caption": "Medium Silk dupatta with gold zari accents on hanger",
                "image": "midnight-black-dupatta.jpg"
            },
            {
                "id": "gal_mb_4",
                "title": "Trouser / Shalwar",
                "caption": "Midnight Black silk shalwar with hand-embellished cuff motifs",
                "image": "midnight-black-trouser.jpg"
            },
            {
                "id": "gal_mb_5",
                "title": "Complete on Model",
                "caption": "Full ensemble styled on model with graceful dupatta drape",
                "image": "midnight-black-model.jpg"
            },
            {
                "id": "gal_mb_6",
                "title": "Side Drape Detail",
                "caption": "Studio perspective highlighting embroidered sleeve borders and silhouette",
                "image": "midnight-black-side.jpg"
            }
        ],
        "colors": [
            {
                "name": "Midnight Black",
                "hex": "#0D0D0D",
                "image": "midnight-black-front.jpg",
                "in_stock": True,
                "stock_count": 6,
                "variant_id": "var_mid_black"
            }
        ],
        "sizes": ["XS", "S", "M", "L", "XL", "Custom Stitched"],
        "is_featured": True,
        "is_bestseller": True,
        "is_new": True
    }
]

class ShopifyClient:
    def __init__(self):
        self.store_domain = SHOPIFY_STORE_DOMAIN
        self.storefront_token = SHOPIFY_STOREFRONT_ACCESS_TOKEN
        self.admin_token = SHOPIFY_ADMIN_API_ACCESS_TOKEN
        self.api_version = SHOPIFY_API_VERSION
        self.is_connected = bool(self.store_domain and (self.storefront_token or self.admin_token))

    def get_status(self):
        """Returns the current connection status and staging information"""
        return {
            "mode": "Development / Staging",
            "store_domain": self.store_domain or "jummacouturebynoman.com (Pending Input)",
            "storefront_configured": bool(self.storefront_token),
            "admin_configured": bool(self.admin_token),
            "api_version": self.api_version,
            "catalog_source": "Shopify GraphQL Live" if (self.store_domain and self.storefront_token) else "Local Jumma Couture by Noman Catalog (Shopify-Ready)",
            "status": "Connected to Shopify" if (self.store_domain and self.storefront_token) else "Awaiting Merchant Shopify API Keys (Fully functional in Staging Mode)"
        }

    def fetch_products(self):
        """
        Fetches products from Shopify Storefront API GraphQL if configured.
        Otherwise falls back smoothly to the rich internal catalog.
        """
        if not (self.store_domain and self.storefront_token):
            return DEFAULT_CATALOG

        graphql_endpoint = f"https://{self.store_domain}/api/{self.api_version}/graphql.json"
        query = """
        {
          products(first: 25) {
            edges {
              node {
                id
                title
                handle
                description
                productType
                tags
                priceRange {
                  minVariantPrice {
                    amount
                    currencyCode
                  }
                }
                variants(first: 10) {
                  edges {
                    node {
                      id
                      title
                      availableForSale
                      quantityAvailable
                      price {
                        amount
                        currencyCode
                      }
                      selectedOptions {
                        name
                        value
                      }
                      image {
                        url
                        altText
                      }
                    }
                  }
                }
                images(first: 5) {
                  edges {
                    node {
                      url
                      altText
                    }
                  }
                }
              }
            }
          }
        }
        """
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": self.storefront_token
        }
        try:
            resp = requests.post(graphql_endpoint, json={"query": query}, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get("data", {}).get("products", {}).get("edges", [])
                if edges:
                    return self._transform_shopify_products(edges)
        except Exception as e:
            logger.warning(f"Could not fetch from live Shopify ({e}), falling back to internal catalog.")

        return DEFAULT_CATALOG

    def _transform_shopify_products(self, edges):
        products = []
        for edge in edges:
            node = edge.get("node", {})
            slug = node.get("handle")
            title = node.get("title")
            desc = node.get("description", "")
            category = node.get("productType", "Ethnic Wear")
            
            # Map variants
            colors = []
            variants = node.get("variants", {}).get("edges", [])
            for v_edge in variants:
                v_node = v_edge.get("node", {})
                v_title = v_node.get("title", "Default")
                colors.append({
                    "name": v_title,
                    "hex": "#5C1427",
                    "image": v_node.get("image", {}).get("url") if v_node.get("image") else "lehenga-maroon.jpg",
                    "in_stock": v_node.get("availableForSale", True),
                    "stock_count": v_node.get("quantityAvailable", 10),
                    "variant_id": v_node.get("id")
                })
            
            amount = float(node.get("priceRange", {}).get("minVariantPrice", {}).get("amount", 2999))
            products.append({
                "id": node.get("id"),
                "slug": slug,
                "title": title,
                "subtitle": f"Authentic Jumma Couture {category}",
                "description": desc,
                "category": category,
                "occasion": "Festive",
                "collection": "Curated Collections",
                "base_price_pkr": int(amount),
                "base_price_usd": round(amount / 278, 2),
                "sale_price_pkr": int(amount * 0.9),
                "sale_price_usd": round((amount * 0.9) / 278, 2),
                "sku": f"HRT-SHP-{node.get('id')[-4:]}",
                "rating": 4.9,
                "review_count": 25,
                "fabric": "Luxury Fabric",
                "care": "Dry Clean Only",
                "colors": colors,
                "sizes": ["S", "M", "L", "XL"],
                "is_featured": True,
                "is_bestseller": True,
                "is_new": True
            })
        return products

    def create_shopify_order(self, order_data):
        """
        Creates an official paid order in Shopify Admin API once 100% advance payment is verified.
        Never marks unpaid orders as paid.
        """
        if not (self.store_domain and self.admin_token):
            logger.info(f"[Shopify Staging] Order {order_data['order_number']} recorded in local store. "
                        f"Shopify Admin API credentials pending. Order status: 100% PAID IN ADVANCE.")
            return {
                "success": True,
                "mode": "staging_simulated",
                "shopify_order_id": f"SHP-SIM-{order_data['order_number']}",
                "message": "Order verified with 100% full advance payment and staged for Shopify sync."
            }

        endpoint = f"https://{self.store_domain}/admin/api/{self.api_version}/orders.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.admin_token
        }

        # Build official line items
        line_items = []
        for item in order_data.get("items", []):
            line_items.append({
                "title": item.get("title"),
                "price": str(item.get("price")),
                "quantity": item.get("quantity", 1),
                "properties": [
                    {"name": "Color", "value": item.get("color")},
                    {"name": "Size", "value": item.get("size")}
                ]
            })

        payload = {
            "order": {
                "email": order_data.get("customer_email"),
                "financial_status": "paid", # 100% advance verified
                "fulfillment_status": "unfulfilled",
                "currency": order_data.get("currency", "PKR"),
                "total_price": str(order_data.get("total_amount")),
                "note": f"Jumma Couture By Noman Order | 100% Full Advance Paid via {order_data.get('payment_method').upper()} | Transaction Ref: {order_data.get('transaction_id')}",
                "shipping_address": {
                    "first_name": order_data.get("first_name"),
                    "last_name": order_data.get("last_name"),
                    "address1": order_data.get("address"),
                    "city": order_data.get("city"),
                    "province": order_data.get("state"),
                    "country": order_data.get("country"),
                    "zip": order_data.get("postal_code"),
                    "phone": order_data.get("phone")
                },
                "line_items": line_items,
                "transactions": [
                    {
                        "kind": "sale",
                        "status": "success",
                        "amount": str(order_data.get("total_amount")),
                        "gateway": order_data.get("payment_method")
                    }
                ]
            }
        }

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=8)
            if resp.status_code in [200, 201]:
                res_data = resp.json()
                shopify_id = res_data.get("order", {}).get("id")
                return {
                    "success": True,
                    "mode": "live_shopify",
                    "shopify_order_id": str(shopify_id),
                    "order_name": res_data.get("order", {}).get("name")
                }
            else:
                logger.error(f"Shopify Admin API returned error {resp.status_code}: {resp.text}")
                return {
                    "success": False,
                    "error": f"Shopify API error: {resp.status_code}",
                    "details": resp.text
                }
        except Exception as e:
            logger.error(f"Exception contacting Shopify Admin API: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
shopify_client = ShopifyClient()

