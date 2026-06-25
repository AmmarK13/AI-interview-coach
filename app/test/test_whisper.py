from faster_whisper import WhisperModel

print("Before model")

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
    cpu_threads=1,
    num_workers=1
)

print("After model")