import asyncio
import json
import websockets
import httpx
import time

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/clubgoer"

async def simulate_user_journey():
    print("[TEST] Starting User Journey Simulation...")

    # 1. Register a new user
    username = f"tester_{int(time.time())}"
    async with httpx.AsyncClient() as client:
        reg_res = await client.post(f"{BASE_URL}/api/register", json={
            "username": username,
            "password": "testpassword123"
        })
        assert reg_res.status_code == 200
        print(f"[TEST] Registered user: {username}")

        # 2. Login
        login_res = await client.post(f"{BASE_URL}/api/login", data={
            "username": username,
            "password": "testpassword123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[TEST] Logged in successfully")

        # 3. Connect via WebSocket
        async with websockets.connect(f"{WS_URL}?token={token}") as ws:
            print("[TEST] WebSocket connected")

            # 4. Request a song
            request_msg = {
                "action": "REQUEST_SONG",
                "track_id": "track_002" # Psytrance track, should fit v1.5.0 logic
            }
            await ws.send(json.dumps(request_msg))
            resp = await ws.recv()
            data = json.loads(resp)
            print(f"[TEST] Request response: {data.get('type')}")

            # 5. Vote for a track
            vote_msg = {
                "action": "VOTE_TRACK",
                "track_id": "track_002"
            }
            await ws.send(json.dumps(vote_msg))
            print("[TEST] Vote sent")

        # 6. Submit feedback
        fb_res = await client.post(f"{BASE_URL}/api/feedback", headers=headers, json={
            "vibe_rating": 5,
            "technical_rating": 4,
            "comment": "Simulation feedback"
        })
        assert fb_res.status_code == 200
        print("[TEST] Feedback submitted")

    print("[TEST] Journey Simulation Complete: SUCCESS")

if __name__ == "__main__":
    asyncio.run(simulate_user_journey())
