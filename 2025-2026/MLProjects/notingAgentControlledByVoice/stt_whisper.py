import numpy as np
from faster_whisper import WhisperModel

class STT:
    def __init__(
        self,
        model_name: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
    ):
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        self.language = language

    def transcribe(
        self,
        audio_16k_f32: np.ndarray,
        beam_size: int = 5,
        best_of: int = 5,
        vad_filter: bool = True,
        temperature: float = 0.0,
        initial_prompt: str | None = None,
    ) -> str:
        # Ensure correct shape/dtype
        audio = np.asarray(audio_16k_f32, dtype=np.float32).reshape(-1)

        segments, _info = self.model.transcribe(
            audio,
            language=self.language,     # avoid wrong-language guesses
            vad_filter=vad_filter,      # removes silence/noise segments
            beam_size=beam_size,        # better decoding than greedy
            best_of=best_of,            # extra candidates (mainly helps greedy; still OK with beam)
            temperature=temperature,    # 0.0 = deterministic, often more consistent
            initial_prompt=initial_prompt,
        )

        return " ".join(s.text.strip() for s in segments).strip()
