import pytest
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_monitoring_endpoints_rbac():
    # 1. Register and Login a regular user
    username = f"user_obs_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})
    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Regular user should be denied access to health
    res_health = client.get("/api/admin/health", headers=headers)
    assert res_health.status_code == 403

def test_health_and_analytics_logic():
    # Manual promotion for admin access
    username = f"admin_obs_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})

    import sqlite3
    conn = sqlite3.connect("tracks.db")
    conn.execute("UPDATE users SET role = 'admin' WHERE username = ?", (username,))
    conn.commit(); conn.close()

    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify Health Endpoint
    res_health = client.get("/api/admin/health", headers=headers)
    assert res_health.status_code == 200
    data = res_health.json()
    assert "system" in data
    assert data["system"]["status"] == "healthy"

    # Verify Analytics Endpoint
    res_report = client.get("/api/admin/analytics/vibe-report", headers=headers)
    assert res_report.status_code == 200
    report = res_report.json()
    assert "genre_metrics" in report
    assert "average_user_ratings" in report
