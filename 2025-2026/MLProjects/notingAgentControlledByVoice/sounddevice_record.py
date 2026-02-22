import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.signal import resample_poly



print(sd.query_devices())
print("Default:", sd.default.device) 

MIC_DEVICE = 1            # Microphone (Realtek HD Audio Mic input) WDM-KS
LOOPBACK_DEVICE = 11         # Haut-parleurs ... Windows WASAPI (output device)
BLOCK = 1024
#set sample rate to 16khz 
SAMPLE_RATE = 48000
#record duration in second
RECORD_DUR = 15

mic_chunks = []
sys_chunks = []



'''
sd.rec(frames, samplerate=None, channels=None, dtype=None,
       out=None, mapping=None, blocking=False, **kwargs)

PARAMETERS
frames (int,required) : number of audio frames (samples per channel) to record
example : frames = int(record_dur*sample_rate)

samplerate (int) : sample frequency in Hz (16kHz,48KHz,...)
controls time resolution and latency/CPU tradeoff

channels (int): number of channels to record
ex : 1 -> mono , 2 -> stereo.

dtype (str or numpy dtype) : Data type of returned array. common :
    "float32" recommended for ML : values ~[-1,1]
    "int16" common PCM WAV; values in [-32758;32767]

device (int or str, via **kwargs) : which input device to record from (mic), or output device for WASAPI loopback.
example : device = mic_idx

block (bool) : 
    if True, sd.rec() waits until recording finishes.
    if False (default), it returns immediately and you call sd.wait()

out (np.ndarray)
Provide your own preallocated array buffer to fill.

mapping (list of int)
Select specific input channels (e.g., choose only left channel).

extra_settings (host-API specific, via **kwargs)


Return : 
sd.rec(..., channels=1) returns shape (N, 1).
'''

def mic_callback(indata, frames, time, status):
    mic_chunks.append(indata.copy())
def sys_callback(indata, frames, time, status):
    sys_chunks.append(indata.copy())

wasapi_loopback = sd.WasapiSettings(exclusive = True)

print("Recording...")

with sd.InputStream(device=MIC_DEVICE, channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCK, callback=mic_callback):
    with sd.InputStream(device=LOOPBACK_DEVICE, channels=2, samplerate=SAMPLE_RATE, blocksize=BLOCK,
        callback=sys_callback, extra_settings=wasapi_loopback):
        sd.sleep(int(RECORD_DUR * 1000))


'''
Opens a continuous mic recording stream.

device=MIC_DEVICE: use your chosen mic device.

channels=1: record mono (best for speech + STT).

samplerate=SR: record at 48kHz (same as system so timing aligns).

blocksize=BLOCK: chunk size per callback.

callback=mic_cb: store each chunk in mic_chunks.

with ... ensures it starts and stops cleanly.

Opens a second stream, but for system audio loopback.

device=LOOPBACK_DEVICE: pick the output device you’re listening on.

channels=2: system audio is usually stereo.

extra_settings=wasapi_loopback: tells sounddevice to record the output (“loopback”).

Uses sys_cb to store chunks into sys_chunks.
'''

# 4) Stitch chunks
mic = np.concatenate(mic_chunks, axis=0)[:, 0]
sys_stereo = np.concatenate(sys_chunks, axis=0)
sys_mono = sys_stereo.mean(axis=1)

# 5) Resample both to 16k (for Whisper later)
def to_16k(x):
    return resample_poly(x, 16000, SAMPLE_RATE).astype(np.float32)

mic_16k = to_16k(mic)
sys_16k = to_16k(sys_mono)

# 6) Save separate tracks (best)
sf.write("mic.wav", mic_16k, 16000)
sf.write("system.wav", sys_16k, 16000)

# 7) Optional mixed track (useful for quick listening)
L = max(len(mic_16k), len(sys_16k))

if len(mic_16k) < L:
    mic_16k = np.pad(mic_16k, (0, L - len(mic_16k)))
if len(sys_16k) < L:
    sys_16k = np.pad(sys_16k, (0, L - len(sys_16k)))

mix = 0.5 * mic_16k + 0.5 * sys_16k
mix = np.clip(mix, -1.0, 1.0)
sf.write("mix.wav", mix, 16000)

print("Saved: mic.wav, system.wav, mix.wav")
print("mic min/max:", float(mic_16k.min()), float(mic_16k.max()))
print("sys min/max:", float(sys_16k.min()), float(sys_16k.max()))