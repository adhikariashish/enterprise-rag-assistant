/* =========================================================
   Endpoints + DOM
========================================================= */
const CHAT_ENDPOINT = "/chat";
const CHAT_STREAM_ENDPOINT = "/chat/stream";

const messagesInner = document.getElementById("messagesInner");
const formEl = document.getElementById("chatForm");
const inputEl = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const newChatBtn = document.getElementById("newChatBtn");
const chatListEl = document.getElementById("chatList");

const messagesEl = document.querySelector(".messages"); 


/* =========================================================
   App state
========================================================= */
let isWaitingForResponse = false;
let currentAbort = null;
let currentTypingRow = null;

let sessions = [];          // {id,title,messages:[{role,text,citations?}], history:[{role,text}]}
let activeChatId = null;
let renamingChatId = null;

// streaming accumulation
let pendingCitations = [];
let streamingAssistantText = "";

/* =========================================================
   Utils
========================================================= */
function escapeHtmlSafe(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function makeId() {
  return "c_" + Math.random().toString(36).slice(2, 10);
}

function scrollToBottom(force = false) {
  const container = messagesEl || messagesInner; // fallback 

  
  const distanceFromBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight;

  const nearBottom = distanceFromBottom < 120;

  if (force || nearBottom) {
    container.scrollTop = container.scrollHeight;
  }
}


function autosizeTextarea() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 180) + "px";
}

function setSendEnabled() {
  const hasText = (inputEl.value || "").trim().length > 0;

  if (isWaitingForResponse) {
    sendBtn.disabled = false; // Stop always clickable
    sendBtn.textContent = "Stop";
  } else {
    sendBtn.textContent = "Send";
    sendBtn.disabled = !hasText;
  }
}



/* =========================================================
   Assistant formatting (safe)
========================================================= */
function formatAssistantTextSafe(text) {
  try {
    const lines = String(text ?? "").split("\n");

    const isBullet = (s) => /^\s*[-•]\s+/.test(s);
    const isNumber = (s) => /^\s*\d+\.\s+/.test(s);

    let html = "";
    let i = 0;

    while (i < lines.length) {
      const raw = lines[i];
      const line = (raw ?? "").trimEnd();

      // skip extra blank lines
      if (line.trim() === "") {
        i++;
        continue;
      }

      if (isBullet(line)) {
        html += "<ul>";
        while (i < lines.length && isBullet(lines[i])) {
          const item = lines[i].replace(/^\s*[-•]\s+/, "");
          html += `<li>${escapeHtmlSafe(item)}</li>`;
          i++;
        }
        html += "</ul>";
        continue;
      }

      if (isNumber(line)) {
        html += "<ol>";
        while (i < lines.length && isNumber(lines[i])) {
          const item = lines[i].replace(/^\s*\d+\.\s+/, "");
          html += `<li>${escapeHtmlSafe(item)}</li>`;
          i++;
        }
        html += "</ol>";
        continue;
      }

      html += `<p>${escapeHtmlSafe(line)}</p>`;
      i++;
    }

    return html || `<p>${escapeHtmlSafe(text)}</p>`;
  } catch {
    return `<p>${escapeHtmlSafe(text)}</p>`;
  }
}

/* =========================================================
   UI: messages
========================================================= */
function makeTypingNode() {
  const wrap = document.createElement("span");
  wrap.className = "typing";
  wrap.innerHTML = "<span></span><span></span><span></span>";
  return wrap;
}

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "assistant") {
    bubble.innerHTML = formatAssistantTextSafe(text);
  } else {
    bubble.textContent = text;
  }

  row.appendChild(bubble);
  messagesInner.appendChild(row);
  scrollToBottom(true);
  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "message assistant";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.appendChild(makeTypingNode());

  row.appendChild(bubble);
  messagesInner.appendChild(row);
  scrollToBottom(true);
  return row;
}

function addAssistantMessageWithCitations(text, citations = []) {
  // Build row so citations are BELOW the bubble (not inside it)
  const row = document.createElement("div");
  row.className = "message assistant assistant-block"; // <-- important

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = formatAssistantTextSafe(text);

  row.appendChild(bubble);

  if (Array.isArray(citations) && citations.length > 0) {
    const citeWrap = document.createElement("div");
    citeWrap.className = "citations";

    const header = document.createElement("button");
    header.type = "button";
    header.className = "citations-toggle";
    header.textContent = `Sources (${citations.length})`;

    const list = document.createElement("div");
    list.className = "citations-list";
    list.style.display = "none";

    citations.forEach((c) => {
      const item = document.createElement("div");
      item.className = "citation-item";

      const src = escapeHtmlSafe(c?.source || "source");
      const page = c?.page ? `, p. ${escapeHtmlSafe(String(c.page))}` : "";

      item.innerHTML = `
        <div class="citation-src">${src}${page}</div>
      `;
      list.appendChild(item);
    });

    header.addEventListener("click", () => {
      list.style.display = (list.style.display === "none") ? "block" : "none";
    });

    citeWrap.appendChild(header);
    citeWrap.appendChild(list);
    row.appendChild(citeWrap);
  }

  messagesInner.appendChild(row);
  scrollToBottom(true);
}



