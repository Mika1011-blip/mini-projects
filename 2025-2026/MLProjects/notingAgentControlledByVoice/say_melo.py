import os
import tempfile
import sounddevice as sd
import soundfile as sf
import unidic_lite
import torch
import contextlib
import sys
import io


# Must be set BEFORE importing melo
os.environ["MECABRC"] = os.path.join(unidic_lite.DICDIR, "mecabrc")
os.environ["MECAB_DICDIR"] = unidic_lite.DICDIR

from melo.api import TTS

_TTS_CACHE = {}

@contextlib.contextmanager
def _silence_output():
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def _get_tts(language: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    key = (language, device)
    if key not in _TTS_CACHE:
        _TTS_CACHE[key] = TTS(language=language, device=device)
    return _TTS_CACHE[key]

def _play_wav(path: str) -> None:
    audio, sr = sf.read(path, dtype="float32")
    sd.play(audio, sr)
    sd.wait()

def say(*, text: str, language: str = "EN", speed: float = 1.0) -> None:
    """
    text     -> what to speak
    language -> "EN" or "FR"
    speed    -> 1.0 normal, >1 faster, <1 slower
    """
    with _silence_output():
        if not text or not text.strip():
            return

        tts = _get_tts(language)
        speaker_id = list(tts.hps.data.spk2id.values())[0]

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        out_path = tmp.name
        tmp.close()

        try:
            tts.tts_to_file(text.strip(), speaker_id, out_path, speed=speed)
            _play_wav(out_path)
        finally:
            try:
                os.remove(out_path)
            except OSError:
                pass


if __name__ == "__main__":
    say(text="Hello, this is English.", language="EN")
    say(text="Bonjour, ceci est du français.", language="FR")
