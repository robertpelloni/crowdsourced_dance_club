import pytest
from fastapi.testclient import TestClient
from src.main import app, get_db_connection
import time

client = TestClient(app)

def test_referral_flow():
    # 1. Register first user
    user1_name = f"referrer_{int(time.time())}"
    resp1 = client.post("/api/register", json={"username": user1_name, "password": "password123"})
    assert resp1.status_code == 200
    ref_code = resp1.json()["referral_code"]
    assert ref_code is not None

    # 2. Register second user with referral code
    user2_name = f"referred_{int(time.time())}"
    resp2 = client.post("/api/register", json={
        "username": user2_name,
        "password": "password456",
        "referral_code": ref_code
    })
    assert resp2.status_code == 200

    # 3. Verify points for referrer
    login_data1 = {"username": user1_name, "password": "password123"}
    token1 = client.post("/api/login", data=login_data1).json()["access_token"]
    me1 = client.get("/api/me", headers={"Authorization": f"Bearer {token1}"}).json()
    assert me1["points"] == 50

    # 4. Verify points for referred user
    login_data2 = {"username": user2_name, "password": "password456"}
    token2 = client.post("/api/login", data=login_data2).json()["access_token"]
    me2 = client.get("/api/me", headers={"Authorization": f"Bearer {token2}"}).json()
    assert me2["points"] == 50
    assert me2["referral_code"] is not None
    assert me2["referral_code"] != ref_code
