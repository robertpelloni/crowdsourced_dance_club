import requests
import time
import subprocess
import os
import signal

def run_smoke_test():
    print("[SMOKE TEST] Starting production smoke test sequence...")

    # 1. Start server in a background process
    # Note: Use a different port to avoid conflicts with other tests
    port = "8005"
    server_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", port],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5) # Allow startup

    base_url = f"http://localhost:{port}"

    try:
        # 2. Check Public Health (if applicable) or Catalog
        res_catalog = requests.get(f"{base_url}/catalog")
        assert res_catalog.status_code == 200
        print("[PASS] Public Catalog API is reachable.")

        # 3. Authenticated Admin Health Check
        # Register/Login
        user_data = {"username": f"smoke_admin_{int(time.time())}", "password": "password123"}
        requests.post(f"{base_url}/api/register", json=user_data)

        # Manual promotion
        import sqlite3
        conn = sqlite3.connect("tracks.db")
        conn.execute("UPDATE users SET role = 'admin' WHERE username = ?", (user_data["username"],))
        conn.commit(); conn.close()

        login_res = requests.post(f"{base_url}/api/login", data=user_data)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check health endpoint
        res_health = requests.get(f"{base_url}/api/admin/health", headers=headers)
        assert res_health.status_code == 200
        health_data = res_health.json()
        assert health_data["system"]["status"] == "healthy"
        print(f"[PASS] Admin Health Monitoring is functional. Status: {health_data['system']['status']}")

        # 4. Analytics Report Verification
        res_report = requests.get(f"{base_url}/api/admin/analytics/vibe-report", headers=headers)
        assert res_report.status_code == 200
        print("[PASS] Vibe Performance Analytics reporting is functional.")

        print("[SUCCESS] Production smoke test completed successfully.")

    except Exception as e:
        print(f"[FAIL] Smoke test failed: {e}")
        raise
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_smoke_test()
