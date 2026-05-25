import asyncio
import json
import websockets
import time

async def mock_audio_engine():
    uri = "ws://localhost:8000/ws/clubgoer"
    print(f"[*] Connecting to Conductor at {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[+] Connected! Monitoring for TRACK_SYNC events.")

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") == "TRACK_SYNC":
                    sync_data = data["data"]
                    print(f"\n[ENGINE] >>> RECEIVED TRACK_SYNC <<<")
                    print(f"[ENGINE] Track: {sync_data['track_id']}")
                    print(f"[ENGINE] BPM: {sync_data['bpm']}")
                    print(f"[ENGINE] Key: {sync_data['key']}")
                    print(f"[ENGINE] Crossfade Start: {sync_data['transition_timestamp']}")

                    # Simulate buffering
                    print("[ENGINE] Buffering and warping track...")
                    await asyncio.sleep(2)
                    print("[ENGINE] Buffer ready for transition.")

                elif data.get("type") == "QUEUE_SYNC":
                    # Periodic heartbeat from Conductor
                    # Send PLAYBACK_STATE back (simulated)
                    playback_state = {
                        "type": "PLAYBACK_STATE",
                        "data": {
                            "current_track_id": data["current_track"]["id"],
                            "playback_position_seconds": time.time() - data["start_time"],
                            "current_bpm": data["target_bpm"],
                            "cpu_load": 0.05
                        }
                    }
                    # Note: /ws/clubgoer currently ignores PLAYBACK_STATE,
                    # but we send it to verify protocol compliance.
                    # await websocket.send(json.dumps(playback_state))

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(mock_audio_engine())
    except KeyboardInterrupt:
        print("\n[*] Engine shut down.")
