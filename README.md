# crowdsourced_dance_club

let's also make this into a server that mixes in realtime and then make phone app clients so that dance club goers can submit songs to mix in and the auto-dj decides based on theme and fit

That sounds like an awesome crowd-sourced project. Building a collaborative, algorithmic club-night engine where users dynamically steer the direction via an app is a great software architecture challenge.

However, moving from an offline compiler script (which has the luxury of looking ahead at whole files) to a real-time streaming server completely changes the engineering constraints. You can't just run heavy librosa time-stretch functions on the fly without causing severe audio dropouts and latency issues.

To build a real-time, zero-latency mixing engine with a mobile crowd-sourcing frontend, you have to break the system architecture into three distinct layers.

The 3-Tier System Architecture
[ Mobile Clients (iOS/Android) ] ──(WebSockets: Song Requests & Votes)──┐
                                                                       ▼
[ Python AI Conductor Server ] ◄──(Redis Queue: Order & Harmony)───────┤
                                                                       ▼
[ C++ Real-time Audio Engine ] ◄──(Low-Latency Live Audio Pipeline)────┘
1. The Mobile Client App (React Native or Flutter)
The Workflow: Users open the app at the venue. It displays the Current Track playing (with its artwork, BPM, and key) and a Voting Queue of upcoming tracks.

The User Action: Dancers can browse a curated catalog of tracks, submit a request, or vote up songs already in the queue.

The Networking: The app maintains a persistent WebSocket connection to the server to receive live, real-time updates of the queue, current playback time, and active votes.

2. The Python AI Conductor (The Gatekeeper Server)
This server acts as the brains of the operation. It hosts the API endpoints for the mobile apps, manages user votes, and runs the "Theme & Fit" evaluation logic.

The Filtering Rule: When a user requests a song, the script uses a lightweight database (like SQLite or PostgreSQL) holding pre-analyzed track metadata (BPM, Key, Energy Level, Genre Sub-tag like "Full-on", "Progressive", or "Twilight").

The "Fit" Algorithm: The conductor evaluates the requested song against the current track using rules like Harmonic Distance (Camelot Wheel step ±1) and Energy Variance (e.g., maximum step change of ±5% energy). If a user requests a slow 135 BPM progressive track while the floor is at a peak 145 BPM full-on twilight state, the AI dynamically lowers its ranking or rejects it, notifying the user that the vibe isn't compatible right now.

3. The Low-Latency Audio Engine (The Heavy Lifter)
Why Python fails here: You cannot easily build the actual real-time audio playback loop in pure Python. Python’s Global Interpreter Lock (GIL) and garbage collection will introduce microscopic hesitations, causing the audio to glitch or skip over the club's sound system.

The Real-Time Solution: You use a low-level framework designed for live audio processing. A common, robust architecture is writing a C++ audio engine utilizing SuperCollider, JUCE, or a specialized Node.js/C++ audio streaming pipeline linked to libsoundio or PortAudio.

How it works in real-time: The engine keeps a high-priority, steady audio buffer open to the hardware soundcard. It streams the current track linearly. When the Conductor Server alerts it that a transition is approaching in 32 bars, the engine pre-loads the winning track from disk into a secondary buffer, performs instant linear interpolation time-stretching to match the current master BPM, and automates the high-pass/low-pass frequency filters in real-time as the tracks crossfade.

The Real-Time WebSocket Conductor (Server Blueprint)
To give you a foundation for the orchestration layer, here is a Python server blueprint using FastAPI and WebSockets. It acts as the central hub—managing a real-time track queue, evaluating incoming mobile song requests based on an energy/BPM "fit" score, and broadcasting the live queue updates out to all connected smartphone clients.

Python
import asyncio
import json
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="Algorithmic DJ Conductor Server")

# Mock database of the curated club music catalog
TRACK_CATALOG = {
    "track_001": {"title": "Awake the Machine", "artist": "Astrix", "bpm": 145.0, "key": "9A", "energy": 9.5},
    "track_002": {"title": "Universal Frequencies", "artist": "Alienatic", "bpm": 145.0, "key": "10A", "energy": 8.8},
    "track_003": {"title": "Mushroom Song (EU Remix)", "artist": "Killerwatts", "bpm": 145.0, "key": "9A", "energy": 9.8},
    "track_004": {"title": "Deep Dive", "artist": "Save The Robot", "bpm": 138.0, "key": "5A", "energy": 6.2}, # Low energy/BPM clash
}

