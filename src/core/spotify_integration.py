import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import requests
import tempfile
import librosa
import numpy as np

# We'll rely on environment variables for keys:
# SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
# If not set, we'll mock the responses for testing purposes.

def get_spotify_client():
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))

def get_track_metadata(url_or_id):
    sp = get_spotify_client()
    if not sp:
        # Return mock data if no API keys
        return {
            "title": "Mock Spotify Track",
            "artist": "Mock Artist",
            "bpm": 138.0,
            "key": "8A",
            "energy": 8.5,
            "genre": "Progressive",
            "preview_url": "mock_url"
        }

    try:
        track = sp.track(url_or_id)
        audio_features = sp.audio_features(track['id'])[0]

        # Mapping Spotify key/mode to Camelot Wheel (simplified approximation)
        key_map_major = {0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B", 6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B"}
        key_map_minor = {0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A", 6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A"}

        key_str = key_map_major.get(audio_features['key'], "8B") if audio_features['mode'] == 1 else key_map_minor.get(audio_features['key'], "8A")

        # Approximate energy 0-10
        energy = audio_features['energy'] * 10

        return {
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "bpm": audio_features['tempo'],
            "key": key_str,
            "energy": round(energy, 1),
            "genre": "Mixed", # Spotify track API doesn't give genre directly, would need artist API
            "preview_url": track['preview_url']
        }
    except Exception as e:
        print(f"Spotify API error: {e}")
        return None

def analyze_audio_from_url(url):
    """
    Downloads audio from URL to a temp file and runs librosa analysis to find BPM.
    Used as fallback if Spotify API lacks data.
    """
    if url == "mock_url":
        return 138.0

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_audio.write(chunk)
                temp_filename = temp_audio.name

            # Use librosa to load and estimate tempo
            y, sr = librosa.load(temp_filename, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            os.remove(temp_filename)
            return float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
    except Exception as e:
        print(f"Error analyzing audio: {e}")

    return 120.0
