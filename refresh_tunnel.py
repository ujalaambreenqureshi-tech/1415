import subprocess
import os
import re
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "ssh_tunnel.log")
URL_FILE = os.path.join(BASE_DIR, "public_url.txt")

def kill_old_ssh():
    try:
        subprocess.run(["powershell", "-Command", "Stop-Process -Name ssh -Force -ErrorAction SilentlyContinue"], timeout=5)
    except Exception:
        pass

def launch_fresh_tunnel():
    kill_old_ssh()
    time.sleep(1)
    
    print("Starting fresh SSH tunnel to localhost.run...")
    cmd = [
        "ssh",
        "-R", "80:127.0.0.1:5000",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=4",
        "-o", "ExitOnForwardFailure=yes",
        "nokey@localhost.run"
    ]
    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
        
    print(f"Spawned SSH PID: {proc.pid}")
    
    url = None
    for _ in range(25):
        time.sleep(1)
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.lhr\.life", content)
                    if matches:
                        url = matches[0]
                        break
            except Exception:
                pass
                
    if url:
        print(f"NEW_LIVE_URL:{url}")
        with open(URL_FILE, "w", encoding="utf-8") as f:
            f.write(url)
            
        # Verify
        time.sleep(2)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"Verified HTTP status: {resp.status}")
        except Exception as e:
            print(f"Verification note: {e}")
            
        # Keep process running
        proc.wait()
    else:
        print("Failed to get URL from localhost.run, output in log:")
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                print(f.read())
        proc.terminate()

def run_forever():
    while True:
        try:
            launch_fresh_tunnel()
        except Exception as e:
            print(f"Tunnel loop error: {e}")
        time.sleep(3)

if __name__ == "__main__":
    run_forever()

