"""End-to-end smoke test: start the API and UI, ask a real question, shut down.

Run with:  python scripts/smoke_test.py   (needs Ollama running and the index built)
"""
import subprocess
import sys
import time

import requests

API = "http://127.0.0.1:8000"
UI = "http://127.0.0.1:8501"


def wait_for(url: str, timeout: float = 90) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if requests.get(url, timeout=2).ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def main() -> int:
    procs = []
    ok = True
    try:
        procs.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "app.api:app", "--port", "8000"]))
        if not wait_for(f"{API}/health"):
            print("FAIL: API did not start")
            return 1
        print("API is up")

        r = requests.post(f"{API}/ask", json={"question": "What is the Betz limit?"}, timeout=300)
        print(f"POST /ask -> {r.status_code}: {r.json()}")
        ok &= r.status_code == 200 and bool(r.json()["answer"])

        r = requests.post(f"{API}/ask", json={"question": "   "}, timeout=10)
        print(f"POST /ask (empty) -> {r.status_code}")
        ok &= r.status_code == 422

        procs.append(subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "ui/app.py",
            "--server.headless", "true", "--server.port", "8501",
            "--browser.gatherUsageStats", "false",
        ]))
        ui_up = wait_for(f"{UI}/_stcore/health")
        print("UI is up" if ui_up else "FAIL: UI did not start")
        ok &= ui_up
    finally:
        for p in procs:
            p.terminate()
    print("SMOKE TEST PASSED" if ok else "SMOKE TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
