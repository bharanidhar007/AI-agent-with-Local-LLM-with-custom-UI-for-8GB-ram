/* Local LLM Chat — vanilla JS, no build step, no CDN. */
"use strict";

const $ = (s) => document.querySelector(s);

const SUGGESTED_MODELS = [
  ["llama3.2:3b", "2.0 GB · great all-rounder"],
  ["llama3.2:1b", "1.3 GB · very fast"],
  ["qwen2.5:3b", "1.9 GB · good at reasoning/code"],
  ["gemma2:2b", "1.6 GB · small and capable"],
  ["phi3.5", "2.2 GB · strong for its size"],
  ["qwen2.5-coder:3b", "1.9 GB · coding"],
  ["qwen2.5:7b", "4.7 GB · best quality, tight on 8 GB"],
  ["llama3.1:8b", "4.9 GB · tight on 8 GB"],
];

const SUGGESTIONS = [
  ["Explain something", "How does a transformer model work, in simple terms?"],
  ["Write code", "Write a Python script that renames files in a folder by date."],
  ["Brainstorm", "Give me 10 project ideas I can build over a weekend."],
  ["Summarise & rewrite", "Help me rewrite this email to sound more professional."],
];

const state = {
  chats: [],
  current: null, // chat id
  messages: [], // [{role, content}]
  models: [],
  ollamaOk: false,
  streaming: false,
  controller: null,
  settings: loadSettings(),
  stickToBottom: true,
};

/* ------------------------------------------------------------------ utils */
function loadSettings() {
  const d = { system: "", temperature: 0.7, model: "", theme: "" };
  try { return Object.assign(d, JSON.parse(localStorage.getItem("llmchat.settings") || "{}")); }
  catch { return d; }
}
function saveSettings() { localStorage.setItem("llmchat.settings", JSON.stringify(state.settings)); }

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) {
    let msg = r.statusText;
    try { msg = (await r.json()).detail || msg; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return r.status === 204 ? null : r.json();
}

let toastTimer;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
}

function fmtGB(bytes) { return (bytes / 1e9).toFixed(1) + " GB"; }

