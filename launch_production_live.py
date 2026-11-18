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
TUNNEL_LOG = os.path.join(BASE_DIR, "cloudflare_live.log")
SSH_LOG = os.path.join(BASE_DIR, "localhost_run.log")

def kill_port_5000():
    try:
        cmd = 'powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"'
        subprocess.run(cmd, shell=True)
    except Exception:
        pass

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

def start_tunnels():
    # Start Cloudflare Tunnel
    cmd_cf = [CLOUDFLARED, "tunnel", "--url", "http://127.0.0.1:5000", "--no-autoupdate"]
    with open(TUNNEL_LOG, "w", encoding="utf-8") as f_cf:
        proc_cf = subprocess.Popen(cmd_cf, stdout=f_cf, stderr=subprocess.STDOUT, text=True)

    # Start localhost.run as backup / secondary high-speed tunnel
    cmd_ssh = [
        "ssh", "-R", "80:127.0.0.1:5000",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=3",
        "nokey@localhost.run"
    ]
    with open(SSH_LOG, "w", encoding="utf-8") as f_ssh:
        proc_ssh = subprocess.Popen(cmd_ssh, stdout=f_ssh, stderr=subprocess.STDOUT, text=True)

    cf_url = None
    lhr_url = None

    for _ in range(30):
        time.sleep(1)
        if not cf_url and os.path.exists(TUNNEL_LOG):
            try:
                with open(TUNNEL_LOG, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                    if matches:
                        cf_url = matches[0]
            except Exception:
                pass

        if not lhr_url and os.path.exists(SSH_LOG):
            try:
                with open(SSH_LOG, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.lhr\.life", content)
                    if matches:
                        lhr_url = matches[0]
            except Exception:
                pass

        if cf_url or lhr_url:
            break

    print("Tunnel discovery status:")
    print("Cloudflare:", cf_url)
    print("localhost.run:", lhr_url)

    # Test which one is faster and responds 200
    chosen_url = None
    for candidate in [cf_url, lhr_url]:
        if not candidate:
            continue
        try:
            start_t = time.time()
            req = urllib.request.Request(candidate, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                elapsed = time.time() - start_t
                print(f"Candidate {candidate} -> HTTP {r.status} in {elapsed:.2f}s")
                if r.status == 200:
                    chosen_url = candidate
                    break
        except Exception as e:
            print(f"Candidate {candidate} failed test: {e}")

    if not chosen_url:
        chosen_url = cf_url or lhr_url

    if chosen_url:
        print("\n" + "#"*60)
        print(f"ACTIVE PUBLIC STORE URL: {chosen_url}")
        print("#"*60 + "\n")
        with open(URL_FILE, "w", encoding="utf-8") as f:
            f.write(chosen_url + "\n")
            if cf_url:
                f.write(f"CLOUDFLARE={cf_url}\n")
            if lhr_url:
                f.write(f"LOCALHOST_RUN={lhr_url}\n")

    # Keep alive
    while True:
        time.sleep(10)

def main():
    kill_port_5000()
    time.sleep(1)
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    if wait_for_flask():
        print("Flask multi-threaded server is LIVE on http://127.0.0.1:5000")
        start_tunnels()
    else:
        print("ERROR: Flask failed to start on port 5000")

if __name__ == "__main__":
    main()

