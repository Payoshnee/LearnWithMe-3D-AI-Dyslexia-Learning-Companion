# Local AI + RAG Setup

The voice-first AI Doodle backend is wired for a local-first stack.

## Recommended Models

- Shared chat / tutor / vision model: `qwen2.5vl:3b`
- Embeddings: `nomic-embed-text:latest` if already installed, or `bge-m3` for stronger multilingual retrieval
- Speech-to-text: Chrome's native Web Speech API
- Text-to-speech now: browser `speechSynthesis`
- Text-to-speech next step: Piper or Kokoro

## Ollama Setup

```bash
ollama pull qwen2.5vl:3b
ollama pull nomic-embed-text
ollama serve
```

The backend reads:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5vl:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
RAG_TOP_K=4
```

## Voice Turn Flow

```text
transcript
-> detect language
-> detect intent
-> retrieve lesson chunks
-> generate local LLM answer
-> return animation states + board + memory update
```

Endpoint:

```text
POST /api/v1/companion/voice-turn
```

If Ollama is not running, the endpoint falls back to deterministic mock RAG so the demo still works.