/* =========================================================
   Sessions (sidebar)
========================================================= */
function getActiveChat() {
  return sessions.find((c) => c.id === activeChatId) || null;
}

function createNewChatSession() {
  const id = makeId();
  const chat = {
    id,
    title: "New chat",
    messages: [{ role: "assistant", text: "Welcome! How can I help you." }],
    history: [],
  };
  sessions.unshift(chat);
  activeChatId = id;
  renderSidebarChats();
  loadChat(id);
  return chat;
}

function setChatTitleIfDefault(chat, userMsg) {
  if (chat.title === "New chat") {
    const t = (userMsg || "").trim().slice(0, 28);
    chat.title = t || "Chat";
    renderSidebarChats();
  }
}

function startRenameChat(chatId) {
  renamingChatId = chatId;
  renderSidebarChats();
}

function renderSidebarChats() {
  if (!chatListEl) return;
  chatListEl.innerHTML = "";

  for (const chat of sessions) {
    // rename mode
    if (renamingChatId === chat.id) {
      const input = document.createElement("input");
      input.className = "sb-rename-input";
      input.type = "text";
      input.value = chat.title === "New chat" ? "" : chat.title;
      input.maxLength = 60;

      const finish = (save) => {
        const v = (input.value || "").trim();
        if (save) chat.title = v || "Chat";
        renamingChatId = null;
        renderSidebarChats();
      };

      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") finish(true);
        if (e.key === "Escape") finish(false);
      });
      input.addEventListener("blur", () => finish(true));

      chatListEl.appendChild(input);
      setTimeout(() => {
        input.focus();
        input.select();
      }, 0);
      continue;
    }

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sb-item sb-chat-btn" + (chat.id === activeChatId ? " active" : "");

    const titleSpan = document.createElement("span");
    titleSpan.className = "sb-chat-title";
    titleSpan.textContent = chat.title;

    const editBtn = document.createElement("span");
    editBtn.className = "sb-chat-edit";
    editBtn.textContent = "✎";
    editBtn.title = "Rename";

    editBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      startRenameChat(chat.id);
    });

    btn.addEventListener("click", () => loadChat(chat.id));
    btn.addEventListener("dblclick", (e) => {
      e.preventDefault();
      startRenameChat(chat.id);
    });

    btn.appendChild(titleSpan);
    btn.appendChild(editBtn);
    chatListEl.appendChild(btn);
  }
}

function loadChat(id) {
  const chat = sessions.find((c) => c.id === id);
  if (!chat) return;

  activeChatId = id;

  // render messages
  messagesInner.innerHTML = "";
  for (const m of chat.messages) {
    if (m.role === "assistant") {
      addAssistantMessageWithCitations(m.text, m.citations || []);
    } else {
      addMessage(m.role, m.text);
    }
  }

  renderSidebarChats();
  scrollToBottom();
}

/* =========================================================
   Theme
========================================================= */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  if (themeIcon) themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
}

(function initTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || saved === "light") return applyTheme(saved);
  const prefersDark =
    window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(prefersDark ? "dark" : "light");
})();

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(current === "dark" ? "light" : "dark");
  });
}

/* =========================================================
   SSE parsing + streaming
========================================================= */
function parseSSEChunk(raw) {
  // returns { events: [{event,data}], rest: string }
  const events = [];
  const parts = raw.split("\n\n");
  const rest = parts.pop() || "";

  for (const block of parts) {
    const lines = block.split("\n");
    let evt = "message";
    let data = "";

    for (const line of lines) {
      if (line.startsWith("event:")) evt = line.slice(6).trim();
      if (line.startsWith("data:")) data += line.slice(5).trim();
    }

    events.push({ event: evt, data });
  }

  return { events, rest };
}

async function streamChat({ message, history, onCitations, onToken, onDone }) {
  const res = await fetch(CHAT_STREAM_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
    signal: currentAbort.signal,
  });

  if (!res.ok) throw new Error(await res.text());
  if (!res.body) throw new Error("No response body (streaming unsupported?)");

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";
  let done = false;

  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

    const parsed = parseSSEChunk(buffer);
    buffer = parsed.rest;

    for (const evt of parsed.events) {
      if (evt.event === "citations") {
        try {
          onCitations(JSON.parse(evt.data || "[]"));
        } catch {
          onCitations([]);
        }
      } else if (evt.event === "token" || evt.event === "message") {
        // token event payload can be JSON {t:"..."} or raw text
        let chunk = "";
        try {
          const obj = JSON.parse(evt.data || "{}");
          chunk = obj.t ?? obj.token ?? obj.text ?? obj.delta ?? obj.content ?? "";
        } catch {
          chunk = evt.data || "";
        }
        if (chunk) onToken(chunk);
      } else if (evt.event === "done") {
        onDone();
        return;
      }
    }
  }

  onDone();
}

