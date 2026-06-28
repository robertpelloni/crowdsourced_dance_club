#!/bin/bash
set -e

echo "[STAGING] Starting deployment pipeline..."

# 1. Environment Check
python3 --version
g++ --version

# 2. Install Dependencies
echo "[STAGING] Installing Python dependencies..."
pip install -r requirements.txt
pip install -r external/auto_dj_script/requirements.txt

# 3. Database Initialization
echo "[STAGING] Initializing database..."
python3 src/init_db.py
if [ ! -f "tracks.db" ]; then
    echo "[ERROR] Database initialization failed: tracks.db not found!"
    exit 1
fi
echo "[STAGING] Database initialization verified."

# 4. Build Audio Engine
echo "[STAGING] Building C++ Audio Engine..."
make -C engine clean
make -C engine
if [ ! -x "engine/cdc_engine" ]; then
    echo "[ERROR] C++ Engine compilation failed: cdc_engine executable not found!"
    exit 1
fi
echo "[STAGING] C++ Engine compiled successfully."

# 5. API Health Check (Background API Start)
echo "[STAGING] Starting FastAPI server for health check..."
export PYTHONPATH=$PYTHONPATH:.
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

echo "[STAGING] Waiting for server to initialize (5s)..."
sleep 5

echo "[STAGING] Hitting /api/events endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/events || true)
if [ "$HEALTH_STATUS" != "200" ]; then
    echo "[ERROR] Conductor API health check failed (HTTP $HEALTH_STATUS)"
    kill $UVICORN_PID
    exit 1
fi
echo "[STAGING] Conductor API /api/events check passed (HTTP 200)."

echo "[STAGING] Shutting down Fast API server..."
kill $UVICORN_PID

# 6. Integration Smoke Test
echo "[STAGING] Running integration smoke tests..."
python3 -m pytest tests/

echo "[STAGING] Deployment to staging environment complete."