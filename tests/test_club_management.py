import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.init_db import init_db
import os

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    yield
    # Cleanup after tests if needed

client = TestClient(app)

def get_token(username, password="password123"):
    # Register first
    client.post("/api/register", json={"username": username, "password": password})
    # Login
    response = client.post("/api/login", data={"username": username, "password": password})
    return response.json()["access_token"]

def test_club_creation():
    token = get_token("club_owner")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/clubs",
        json={"name": "Test Club", "description": "A club for testing"},
        headers=headers
    )
    assert response.status_code == 200
    club_id = response.json()["id"]
    assert club_id.startswith("club_")

    # Verify listing
    response = client.get("/api/clubs", headers=headers)
    assert response.status_code == 200
    clubs = response.json()
    assert any(c["id"] == club_id for c in clubs)

def test_club_member_management():
    owner_token = get_token("owner_user")
    member_token = get_token("member_user")

    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Create club
    resp = client.post("/api/clubs", json={"name": "Member Test Club"}, headers=owner_headers)
    club_id = resp.json()["id"]

    # Add member
    resp = client.post(
        f"/api/clubs/{club_id}/members",
        json={"username": "member_user", "role": "member"},
        headers=owner_headers
    )
    assert resp.status_code == 200

    # Verify club details
    resp = client.get(f"/api/clubs/{club_id}", headers=owner_headers)
    assert resp.status_code == 200
    members = resp.json()["members"]
    assert any(m["username"] == "member_user" for m in members)

    # Non-admin cannot add member
    member_headers = {"Authorization": f"Bearer {member_token}"}
    resp = client.post(
        f"/api/clubs/{club_id}/members",
        json={"username": "another_user", "role": "member"},
        headers=member_headers
    )
    assert resp.status_code == 403

def test_club_role_update_and_removal():
    owner_token = get_token("admin_user")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Create club
    resp = client.post("/api/clubs", json={"name": "Role Test Club"}, headers=owner_headers)
    club_id = resp.json()["id"]

    # Add member
    get_token("target_user") # register target user
    client.post(f"/api/clubs/{club_id}/members", json={"username": "target_user", "role": "member"}, headers=owner_headers)

    # Get user_id
    resp = client.get(f"/api/clubs/{club_id}", headers=owner_headers)
    user_id = [m["user_id"] for m in resp.json()["members"] if m["username"] == "target_user"][0]

    # Update role
    resp = client.patch(
        f"/api/clubs/{club_id}/members/{user_id}",
        json={"role": "admin"},
        headers=owner_headers
    )
    assert resp.status_code == 200

    # Remove member
    resp = client.delete(f"/api/clubs/{club_id}/members/{user_id}", headers=owner_headers)
    assert resp.status_code == 200

    # Verify removal
    resp = client.get(f"/api/clubs/{club_id}", headers=owner_headers)
    assert not any(m["user_id"] == user_id for m in resp.json()["members"])
