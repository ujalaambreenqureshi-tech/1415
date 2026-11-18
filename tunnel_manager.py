import subprocess
import re
import time
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "live_tunnel.log")
URL_FILE = os.path.join(BASE_DIR, "public_url.txt")

def start_tunnel():
    print("Initiating single robust SSH tunnel...")
    # Kill any existing ssh processes first
    try:
        subprocess.run(["powershell", "-Command", "Stop-Process -Name ssh -Force -ErrorAction SilentlyContinue"], timeout=5)
    except Exception:
        pass
    time.sleep(1)

    cmd = [
        "ssh",
        "-R", "80:127.0.0.1:5000",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=20",
        "-o", "ServerAliveCountMax=5",
        "-o", "ExitOnForwardFailure=yes",
        "nokey@localhost.run"
    ]

    with open(LOG_FILE, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, text=True)

    print(f"SSH process started with PID: {proc.pid}")

    found_url = None
    for attempt in range(25):
        time.sleep(1)
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.lhr\.life", content)
                    if matches:
                        found_url = matches[0]
                        break
            except Exception:
                pass

    if not found_url:
        print("Could not obtain URL from localhost.run. Retrying...")
        proc.terminate()
        return False

    print(f"Acquired URL: {found_url}")
    with open(URL_FILE, "w", encoding="utf-8") as f:
        f.write(found_url)

    # Verify HTTP response
    verified = False
    for i in range(6):
        time.sleep(2)
        try:
            req = urllib.request.Request(found_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    print(f"TUNNEL_VERIFIED_200: {found_url}")
                    verified = True
                    break
        except Exception as e:
            print(f"Verification attempt {i+1} wait: {e}")

    # Wait for process to exit or monitor
    proc.wait()
    print("SSH process exited.")
    return True

def main():
    while True:
        try:
            start_tunnel()
        except Exception as e:
            print(f"Exception in tunnel runner: {e}")
        time.sleep(3)

if __name__ == "__main__":
    main()