/* --------------------------------------------------------- markdown (tiny) */
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function inline(s) {
  const codes = [];
  s = s.replace(/`([^`\n]+)`/g, (_, c) => { codes.push(c); return `@@IC${codes.length - 1}@@`; });
  s = s
    .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*\n]*)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  return s.replace(/@@IC(\d+)@@/g, (_, i) => `<code>${codes[+i]}</code>`);
}

function renderMarkdown(src) {
  const blocks = [];
  // Fenced code blocks (also handles an unterminated block while streaming).
  src = src.replace(/```([\w+-]*)[^\n]*\n([\s\S]*?)(```|$)/g, (_, lang, code) => {
    blocks.push({ lang, code: code.replace(/\n$/, "") });
    return `\n@@CB${blocks.length - 1}@@\n`;
  });
  const lines = escapeHtml(src).split("\n");
  let html = "", list = null, para = [];
  const flushPara = () => { if (para.length) { html += `<p>${inline(para.join("<br>"))}</p>`; para = []; } };
  const flushList = () => { if (list) { html += `</${list}>`; list = null; } };

  for (const line of lines) {
    let m;
    if ((m = line.match(/^@@CB(\d+)@@$/))) {
      flushPara(); flushList();
      const b = blocks[+m[1]];
      html += `<div class="codeblock"><div class="codehead"><span>${escapeHtml(b.lang || "code")}</span>` +
              `<button data-copy>Copy</button></div><pre><code>${escapeHtml(b.code)}</code></pre></div>`;
    } else if (!line.trim()) {
      flushPara(); flushList();
    } else if ((m = line.match(/^(#{1,4})\s+(.*)$/))) {
      flushPara(); flushList();
      html += `<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`;
    } else if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
      flushPara(); flushList(); html += "<hr>";
    } else if ((m = line.match(/^\s*[-*+]\s+(.*)$/))) {
      flushPara();
      if (list !== "ul") { flushList(); html += "<ul>"; list = "ul"; }
      html += `<li>${inline(m[1])}</li>`;
    } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
      flushPara();
      if (list !== "ol") { flushList(); html += "<ol>"; list = "ol"; }
      html += `<li>${inline(m[1])}</li>`;
    } else if ((m = line.match(/^&gt;\s?(.*)$/))) {
      flushPara(); flushList();
      html += `<blockquote>${inline(m[1])}</blockquote>`;
    } else {
      flushList(); para.push(line);
    }
  }
  flushPara(); flushList();
  return html;
}

/* --------------------------------------------------------------- rendering */
function currentModel() {
  return $("#modelSelect").value || state.settings.model || "";
}

function renderModels(defaultName) {
  const sel = $("#modelSelect");
  sel.innerHTML = "";
  if (!state.models.length) {
    sel.innerHTML = `<option value="">No models installed</option>`;
    return;
  }
  for (const m of state.models) {
    const o = document.createElement("option");
    o.value = m.name;
    o.textContent = `${m.name}  (${fmtGB(m.size)})`;
    sel.appendChild(o);
  }
  const names = state.models.map((m) => m.name);
  const pick = [state.settings.model, defaultName, defaultName + ":latest"].find((n) => n && names.includes(n)) || names[0];
  sel.value = pick;
}

function groupLabel(ts) {
  const d = new Date(ts * 1000), now = new Date();
  const days = Math.floor((new Date(now.getFullYear(), now.getMonth(), now.getDate()) -
                           new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return "Previous 7 days";
  if (days < 30) return "Previous 30 days";
  return "Older";
}

function renderChatList() {
  const box = $("#chatList");
  const q = $("#search").value.trim().toLowerCase();
  const chats = state.chats.filter((c) => !q || c.title.toLowerCase().includes(q));
  box.innerHTML = "";
  if (!chats.length) {
    box.innerHTML = `<div class="empty-list">${q ? "No matching chats" : "No chats yet. Say hello!"}</div>`;
    return;
  }
  let last = "";
  for (const c of chats) {
    const g = groupLabel(c.updated_at);
    if (g !== last) {
      const h = document.createElement("div");
      h.className = "chat-group"; h.textContent = g; box.appendChild(h); last = g;
    }
    const el = document.createElement("div");
    el.className = "chat-item" + (c.id === state.current ? " active" : "");
    el.innerHTML = `<span class="t"></span><span class="acts">` +
      `<button class="mini" data-act="rename" title="Rename">✎</button>` +
      `<button class="mini del" data-act="delete" title="Delete">✕</button></span>`;
    el.querySelector(".t").textContent = c.title;
    el.addEventListener("click", (e) => {
      const act = e.target.closest("[data-act]")?.dataset.act;
      if (act === "rename") renameChat(c);
      else if (act === "delete") deleteChat(c);
      else openChat(c.id);
    });
    box.appendChild(el);
  }
}

function renderThread() {
  const th = $("#thread");
  th.innerHTML = "";
  if (!state.messages.length) {
    const w = document.createElement("div");
    w.className = "welcome";
    w.innerHTML = `<h1>What can I help with?</h1><p>Your own private AI — nothing leaves this computer.</p><div class="suggest"></div>`;
    const s = w.querySelector(".suggest");
    for (const [title, prompt] of SUGGESTIONS) {
      const b = document.createElement("button");
      b.innerHTML = `<b>${title}</b><small></small>`;
      b.querySelector("small").textContent = prompt;
      b.addEventListener("click", () => send(prompt));
      s.appendChild(b);
    }
    th.appendChild(w);
    return;
  }
  state.messages.forEach((m, i) => th.appendChild(messageEl(m, i)));
  scrollDown(true);
}

function messageEl(m, i) {
  const isLast = i === state.messages.length - 1;
  const el = document.createElement("div");
  el.className = `msg ${m.role}` + (isLast ? " last" : "");
  const body = document.createElement("div");
  body.className = "body";
  if (m.role === "user") body.textContent = m.content;
  else body.innerHTML = renderMarkdown(m.content);

  const col = document.createElement("div");
  col.className = "col";
  col.appendChild(body);

  if (m.role === "assistant") {
    const av = document.createElement("div");
    av.className = "avatar"; av.textContent = "A";
    el.appendChild(av);
    const acts = document.createElement("div");
    acts.className = "msg-actions";
    acts.innerHTML = `<button class="mini" data-a="copy">Copy</button>` +
      (isLast ? `<button class="mini" data-a="regen">↻ Regenerate</button>` : "");
    acts.addEventListener("click", (e) => {
      const a = e.target.dataset.a;
      if (a === "copy") { navigator.clipboard.writeText(m.content); toast("Copied"); }
      if (a === "regen") regenerate();
    });
    if (!(state.streaming && isLast)) col.appendChild(acts);
  } else if (isLast && !state.streaming) {
    // A user message with no reply (e.g. Ollama was down): offer a retry.
    const acts = document.createElement("div");
    acts.className = "msg-actions";
    acts.innerHTML = `<button class="mini" data-a="regen">↻ Get a reply</button>`;
    acts.addEventListener("click", regenerate);
    col.appendChild(acts);
  }
  el.appendChild(col);
  return el;
}

function scrollDown(force) {
  const box = $("#messages");
  if (force || state.stickToBottom) box.scrollTop = box.scrollHeight;
}

/* ------------------------------------------------------------------- data */
async function loadModels() {
  try {
    const r = await api("/api/models");
    state.ollamaOk = r.ok;
    state.models = r.models;
    renderModels(r.default);
    const banner = $("#banner");
    if (!r.ok) {
      banner.classList.remove("hidden");
      banner.innerHTML = `Can't reach Ollama at <code>${escapeHtml(r.ollama)}</code>. Install it from ` +
        `<a href="https://ollama.com/download" target="_blank" rel="noopener">ollama.com/download</a>, ` +
        `then run <code>ollama serve</code>.`;
    } else if (!r.models.length) {
      banner.classList.remove("hidden");
      banner.innerHTML = `No models installed yet. Click <b>Get model</b> and download <code>${escapeHtml(r.default)}</code> to start.`;
    } else {
      banner.classList.add("hidden");
    }
    $("#status").innerHTML = `<span class="dot ${r.ok ? "" : "off"}"></span>${r.ok ? "Ollama connected" : "Ollama offline"}`;
  } catch (e) {
    $("#status").innerHTML = `<span class="dot off"></span>Server offline`;
  }
}

