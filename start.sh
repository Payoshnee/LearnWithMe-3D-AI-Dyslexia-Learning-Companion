#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8080}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PROCESS_IDS=()

fail() {
  echo "[error] $1" >&2
  exit 1
}

cleanup() {
  trap - EXIT INT TERM
  if [ "${#PROCESS_IDS[@]}" -gt 0 ]; then
    echo
    echo "Stopping DyslexiaLearn..."
    kill "${PROCESS_IDS[@]}" 2>/dev/null || true
    wait "${PROCESS_IDS[@]}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

[ -x "$BACKEND_DIR/venv/bin/python" ] || fail "Backend environment is missing. Run ./setup.sh first."
[ -d "$FRONTEND_DIR/node_modules" ] || fail "Frontend dependencies are missing. Run ./setup.sh first."

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    docker compose -f "$PROJECT_DIR/docker/docker-compose.yml" up -d
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    docker-compose -f "$PROJECT_DIR/docker/docker-compose.yml" up -d
  fi
else
  echo "[warn] Docker is not running; expecting PostgreSQL to already be available."
fi

if command -v ollama >/dev/null 2>&1; then
  if ! curl --silent --fail http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama..."
    ollama serve >/tmp/dyslexialearn-ollama.log 2>&1 &
    PROCESS_IDS+=("$!")
  fi
else
  echo "[warn] Ollama is not installed; open-ended LLM answers may be unavailable."
fi

echo "Starting backend on http://localhost:${BACKEND_PORT}..."
(
  cd "$BACKEND_DIR"
  exec venv/bin/python -m uvicorn app.main:app --reload --port "$BACKEND_PORT"
) &
BACKEND_PID="$!"
PROCESS_IDS+=("$BACKEND_PID")

echo "Starting frontend on http://localhost:${FRONTEND_PORT}..."
if command -v pnpm >/dev/null 2>&1; then
  (
    cd "$FRONTEND_DIR"
    exec pnpm dev --port "$FRONTEND_PORT"
  ) &
else
  command -v npm >/dev/null 2>&1 || fail "npm or pnpm is required. Run ./setup.sh first."
  (
    cd "$FRONTEND_DIR"
    exec npm run dev -- --port "$FRONTEND_PORT"
  ) &
fi
FRONTEND_PID="$!"
PROCESS_IDS+=("$FRONTEND_PID")

echo
echo "DyslexiaLearn is running. Open http://localhost:${FRONTEND_PORT} in Chrome."
echo "Press Ctrl+C to stop the frontend and backend."

while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 1
done

echo "[error] A project service stopped unexpectedly." >&2
exit 1
