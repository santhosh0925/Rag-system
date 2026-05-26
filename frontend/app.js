const $ = (id) => document.getElementById(id);

function setStatus(el, msg, kind) {
  el.textContent = msg || "";
  el.classList.remove("ok", "err");
  if (kind) el.classList.add(kind);
}

function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `bubble ${role}`;

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = role === "user" ? "You" : "Assistant";

  const body = document.createElement("div");
  body.textContent = text;

  wrap.appendChild(meta);
  wrap.appendChild(body);
  $("messages").appendChild(wrap);
  $("messages").scrollTop = $("messages").scrollHeight;
}

function getApiBase() {
  const raw = $("apiBase").value.trim();
  return raw.replace(/\/+$/, "");
}

async function api(path, opts = {}) {
  const base = getApiBase();
  const url = `${base}${path}`;
  const res = await fetch(url, opts);
  const isJson = (res.headers.get("content-type") || "").includes("application/json");
  const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => "");
  if (!res.ok) {
    const detail = data?.detail || data?.message || (typeof data === "string" ? data : null);
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data;
}

function defaultApiBase() {
  const sameOrigin = window.location.origin;
  if (sameOrigin && sameOrigin !== "null") return sameOrigin;
  return "http://127.0.0.1:8000";
}

function init() {
  $("apiBase").value = defaultApiBase();

  $("pingBtn").addEventListener("click", async () => {
    setStatus($("pingStatus"), "Pinging…");
    try {
      await api("/api/health");
      setStatus($("pingStatus"), "OK", "ok");
    } catch (e) {
      setStatus($("pingStatus"), e.message, "err");
    }
  });

  $("uploadBtn").addEventListener("click", async () => {
    setStatus($("ingestStatus"), "");
    const files = $("files").files;
    if (!files || files.length === 0) {
      setStatus($("pingStatus"), "Pick one or more .txt files first.", "err");
      return;
    }
    setStatus($("pingStatus"), "Uploading…");
    try {
      const fd = new FormData();
      for (const f of files) fd.append("files", f);
      const out = await api("/api/upload", { method: "POST", body: fd });
      setStatus($("pingStatus"), `Uploaded: ${out.saved.join(", ")}`, "ok");
    } catch (e) {
      setStatus($("pingStatus"), e.message, "err");
    }
  });

  $("ingestBtn").addEventListener("click", async () => {
    setStatus($("ingestStatus"), "Ingesting…");
    try {
      await api("/api/ingest", { method: "POST" });
      setStatus($("ingestStatus"), "Ingest complete.", "ok");
    } catch (e) {
      setStatus($("ingestStatus"), e.message, "err");
    }
  });

  $("chatForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    setStatus($("chatStatus"), "");
    const q = $("question").value.trim();
    if (!q) return;
    $("question").value = "";
    addMessage("user", q);
    setStatus($("chatStatus"), "Thinking…");
    try {
      const out = await api("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      addMessage("assistant", out.answer);
      setStatus($("chatStatus"), "", "ok");
    } catch (e) {
      addMessage("assistant", `Error: ${e.message}`);
      setStatus($("chatStatus"), e.message, "err");
    }
  });
}

init();

