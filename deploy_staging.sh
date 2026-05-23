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

# 4. Build Audio Engine
echo "[STAGING] Building C++ Audio Engine..."
cd engine
make clean
make
cd ..

# 5. Integration Smoke Test
echo "[STAGING] Running integration smoke tests..."
export PYTHONPATH=$PYTHONPATH:.
python3 -m pytest tests/

echo "[STAGING] Deployment to staging environment complete."
