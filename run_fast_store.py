import subprocess
import threading
import time
import re
import os
import urllib.request
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = os.path.dirname(BASE_DIR)
CLOUDFLARED = os.path.join(SCRATCH_DIR, "cloudflared.exe")
if not os.path.exists(CLOUDFLARED):
    CLOUDFLARED = os.path.join(BASE_DIR, "cloudflared.exe")

URL_FILE = os.path.join(BASE_DIR, "public_url.txt")
LOG_FILE = os.path.join(BASE_DIR, "fast_tunnel.log")

def run_flask():
    print("Launching Flask multi-threaded server...")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "app.py")], env=env)

def wait_for_local_flask():
    print("Waiting for local Flask server to be ready on port 5000...")
    for i in range(20):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000", timeout=2) as r:
                if r.status == 200:
                    print(f"Local Flask is READY (HTTP 200) in {i+1}s!")
                    return True
        except Exception:
            pass
    print("Local Flask failed to start in time.")
    return False

def run_cloudflare_tunnel():
    print(f"Starting Cloudflare Fast Edge Tunnel: {CLOUDFLARED}...")
    cmd = [CLOUDFLARED, "tunnel", "--url", "http://127.0.0.1:5000", "--no-autoupdate"]
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    public_url = None
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                    if matches:
                        public_url = matches[0]
                        break
            except Exception:
                pass

    if public_url:
        print("\n" + "="*50)
        print(f"⚡ FAST CLOUDFLARE PUBLIC URL: {public_url}")
        print("="*50 + "\n")
        with open(URL_FILE, "w", encoding="utf-8") as f:
            f.write(public_url)

        # Immediate verification
        try:
            req = urllib.request.Request(public_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"Verified Cloudflare Edge Status: {resp.status} (SUCCESS)")
        except Exception as e:
            print(f"Edge verification notice: {e}")

        proc.wait()
    else:
        print("Could not obtain trycloudflare.com URL from logs:")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                print(f.read())
        proc.terminate()

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    if wait_for_local_flask():
        run_cloudflare_tunnel()
    else:
        print("Aborting tunnel startup because Flask did not respond.")

if __name__ == "__main__":
    main()

