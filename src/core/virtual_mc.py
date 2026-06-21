import os
import uuid
import tempfile
from gtts import gTTS

def generate_hype_announcement(velocity: int, trend: str, archetype: str) -> str:
    """Generates a text announcement based on the room's energy."""
    if trend == "rising" and velocity >= 5:
        return "Energy is peaking! Get ready for the drop!"
    elif archetype == "Bass Swap":
        return "Switching the bassline... hold on!"
    elif archetype == "HPF Sweep":
        return "Taking it higher!"
    elif trend == "falling":
        return "Let's cool it down and catch a vibe."
    else:
        return "Keep the energy moving."

def create_tts_audio(text: str) -> str:
    """Uses gTTS to create an MP3 file of the text and returns the file path."""
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        # We need a persistent location accessible by the C++ engine.
        filepath = os.path.join(tempfile.gettempdir(), f"mc_hype_{uuid.uuid4().hex}.mp3")
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"[Virtual MC] Error generating TTS: {e}")
        return ""
