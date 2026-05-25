# Project Libraries & Dependencies

This document lists all major libraries used in the project, their versions (where specified), and the rationale for their selection within the 3-tier architecture.

## Tier 2: Python AI Conductor (Main Project)

| Library | Version | Role | Reason for Selection |
| :--- | :--- | :--- | :--- |
| **FastAPI** | Latest | Web Framework | Extremely fast (Starlette-based), native async support, and automatic OpenAPI documentation. Perfect for low-latency WebSockets. |
| **Uvicorn** | Latest | ASGI Server | The industry standard for running FastAPI applications with high concurrency. |
| **Pydantic** | v2+ | Data Validation | Ensures that track metadata and WebSocket payloads are type-safe and validated at the boundary. |
| **Websockets** | Latest | Real-time Comms | Used by FastAPI to handle persistent connections with mobile clients for queue synchronization. |
| **SQLite3** | Standard | Database | Zero-configuration, file-based persistence. Ideal for the `TRACK_CATALOG` and `upcoming_queue` in a prototype/on-premise venue setup. |
| **Pytest** | v9+ | Testing | Robust testing framework used for verifying API endpoints and the `evaluate_track_fit` logic. |
| **HTTPX** | Latest | Async HTTP Client | Used within tests to perform asynchronous requests to the FastAPI application. |

## Submodule: Audio Processing (external/auto_dj_script)

| Library | Version | Role | Reason for Selection |
| :--- | :--- | :--- | :--- |
| **Librosa** | 0.11.0 | Audio Analysis | The gold standard for feature extraction. Used to detect BPM, Harmonic Key (chroma), and Energy (RMS/Spectral) levels. |
| **NumPy** | 2.0.0+ | Math/Arrays | Provides the high-performance numerical arrays used for all digital signal processing. |
| **SciPy** | 1.13.0+ | DSP Filters | Used for implementing Butterworth filters (High-pass/Low-pass) in the offline rendering pipeline. |
| **Pydub** | 0.25.1 | Audio Utility | Simplifies audio file slicing, concatenation, and format conversion. |
| **Soundfile** | 0.13.1 | Audio I/O | Handles high-bitrate reading and writing of FLAC/WAV files without compression artifacts. |
| **PyLoudNorm** | 0.2.0 | Normalization | Implements EBU R128 loudness normalization to ensure consistent volume across the mix. |
| **TQDM** | 4.67.3 | UX | Provides progress bars for long-running offline render tasks. |

## Tier 3: C++ Real-Time Audio Engine (engine/)

| Library | Role | Reason for Selection |
| :--- | :--- | :--- |
| **PortAudio** | Audio I/O | Cross-platform, low-latency API for real-time audio playback. |
| **libwebsockets** | Networking | Lightweight, high-performance C library for WebSocket client/server communication. |
| **nlohmann/json** | Data Handling | Header-only JSON library for C++. Easy to integrate and used for protocol parsing. |
| **SoundTouch** | DSP/Tempo | Optimized C++ library for real-time tempo and pitch shifting without changing each other. |

## Tier 1: Mobile App (Initialized)

| Library | Role | Reason for Selection |
| :--- | :--- | :--- |
| **React Native** | Cross-platform UI | Allows for a single codebase for both iOS and Android with native performance. |
| **Expo** | Development Tooling | Simplifies deployment, haptic integration, and local development workflows. |
| **React Native Haptic Feedback** | User Engagement | Provides tactile pulses synchronized with the music's beat or transitions. |
