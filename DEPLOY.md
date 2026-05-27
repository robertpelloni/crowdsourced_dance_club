# Deployment Guide: Crowdsourced Dance Club (CDC)

This document outlines the procedures for deploying CDC to staging and production environments.

## Architecture Overview
- **Brain (Python):** FastAPI orchestration, RBAC, and ML-ready vibe scoring.
- **Body (C++):** Real-time audio engine with PortAudio, SoundTouch, and low-latency DSP.
- **Interface (Web/Mobile):** React Native mobile client and PWA Admin dashboard.

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
**Prerequisites:** Python 3.12+, `pip`, `sqlite3`.

**Environment Variables:**
- `SECRET_KEY`: (Required) Cryptographic secret for JWT signing.
- `PORT`: (Optional) Default is 8000.
- `DEBUG`: Set to `False` in production.

**Run Production Command:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 80 --workers 4
```

### 2. Audio Engine (C++)
**Prerequisites:** `g++` (C++20), `PortAudio`, `libwebsockets`, `libsndfile`, `SoundTouch`, `nlohmann-json-dev`.

**Production Build:**
```bash
cd engine
make clean
make CXXFLAGS="-O3 -std=c++20 -DNDEBUG"
./cdc_engine
```

---

## 📱 Mobile App (Expo)
1. **Configure API Endpoint:**
   - Scan the QR code from the server's `/sync-qr` endpoint to automatically configure the mobile client.
2. **Build for Release:**
   ```bash
   cd mobile
   npx expo prebuild
   # Build for Android/iOS following standard Expo/React Native procedures.
   ```

## 🔒 Security Hardening
- **JWT:** Ensure `SECRET_KEY` is rotated periodically.
- **RBAC:** Admin privileges are restricted to the `admin` role in the `users` table.
- **WebSocket:** Use `wss://` (Secure WebSockets) in production by terminating SSL at the load balancer or reverse proxy level (e.g., Nginx).

## 📊 Monitoring
- **Crowd Stats:** Monitor `/api/live/crowd-stats` for engagement metrics.
- **Vibe Logs:** Analyze `vibe_performance_logs` table in `tracks.db` for ML model training data.
