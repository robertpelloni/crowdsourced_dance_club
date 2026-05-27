# Real-Time Audio Engine Protocol (v1.0)

This document defines the communication protocol between the **Python AI Conductor** (Server) and the **C++ Real-Time Audio Engine** (Client/Player).

## Communication Method
- **Primary:** WebSockets (Low-latency JSON payloads)
- **Secondary/Optional:** OSC (Open Sound Control) for high-performance parameter modulation.

## WebSocket Message Types

### 1. Track Sync (Server -> Engine)
Sent when the conductor prepares the next track for the engine's secondary buffer.

```json
{
  "type": "TRACK_SYNC",
  "data": {
    "track_id": "track_002",
    "filepath": "/path/to/audio/universal_frequencies.flac",
    "bpm": 145.0,
    "key": "10A",
    "energy": 8.8,
    "transition_timestamp": 1725430800.5,
    "crossfade_duration": 15.0
  }
}
```

### 2. Playback State (Engine -> Server)
Sent periodically (e.g., every 100ms) by the engine to keep the conductor informed of actual playback progress.

```json
{
  "type": "PLAYBACK_STATE",
  "data": {
    "current_track_id": "track_001",
    "playback_position_seconds": 124.5,
    "current_bpm": 145.0,
    "cpu_load": 0.12
  }
}
```

### 3. Master Controls (Server -> Engine)
Immediate overrides from the Conductor/Admin.

```json
{
  "type": "MASTER_CONTROL",
  "data": {
    "action": "SKIP_NOW",
    "target_bpm": 148.0,
    "master_volume": 0.8
  }
}
```

## Performance Constraints
- The Audio Engine MUST maintain a high-priority audio thread.
- WebSocket handling MUST be performed on a separate networking thread to avoid blocking the audio callback.
- Jitter buffer management is required if streaming over a network rather than local Unix sockets.
