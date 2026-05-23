import pytest
import time
from fastapi.testclient import TestClient
from src.main import app, get_db_connection

client = TestClient(app)

def test_rbac_restrictions():
    # 1. Register a normal user
    username = f"regular_user_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})

    # 2. Login
    resp = client.post("/api/login", data={"username": username, "password": "password123"})
    token = resp.json()["access_token"]

    # 3. Try to access admin-restricted WebSocket action (simulated via API if available,
    # but here we mainly check if role is 'user')
    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["role"] == "user"

def test_admin_promotion():
    # Manual promotion for test
    username = f"admin_user_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "adminpass"})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    resp = client.post("/api/login", data={"username": username, "password": "adminpass"})
    token = resp.json()["access_token"]

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["role"] == "admin"
