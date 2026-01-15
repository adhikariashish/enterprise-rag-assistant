# app/web/chat_ui.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

router = APIRouter(prefix="/ui", tags=["web-ui"])

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Consultancy RAG Bot</title>
  <style>
    :root{
      --bg: #0b0f14;
      --panel: #0f1520;
      --panel2:#0c1220;
      --border:#223047;
      --text:#e6edf3;
      --muted:#9fb0c3;
      --accent:#3b82f6;
      --bubble-user:#2563eb;
      --bubble-bot:#141e2e;
      --bubble-bot-2:#101827;
      --shadow: 0 10px 30px rgba(0,0,0,0.35);
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    html,body { height: 100%; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }

    /* Layout */
    .app {
      height: 100%;
      display: grid;
      grid-template-columns: 300px 1fr;
    }

    /* Sidebar */
    .sidebar {
      background: linear-gradient(180deg, #0b1220, #090e14);
      border-right: 1px solid var(--border);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .brand {
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      padding: 10px 10px;
      border:1px solid var(--border);
      border-radius: var(--radius);
      background: rgba(255,255,255,0.02);
      box-shadow: var(--shadow);
    }
    .brand h1{
      font-size: 14px;
      margin:0;
      font-weight:700;
      letter-spacing: 0.2px;
    }
    .badge{
      font-size: 11px;
      color: var(--muted);
      border:1px solid var(--border);
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(255,255,255,0.02);
      white-space: nowrap;
    }

    .btn {
      display:flex;
      gap:10px;
      align-items:center;
      justify-content:center;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 14px;
      cursor: pointer;
      user-select: none;
    }
    .btn:hover { border-color: var(--accent); }
    .btn.primary{
      background: rgba(59,130,246,0.15);
      border-color: rgba(59,130,246,0.5);
    }
    .btn.primary:hover{
      border-color: var(--accent);
      background: rgba(59,130,246,0.22);
    }

    .list {
      flex: 1;
      overflow:auto;
      padding: 6px 2px;
      display:flex;
      flex-direction: column;
      gap: 8px;
    }
    .chatItem{
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.02);
      border-radius: 14px;
      padding: 10px 10px;
      cursor:pointer;
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:10px;
    }
    .chatItem:hover { border-color: rgba(59,130,246,0.7); }
    .chatItem.active {
      border-color: rgba(59,130,246,0.9);
      background: rgba(59,130,246,0.10);
    }
    .chatTitle{
      font-size: 13px;
      font-weight: 650;
      margin:0;
      line-height: 1.2;
    }
    .chatMeta{
      margin-top: 4px;
      font-size: 11px;
      color: var(--muted);
      line-height: 1.2;
    }
    .chatActions{
      display:flex;
      flex-direction: column;
      gap: 6px;
      opacity: 0.9;
    }
    .iconBtn{
      border: 1px solid var(--border);
      background: rgba(0,0,0,0.15);
      color: var(--text);
      border-radius: 10px;
      padding: 6px 8px;
      cursor:pointer;
      font-size: 12px;
      line-height: 1;
    }
    .iconBtn:hover { border-color: var(--accent); }

    .hint{
      font-size: 12px;
      color: var(--muted);
      padding: 10px;
      border: 1px dashed rgba(255,255,255,0.12);
      border-radius: 14px;
      background: rgba(255,255,255,0.02);
    }

    /* Main */
    .main{
      display:flex;
      flex-direction: column;
      height:100%;
      min-width: 0;
    }
    .topbar{
      padding: 12px 18px;
      border-bottom: 1px solid var(--border);
      background: rgba(15,21,32,0.75);
      backdrop-filter: blur(6px);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
    }
    .topbar .title{
      display:flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }
    .topbar .title strong{
      font-size: 14px;
      font-weight: 800;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .topbar .title span{
      font-size: 12px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .topbar .right{
      display:flex;
      align-items:center;
      gap:10px;
    }
    .pill{
      font-size: 12px;
      color: var(--muted);
      border:1px solid var(--border);
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,0.02);
    }

    .chatArea{
      flex:1;
      overflow:auto;
      padding: 18px;
      background: radial-gradient(1200px 600px at 60% -10%, rgba(59,130,246,0.12), transparent 55%),
                  radial-gradient(900px 400px at 10% 10%, rgba(255,255,255,0.06), transparent 50%),
                  var(--bg);
    }

    .msgRow{
      display:flex;
      gap: 10px;
      margin: 10px 0;
      align-items:flex-end;
    }
    .msgRow.me{ justify-content:flex-end; }
    .msgRow.bot{ justify-content:flex-start; }

    .avatar{
      width: 30px;
      height: 30px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.04);
      display:flex;
      align-items:center;
      justify-content:center;
      font-size: 13px;
      color: var(--muted);
      flex: 0 0 auto;
    }

    .bubble{
      max-width: 820px;
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.06);
      white-space: pre-wrap;
      line-height: 1.45;
      box-shadow: var(--shadow);
    }
    .me .bubble{
      background: linear-gradient(180deg, rgba(37,99,235,0.95), rgba(37,99,235,0.75));
      color: #fff;
      border-color: rgba(255,255,255,0.12);
    }
    .bot .bubble{
      background: linear-gradient(180deg, rgba(20,30,46,0.95), rgba(16,24,39,0.85));
      color: var(--text);
      border-color: rgba(255,255,255,0.08);
    }

    .bubble .metaLine{
      margin-top: 10px;
      font-size: 12px;
      color: var(--muted);
      opacity: 0.95;
    }

    details.cites{
      margin-top: 10px;
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 12px;
      padding: 8px 10px;
      background: rgba(0,0,0,0.14);
    }
    details.cites > summary{
      cursor: pointer;
      font-size: 12px;
      color: var(--muted);
      list-style: none;
      user-select: none;
    }
    details.cites > summary::-webkit-details-marker { display:none; }
    .citeList{
      margin-top: 10px;
      font-size: 12px;
      color: var(--text);
      line-height: 1.4;
      white-space: pre-wrap;
    }
    .citeItem{
      padding: 8px 8px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.03);
      margin-bottom: 8px;
    }
    .citeItem .small{
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
      white-space: pre-wrap;
    }

    /* Composer */
    .composer{
      padding: 14px 18px;
      border-top: 1px solid var(--border);
      background: rgba(15,21,32,0.8);
      backdrop-filter: blur(6px);
    }
    .composerRow{
      display:flex;
      gap: 10px;
      align-items:center;
    }
    .input{
      flex:1;
      padding: 12px 12px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(11,18,32,0.9);
      color: var(--text);
      outline: none;
      box-shadow: var(--shadow);
    }
    .input:focus{ border-color: rgba(59,130,246,0.85); }
    .send{
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(59,130,246,0.5);
      background: rgba(59,130,246,0.18);
      color: var(--text);
      cursor:pointer;
      box-shadow: var(--shadow);
      min-width: 92px;
    }
    .send:hover{ background: rgba(59,130,246,0.25); border-color: rgba(59,130,246,0.9); }
    .footerNote{
      margin-top: 10px;
      font-size: 12px;
      color: var(--muted);
      display:flex;
      justify-content:space-between;
      gap:10px;
      flex-wrap: wrap;
    }

    @media (max-width: 900px){
      .app{ grid-template-columns: 1fr; }
      .sidebar{ display:none; }
      .bubble{ max-width: 100%; }
    }
  </style>
