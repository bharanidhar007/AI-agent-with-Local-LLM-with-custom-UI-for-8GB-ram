"""Local LLM chat server.

FastAPI + SQLite, talking to a local Ollama instance.
Serves the web UI from ./static and keeps all chats in ./data/chats.db.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --------------------------------------------------------------------------
# Config (override with environment variables)
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "chats.db"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
# Context window. Bigger = more RAM. 4096 is a safe default for 8 GB machines.
NUM_CTX = int(os.getenv("NUM_CTX", "4096"))
# How long Ollama keeps the model in RAM after the last message.
KEEP_ALIVE = os.getenv("KEEP_ALIVE", "10m")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

DEFAULT_TITLE = "New chat"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS chats (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    model       TEXT,
    created_at  REAL NOT NULL,
    updated_at  REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, id);
"""


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


with db() as _c:
    _c.execute("PRAGMA journal_mode = WAL")
    _c.executescript(SCHEMA)

# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
app = FastAPI(title="Local LLM Chat")


class NewChat(BaseModel):
    model: Optional[str] = None
    title: Optional[str] = None


class RenameChat(BaseModel):
    title: str


class SendBody(BaseModel):
    content: str = ""
    model: Optional[str] = None
    system: Optional[str] = None
    temperature: Optional[float] = None
    regenerate: bool = False


class PullBody(BaseModel):
    name: str


def chat_row(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"],
        "title": r["title"],
        "model": r["model"],
        "created_at": r["created_at"],
        "updated_at": r["updated_at"],
    }


# ---- models ---------------------------------------------------------------
@app.get("/api/models")
async def list_models():
    """Installed Ollama models, plus whether Ollama is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            models = [
                {"name": m["name"], "size": m.get("size", 0)}
                for m in r.json().get("models", [])
            ]
            models.sort(key=lambda m: m["name"])
            return {"ok": True, "models": models, "default": DEFAULT_MODEL, "ollama": OLLAMA_URL}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "models": [], "default": DEFAULT_MODEL, "ollama": OLLAMA_URL, "error": str(e)}


@app.post("/api/pull")
async def pull_model(body: PullBody):
    """Stream Ollama's download progress (newline-delimited JSON)."""
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "Model name required")

    async def gen():
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(None, connect=5)) as client:
                async with client.stream(
                    "POST", f"{OLLAMA_URL}/api/pull", json={"model": name, "name": name, "stream": True}
                ) as r:
                    if r.status_code != 200:
                        text = (await r.aread()).decode(errors="ignore")
                        yield json.dumps({"error": text or f"HTTP {r.status_code}"}) + "\n"
                        return
                    async for line in r.aiter_lines():
                        if line:
                            yield line + "\n"
        except httpx.HTTPError as e:
            yield json.dumps({"error": f"Cannot reach Ollama: {e}"}) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


# ---- chats ----------------------------------------------------------------
@app.get("/api/chats")
def list_chats():
    with db() as c:
        rows = c.execute("SELECT * FROM chats ORDER BY updated_at DESC").fetchall()
    return [chat_row(r) for r in rows]


@app.post("/api/chats")
def create_chat(body: NewChat):
    now = time.time()
    cid = uuid.uuid4().hex[:12]
    with db() as c:
        c.execute(
            "INSERT INTO chats (id, title, model, created_at, updated_at) VALUES (?,?,?,?,?)",
            (cid, body.title or DEFAULT_TITLE, body.model, now, now),
        )
        row = c.execute("SELECT * FROM chats WHERE id=?", (cid,)).fetchone()
    return chat_row(row)


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    with db() as c:
        chat = c.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
        if not chat:
            raise HTTPException(404, "Chat not found")
        msgs = c.execute(
            "SELECT role, content, created_at FROM messages WHERE chat_id=? ORDER BY id", (chat_id,)
        ).fetchall()
    return {**chat_row(chat), "messages": [dict(m) for m in msgs]}