/* =========================================================
   Send / Stop behavior
========================================================= */
function stopStreamingUIOnly() {
  // client-side stop
  try {
    if (currentAbort) currentAbort.abort();
  } catch {}

  if (currentTypingRow) {
    currentTypingRow.remove();
    currentTypingRow = null;
  }

  isWaitingForResponse = false;
  currentAbort = null;
  setSendEnabled();
}

sendBtn.addEventListener("click", (e) => {
  if (!isWaitingForResponse) return; // normal submit handled by form submit
  e.preventDefault();
  stopStreamingUIOnly();

  // UI-only system message (don’t add to history)
  const chat = getActiveChat();
  addMessage("system", "Okay — I’ll stop here.");
  if (chat) chat.messages.push({ role: "system", text: "Okay — I’ll stop here." });
});

/* =========================================================
   Event wiring
========================================================= */
inputEl.addEventListener("input", () => {
  setSendEnabled();
  autosizeTextarea();
});

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    if (isWaitingForResponse) return; // block enter-submit while waiting
    e.preventDefault();
    if (!sendBtn.disabled) formEl.requestSubmit();
  }
});

newChatBtn.addEventListener("click", () => {
  // if running, stop UI
  if (isWaitingForResponse) stopStreamingUIOnly();

  const chat = getActiveChat();
  const hasUserMessage =
    chat &&
    Array.isArray(chat.messages) &&
    chat.messages.some((m) => m.role === "user" && (m.text || "").trim().length > 0);

  // Only create a new chat if current has a user message (avoid blank chats)
  if (!chat || hasUserMessage) {
    createNewChatSession();
  } else {
    // current is blank -> do nothing, just focus
    inputEl.value = "";
    autosizeTextarea();
    inputEl.focus();
  }

  setSendEnabled();
});

/* =========================================================
   Submit handler (STREAMING)
========================================================= */
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Ensure chat exists
  if (!getActiveChat()) createNewChatSession();
  const chat = getActiveChat();

  const msg = (inputEl.value || "").trim();
  if (!msg) return;
  if (isWaitingForResponse) return;

  // Render user msg
  addMessage("user", msg);
  chat.messages.push({ role: "user", text: msg });
  setChatTitleIfDefault(chat, msg);

  // Add to backend history
  chat.history.push({ role: "user", text: msg });

  // reset input
  inputEl.value = "";
  autosizeTextarea();

  // waiting state
  isWaitingForResponse = true;
  setSendEnabled();

  // streaming state reset
  pendingCitations = [];
  streamingAssistantText = "";

  // show typing bubble for streaming output (we will replace it with final)
  currentTypingRow = addTyping();
  currentAbort = new AbortController();

  try {
    await streamChat({
      message: msg,
      history: chat.history,
      onCitations: (cites) => {
        // IMPORTANT: only store here — do not render here
        pendingCitations = Array.isArray(cites) ? cites : [];
      },
      onToken: (chunk) => {
        streamingAssistantText += chunk;

        // Update typing bubble to show partial text
        if (currentTypingRow) {
          const bubble = currentTypingRow.querySelector(".bubble");
          if (bubble) bubble.innerHTML = formatAssistantTextSafe(streamingAssistantText);
          scrollToBottom(true);
        }
      },
      onDone: () => {},
    });

    // Replace typing bubble with final assistant message + citations (BOTTOM only)
    if (currentTypingRow) currentTypingRow.remove();
    currentTypingRow = null;

    const finalText =
      (streamingAssistantText || "").trim() || "Sorry — I couldn’t generate a response.";

    addAssistantMessageWithCitations(finalText, pendingCitations);

    // persist messages
    chat.messages.push({ role: "assistant", text: finalText, citations: pendingCitations });

    // persist history (NO citations in history, just text)
    chat.history.push({ role: "assistant", text: finalText });
  } catch (err) {
    if (currentTypingRow) currentTypingRow.remove();
    currentTypingRow = null;

    if (err?.name === "AbortError") {
      // already handled by Stop click; keep quiet
    } else {
      addMessage("system", "Sorry — something went wrong contacting the server.");
      chat.messages.push({ role: "system", text: "Sorry — something went wrong contacting the server." });
      console.error(err);
    }
  } finally {
    isWaitingForResponse = false;
    currentAbort = null;
    setSendEnabled();
    inputEl.focus();
  }
});

/* =========================================================
   Init
========================================================= */
setSendEnabled();
autosizeTextarea();
createNewChatSession();
