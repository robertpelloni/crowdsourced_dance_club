import pytest
import time
from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app
from src.db.database import get_db_connection

client = TestClient(app)

def test_vibe_summary_public_endpoint():
    """Verify that /api/analytics/vibe-summary returns aggregated metrics with expected structure."""
    response = client.get("/api/analytics/vibe-summary")
    assert response.status_code == 200
    data = response.json()
    assert "genre_metrics" in data
    assert "average_user_ratings" in data
    assert "vibe" in data["average_user_ratings"]
    assert "technical" in data["average_user_ratings"]

def test_admin_vibe_report_rbac():
    """Verify that /api/admin/analytics/vibe-report requires admin authorization."""
    # Unauthorized
    unauth_res = client.get("/api/admin/analytics/vibe-report")
    assert unauth_res.status_code == 401

    # Register normal user
    ts = int(time.time() * 1000)
    normal_username = f"user_analytics_{ts}"
    client.post("/api/register", json={"username": normal_username, "password": "password123"})
    login_user = client.post("/api/login", data={"username": normal_username, "password": "password123"}).json()
    user_token = login_user["access_token"]

    forbidden_res = client.get(
        "/api/admin/analytics/vibe-report",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert forbidden_res.status_code == 403

    # Register admin user and promote role
    admin_username = f"admin_analytics_{ts}"
    client.post("/api/register", json={"username": admin_username, "password": "password123"})
    conn = get_db_connection()
    conn.execute("UPDATE users SET role = 'admin' WHERE username = ?", (admin_username,))
    conn.commit()
    conn.close()

    login_admin = client.post("/api/login", data={"username": admin_username, "password": "password123"}).json()
    admin_token = login_admin["access_token"]

    admin_res = client.get(
        "/api/admin/analytics/vibe-report",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    data = admin_res.json()
    assert "genre_metrics" in data
    assert "average_user_ratings" in data

def test_analytics_data_aggregation_with_feedback():
    """Verify that feedback and performance logs are properly aggregated."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now = datetime.utcnow().isoformat()
        # Seed test feedback with timestamp
        cursor.execute("INSERT INTO feedback (user_id, vibe_rating, technical_rating, timestamp) VALUES (?, ?, ?, ?)",
                       ("test_user_analytics", 5, 4, now))
        conn.commit()

        response = client.get("/api/analytics/vibe-summary")
        assert response.status_code == 200
        data = response.json()
        assert data["average_user_ratings"]["vibe"] > 0
        assert data["average_user_ratings"]["technical"] > 0
    finally:
        cursor.execute("DELETE FROM feedback WHERE user_id = ?", ("test_user_analytics",))
        conn.commit()
        conn.close()
