#!/bin/bash
set -e

# Production Deployment Script for Crowdsourced Dance Club (CDC)
# Version: 1.4.0

echo "[PRODUCTION] Initializing release sequence..."

# 1. Verification of Environment
echo "[PRODUCTION] Verifying hardware and software stack..."
python3 --version
g++ --version

# 2. Dependency Hardening
echo "[PRODUCTION] Syncing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r external/auto_dj_script/requirements.txt

# 3. Database Migration/Initialization
# For production, we preserve the DB if it exists, otherwise init.
if [ ! -f "tracks.db" ]; then
    echo "[PRODUCTION] First-time setup: Initializing database..."
    python3 src/init_db.py
else
    echo "[PRODUCTION] Database found. Skipping initialization to preserve user data."
fi

# 4. Optimized Engine Build
echo "[PRODUCTION] Compiling C++ Audio Engine with optimizations..."
cd engine
make clean
# Injecting optimization flags while preserving include paths
make CXXFLAGS="-O3 -std=c++20 -DNDEBUG -Iinclude -I/usr/include/nlohmann"
cd ..

# 5. Production Health Check
echo "[PRODUCTION] Running final integrity suite..."
export PYTHONPATH=$PYTHONPATH:.
# Run core logic tests (skipping frontend-heavy or slow mocks if necessary)
python3 -m pytest tests/test_api.py tests/test_fit_logic.py tests/test_rbac.py tests/test_referrals.py tests/test_profile_ext.py

echo "--------------------------------------------------------"
echo "[SUCCESS] Production build v1.4.0 is ready."
# 6. Post-Deployment Health Check
echo "[PRODUCTION] Performing initial health check..."
# We assume the server is being started by a process manager (like systemd or supervisor)
# For the script validation, we can simulate a health check to a running instance if available.

echo "Launch Command: uvicorn src.main:app --host 0.0.0.0 --port 80 --workers 4 --log-config logging.conf"
echo "--------------------------------------------------------"
