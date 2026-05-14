// Chatbot module
const Chatbot = (() => {
  let history = [];

  function addMessage(role, text) {
    history.push({ role, content: text });
    const msgs = document.getElementById("chat-messages");
    const div = document.createElement("div");
    div.className = `msg ${role}`;
    const initial = role === "user" ? (DentAI.getUser()?.full_name || "U")[0].toUpperCase() : "🦷";
    div.innerHTML = `
      <div class="msg-avatar">${initial}</div>
      <div class="msg-bubble">${escapeHtml(text).replace(/\n/g, "<br>")}</div>
    `;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function sendMessage(message) {
    if (!message.trim()) return;
    addMessage("user", message);
    const inputEl = document.getElementById("chat-input");
    if (inputEl) inputEl.value = "";

    const typing = document.createElement("div");
    typing.className = "msg assistant";
    typing.id = "typing-indicator";
    typing.innerHTML = `<div class="msg-avatar">🦷</div><div class="msg-bubble"><span class="spinner"></span></div>`;
    document.getElementById("chat-messages").appendChild(typing);

    try {
      const data = await DentAI.apiFetch("/api/chat/message", {
        method: "POST",
        body: JSON.stringify({ message, history: history.slice(-10) }),
      });
      document.getElementById("typing-indicator")?.remove();
      addMessage("assistant", data.response);
    } catch (e) {
      document.getElementById("typing-indicator")?.remove();
      addMessage("assistant", "Sorry, I encountered an error. Please try again.");
    }
  }

  function init() {
    const btn = document.getElementById("send-btn");
    const input = document.getElementById("chat-input");
    if (btn) btn.addEventListener("click", () => sendMessage(input.value));
    if (input) {
      input.addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendMessage(input.value);
        }
      });
    }
    // Welcome message
    setTimeout(() => addMessage("assistant",
      "👋 Hello! I'm DentAI, your oral pathology education assistant. " +
      "Ask me anything about dental caries, periodontitis, oral lesions, or quiz preparation!"), 500);
  }

  return { init, sendMessage };
})();
