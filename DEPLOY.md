# DEPLOY.md

## Environment Requirements
- Python 3.9+
- SQLite3
- ffmpeg (for `auto_dj_script` processing)

## Local Development
1. Clone the repo with submodules: `git clone --recursive <repo_url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize the database: `python src/init_db.py`
4. Start the server: `uvicorn src.main:app --reload`
5. Access the PWA at `http://localhost:8000/static/index.html`

## Cloud Deployment
- The FastAPI Conductor can be deployed to AWS/GCP/Heroku.
- The C++ Audio Engine should ideally run on a local machine connected to the venue's sound system, communicating with the cloud Conductor via WebSockets.