async function loadChats() {
  state.chats = await api("/api/chats");
  renderChatList();
}

async function openChat(id) {
  if (state.streaming) return toast("Wait for the reply to finish, or press stop");
  const c = await api(`/api/chats/${id}`);
  state.current = id;
  state.messages = c.messages.map(({ role, content }) => ({ role, content }));
  if (c.model && state.models.some((m) => m.name === c.model)) $("#modelSelect").value = c.model;
  localStorage.setItem("llmchat.last", id);
  renderChatList();
  renderThread();
  closeSidebar();
  $("#input").focus();
}

function newChat() {
  if (state.streaming) return toast("Wait for the reply to finish, or press stop");
  state.current = null;
  state.messages = [];
  localStorage.removeItem("llmchat.last");
  renderChatList();
  renderThread();
  closeSidebar();
  $("#input").focus();
}

async function renameChat(c) {
  const t = prompt("Rename chat", c.title);
  if (t === null) return;
  const r = await api(`/api/chats/${c.id}`, { method: "PATCH", body: JSON.stringify({ title: t }) });
  c.title = r.title;
  renderChatList();
}

async function deleteChat(c) {
  if (!confirm(`Delete "${c.title}"? This can't be undone.`)) return;
  await api(`/api/chats/${c.id}`, { method: "DELETE" });
  state.chats = state.chats.filter((x) => x.id !== c.id);
  if (state.current === c.id) newChat(); else renderChatList();
}

