#!/usr/bin/env bash
# One-command launcher for Linux / macOS.
set -e
cd "$(dirname "$0")"

MODEL="${DEFAULT_MODEL:-llama3.2:3b}"
export DEFAULT_MODEL="$MODEL"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed. Get it from https://ollama.com/download and re-run this script."
  exit 1
fi

# Start Ollama if it isn't already running.
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Starting Ollama..."
  (ollama serve >/dev/null 2>&1 &)
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
  done
fi

# Download the default model the first time.
if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$MODEL"; then
  echo "Downloading $MODEL (one-time, ~2 GB)..."
  ollama pull "$MODEL"
fi

# Python environment.
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

URL="http://127.0.0.1:${PORT:-8000}"
(sleep 2; (command -v xdg-open >/dev/null && xdg-open "$URL") || (command -v open >/dev/null && open "$URL") || true) >/dev/null 2>&1 &

python server.py
