import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.tts import text_to_speech

if __name__ == "__main__":
    print("Testing text-to-speech conversion...")
    text = "Hello my name is Ammar Khan and I am a fat ass."
    output_path = "app/audio/answers/test_welcome2.wav"
    
    text_to_speech(text, output_path)
    
    if os.path.exists(output_path):
        print(f"Success! Speech file saved at: {output_path} (Size: {os.path.getsize(output_path)} bytes)")
    else:
        print("Error: Output file was not generated.")
