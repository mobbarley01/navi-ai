import subprocess
import whisper
import os
import re

CARD = "plughw:2,0"
DURATION = 7
TMP_FILE = "/tmp/navi_listen.wav"

_model = None

def _load_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")

def _is_garbage(text):
    if not text:
        return True
    if re.search(r'[\u0400-\u04FF\u0370-\u03FF\u4E00-\u9FFF]', text):
        return True
    words = text.split()
    if len(words) >= 4:
        unique = set(w.lower().strip('.,!?') for w in words)
        if len(unique) <= 2:
            return True
    return False

def listen(duration=DURATION):
    _load_model()
    try:
        subprocess.run([
            "arecord",
            "-D", CARD,
            "-f", "cd",
            "-t", "wav",
            "-d", str(duration),
            TMP_FILE
        ], check=True, capture_output=True)

        result = _model.transcribe(
            TMP_FILE,
            fp16=False,
            language="en",
            temperature=0,
            condition_on_previous_text=False
        )
        text = result["text"].strip()

        if _is_garbage(text):
            return ""

        for wrong in ["Navy", "navy", "Neville", "neville", "Navvy", "navvy"]:
            text = text.replace(wrong, "Navi")

        return text

    except Exception as e:
        print(f"[speech_to_text] Error: {e}")
        return ""

    finally:
        if os.path.exists(TMP_FILE):
            os.remove(TMP_FILE)


if __name__ == "__main__":
    print(f"Recording {DURATION} seconds... speak now.")
    text = listen()
    if text:
        print(f"Heard: {text}")
    else:
        print("Nothing heard or transcription failed.")