/* ---------------------------------------------------------------- sending */
function setStreaming(on) {
  state.streaming = on;
  const b = $("#sendBtn");
  b.textContent = on ? "■" : "↑";
  b.title = on ? "Stop" : "Send";
  b.classList.toggle("stop", on);
  b.disabled = false;
}

async function send(text, regen = false) {
  if (state.streaming) return;
  if (!state.models.length || !currentModel()) {
    toast(state.ollamaOk ? "Download a model first (Get model)" : "Ollama isn't running");
    return;
  }
  if (!regen) {
    text = (text || "").trim();
    if (!text) return;
  }
  if (!state.current) {
    const c = await api("/api/chats", { method: "POST", body: JSON.stringify({ model: currentModel() }) });
    state.current = c.id;
    state.chats.unshift(c);
  }
  if (regen) {
    while (state.messages.length && state.messages[state.messages.length - 1].role === "assistant") state.messages.pop();
  } else {
    state.messages.push({ role: "user", content: text });
  }
  const reply = { role: "assistant", content: "" };
  state.messages.push(reply);
  state.stickToBottom = true;
  setStreaming(true);
  renderThread();

  const el = $("#thread").lastElementChild;
  el.classList.add("streaming");
  const body = el.querySelector(".body");
  let raf = 0;
  const paint = () => { raf = 0; body.innerHTML = renderMarkdown(reply.content); scrollDown(); };

  const controller = new AbortController();
  state.controller = controller;
  let errMsg = "", tps = null;

  try {
    const r = await fetch(`/api/chats/${state.current}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        content: regen ? "" : text,
        regenerate: regen,
        model: currentModel(),
        system: state.settings.system,
        temperature: state.settings.temperature,
      }),
    });
    if (!r.ok) {
      let d = r.statusText;
      try { d = (await r.json()).detail || d; } catch { /* ignore */ }
      throw new Error(d);
    }
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line) continue;
        const ev = JSON.parse(line);
        if (ev.type === "meta") {
          const c = state.chats.find((x) => x.id === ev.chat_id);
          if (c) { c.title = ev.title; c.model = ev.model; c.updated_at = Date.now() / 1000; }
          state.chats.sort((a, b) => b.updated_at - a.updated_at);
          renderChatList();
        } else if (ev.type === "token") {
          reply.content += ev.content;
          if (!raf) raf = requestAnimationFrame(paint);
        } else if (ev.type === "error") {
          errMsg = ev.message;
        } else if (ev.type === "done") {
          tps = ev.tokens_per_sec;
        }
      }
    }
  } catch (e) {
    if (e.name !== "AbortError") errMsg = e.message || String(e);
  } finally {
    if (raf) cancelAnimationFrame(raf);
    state.controller = null;
    setStreaming(false);
    if (!reply.content.trim()) state.messages.pop(); // nothing was saved server-side either
    renderThread();
    if (errMsg) {
      const box = document.createElement("div");
      box.className = "msg-err";
      box.textContent = "⚠ " + errMsg;
      $("#thread").appendChild(box);
      scrollDown(true);
      loadModels();
    } else if (tps) {
      const m = document.createElement("div");
      m.className = "meta";
      m.textContent = `${tps} tokens/sec`;
      const last = $("#thread").lastElementChild?.querySelector(".col");
      if (last) last.appendChild(m);
    }
    loadChats();
  }
}

function regenerate() { send("", true); }

function stop() { if (state.controller) state.controller.abort(); }

/* -------------------------------------------------------------------- UI */
function closeSidebar() { $("#sidebar").classList.remove("open"); $("#scrim").classList.remove("open"); }

function applyTheme(t) {
  if (!t) t = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  document.documentElement.dataset.theme = t;
}

function setupPullDialog() {
  const chips = $("#pullChips");
  for (const [name, note] of SUGGESTED_MODELS) {
    const c = document.createElement("button");
    c.type = "button"; c.className = "chip"; c.textContent = name; c.title = note;
    c.addEventListener("click", () => { $("#pullName").value = name; $("#pullStatus").textContent = note; });
    chips.appendChild(c);
  }
  $("#pullBtn").addEventListener("click", () => {
    $("#pullName").value = $("#pullName").value || "llama3.2:3b";
    $("#pullDlg").showModal();
  });
  $("#pullGo").addEventListener("click", async () => {
    const name = $("#pullName").value.trim();
    if (!name) return;
    const bar = $("#pullBar"), wrap = $("#pullProgress"), status = $("#pullStatus"), go = $("#pullGo");
    go.disabled = true; wrap.classList.remove("hidden"); bar.style.width = "0";
    status.textContent = "Starting…";
    try {
      const r = await fetch("/api/pull", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) });
      const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = "", failed = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
          if (!line) continue;
          const ev = JSON.parse(line);
          if (ev.error) { failed = ev.error; continue; }
          if (ev.total && ev.completed) {
            const pct = Math.round((ev.completed / ev.total) * 100);
            bar.style.width = pct + "%";
            status.textContent = `${ev.status} — ${pct}% (${fmtGB(ev.completed)} / ${fmtGB(ev.total)})`;
          } else status.textContent = ev.status || "";
        }
      }
      if (failed) { status.textContent = "Failed: " + failed; }
      else {
        status.textContent = "Done! Model is ready.";
        state.settings.model = name; saveSettings();
        await loadModels();
        toast(`${name} installed`);
      }
    } catch (e) {
      status.textContent = "Failed: " + e.message;
    } finally {
      go.disabled = false;
    }
  });
}

function init() {
  applyTheme(state.settings.theme);

  $("#newChat").addEventListener("click", newChat);
  $("#search").addEventListener("input", renderChatList);
  $("#menuBtn").addEventListener("click", () => { $("#sidebar").classList.add("open"); $("#scrim").classList.add("open"); });
  $("#scrim").addEventListener("click", closeSidebar);
  $("#themeBtn").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    state.settings.theme = next; saveSettings(); applyTheme(next);
  });
  $("#modelSelect").addEventListener("change", (e) => { state.settings.model = e.target.value; saveSettings(); });
  $("#exportBtn").addEventListener("click", () => {
    if (!state.current) return toast("Nothing to export yet");
    window.location = `/api/chats/${state.current}/export`;
  });

  // settings dialog
  $("#settingsBtn").addEventListener("click", () => {
    $("#sysPrompt").value = state.settings.system;
    $("#temp").value = state.settings.temperature;
    $("#tempVal").textContent = state.settings.temperature;
    $("#settingsDlg").showModal();
  });
  $("#temp").addEventListener("input", (e) => { $("#tempVal").textContent = e.target.value; });
  $("#saveSettings").addEventListener("click", () => {
    state.settings.system = $("#sysPrompt").value;
    state.settings.temperature = parseFloat($("#temp").value);
    saveSettings();
    toast("Settings saved");
  });

  // composer
  const input = $("#input");
  const grow = () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 200) + "px"; };
  input.addEventListener("input", grow);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      doSend();
    }
  });
  function doSend() {
    const t = input.value;
    if (!t.trim()) return;
    input.value = ""; grow();
    send(t);
  }
  $("#sendBtn").addEventListener("click", () => (state.streaming ? stop() : doSend()));

  // code-block copy buttons (event delegation)
  $("#thread").addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy]");
    if (!b) return;
    const code = b.closest(".codeblock").querySelector("code").textContent;
    navigator.clipboard.writeText(code);
    b.textContent = "Copied!";
    setTimeout(() => (b.textContent = "Copy"), 1500);
  });

  // auto-scroll only while the user is near the bottom
  $("#messages").addEventListener("scroll", (e) => {
    const el = e.target;
    state.stickToBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  });

  setupPullDialog();

  (async () => {
    await loadModels();
    await loadChats();
    const last = localStorage.getItem("llmchat.last");
    if (last && state.chats.some((c) => c.id === last)) await openChat(last);
    else renderThread();
    setInterval(() => { if (!state.ollamaOk || !state.models.length) loadModels(); }, 8000);
  })();
}

init();
