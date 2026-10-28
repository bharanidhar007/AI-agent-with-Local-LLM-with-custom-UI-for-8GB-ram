# Local LLM Chat

A private, ChatGPT/Claude-style chat app that runs entirely on your own computer — tuned for **8 GB RAM** machines.

- **Model runner:** [Ollama](https://ollama.com) (handles downloading and running quantized models efficiently)
- **App:** a tiny Python server (FastAPI + SQLite) and a plain HTML/JS interface — no Node, no build step, no internet needed once a model is downloaded
- **Chat history:** every conversation is saved to `data/chats.db` and reappears when you restart

## Features

- Streaming replies with a **Stop** button and **Regenerate**
- Saved chat history with sidebar, search, rename, delete, and Markdown **export**
- Markdown rendering with code blocks and one-click **Copy**
- Switch models from a dropdown; **download new models** from inside the UI
- System prompt and temperature settings
- Light / dark theme, mobile-friendly layout
- Shows tokens/sec after each reply so you can see what your hardware can do

## Quick start

1. **Install Ollama:** https://ollama.com/download
2. **Install Python 3.9+** if you don't have it.
3. Run the launcher:

   ```bash
   # Linux / macOS
   ./run.sh

   # Windows
   run.bat
   ```

   The first run creates a virtual environment, installs three small Python packages, downloads the default model (`llama3.2:3b`, about 2 GB), and opens http://127.0.0.1:8000.

Manual setup, if you prefer:

```bash
ollama pull llama3.2:3b
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

## Picking a model for 8 GB RAM

Your OS and browser already use a few GB, so roughly **4–5 GB** is what's realistically left for the model. Sizes below are approximate (4-bit quantized, Ollama's default).

| Model | Size | Notes |
|---|---|---|
| `llama3.2:3b` | ~2.0 GB | **Default.** Good all-rounder, comfortable on 8 GB |
| `llama3.2:1b` | ~1.3 GB | Very fast, simpler answers |
| `qwen2.5:3b` | ~1.9 GB | Strong at reasoning and code for its size |
| `gemma2:2b` | ~1.6 GB | Small and capable |
| `phi3.5` | ~2.2 GB | Good for its size |
| `qwen2.5-coder:3b` | ~1.9 GB | Coding focused |
| `qwen2.5:7b` | ~4.7 GB | Best quality, but tight: close other apps first |
| `llama3.1:8b` | ~4.9 GB | Tight, may swap to disk and slow down |

Newer models are released often. Anything at https://ollama.com/library that is **3B parameters or smaller** (or a 7B with 4-bit quantization if you close other apps) should work. Use the **Get model** button to download one.

### Tips for squeezing the most out of 8 GB

- Close heavy apps (browser tabs, IDEs) when using a 7B model.
- Lower the context window with `NUM_CTX=2048` to save RAM; raise it for longer conversations if you have headroom.
- `KEEP_ALIVE=2m` makes Ollama unload the model from RAM sooner after you stop chatting (default `10m`).
- If replies are very slow (under ~2 tokens/sec), the model is too big. Drop to a smaller one.
- If you have a GPU, Ollama will use it automatically.

## Configuration

Set these environment variables before starting (e.g. `PORT=9000 python server.py`):

| Variable | Default | What it does |
|---|---|---|
| `DEFAULT_MODEL` | `llama3.2:3b` | Model the launcher downloads and pre-selects |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Where Ollama is running |
| `NUM_CTX` | `4096` | Context window in tokens (more = more RAM) |
| `KEEP_ALIVE` | `10m` | How long the model stays loaded when idle |
| `HOST` | `127.0.0.1` | Use `0.0.0.0` to open it to other devices on your network (there is no login, so only do this on a trusted network) |
| `PORT` | `8000` | Web port |
| `DATA_DIR` | `./data` | Where `chats.db` lives |

## Project layout

```
local-llm-chat/
├── server.py          # API, SQLite storage, streaming proxy to Ollama
├── requirements.txt
├── run.sh / run.bat   # one-command launchers
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js         # the whole UI, no framework
└── data/chats.db      # created on first run: all your chats
```

**Backup / move your chats:** copy `data/chats.db`. **Wipe everything:** delete it.

## Troubleshooting

- **"Can't reach Ollama"** — start it with `ollama serve` (the desktop app does this automatically).
- **"model not found"** — click **Get model** or run `ollama pull <name>`.
- **Out-of-memory or the computer freezes** — use a smaller model or a smaller `NUM_CTX`.
- **Port already in use** — run with `PORT=8001`.