class TrackState:
    def __init__(self):
        # Current state of the club sound system
        self.current_track = TRACK_CATALOG["track_001"]
        self.target_bpm = 145.0
        self.upcoming_queue: List[Dict] = []
        self.connected_clients: List[WebSocket] = []

dj_state = TrackState()

class ConnectionManager:
    """Manages active smartphone WebSocket client connections."""
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        dj_state.connected_clients.append(websocket)
        # Immediately push current state to the new client
        await websocket.send_json(self.get_broadcast_payload())

    def disconnect(self, websocket: WebSocket):
        dj_state.connected_clients.remove(websocket)

    async def broadcast_queue_update(self):
        payload = self.get_broadcast_payload()
        for connection in dj_state.connected_clients:
            try:
                await connection.send_json(payload)
            except Exception:
                pass # Handle dead connections gracefully

    def get_broadcast_payload(self):
        return {
            "type": "QUEUE_SYNC",
            "current_track": dj_state.current_track,
            "target_bpm": dj_state.target_bpm,
            "queue": dj_state.upcoming_queue
        }

manager = ConnectionManager()

def evaluate_track_fit(requested_track: Dict, current_track: Dict) -> tuple[bool, str]:
    """
    Algorithmic Vibe Check: Assesses if a requested song safely fits 
    the current energy matrix and tempo of the dancefloor.
    """
    # Rule 1: Tempo Check (Prevent severe time-stretching distortion)
    bpm_delta = abs(requested_track["bpm"] - current_track["bpm"])
    if bpm_delta > 5.0:
        return False, f"BPM clash too severe ({requested_track['bpm']} vs {current_track['bpm']}). Would cause audio warp distortion."
    
    # Rule 2: Energy Vibe Check (Prevent killing the dancefloor energy)
    energy_delta = abs(requested_track["energy"] - current_track["energy"])
    if energy_delta > 3.0:
         return False, "Energy delta error: Transition is too abrupt for the current floor vibe."
         
    return True, "Track fits the sonic profile perfectly."

