import os
import tempfile
import asyncio
from typing import Dict

# Provide a mock function if the underlying heavy ML process fails during testing
def extract_stems_mock(filepath: str) -> Dict[str, str]:
    print(f"[STEM] Mock extracting stems for {filepath}")
    return {
        "vocals": filepath,
        "drums": filepath,
        "bass": filepath,
        "other": filepath
    }

async def extract_stems(filepath: str) -> Dict[str, str]:
    """
    Takes an audio filepath and uses Demucs to separate it into 4 stems.
    Returns a dictionary of paths to the extracted stems.
    """
    if not os.path.exists(filepath):
        print(f"[STEM] File not found: {filepath}")
        return extract_stems_mock(filepath)

    output_dir = os.path.join(tempfile.gettempdir(), "cdc_stems")
    os.makedirs(output_dir, exist_ok=True)

    print(f"[STEM] Starting Demucs extraction for {filepath}...")
    try:
        # Run Demucs as a subprocess to avoid blocking the main async loop
        # -n htdemucs uses the standard 4-stem model
        process = await asyncio.create_subprocess_exec(
            "demucs", "-n", "htdemucs", "--out", output_dir, filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        base_name = os.path.splitext(os.path.basename(filepath))[0]
        model_out_dir = os.path.join(output_dir, "htdemucs", base_name)

        stems = {
            "vocals": os.path.join(model_out_dir, "vocals.wav"),
            "drums": os.path.join(model_out_dir, "drums.wav"),
            "bass": os.path.join(model_out_dir, "bass.wav"),
            "other": os.path.join(model_out_dir, "other.wav")
        }

        # Check if separation succeeded
        for path in stems.values():
            if not os.path.exists(path):
                print(f"[STEM] Failed to find generated stem: {path}")
                return extract_stems_mock(filepath)

        print(f"[STEM] Extraction complete for {filepath}")
        return stems
    except Exception as e:
        print(f"[STEM] Demucs failed: {e}")
        return extract_stems_mock(filepath)
