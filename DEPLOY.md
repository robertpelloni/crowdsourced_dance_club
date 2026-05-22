# Deployment Instructions

## Conductor Server (Python)
### Prerequisites
- Python 3.12+
- pip

### Setup
1. Clone the repository with submodules:
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