@app.websocket("/ws/clubgoer")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time portal for clubgoers to vote and request songs."""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for incoming JSON messages from a user's phone
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "REQUEST_SONG":
                track_id = message.get("track_id")
                requested_track = TRACK_CATALOG.get(track_id)
                
                if not requested_track:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found in club database."})
                    continue
                
                # Run the algorithmic fit validation
                fits, reason = evaluate_track_fit(requested_track, dj_state.current_track)
                
                if fits:
                    # Append to queue and notify the entire room via real-time broadcast
                    dj_state.upcoming_queue.append(requested_track)
                    await websocket.send_json({"type": "REQUEST_ACCEPTED", "message": reason})
                    await manager.broadcast_queue_update()
                else:
                    # Deny request and give the user feedback on why it failed the vibe check
                    await websocket.send_json({"type": "REQUEST_DENIED", "message": reason})
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
What to Tackle Next
To bring this platform to life, the execution splits cleanly down the middle:

The Infrastructure Frontend: You would build a frontend interface (like a React Native mobile view) that talks to this server, sending REQUEST_SONG payloads when a user taps a track card and listening for QUEUE_SYNC messages to render the updated track stack dynamically.

The Audio Pipeline Backend: You would pipe the server's validated upcoming_queue array into a dedicated audio application framework. The audio application listens to the server queue, reads the actual audio file data off the disk, and runs the live mixing blocks over the venue speakers.

This completely shifts the concept from a static, pre-rendered playback file to a highly reactive, real-time interactive audio installation.

should i make that as a separate project or a fork of this one?

To give you the most accurate advice, I need a little more context on what "that" and "this one" refer to.

Since your current prompt is a standalone question, could you tell me a bit about the project you are looking at and the new features or changes you are planning to make?

the auto_dj_script from the start of the conversation, should i fork the existing project jules has been working on or just add this functionality to it?

Make it a separate project (or a completely isolated repository)—do not add it directly into Jules’s existing script.

While the core concept is the same, the actual engineering under the hood is night and day. If you try to force real-time server architecture into an offline compiler script, you will rip apart his codebase, cause immense merge friction, and end up breaking the utility he already built.

Here is why keeping them strictly separate is the smart play:

1. The Core Engines are Mutually Exclusive
Jules’s Script is a Batch Processor. It relies on CPU-heavy lookaheads (librosa time-stretching, full-array NumPy data operations, and multi-gigabyte file manipulation) to render an uncompressed .flac file to disk. It doesn’t care about latency or RAM constraints because it runs offline.

Your Server System is an Asynchronous Stream Controller. It relies on non-blocking task loops, concurrent WebSocket pipelines, and low-latency buffer feeding.

If you drop real-time audio arrays and network sockets into an offline compiler, Jules’s sequential loops will choke the server, causing micro-stutters and audio dropouts on your stream.

2. Dependency Pollution
Jules’s script is lean—it just needs an audio decoder (ffmpeg) and math processors (numpy, librosa, scipy).
Your project requires an entire web infrastructure stack: async network frameworks (FastAPI, uvicorn), database connectors for track matching, and client-facing network protocols. Forcing your massive network dependencies into his local script creates a bloated repository that is a nightmare to deploy or debug.

3. The Clean Architecture Play: Split-Service Design
The most elegant way to execute this is to keep Jules’s code intact as a microservice, rather than deleting it.

[ Your FastAPI Server ] ──(Trigger Network Request)──> [ Jules's Compiler Script ] 
                                                                 │
                                                          (Renders Master File)
                                                                 │
                                                                 ▼
[ Complete Live Set ] <──(Stream Finished WAV/FLAC) <────────────┘
If a user wants to render a static, pre-planned 5-hour mix ahead of time, your API can simply hit Jules’s script in a background worker thread (like Celery), let it chew on the audio arrays offline, and then return the polished file to the app client.

Keep Jules's script as a standalone, specialized backend utility tool, and build your real-time crowd-sourced streaming network as a fresh, separate repository. It protects his working code and gives you a completely clean slate to build an interactive platform.

should i include auto_dj_script as a submodule in the new project?

Yes, using a Git submodule is exactly the right software engineering move here.

It gives you the best of both worlds: your new streaming network project stays completely clean and decoupled, but you still maintain a direct, version-controlled link to Jules's compiler code without duplicating files or copy-pasting code.

Here is why this fits your architecture perfectly, along with the operational pipeline to set it up:

Why a Submodule Wins Here
Upstream Syncing: If Jules updates his time-stretching logic, fixes a bug in the high-pass filter DSP block, or optimizes librosa memory usage, you don’t have to manually port those changes over. You just pull the updates directly into your submodule.

Separation of Concerns: Your main repository focuses entirely on network orchestration, WebSocket traffic, database track matching, and client app API routes. Jules's code sits quietly in its own directory, acting strictly as an internal processing utility.

Clean Deployment: When you deploy your server to a cloud instance, Git will pull down your networking stack and then initialize his processing scripts automatically, keeping environmental dependencies isolated.

How to Initialize the Submodule Architecture
When you are ready to link Jules's repo into your new server project, open your terminal in the root of your new project directory and run the following commands:

Bash
# 1. Add Jules's repository as a submodule in a specific subfolder
git submodule add https://github.com/username/auto_dj_script.git external/auto_dj_script

# 2. Commit the new tracking link to your repository
git add .gitmodules external/auto_dj_script
git commit -m "infrastructure: integrate auto_dj_script as an external compilation submodule"
This creates a hidden .gitmodules file in your root directory that maps the exact commit hash of his project to yours, ensuring your server always pulls the exact version of his code that you tested against.

Integrating the Code via Your Python Pipeline
Once it's linked, importing his compiler function into your FastAPI server is incredibly clean. You just treat that subdirectory as a standard local Python module.

In your server script, you can import and trigger his offline rendering pipeline as a background task like this:

Python
import sys
import os
from fastapi import FastAPI, BackgroundTasks

# Append the submodule directory to the system path so Python can resolve imports
sys.path.append(os.path.abspath("./external/auto_dj_script"))

# Import Jules's core compilation engine directly
from auto_dj_script import compile_master_set 

app = FastAPI()

def run_offline_compiler_worker(source_dir, output_file):
    """Background worker that calls the submodule to crunch audio offline."""
    compile_master_set(source_dir, output_file, bpm=145.0)

@app.post("/api/render-set")
async def render_compiled_set(background_tasks: BackgroundTasks):
    """
    API endpoint that accepts a finalized room playlist from the phone apps
    and spins up Jules's script in a background thread to render the WAV.
    """
    source_folder = "./pending_room_tracks"
    output_path = "./static_renders/final_room_mix.flac"
    
    # Delegate the heavy lifting to the submodule without blocking the main event loop
    background_tasks.add_task(run_offline_compiler_worker, source_folder, output_path)
    
    return {"status": "processing", "message": "Submodule background worker initialized."}
This keeps your real-time WebSocket loops lightning-fast and responsive for the dancers' phones, while delegating the heavy NumPy array processing to Jules's submodule completely on the side. It's a textbook, highly professional multi-service design pattern.