@app.patch("/api/chats/{chat_id}")
def rename_chat(chat_id: str, body: RenameChat):
    title = body.title.strip()[:120] or DEFAULT_TITLE
    with db() as c:
        cur = c.execute("UPDATE chats SET title=? WHERE id=?", (title, chat_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Chat not found")
    return {"id": chat_id, "title": title}


@app.delete("/api/chats/{chat_id}", status_code=204)
def delete_chat(chat_id: str):
    with db() as c:
        c.execute("DELETE FROM chats WHERE id=?", (chat_id,))


@app.get("/api/chats/{chat_id}/export")
def export_chat(chat_id: str):
    data = get_chat(chat_id)
    parts = [f"# {data['title']}", ""]
    for m in data["messages"]:
        who = "You" if m["role"] == "user" else "Assistant"
        parts += [f"**{who}:**", "", m["content"], ""]
    safe = "".join(ch if ch.isalnum() or ch in "-_ " else "_" for ch in data["title"]).strip() or "chat"
    return PlainTextResponse(
        "\n".join(parts),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{safe}.md"'},
    )


# ---- sending messages -----------------------------------------------------
def build_context(history: list[dict], system: Optional[str]) -> list[dict]:
    """Keep the most recent messages that fit in roughly NUM_CTX tokens."""
    budget_chars = max(1000, (NUM_CTX - 600) * 3)  # ~3 chars/token, leave room for the reply
    kept: list[dict] = []
    used = 0
    for m in reversed(history):
        used += len(m["content"])
        if kept and used > budget_chars:
            break
        kept.append(m)
    kept.reverse()
    msgs: list[dict] = []
    if system and system.strip():
        msgs.append({"role": "system", "content": system.strip()})
    return msgs + kept


@app.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: str, body: SendBody):
    now = time.time()
    with db() as c:
        chat = c.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
        if not chat:
            raise HTTPException(404, "Chat not found")

        title = chat["title"]
        if body.regenerate:
            # Drop any assistant reply that follows the last user message.
            c.execute(
                """DELETE FROM messages WHERE chat_id=? AND role='assistant' AND id >
                   COALESCE((SELECT MAX(id) FROM messages WHERE chat_id=? AND role='user'), 0)""",
                (chat_id, chat_id),
            )
        else:
            text = body.content.strip()
            if not text:
                raise HTTPException(400, "Empty message")
            c.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?,?,?,?)",
                (chat_id, "user", text, now),
            )
            if title == DEFAULT_TITLE:
                title = " ".join(text.split())[:48] or DEFAULT_TITLE

        history = [
            {"role": r["role"], "content": r["content"]}
            for r in c.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,))
        ]
        if not history or history[-1]["role"] != "user":
            raise HTTPException(400, "Nothing to reply to")

        model = body.model or chat["model"] or DEFAULT_MODEL
        c.execute("UPDATE chats SET title=?, model=?, updated_at=? WHERE id=?", (title, model, now, chat_id))

    options = {"num_ctx": NUM_CTX}
    if body.temperature is not None:
        options["temperature"] = body.temperature
    payload = {
        "model": model,
        "messages": build_context(history, body.system),
        "stream": True,
        "options": options,
        "keep_alive": KEEP_ALIVE,
    }

    async def gen():
        parts: list[str] = []
        yield json.dumps({"type": "meta", "chat_id": chat_id, "title": title, "model": model}) + "\n"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(None, connect=5)) as client:
                async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as r:
                    if r.status_code != 200:
                        text = (await r.aread()).decode(errors="ignore")
                        try:
                            text = json.loads(text).get("error", text)
                        except Exception:  # noqa: BLE001
                            pass
                        yield json.dumps({"type": "error", "message": text or f"Ollama returned HTTP {r.status_code}"}) + "\n"
                        return
                    async for line in r.aiter_lines():
                        if not line:
                            continue
                        obj = json.loads(line)
                        if "error" in obj:
                            yield json.dumps({"type": "error", "message": obj["error"]}) + "\n"
                            return
                        piece = obj.get("message", {}).get("content", "")
                        if piece:
                            parts.append(piece)
                            yield json.dumps({"type": "token", "content": piece}) + "\n"
                        if obj.get("done"):
                            tps = None
                            if obj.get("eval_count") and obj.get("eval_duration"):
                                tps = round(obj["eval_count"] / (obj["eval_duration"] / 1e9), 1)
                            yield json.dumps({"type": "done", "tokens_per_sec": tps}) + "\n"
        except httpx.ConnectError:
            yield json.dumps(
                {"type": "error", "message": f"Can't reach Ollama at {OLLAMA_URL}. Is it running? (try: ollama serve)"}
            ) + "\n"
        except httpx.HTTPError as e:
            yield json.dumps({"type": "error", "message": f"Connection to Ollama failed: {e}"}) + "\n"
        finally:
            # Save whatever was generated, including partial replies when the user hits Stop.
            reply = "".join(parts).strip()
            if reply:
                with db() as c2:
                    c2.execute(
                        "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?,?,?,?)",
                        (chat_id, "assistant", reply, time.time()),
                    )
                    c2.execute("UPDATE chats SET updated_at=? WHERE id=?", (time.time(), chat_id))

    return StreamingResponse(gen(), media_type="application/x-ndjson")


# ---- static UI (must be last) --------------------------------------------
app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    print(f"\n  Local LLM Chat -> http://{HOST}:{PORT}   (Ollama: {OLLAMA_URL}, default model: {DEFAULT_MODEL})\n")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
