const API_BASE   = "http://localhost:8000";
  const MAX_CHARS  = 1500;

  let activeTask = "log_analysis";
  let isLoading  = false;

  // ── Task selector ──
  document.querySelectorAll(".task-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".task-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeTask = btn.dataset.task;
    });
  });

  // ── Textarea auto-resize ──
  const input = document.getElementById("userInput");
  const charCount = document.getElementById("charCount");

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
    const len = input.value.length;
    charCount.textContent = `${len} / ${MAX_CHARS}`;
    charCount.className = "char-count" + (len > MAX_CHARS ? " over" : len > 1200 ? " warn" : "");
  });

  // ── Enter to send (Shift+Enter = new line) ──
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  document.getElementById("sendBtn").addEventListener("click", sendMessage);

  // ── DOM helpers ──
  function appendMsg(role, content, task = null) {
    const msgs = document.getElementById("messages");
    const div  = document.createElement("div");
    div.className = `msg ${role}`;

    let inner = "";
    if (role === "user") {
      inner = `<div class="avatar user-av">tú</div>
               <div class="bubble">${escHtml(content)}</div>`;
    } else if (role === "bot") {
      const tag = task === "log_analysis"
        ? `<span class="task-tag tag-log">log_analysis</span>`
        : `<span class="task-tag tag-alert">alert_classification</span>`;
      inner = `<div class="avatar bot-av">IA</div>
               <div class="bubble">${tag}<br>${formatResponse(content)}</div>`;
    } else if (role === "error-msg") {
      inner = `<div class="bubble">⚠️ ${escHtml(content)}</div>`;
    }

    div.innerHTML = inner;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  }

  function appendTyping() {
    const msgs = document.getElementById("messages");
    const div  = document.createElement("div");
    div.className = "msg bot";
    div.id = "typing-indicator";
    div.innerHTML = `<div class="avatar bot-av">IA</div>
                     <div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function removeTyping() {
    document.getElementById("typing-indicator")?.remove();
  }

  function escHtml(t) {
    return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  function formatResponse(text) {
    // Formato básico: negritas con **texto**, saltos de línea, bloques de código
    return escHtml(text)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code style='background:#0d1117;padding:1px 5px;border-radius:3px;font-family:var(--font-mono);font-size:12px'>$1</code>")
      .replace(/\n/g, "<br>");
  }

  // ── Send message ──
  async function sendMessage() {
    const text = input.value.trim();
    if (!text || isLoading) return;
    if (text.length > MAX_CHARS) {
      appendMsg("error-msg", `El mensaje excede ${MAX_CHARS} caracteres.`);
      return;
    }

    isLoading = true;
    document.getElementById("sendBtn").disabled = true;
    input.value = "";
    input.style.height = "auto";
    charCount.textContent = `0 / ${MAX_CHARS}`;
    charCount.className = "char-count";

    appendMsg("user", text);
    appendTyping();

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: activeTask, message: text }),
      });

      removeTyping();

      if (!res.ok) {
        const err = await res.json();
        appendMsg("error-msg", err.detail || "Error desconocido del servidor.");
      } else {
        const data = await res.json();
        appendMsg("bot", data.response, data.task);
      }
    } catch (e) {
      removeTyping();
      appendMsg("error-msg", "No se pudo conectar con la API. Verifica que el servidor esté corriendo en localhost:8000");
    }

    isLoading = false;
    document.getElementById("sendBtn").disabled = false;
    input.focus();
  }