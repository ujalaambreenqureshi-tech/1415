import os
import re

template_dir = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce\templates"

for fname in sorted(os.listdir(template_dir)):
    if not fname.endswith(".html"):
        continue
    path = os.path.join(template_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    issues = []
    for idx, line in enumerate(lines, 1):
        # find width: Xpx where X > 300 and not max-width
        m = re.findall(r"(?<!max-)(?<!min-)width\s*:\s*([3-9]\d{2,}|\d{4,})px", line, re.I)
        if m:
            issues.append((idx, f"Fixed width: {m}", line.strip()[:100]))
        # find inline grid-template-columns with multi columns without media query
        if "grid-template-columns" in line and "<style" not in line and "@media" not in line:
            issues.append((idx, "Inline grid", line.strip()[:100]))

    if issues:
        print(f"\n=== {fname} ({len(issues)} issues) ===")
        for line_num, typ, snippet in issues[:10]:
            print(f"  Line {line_num} [{typ}]: {snippet}")
