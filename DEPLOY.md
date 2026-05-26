# Deployment Guide: Crowdsourced Dance Club (CDC)

## Conductor Server (Python)
### Prerequisites
- Python 3.12+
- pip

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
   git clone --recursive <repo-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r external/auto_dj_script/requirements.txt
   ```
3. Initialize the database:
   ```bash
   python src/init_db.py
   ```
4. Run the server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

## Audio Engine (C++)
### Prerequisites
- g++ (C++11 support)
- PortAudio
- libwebsockets
- libsndfile
- SoundTouch
- nlohmann-json-dev

### Build & Run
```bash
cd engine
make
./cdc_engine
```

## Web Client Prototype
Accessible at `http://localhost:8000` once the Conductor Server is running.
- **Admin Mode:** Tap the "CDC" header 5 times to enable.
