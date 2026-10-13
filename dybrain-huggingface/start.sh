#!/usr/bin/env sh
set -eu

export OLLAMA_HOST="127.0.0.1:11434"
MODEL="${DYBRAIN_MODEL:-qwen2.5vl:3b}"

ollama serve >/tmp/ollama.log 2>&1 &

until curl --silent --fail http://127.0.0.1:11434/api/tags >/dev/null 2>&1; do
  sleep 1
done

if ! ollama list | awk 'NR > 1 {print $1}' | grep -Fx "$MODEL" >/dev/null; then
  ollama pull "$MODEL"
fi

exec uvicorn app:app --host 0.0.0.0 --port "${PORT:-7860}"
