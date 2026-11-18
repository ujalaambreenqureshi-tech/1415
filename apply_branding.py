import os

base_dir = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce"

replacements = [
    ("Heritage | Ethnic Luxury Couture", "Jumma Couture By Noman | Luxury Couture"),
    ("Heritage | Ethnic Luxury — Official Storefront", "Jumma Couture By Noman — Official Luxury Storefront"),
    ("Heritage | Ethnic Luxury", "Jumma Couture By Noman"),
    ("Heritage Ethnic Luxury", "Jumma Couture By Noman"),
    ("The Heritage Legacy", "Jumma Couture By Noman"),
    ("Handcrafted with Heritage", "Handcrafted by Jumma Couture By Noman"),
    ("Heritage was founded", "Jumma Couture By Noman was founded"),
    ("vip@heritage-luxury.com", "vip@jummacouturebynoman.com"),
    ("Heritage2026!", "JummaCouture2026!"),
    ("Join Heritage VIP", "Join Jumma Couture By Noman VIP"),
    ("Join Heritage", "Join Jumma Couture By Noman"),
    ("Certified Heritage Handcrafted", "Certified Jumma Couture By Noman Handcrafted"),
    ("What is Heritage's payment policy?", "What is Jumma Couture By Noman's payment policy?"),
    ("Heritage operates strictly on a", "Jumma Couture By Noman operates strictly on a"),
    ("Heritage complies with international", "Jumma Couture By Noman complies with international"),
    ("By placing an order on Heritage,", "By placing an order on Jumma Couture By Noman,"),
    ("Artisan Spotlight & Heritage", "Artisan Spotlight & Brand Story"),
    ("Preserve in Heritage", "Preserve in Jumma Couture By Noman"),
    ("Heritage bespoke", "Jumma Couture By Noman bespoke"),
    ("Heritage luxury", "Jumma Couture By Noman luxury"),
    ("Authentic Heritage", "Authentic Jumma Couture By Noman"),
    ("Local Heritage Luxury Catalog", "Local Jumma Couture By Noman Catalog"),
    ("Starting Heritage Ethnic Luxury Store", "Starting Jumma Couture By Noman Store"),
]

updated_files = []
for root, dirs, files in os.walk(base_dir):
    if ".git" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith((".html", ".py", ".md")) and f not in ["clean_push.py", "git_sync.py", "apply_branding.py"]:
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
            
            orig = content
            for old_str, new_str in replacements:
                content = content.replace(old_str, new_str)
            
            if content != orig:
                with open(p, "w", encoding="utf-8") as fp:
                    fp.write(content)
                rel = os.path.relpath(p, base_dir)
                updated_files.append(rel)
                print(f"Updated: {rel}")

print(f"\nSuccessfully updated branding in {len(updated_files)} files!")

