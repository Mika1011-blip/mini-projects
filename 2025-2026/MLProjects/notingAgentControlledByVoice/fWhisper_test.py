import os
import wave
import pyaudio
#os.add_dll_directory(r"C:/Program Files/NVIDIA/CUDNN/v9.17/bin/12.9")
#os.add_dll_directory(r"C:\Program Files\NVIDIA\CUDNN\v9.17\bin\12.9")
from faster_whisper import WhisperModel

# ---------- config ----------


SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = 1024
CHUNK_LENGTH_SEC = 5

DEVICE = "cuda"  # set to "cpu" if you don't have CUDA working
LANGUAGE = "fr"  # or "en", or None to auto-detect

NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"


def record_chunk(p: pyaudio.PyAudio, stream: pyaudio.Stream, file_path: str, chunk_length: float = 1.0):
    """Record chunk_length seconds of audio and save to file_path as WAV."""
    frames = []
    num_frames = int(SAMPLE_RATE / FRAMES_PER_BUFFER * chunk_length)

    for _ in range(num_frames):
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frames.append(data)

    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(SAMPLE_RATE)                 # IMPORTANT: missing in your code
    wf.writeframes(b"".join(frames))
    wf.close()


def transcribe_chunk(model: WhisperModel, wav_path: str) -> str:
    """Transcribe a single wav file and return text."""
    segments, info = model.transcribe(
        wav_path,
        language=LANGUAGE,
        vad_filter=True,     # helps ignore silence inside chunk
        beam_size=3,         # lower latency
    )
    text = "".join(seg.text for seg in segments).strip()
    return text


def main2():
    model = WhisperModel(
        "large-v3",  # try "base" if you want faster, "medium" for better accuracy
        device=("cuda" if DEVICE == "cuda" else "cpu"),
        compute_type=("float16" if DEVICE == "cuda" else "int8"),
    )


    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,            # stereo
        rate=SAMPLE_RATE,      # often 44100 or 48000
        input=True,            # default recording device (now Stereo Mix)
        frames_per_buffer=FRAMES_PER_BUFFER,
    )

    accumulated = []
    print("🎙️ Recording... Ctrl+C to stop.")

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file, chunk_length=CHUNK_LENGTH_SEC)

            transcription = transcribe_chunk(model, chunk_file)
            if transcription:
                print(NEON_GREEN + transcription + RESET_COLOR)
                accumulated.append(transcription)

            os.remove(chunk_file)

    except KeyboardInterrupt:
        print("\nStopping...")
        full = " ".join(accumulated).strip()
        with open("log.txt", "w", encoding="utf-8") as f:
            f.write(full)
        print("Saved log.txt")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main2()
