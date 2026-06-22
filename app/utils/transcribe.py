from faster_whisper import WhisperModel


_model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
)


def transcribe_audio(file_path: str) -> dict:
    """Transcribe an audio file and return the transcript plus duration metadata."""

    segments, _info = _model.transcribe(file_path)
    transcript = " ".join(segment.text.strip() for segment in segments).strip()
    duration_seconds = getattr(_info, "duration", None)

    return {
        "transcript": transcript,
        "duration_seconds": duration_seconds,
    }