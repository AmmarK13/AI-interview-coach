import os
import wave
from piper.voice import PiperVoice

VOICE_MODEL_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../core/tts_models/en_US-lessac-medium.onnx"
    )
)

_voice_instance = None

def get_voice() -> PiperVoice:
    global _voice_instance
    if _voice_instance is None:
        if not os.path.exists(VOICE_MODEL_PATH):
            raise FileNotFoundError(
                f"Piper TTS model file not found at {VOICE_MODEL_PATH}. "
                "Please download it first."
            )
        _voice_instance = PiperVoice.load(VOICE_MODEL_PATH)
    return _voice_instance

def text_to_speech(text: str, output_wav_path: str) -> None:
    """
    Converts a string of text to speech, saving it as a WAV file at output_wav_path.
    """
    # Ensure directory containing output_wav_path exists
    dir_name = os.path.dirname(output_wav_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    voice = get_voice()
    with wave.open(output_wav_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
