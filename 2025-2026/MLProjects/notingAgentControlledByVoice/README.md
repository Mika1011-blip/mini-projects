# Voice Note Agent (Local)

Voice-driven assistant prototype combining:

- Voice Activity Detection (VAD) recording
- Whisper speech-to-text
- Local LLM response generation
- Optional RAG over local `vault.txt`
- TTS playback

## Main Files

- `app.py` : orchestrates listen -> transcribe -> command/LLM -> speak.
- `vad_record_utterance.py` : microphone capture with `webrtcvad`.
- `stt_whisper.py` : faster-whisper wrapper.
- `llmModel.py` : local OpenAI-compatible API client + RAG integration.
- `rag_index.py` : chunking, embedding, retrieval.
- `commands.py` : vault operations (open/insert/empty).
- `say_melo.py` : TTS playback with MeloTTS.

## Runtime Dependencies

- Python 3.x
- `faster-whisper`, `sounddevice`, `soundfile`, `webrtcvad`
- `requests`, `sentence-transformers`, `numpy`
- `torch`, `melo`, `unidic_lite`

## External Services / Assumptions

- Local LLM endpoint at `http://127.0.0.1:1234/v1`.
- A compatible model available (default in code: `openai/gpt-oss-20b`).
- Microphone device index in `vad_record_utterance.py` must match local machine.

## Run

- `python app.py`

## Important Notes

- This is a local experimental prototype, not production-hardened.
- Keep secrets/tokens out of notebooks and scripts.
- If using GPU STT (`device="cuda"`), ensure CUDA runtime is available.
