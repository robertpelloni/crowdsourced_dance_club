import time
import json
from locust import HttpUser, task, between, events
import websocket
import threading

class CrowdMember(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Connect to WebSocket on start"""
        self.ws = websocket.WebSocket()
        # Connect to the clubgoer socket for requesting and voting
        self.ws.connect(f"ws://{self.host.replace('http://', '').replace('https://', '')}/ws/clubgoer")

        # Start a background thread to receive messages to keep socket alive
        def receive_messages():
            while True:
                try:
                    self.ws.recv()
                except Exception:
                    break
        threading.Thread(target=receive_messages, daemon=True).start()

    @task(3)
    def vote_on_random_track(self):
        """Simulate high-frequency voting"""
        self.ws.send(json.dumps({
            "action": "VOTE_TRACK",
            "track_id": "track_002"  # Hardcoding a likely catalog track for load
        }))

    @task(1)
    def request_new_track(self):
        """Simulate requesting a new track occasionally"""
        self.ws.send(json.dumps({
            "action": "REQUEST_SONG",
            "track_id": "track_003"
        }))

    @task(2)
    def fetch_catalog(self):
        """Simulate users looking at the catalog"""
        self.client.get("/catalog", name="Fetch Catalog")

    def on_stop(self):
        self.ws.close()

# Note: You can run this with `locust -f tests/locustfile.py --host http://localhost:80`
