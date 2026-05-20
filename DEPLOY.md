# Deployment Instructions

## Conductor Server (Python)
### Prerequisites
- Python 3.9+
- pip

### Setup
1. Clone the repository with submodules:
   ```bash
   git clone --recursive <repo-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

## Audio Engine (TBD)
- Deployment instructions for the C++ audio engine will be added in Phase 3.

## Mobile Client (TBD)
- Deployment instructions for the mobile app will be added in Phase 2.
