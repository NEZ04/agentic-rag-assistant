"""Wait for the Docker stack to come up, then ask it a question.

Run with:  python -m scripts.docker_check  (after `docker compose up -d`)
Ports can be changed with API_PORT / UI_PORT, same as docker-compose.yml.
"""
import os
import sys
import time

import requests

API = f"http://localhost:{os.getenv('API_PORT', '8000')}"
UI = f"http://localhost:{os.getenv('UI_PORT', '8501')}"


def wait_for(url: str, timeout: float) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if requests.get(url, timeout=3).ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(5)
    return False


ok = wait_for(f"{API}/health", 20 * 60)
print(f"API health ({API}): {'up' if ok else 'NOT UP'}")
if ok:
    r = requests.post(f"{API}/ask", json={"question": "What is the Betz limit?"}, timeout=600)
    print(f"POST /ask -> {r.status_code}: {r.text}")
    ok = r.status_code == 200 and "59" in r.text
ui_ok = wait_for(f"{UI}/_stcore/health", 120)
print(f"UI health ({UI}): {'up' if ui_ok else 'NOT UP'}")
print("DOCKER CHECK PASSED" if ok and ui_ok else "DOCKER CHECK FAILED")
sys.exit(0 if ok and ui_ok else 1)
