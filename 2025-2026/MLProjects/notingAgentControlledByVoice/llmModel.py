import requests
from commands import *
from rag_index import *
import time

#print(requests.get("http://127.0.0.1:1234/v1/models", timeout=10).json())

class LocalLLM:
    def __init__(self, base_url="http://127.0.0.1:1234/v1", model=None, timeout=60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _resolve_model(self):
        if self.model:
            return self.model
        r = requests.get(f"{self.base_url}/models", timeout=self.timeout)
        r.raise_for_status()
        models = r.json().get("data", [])
        if not models:
            raise RuntimeError("No models returned by /v1/models. Is the server running?")
        self.model = models[0]["id"]
        return self.model

    def chat_messages(self, messages, max_tokens: int = 160, temperature: float = 0.4) -> str:
        model_id = self._resolve_model()
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        r = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

def build_messages(system_text: str, context_text: str, user_text: str):
    ctx = context_text if context_text.strip() else "(none)"
    return [
        {"role": "system", "content": system_text},
        {"role": "system", "content": f"CONTEXT:\n{ctx}"},
        {"role": "user", "content": user_text},
    ]


INSTRUCTION = """You are Emma, an efficient executive assistant.
Style: concise, calm, professional.
Rules:
- Reply in 1–2 sentences unless the user asks for detail.
- If the user asks about their info, use CONTEXT only; don’t invent.
- No chain-of-thought. Final answer only.
- if talked to in french, answer in french
- if talked to in english, answer in english"""

def get_modelReply(user_message : str):
    t0 = time.perf_counter()
    vault_context = open_vault()
    model = LocalLLM(
        base_url="http://127.0.0.1:1234/v1",
        model="openai/gpt-oss-20b",        # None = auto-pick first model from /v1/models
        timeout=60
    )
    build_rag_index(
        vault_text=vault_context, 
        embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunks_file="rag_chunks.json",
        emb_file="rag_embeddings.npy"
    )
    context_text = retrieve_context(
        query=user_message,
        embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
        top_k=5,
        chunks_file="rag_chunks.json",
        emb_file="rag_embeddings.npy"
    )
    messages = build_messages(
        system_text=INSTRUCTION,
        context_text=context_text,
        user_text=user_message
        )

    reply = model.chat_messages(
        messages=messages,
        max_tokens=120,
        temperature=0.3
    )
    t1 = time.perf_counter()
    print(f"LLM latency: {(t1 - t0)*1000:.1f} ms")
    return reply

if __name__ == "__main__" :
    get_modelReply("What's your name ?")