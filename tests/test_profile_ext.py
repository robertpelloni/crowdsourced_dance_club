import pytest
from fastapi.testclient import TestClient
from src.main import app
import time

client = TestClient(app)

def test_user_update_vibe_pref():
    # 1. Register and Login
    username = f"user_update_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})
    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update Vibe Preference
    update_res = client.patch("/api/me", json={"vibe_preference": "Techno"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["vibe_preference"] == "Techno"

    # 3. Verify on /api/me
    me_res = client.get("/api/me", headers=headers)
    assert me_res.json()["vibe_preference"] == "Techno"

def test_history_endpoints():
    username = f"user_hist_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})
    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Should be empty initially
    res_req = client.get("/api/me/history/requests", headers=headers)
    assert len(res_req.json()) == 0

    res_vote = client.get("/api/me/history/votes", headers=headers)
    assert len(res_vote.json()) == 0

def test_liked_songs_history():
    username = f"user_likes_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})
    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Should be empty initially
    res = client.get("/api/me/history/likes", headers=headers)
    assert len(res.json()) == 0

    # Like a song
    client.post("/api/feedback/song", json={"track_id": "track_001", "is_like": True}, headers=headers)

    # Verify history
    res = client.get("/api/me/history/likes", headers=headers)
    assert len(res.json()) == 1
    assert res.json()[0]["track_id"] == "track_001"

def test_change_password():
    username = f"user_pwd_{int(time.time())}"
    client.post("/api/register", json={"username": username, "password": "password123"})

    login_res = client.post("/api/login", data={"username": username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Change password correctly
    change_res = client.post("/api/me/change-password",
                             json={"current_password": "password123", "new_password": "new_password_456"},
                             headers=headers)
    assert change_res.status_code == 200

    # 2. Try logging in with old password (should fail)
    bad_login = client.post("/api/login", data={"username": username, "password": "password123"})
    assert bad_login.status_code == 401

    # 3. Login with new password (should succeed)
    good_login = client.post("/api/login", data={"username": username, "password": "new_password_456"})
    assert good_login.status_code == 200
