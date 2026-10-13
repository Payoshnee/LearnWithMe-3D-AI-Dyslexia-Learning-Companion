#!/usr/bin/env sh
set -eu
export OLLAMA_HOST="127.0.0.1:11434"
ollama serve >/tmp/ollama.log 2>&1 &
until curl --silent --fail http://127.0.0.1:11434/api/tags >/dev/null 2>&1; do sleep 1; done
ollama pull "${DYBRAIN_MODEL:-qwen2.5vl:3b}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-7860}"