</head>

<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <h1>Consultancy Bot</h1>
      <div class="badge">Local RAG</div>
    </div>

    <div class="btn primary" id="newChatBtn">+ New chat</div>

    <div class="list" id="chatList"></div>

    <div class="hint">
      Tip: Put PDFs into <b>data/docs/&lt;doc_type&gt;</b> and re-ingest.
      <div style="margin-top:6px; color: var(--muted);">
        Doc types: moa, aoa, memo, rule
      </div>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="title">
        <strong id="activeTitle">New chat</strong>
        <span id="activeSubtitle">Ask about MOA / AOA / memo / rule PDFs</span>
      </div>
      <div class="right">
        <div class="pill" id="statusPill">Ready</div>
      </div>
    </div>

    <div class="chatArea" id="chatArea"></div>

    <div class="composer">
      <div class="composerRow">
        <input class="input" id="inp" placeholder="Message..." autocomplete="off" />
        <button class="send" id="sendBtn">Send</button>
      </div>
      <div class="footerNote">
        <span>Enter to send • Shift+Enter for newline</span>
        <span>UI: /ui • API: /chat</span>
      </div>
    </div>
  </main>
</div>

<script>
(function(){
  // ---------- Storage helpers ----------
  var KEY = "consultancy_rag_ui_chats_v1";

  function nowTs(){ return new Date().toISOString(); }

  function loadState(){
    try{
      var raw = localStorage.getItem(KEY);
      if(!raw) return { activeId: null, chats: {} };
      var st = JSON.parse(raw);
      if(!st || typeof st !== "object") return { activeId: null, chats: {} };
      if(!st.chats) st.chats = {};
      return st;
    }catch(e){
      return { activeId: null, chats: {} };
    }
  }

  function saveState(st){
    localStorage.setItem(KEY, JSON.stringify(st));
  }

  function newId(){
    return "c_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
  }

  function summarizeTitle(msg){
    msg = (msg || "").trim();
    if(!msg) return "New chat";
    if(msg.length <= 40) return msg;
    return msg.slice(0, 40) + "...";
  }

  // ---------- DOM ----------
  var chatList = document.getElementById("chatList");
  var chatArea = document.getElementById("chatArea");
  var newChatBtn = document.getElementById("newChatBtn");
  var inp = document.getElementById("inp");
  var sendBtn = document.getElementById("sendBtn");
  var activeTitle = document.getElementById("activeTitle");
  var activeSubtitle = document.getElementById("activeSubtitle");
  var statusPill = document.getElementById("statusPill");

  // ---------- State ----------
  var state = loadState();

  function ensureActiveChat(){
    if(state.activeId && state.chats[state.activeId]) return;
    var id = newId();
    state.activeId = id;
    state.chats[id] = {
      id: id,
      title: "New chat",
      created_at: nowTs(),
      updated_at: nowTs(),
      messages: [
        { role: "assistant", text: "Hi! Ask me about MOA / AOA / memo / rule PDFs.", citations: [] }
      ]
    };
    saveState(state);
  }

  ensureActiveChat();

  // ---------- UI rendering ----------
  function clearEl(el){
    while(el.firstChild) el.removeChild(el.firstChild);
  }

  function renderChatList(){
    clearEl(chatList);

    var ids = Object.keys(state.chats);
    ids.sort(function(a,b){
      var A = state.chats[a].updated_at || "";
      var B = state.chats[b].updated_at || "";
      return (A < B) ? 1 : (A > B) ? -1 : 0;
    });

    for(var i=0;i<ids.length;i++){
      (function(chatId){
        var c = state.chats[chatId];

        var item = document.createElement("div");
        item.className = "chatItem" + (chatId === state.activeId ? " active" : "");

        var left = document.createElement("div");
        left.style.minWidth = "0";

        var t = document.createElement("div");
        t.className = "chatTitle";
        t.textContent = c.title || "New chat";

        var m = document.createElement("div");
        m.className = "chatMeta";
        var count = (c.messages && c.messages.length) ? c.messages.length : 0;
        m.textContent = count + " msgs";

        left.appendChild(t);
        left.appendChild(m);

        var actions = document.createElement("div");
        actions.className = "chatActions";

        var del = document.createElement("button");
        del.className = "iconBtn";
        del.textContent = "🗑";
        del.title = "Delete chat";
        del.onclick = function(ev){
          ev.stopPropagation();
          delete state.chats[chatId];
          if(state.activeId === chatId){
            state.activeId = null;
            ensureActiveChat();
          }
          saveState(state);
          renderChatList();
          renderActiveChat();
        };

        actions.appendChild(del);

        item.appendChild(left);
        item.appendChild(actions);

        item.onclick = function(){
          state.activeId = chatId;
          saveState(state);
          renderChatList();
          renderActiveChat();
        };

        chatList.appendChild(item);
      })(ids[i]);
    }
  }

  function makeMsgRow(role, text, citations){
    var row = document.createElement("div");
    row.className = "msgRow " + (role === "user" ? "me" : "bot");

    if(role !== "user"){
      var av = document.createElement("div");
      av.className = "avatar";
      av.textContent = "AI";
      row.appendChild(av);
    }

    var bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text || "";

    // citations for assistant messages
    if(role !== "user" && Array.isArray(citations) && citations.length > 0){
      var details = document.createElement("details");
      details.className = "cites";

      var sum = document.createElement("summary");
      sum.textContent = "Citations (" + citations.length + ")";
      details.appendChild(sum);

      var list = document.createElement("div");
      list.className = "citeList";

      for(var i=0;i<citations.length;i++){
        var c = citations[i] || {};
        var src = (typeof c.source === "string" && c.source) ? c.source : "unknown";
        var dt = (typeof c.doc_type === "string" && c.doc_type) ? c.doc_type
               : (typeof c.locator === "string" && c.locator) ? c.locator : "";
        var pg = (c.page !== undefined && c.page !== null) ? ("p." + c.page) : "";
        var sn = (typeof c.snippet === "string" && c.snippet) ? c.snippet : "";

        var item = document.createElement("div");
        item.className = "citeItem";

        var head = document.createElement("div");
        head.textContent = src + (pg ? (" | " + pg) : "") + (dt ? (" | " + dt) : "");

        item.appendChild(head);

        if(sn){
          var sm = document.createElement("div");
          sm.className = "small";
          sm.textContent = sn;
          item.appendChild(sm);
        }
        list.appendChild(item);
      }

      details.appendChild(list);
      bubble.appendChild(details);
    }

    if(role === "user"){
      row.appendChild(bubble);
    }else{
      row.appendChild(bubble);
    }

    return row;
  }

  function renderActiveChat(){
    ensureActiveChat();
    var c = state.chats[state.activeId];

    activeTitle.textContent = c.title || "New chat";
    activeSubtitle.textContent = "Doc routing: moa / aoa / memo / rule";

    clearEl(chatArea);

    var msgs = c.messages || [];
    for(var i=0;i<msgs.length;i++){
      var m = msgs[i];
      chatArea.appendChild(makeMsgRow(m.role, m.text, m.citations));
    }

    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function setStatus(txt){
    statusPill.textContent = txt;
  }

  // ---------- API ----------
  async function callChat(message){
    var c = state.chats[state.activeId];
    var msgs = (c && c.messages) ? c.messages : [];

    // last 12 messages = last 6 turns (user+assistant)
    var start = Math.max(0, msgs.length - 12);

    var history = [];
    for (var i = start; i < msgs.length; i++) {
        var m = msgs[i];
        if (!m || !m.role || !m.text) continue;

        var role = (m.role === "assistant") ? "assistant" : "user";
        history.push({ role: role, text: m.text });
    }

    var payload = {
        message: message,
        session_id: state.activeId,
        history: history
    };

    var res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if(!res.ok){
        var t = await res.text();
        throw new Error(t || ("HTTP " + res.status));
    }
    return await res.json();
  }

  function pushMessage(role, text, citations){
    var c = state.chats[state.activeId];
    if(!c.messages) c.messages = [];
    c.messages.push({ role: role, text: text, citations: citations || [] });
    c.updated_at = nowTs();

    // set title from first user message
    if(role === "user" && (c.title === "New chat" || !c.title)){
      c.title = summarizeTitle(text);
    }

    saveState(state);
  }

  function addTyping(){
    var row = document.createElement("div");
    row.className = "msgRow bot";
    row.id = "typingRow";

    var av = document.createElement("div");
    av.className = "avatar";
    av.textContent = "AI";
    row.appendChild(av);

    var bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = "Typing…";
    row.appendChild(bubble);

    chatArea.appendChild(row);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function removeTyping(){
    var t = document.getElementById("typingRow");
    if(t && t.parentNode) t.parentNode.removeChild(t);
  }

  // ---------- Actions ----------
  async function onSend(){
    var message = inp.value || "";
    message = message.trim();
    if(!message) return;

    setStatus("Thinking…");

    // render user message immediately
    pushMessage("user", message, []);
    renderChatList();
    renderActiveChat();

    inp.value = "";
    inp.focus();

    addTyping();

    try{
      var out = await callChat(message);

      removeTyping();

      // backend may return {answer,citations} or {response,citations}
      var ans = out.answer || out.response || "(no answer)";
      var cites = Array.isArray(out.citations) ? out.citations : [];

      pushMessage("assistant", ans, cites);
      renderChatList();
      renderActiveChat();

      setStatus("Ready");
    }catch(e){
      removeTyping();
      pushMessage("assistant", "Error: " + (e && e.message ? e.message : String(e)), []);
      renderChatList();
      renderActiveChat();
      setStatus("Error");
    }
  }

  function createNewChat(){
    var id = newId();
    state.activeId = id;
    state.chats[id] = {
      id: id,
      title: "New chat",
      created_at: nowTs(),
      updated_at: nowTs(),
      messages: [
        { role: "assistant", text: "Hi! Ask me about MOA / AOA / memo / rule PDFs.", citations: [] }
      ]
    };
    saveState(state);
    renderChatList();
    renderActiveChat();
    inp.focus();
  }

  // Enter to send, Shift+Enter for newline
  inp.addEventListener("keydown", function(e){
    if(e.key === "Enter" && !e.shiftKey){
      e.preventDefault();
      onSend();
    }
  });
  sendBtn.addEventListener("click", onSend);
  newChatBtn.addEventListener("click", createNewChat);

  // initial render
  renderChatList();
  renderActiveChat();
  inp.focus();
  setStatus("Ready");
})();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def ui_home():
    return HTML

@router.get("/health", response_class=PlainTextResponse)
def ui_health():
    return "ok"
