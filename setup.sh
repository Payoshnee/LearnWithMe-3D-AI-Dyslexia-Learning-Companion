#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
NC="\033[0m"

OLLAMA_CHAT_MODEL="${OLLAMA_CHAT_MODEL:-qwen2.5vl:3b}"
OLLAMA_EMBEDDING_MODEL="${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"

echo "=========================================="
echo " DyslexiaLearn Local AI Setup (Mac/Linux)"
echo "=========================================="
echo

need_command() {
  local command_name="$1"
  local install_hint="$2"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo -e "${RED}[missing] ${command_name}${NC}"
    echo "Install: ${install_hint}"
    exit 1
  fi
  echo -e "${GREEN}[ok] ${command_name}${NC}"
}

optional_command() {
  local command_name="$1"
  local install_hint="$2"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo -e "${YELLOW}[optional missing] ${command_name}${NC}"
    echo "Install if needed: ${install_hint}"
    return 1
  fi
  echo -e "${GREEN}[ok] ${command_name}${NC}"
}

echo "--> Checking prerequisites"
need_command node "https://nodejs.org/"
need_command python3 "https://www.python.org/downloads/"
need_command curl "Install curl with your package manager."
need_command ollama "https://ollama.com/"
need_command piper "Install Piper TTS, for example: brew install piper-tts on macOS."

if command -v pnpm >/dev/null 2>&1; then
  PACKAGE_MANAGER="pnpm"
else
  need_command npm "Install Node.js from https://nodejs.org/"
  PACKAGE_MANAGER="npm"
fi
echo -e "${GREEN}[ok] frontend package manager: ${PACKAGE_MANAGER}${NC}"

DOCKER_AVAILABLE=0
if optional_command docker "https://www.docker.com/products/docker-desktop/"; then
  DOCKER_AVAILABLE=1
fi

echo
echo "--> Installing backend dependencies"
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo
echo "--> Installing frontend dependencies"
cd "$ROOT_DIR/frontend"
if [ "$PACKAGE_MANAGER" = "pnpm" ]; then
  pnpm install
else
  npm install
fi

echo
echo "--> Starting PostgreSQL with Docker, if available"
cd "$ROOT_DIR"
if [ "$DOCKER_AVAILABLE" = "1" ]; then
  if docker compose version >/dev/null 2>&1; then
    docker compose -f docker/docker-compose.yml up -d || echo -e "${YELLOW}[warn] Docker database did not start. Check Docker Desktop.${NC}"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f docker/docker-compose.yml up -d || echo -e "${YELLOW}[warn] Docker database did not start. Check Docker Desktop.${NC}"
  else
    echo -e "${YELLOW}[warn] Docker is installed but Docker Compose is unavailable.${NC}"
  fi
else
  echo -e "${YELLOW}[skip] Docker unavailable. Use your own PostgreSQL or update backend/.env.${NC}"
fi

echo
echo "--> Checking Ollama"
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo -e "${YELLOW}[warn] Ollama is installed but not responding at localhost:11434.${NC}"
  echo "Start Ollama, then run these manually if pulls fail:"
  echo "  ollama pull ${OLLAMA_CHAT_MODEL}"
  echo "  ollama pull ${OLLAMA_EMBEDDING_MODEL}"
else
  echo -e "${GREEN}[ok] Ollama is running${NC}"
fi

echo
echo "--> Pulling local AI models"
ollama pull "$OLLAMA_CHAT_MODEL" || echo -e "${YELLOW}[warn] Could not pull ${OLLAMA_CHAT_MODEL}.${NC}"
ollama pull "$OLLAMA_EMBEDDING_MODEL" || echo -e "${YELLOW}[warn] Could not pull ${OLLAMA_EMBEDDING_MODEL}.${NC}"

echo
echo "--> Downloading Piper voices"
chmod +x "$ROOT_DIR/backend/scripts/download_piper_voices.sh"
"$ROOT_DIR/backend/scripts/download_piper_voices.sh" "$ROOT_DIR/backend/tts/voices"

echo
echo "--> Writing backend local environment"
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
fi
python3 - <<PY
from pathlib import Path
path = Path("backend/.env")
values = {
    "OLLAMA_CHAT_MODEL": "${OLLAMA_CHAT_MODEL}",
    "OLLAMA_EMBEDDING_MODEL": "${OLLAMA_EMBEDDING_MODEL}:latest" if "${OLLAMA_EMBEDDING_MODEL}" == "nomic-embed-text" else "${OLLAMA_EMBEDDING_MODEL}",
    "TTS_ENGINE": "piper",
    "PIPER_BINARY_PATH": "piper",
    "PIPER_VOICE_DIR": "tts/voices",
}
lines = path.read_text().splitlines() if path.exists() else []
seen = set()
next_lines = []
for line in lines:
    key = line.split("=", 1)[0] if "=" in line else None
    if key in values:
        next_lines.append(f"{key}={values[key]}")
        seen.add(key)
    else:
        next_lines.append(line)
for key, value in values.items():
    if key not in seen:
        next_lines.append(f"{key}={value}")
path.write_text("\\n".join(next_lines) + "\\n")
PY

echo
echo "=========================================="
echo -e "${GREEN} Setup complete.${NC}"
echo "=========================================="
echo
echo "Start backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8080"
echo
echo "Start frontend:"
if [ "$PACKAGE_MANAGER" = "pnpm" ]; then
  echo "  cd frontend && pnpm dev"
else
  echo "  cd frontend && npm run dev"
fi
echo
echo "Quality profile:"
echo "  OLLAMA_CHAT_MODEL=${OLLAMA_CHAT_MODEL}"
echo "  TTS_ENGINE=piper"
