import urllib.request
import json

url = "https://api.github.com/repos/ujalaambreenqureshi-tech/1415/contents"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    items = json.loads(resp.read().decode())
    print(f"Total root items on GitHub: {len(items)}")
    for item in sorted(items, key=lambda x: (x.get("type") != "dir", x.get("name"))):
        t = "[DIR] " if item.get("type") == "dir" else "[FILE]"
        print(f" {t} {item.get('name')}")

