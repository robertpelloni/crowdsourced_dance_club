# Deployment Guide: Crowdsourced Dance Club (CDC)

This document outlines the procedures for deploying CDC to staging and production environments up to Phase 5.

## Architecture Overview
- **Brain (Python):** FastAPI orchestration, Neural Conductor (scikit-learn ML), and multi-tenant scaling via Redis Pub/Sub.
- **Body (C++):** Real-time audio engine with PortAudio, SoundTouch, libftdi (for DMX hardware), and instantaneous RMS/Peak telemetry extraction.
- **Interface (Web/Mobile):** React Native mobile client, PWA Admin dashboard, and Three.js WebXR ("Vibe Orb").

---

## 🚀 Rapid Deployment (Recommended)

### Staging
Use the automated staging script for CI/CD or internal testing:
```bash
./deploy_staging.sh
```

### Production
Use the production script for optimized performance and non-destructive DB handling:
```bash
./deploy_production.sh
```

---

## 🛠 Manual Configuration

### 1. Conductor Server (Python)
**Prerequisites:** Python 3.12+, `pip`, `sqlite3`, `redis-server`.

**Environment Variables:**
- `SECRET_KEY`: (Required) Cryptographic secret for JWT signing.
- `PORT`: (Optional) Default is 8000.
- `DEBUG`: Set to `False` in production.

**Run Production Command:**
```bash
# Ensure Redis is running in the background for Pub/Sub scaling
redis-server &
uvicorn src.main:app --host 0.0.0.0 --port 80 --workers 4
```

### 2. Audio Engine (C++)
**Prerequisites:** `g++` (C++20), `PortAudio`, `libwebsockets`, `libsndfile`, `SoundTouch`, `libftdi1-dev`, `nlohmann-json-dev`.

**Production Build:**
```bash
cd engine
make clean
make CXXFLAGS="-O3 -std=c++20 -DNDEBUG"
./cdc_engine
```

---

## 📱 Mobile App (Expo) & WebXR
1. **Configure API Endpoint:**
   - Scan the QR code from the server's `/sync-qr` endpoint to automatically configure the mobile client.
2. **Launch WebXR Visualizer:**
   - Navigate to `/static/vibe_orb.html` on a connected display to render the real-time audio-reactive Three.js representation.

## 🔒 Security Hardening
- **JWT:** Ensure `SECRET_KEY` is rotated periodically.
- **RBAC:** Admin privileges are restricted to the `admin` role in the `users` table.
- **WebSocket:** Use `wss://` (Secure WebSockets) in production by terminating SSL at the load balancer or reverse proxy level (e.g., Nginx).

## 📊 Monitoring
- **Crowd Stats:** Monitor `/api/live/crowd-stats` for engagement metrics.
- **Shadow Pilot:** Review `/api/admin/shadow-pilot/status` to ensure background auto-healing processes are healthy.
- **Vibe Logs:** Analyze `vibe_performance_logs` table in `tracks.db` for ML model training data.
