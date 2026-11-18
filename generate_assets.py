"""
Asset generator for Jumma Couture By Noman store
Theme: Ivory + Black + Champagne Gold Luxury (Clean Minimalist Luxury Edition)
Removes all background concentric circles and busy mandalas.
Presents clean, pure, ultra-luxury product cards and backgrounds.
"""
import os
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "static", "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Haute Luxury Palette
COLOR_IVORY = "#FAF8F5"
COLOR_BLACK = "#0E0D0D"
COLOR_GOLD = "#CBB279"
COLOR_GOLD_LIGHT = "#EADBBA"

def make_product_card_image(filename, bg_color, frame_color, title, subtitle, accent_border):
    width, height = 700, 900
    im = Image.new("RGB", (width, height), bg_color)
    d = ImageDraw.Draw(im)
    
    # Clean, subtle luxury rectangular borders (NO CIRCLES!)
    d.rectangle([24, 24, width - 24, height - 24], outline=frame_color, width=2)
    d.rectangle([34, 34, width - 34, height - 34], outline="#EADBBA", width=1)
    
    # Clean inner luxury arch outline (just a clean arch, NO concentric circles inside)
    arch_top = 100
    arch_h = 440
    d.arc([140, arch_top, width - 140, arch_top + arch_h], start=180, end=0, fill=frame_color, width=2)
    d.line([140, arch_top + arch_h // 2, 140, 600], fill=frame_color, width=2)
    d.line([width - 140, arch_top + arch_h // 2, width - 140, 600], fill=frame_color, width=2)
    d.line([140, 600, width - 140, 600], fill=frame_color, width=2)

    # Subtle corner flourishes
    for (x, y) in [(44, 44), (width - 64, 44), (44, height - 64), (width - 64, height - 64)]:
        d.rectangle([x, y, x + 16, y + 16], outline=frame_color, width=1)
        
    # Lower Label Card (Pure Ivory with Clean Champagne Gold Border)
    card_top = 660
    d.rounded_rectangle([60, card_top, width - 60, height - 60], radius=8, fill="#FFFFFF", outline="#CBB279", width=1)
    
    # High-End Brand Label
    d.text((width // 2 - 120, card_top + 28), "HERITAGE ETHNIC LUXURY", fill="#CBB279", font=None)
    d.text((width // 2 - 110, card_top + 62), title.upper(), fill="#0E0D0D", font=None)
    d.text((width // 2 - 100, card_top + 98), subtitle, fill="#5C5549", font=None)
    
    im.save(os.path.join(IMG_DIR, filename), quality=95)

def generate_all():
    # Product cards with clean Ivory base + Noir + Champagne Gold (Zero background circles)
    variants = [
        # Zari Embroidered Lehenga
        ("lehenga-maroon.jpg", "#FAF8F5", "#CBB279", "Zari Embroidered Lehenga", "Ivory Raw Silk & Antique Gold", "#D8C28E"),
        ("lehenga-emerald.jpg", "#F7F4EC", "#0E0D0D", "Zari Embroidered Lehenga", "Noir Velvet & Champagne Dabka", "#CBB279"),
        ("lehenga-navy.jpg", "#FAF8F5", "#A58745", "Zari Embroidered Lehenga", "Alabaster Silk & Gold Tilla", "#EADBBA"),
        ("lehenga-plum.jpg", "#F9F6F0", "#0E0D0D", "Zari Embroidered Lehenga", "Imperial Black & Golden Brocade", "#CBB279"),
        
        # Embellished Organza Saree
        ("saree-mauve.jpg", "#FAF8F5", "#CBB279", "Embellished Organza Saree", "Champagne Gold Muted Zari", "#D8C28E"),
        ("saree-champagne.jpg", "#FCFAF7", "#A58745", "Embellished Organza Saree", "Pure Champagne Tissue Saree", "#CBB279"),
        ("saree-sage.jpg", "#F7F4EC", "#0E0D0D", "Embellished Organza Saree", "Noir Trim Embellished Organza", "#D8C28E"),
        ("saree-crimson.jpg", "#FAF8F5", "#CBB279", "Embellished Organza Saree", "Ivory Chiffon & Gotta Patti", "#A58745"),
        
        # Handwoven Silk Kurta Set
        ("kurta-forest.jpg", "#F7F4EC", "#0E0D0D", "Handwoven Silk Kurta Set", "Noir Raw Silk & Gold Resham", "#CBB279"),
        ("kurta-mustard.jpg", "#FCFAF7", "#CBB279", "Handwoven Silk Kurta Set", "Champagne Chanderi Silk", "#D8C28E"),
        ("kurta-ivory.jpg", "#FAF8F5", "#0E0D0D", "Handwoven Silk Kurta Set", "Pure Alabaster Silk Brocade", "#CBB279"),
        ("kurta-terracotta.jpg", "#F9F6F0", "#A58745", "Handwoven Silk Kurta Set", "Gold Zardozi Silk Silhouette", "#EADBBA"),
        
        # Anarkali Suit Set
        ("anarkali-yellow.jpg", "#FCFAF7", "#CBB279", "Anarkali Suit Set", "Champagne Flared 24-Kali Gown", "#D8C28E"),
        ("anarkali-peach.jpg", "#FAF8F5", "#0E0D0D", "Anarkali Suit Set", "Noir Velvet & Gold Gotta Anarkali", "#CBB279"),
        ("anarkali-mint.jpg", "#F7F4EC", "#A58745", "Anarkali Suit Set", "Ivory Silk & Champagne Tilla", "#EADBBA"),
        ("anarkali-ruby.jpg", "#FAF8F5", "#0E0D0D", "Anarkali Suit Set", "Regal Noir & Gold Imperial Gown", "#CBB279"),
        
        # Accessories / Potlis
        ("potli-gold.jpg", "#FAF8F5", "#CBB279", "Zari Velvet Potli", "Champagne Gold & Pearl Tassel", "#D8C28E"),
        ("hero-banner.jpg", "#FAF8F5", "#CBB279", "Timeless Traditions", "Ivory, Black & Champagne Gold", "#0E0D0D"),
        ("artisan-spotlight.jpg", "#FAF8F5", "#CBB279", "Artisan Spotlight", "Master Craftsmen at Heritage", "#0E0D0D")
    ]
    
    for filename, bg, frame, title, sub, border in variants:
        make_product_card_image(filename, bg, frame, title, sub, border)
        
    print(f"Generated {len(variants)} clean assets without background circles.")

if __name__ == "__main__":
    generate_all()
