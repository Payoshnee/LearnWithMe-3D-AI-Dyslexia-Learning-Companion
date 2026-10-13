#!/usr/bin/env bash
set -euo pipefail

VOICE_DIR="${1:-backend/tts/voices}"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

mkdir -p "$VOICE_DIR"

download_voice() {
  local lang_path="$1"
  local voice_name="$2"
  local quality="$3"
  local file="${voice_name}-${quality}.onnx"
  local url="${BASE_URL}/${lang_path}/${quality}/${file}"

  echo "Downloading ${file}"
  curl -L --fail "${url}?download=true" -o "${VOICE_DIR}/${file}"
  curl -L --fail "${url}.json?download=true" -o "${VOICE_DIR}/${file}.json"
}

download_voice "en/en_US/lessac" "en_US-lessac" "medium"
download_voice "en/en_US/amy" "en_US-amy" "medium"
download_voice "en/en_US/ryan" "en_US-ryan" "medium"
download_voice "en/en_GB/alan" "en_GB-alan" "medium"

echo "Piper voices are ready in ${VOICE_DIR}"
