import urllib.request
import os
import subprocess
import time
import re

EXE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared.exe")

def download_cloudflared():
    if not os.path.exists(EXE_PATH):
        print("Downloading cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, EXE_PATH)
        print("Downloaded cloudflared.exe successfully.")
    else:
        print("cloudflared.exe already exists.")

def start_tunnel():
    download_cloudflared()
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tunnel.log")
    cmd = [EXE_PATH, "tunnel", "--url", "http://127.0.0.1:5000"]
    with open(log_file, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
    
    print("Cloudflared process started PID:", proc.pid)
    url = None
    for _ in range(25):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                content = f.read()
                matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if matches:
                    url = matches[0]
                    break
    if url:
        print("PUBLIC_URL:" + url)
        # Write to a file so we can read it easily
        with open("public_url.txt", "w") as f:
            f.write(url)
    else:
        print("Waiting for URL...")

if __name__ == "__main__":
    start_tunnel()

