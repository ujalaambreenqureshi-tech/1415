import subprocess
import re
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "ssh_tunnel.log")
URL_FILE = os.path.join(BASE_DIR, "public_url.txt")

def start_tunnel_once():
    print("Initiating SSH tunnel to localhost.run...")
    cmd = [
        "ssh",
        "-R", "80:127.0.0.1:5000",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-o", "ExitOnForwardFailure=yes",
        "nokey@localhost.run"
    ]
    
    with open(LOG_PATH, "w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True
        )
        
    public_url = None
    for _ in range(20):
        time.sleep(1)
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.lhr\.life", content)
                    if matches:
                        public_url = matches[0]
                        break
            except Exception:
                pass

    if public_url:
        print(f"ONLINE_PUBLIC_URL:{public_url}")
        with open(URL_FILE, "w", encoding="utf-8") as pf:
            pf.write(public_url)
        proc.wait()
    else:
        print("localhost.run did not return URL quickly, trying pinggy fallback...")
        proc.terminate()
        start_pinggy_tunnel()

def start_pinggy_tunnel():
    print("Starting Pinggy tunnel...")
    cmd = [
        "ssh",
        "-p", "443",
        "-R", "0:127.0.0.1:5000",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "a.pinggy.io"
    ]
    with open(LOG_PATH, "w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True
        )
    public_url = None
    for _ in range(20):
        time.sleep(1)
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = re.findall(r"https://[a-zA-Z0-9-]+\.(?:free\.)?pinggy\.link", content)
                    if matches:
                        public_url = matches[0]
                        break
            except Exception:
                pass
    if public_url:
        print(f"ONLINE_PINGGY_URL:{public_url}")
        with open(URL_FILE, "w", encoding="utf-8") as pf:
            pf.write(public_url)
        proc.wait()
    else:
        print("Pinggy did not return URL")
        proc.terminate()

def run_loop():
    while True:
        try:
            start_tunnel_once()
        except Exception as e:
            print("Error in tunnel:", e)
        time.sleep(3)

if __name__ == "__main__":
    run_loop()
