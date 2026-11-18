import os
import re

template_dir = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce\templates"
report = []

for fname in sorted(os.listdir(template_dir)):
    if not fname.endswith(".html"):
        continue
    path = os.path.join(template_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    fixed_widths = re.findall(r"width\s*:\s*([4-9]\d{2,}|\d{4,})px", content, re.I)
    tables = re.findall(r"<table[^>]*>", content, re.I)
    inline_grids = re.findall(r"grid-template-columns\s*:\s*([^;\"'>]+)", content, re.I)
    
    report.append({
        "file": fname,
        "fixed_widths": set(fixed_widths),
        "tables": len(tables),
        "inline_grids": inline_grids
    })

print(f"{'FILE':<22} | {'FIXED WIDTHS >400px':<22} | {'TABLES':<8} | {'INLINE GRIDS'}")
print("-" * 80)
for r in report:
    fw = ", ".join(r["fixed_widths"]) if r["fixed_widths"] else "None"
    tb = str(r["tables"]) if r["tables"] else "0"
    ig = "; ".join(r["inline_grids"][:2]) if r["inline_grids"] else "None"
    print(f"{r['file']:<22} | {fw:<22} | {tb:<8} | {ig}")
