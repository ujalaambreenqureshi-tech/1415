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
LOG_FILE = os.path.join(BASE_DIR, "tunnel_http2.log")

def run_flask():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "app.py")], env=env)

def wait_for_flask():
    for _ in range(25):
        time.sleep(1)
        try:
            req = urllib.request.Request("http://127.0.0.1:5000", headers={"User-Agent": "HealthCheck"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
    return False

def run_tunnel_cycle():
    # Clear log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    cmd = [
        CLOUDFLARED, "tunnel",
        "--protocol", "http2",
        "--url", "http://127.0.0.1:5000",
        "--no-autoupdate",
        "--edge-ip-version", "4"
    ]
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    public_url = None
    for _ in range(35):
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
        print("\n" + "="*60, flush=True)
        print(f"ROCK-SOLID PUBLIC LIVE URL: {public_url}", flush=True)
        print("="*60 + "\n", flush=True)
        with open(URL_FILE, "w", encoding="utf-8") as f:
            f.write(public_url + "\n")

    # Monitor proc and log for errors
    while True:
        time.sleep(5)
        if proc.poll() is not None:
            print("Tunnel process exited, restarting...", flush=True)
            break
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    log_data = f.read()
                    if "Tunnel not found" in log_data or "Unauthorized" in log_data:
                        print("Tunnel expired, terminating to re-acquire fresh tunnel...", flush=True)
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except Exception:
                            proc.kill()
                        break
            except Exception:
                pass

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    if wait_for_flask():
        print("Flask is alive and responding on port 5000.", flush=True)
        while True:
            try:
                run_tunnel_cycle()
            except Exception as e:
                print(f"Tunnel restart loop error: {e}", flush=True)
                time.sleep(2)
    else:
        print("Flask failed to start.", flush=True)

if __name__ == "__main__":
    main()
