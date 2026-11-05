import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_live_audio_stream_endpoint():
    """Verify that /api/audio/stream returns an audio/wav streaming response with a valid WAV header."""
    with client.stream("GET", "/api/audio/stream") as response:
        assert response.status_code == 200
        assert "audio/wav" in response.headers.get("content-type", "")

        # Read first chunk which contains the 44-byte WAV header
        header_chunk = next(response.iter_bytes())
        assert len(header_chunk) >= 44
        assert header_chunk[:4] == b"RIFF"
        assert header_chunk[8:12] == b"WAVE"
        assert header_chunk[12:16] == b"fmt "

def test_live_audio_stream_continuous_pcm_data():
    """Verify that the stream emits non-empty PCM audio byte chunks."""
    with client.stream("GET", "/api/audio/stream") as response:
        chunks = []
        iterator = response.iter_bytes()
        # Read header + first 2 audio chunks
        for _ in range(3):
            chunks.append(next(iterator))
        assert len(chunks) == 3
        assert all(len(c) > 0 for c in chunks)
