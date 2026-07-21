#!/bin/bash
set -e

echo "Building C++ Audio Engine..."
make -C engine clean all

echo "Starting Python Conductor Server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
PID_SERVER=$!

echo "Starting C++ Real-Time Engine in Production Mode..."
./engine/audio_engine &
PID_ENGINE=$!

echo "System running. Press Ctrl+C to stop."
wait $PID_SERVER $PID_ENGINE
