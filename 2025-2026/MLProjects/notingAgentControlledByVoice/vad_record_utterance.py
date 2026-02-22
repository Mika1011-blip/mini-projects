import queue
import collections
import numpy as np
import sounddevice as sd
import soundfile as sf
import webrtcvad
from datetime import datetime


# ---- CONFIG ----
MIC_DEVICE = 1          # your mic
SR = 16000               # required by many STT pipelines; good for webrtcvad too
FRAME_MS = 20            # webrtcvad supports 10/20/30 ms
FRAME_SAMPLES = SR * FRAME_MS // 1000   # 16000 * 20 / 1000 = 320 samples
BLOCKSIZE = FRAME_SAMPLES               # one VAD frame per callback

VAD_AGGRESSIVENESS = 2   # 0=least, 3=most aggressive (try 2 first)
START_TRIGGER_FRAMES = 6 # ~120ms speech required to start
END_SILENCE_FRAMES = 18  # ~360ms silence required to stop

# ----------------

def int16_to_float32(x: np.ndarray) -> np.ndarray:
    # Convert PCM int16 [-32768, 32767] to float32 [-1, 1]
    return (x.astype(np.float32) / 32768.0)

def record_one_utterance(num_input : int = 0):
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

    q = queue.Queue()
    ring = collections.deque(maxlen=START_TRIGGER_FRAMES)

    triggered = False
    voiced_frames = []
    silence_count = 0

    def cb(indata, frames, time, status):
        # indata shape: (FRAME_SAMPLES, 1) dtype=int16
        q.put(indata.copy())

    print("IM LISTENING... speak a sentence (Ctrl+C to stop).")

    with sd.InputStream(
        device=MIC_DEVICE,
        channels=1,
        samplerate=SR,
        blocksize=BLOCKSIZE,
        dtype="int16",
        callback=cb,
    ):
        while True:
            frame = q.get()                 # (320,1) int16
            frame = frame[:, 0]             # (320,)  int16

            # webrtcvad expects raw bytes of 16-bit PCM mono
            is_speech = vad.is_speech(frame.tobytes(), SR)

            if not triggered:
                ring.append((frame, is_speech))
                speech_votes = sum(1 for _, s in ring if s)

                # Start when enough frames in the ring are speech
                if speech_votes >= START_TRIGGER_FRAMES:
                    triggered = True
                    # include the buffered frames so we don't cut the start
                    voiced_frames.extend([f for f, _ in ring])
                    ring.clear()
                    silence_count = 0
            else:
                voiced_frames.append(frame)

                if is_speech:
                    silence_count = 0
                else:
                    silence_count += 1

                # Stop after enough consecutive silence frames
                if silence_count >= END_SILENCE_FRAMES:
                    break

    if not voiced_frames:
        return None

    audio_int16 = np.concatenate(voiced_frames, axis=0)
    audio_f32 = int16_to_float32(audio_int16)
    #sf.write(f"mic_{num_input}.wav", audio_f32, 16000)
    return audio_f32

if __name__ == "__main__":
    audio = record_one_utterance()

    if audio is None:
        print("No utterance captured.")
    else:
        sf.write("utterance.wav", audio, SR)
        print(f"✅ Saved utterance.wav ({len(audio)/SR:.2f}s)")
        print("min/max:", float(audio.min()), float(audio.max()))
