import subprocess
import re

WHISPER_CLI = r"D:\Ai-interview-coach\whisper_cpp\whisper-cli.exe"
MODEL_PATH = r"D:\Ai-interview-coach\whisper_cpp\models\ggml-tiny.bin"


def transcribe_audio_ammar(file_path: str) -> dict:
    """Transcribe audio using whisper.cpp CLI"""

    result = subprocess.run(
        [
            WHISPER_CLI,
            "-m", MODEL_PATH,
            "-f", file_path,
            "-nt",   # no timestamps
            "-np"    # no progress spam
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    # ----------------------------
    # 1. Extract transcript
    # ----------------------------
    transcript = output

    # ----------------------------
    # 2. Extract duration (from stderr or stdout logs)
    # whisper.cpp often prints something like:
    # "audio duration = 12.34 sec"
    # ----------------------------
    duration_seconds = None

    combined = output + "\n" + (result.stderr or "")

    match = re.search(r"(\d+(\.\d+)?)\s*sec", combined)
    if match:
        duration_seconds = float(match.group(1))

    # fallback if not found
    if duration_seconds is None:
        duration_seconds = 0.0

    return {
        "transcript": transcript,
        "duration_seconds": duration_seconds
    }