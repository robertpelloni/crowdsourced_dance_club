import os
import requests
import tempfile

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    spotipy = None
    SpotifyClientCredentials = None
    SPOTIPY_AVAILABLE = False

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    librosa = None
    np = None
    LIBROSA_AVAILABLE = False

# We'll rely on environment variables for keys:
# SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
# If not set or if spotipy is not installed, we'll mock the responses for testing purposes.

def get_spotify_client():
    if not SPOTIPY_AVAILABLE:
        return None
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

def search_spotify_tracks(query, limit=5):
    """
    Searches Spotify for tracks matching a search query.
    Falls back to a curated mock set if Spotify API credentials are not set.
    """
    sp = get_spotify_client()
    if not sp:
        # Curated mock catalog representing the Infinite Catalog
        curated_mock_pool = [
            {"id": "mock_sp_1", "title": "Strobe", "artist": "deadmau5", "bpm": 128.0, "key": "8B", "energy": 7.8, "genre": "Progressive House"},
            {"id": "mock_sp_2", "title": "Opus", "artist": "Eric Prydz", "bpm": 126.0, "key": "11B", "energy": 8.6, "genre": "Progressive House"},
            {"id": "mock_sp_3", "title": "Sun & Moon", "artist": "Above & Beyond", "bpm": 134.0, "key": "4A", "energy": 8.9, "genre": "Trance"},
            {"id": "mock_sp_4", "title": "Language", "artist": "Porter Robinson", "bpm": 128.0, "key": "7B", "energy": 8.2, "genre": "Electro"},
            {"id": "mock_sp_5", "title": "Children", "artist": "Robert Miles", "bpm": 138.0, "key": "10A", "energy": 8.4, "genre": "Dream Trance"},
            {"id": "mock_sp_6", "title": "Adagio for Strings", "artist": "Tiësto", "bpm": 140.0, "key": "5A", "energy": 9.5, "genre": "Trance"},
        ]
        q_lower = query.lower().strip()
        matched = [
            t for t in curated_mock_pool
            if q_lower in t["title"].lower() or q_lower in t["artist"].lower() or q_lower in t["genre"].lower()
        ]
        if not matched and q_lower:
            # Generate dynamic mock result based on user query
            matched = [{
                "id": f"mock_dynamic_{abs(hash(query)) % 10000}",
                "title": query.title(),
                "artist": "Dynamic Artist",
                "bpm": 132.0,
                "key": "9A",
                "energy": 8.0,
                "genre": "Dance",
            }]
        return matched[:limit]

    try:
        results = sp.search(q=query, type='track', limit=limit)
        items = results.get('tracks', {}).get('items', [])
        formatted = []
        for item in items:
            track_id = item['id']
            try:
                features = sp.audio_features([track_id])[0] or {}
            except Exception:
                features = {}

            key_map_major = {0: "8B", 1: "3B", 2: "10B", 3: "5B", 4: "12B", 5: "7B", 6: "2B", 7: "9B", 8: "4B", 9: "11B", 10: "6B", 11: "1B"}
            key_map_minor = {0: "5A", 1: "12A", 2: "7A", 3: "2A", 4: "9A", 5: "4A", 6: "11A", 7: "6A", 8: "1A", 9: "8A", 10: "3A", 11: "10A"}

            k_idx = features.get('key', 0)
            mode = features.get('mode', 1)
            key_str = key_map_major.get(k_idx, "8B") if mode == 1 else key_map_minor.get(k_idx, "8A")
            energy = round(features.get('energy', 0.8) * 10, 1)
            tempo = round(features.get('tempo', 128.0), 1)

            formatted.append({
                "id": track_id,
                "title": item['name'],
                "artist": item['artists'][0]['name'] if item.get('artists') else "Unknown",
                "bpm": tempo,
                "key": key_str,
                "energy": energy,
                "genre": "Dance",
                "preview_url": item.get('preview_url')
            })
        return formatted
    except Exception as e:
        print(f"Error searching Spotify: {e}")
        return []

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
