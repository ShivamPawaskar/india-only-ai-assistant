const form = document.querySelector("#questionForm");
const input = document.querySelector("#questionInput");
const messages = document.querySelector("#messages");
const statusBox = document.querySelector("#status");
const configBar = document.querySelector("#configBar");
const sendButton = document.querySelector("#sendButton");
const suggestionButtons = document.querySelectorAll(".suggestions button");
const charCount = document.querySelector("#charCount");
let typingMessage = null;
let isBusy = false;

function setStatus(text, mode = "ready") {
  statusBox.className = `status ${mode === "ready" ? "" : mode}`.trim();
  statusBox.replaceChildren();

  const dot = document.createElement("span");
  dot.setAttribute("aria-hidden", "true");
  statusBox.append(dot, document.createTextNode(text));
}

function addMessage(role, text, options = {}) {
  const item = document.createElement("article");
  item.className = `message ${role}${options.refused ? " refused" : ""}${options.error ? " error" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "IN";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  item.append(avatar, bubble);
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  if (typingMessage) {
    return;
  }

  const item = document.createElement("article");
  item.className = "message assistant typing";
  item.setAttribute("aria-label", "Assistant is thinking");

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "IN";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  for (let index = 0; index < 3; index += 1) {
    const dot = document.createElement("span");
    dot.className = "typing-dot";
    bubble.appendChild(dot);
  }

  item.append(avatar, bubble);
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
  typingMessage = item;
}

function hideTyping() {
  if (!typingMessage) {
    return;
  }

  typingMessage.remove();
  typingMessage = null;
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 168)}px`;
  charCount.textContent = `${input.value.length}/2000`;
}

function setBusyState(nextBusy) {
  isBusy = nextBusy;
  sendButton.disabled = nextBusy;
  suggestionButtons.forEach((button) => {
    button.disabled = nextBusy;
  });
}

async function loadConfig(options = {}) {
  const shouldUpdateStatus = options.updateStatus !== false;

  try {
    const response = await fetch("/api/config");
    const config = await response.json();
    const keyText = config.has_key ? "API key ready" : "API key missing";
    configBar.textContent = `${config.provider} / ${config.model || "no model selected"} - ${keyText}`;

    if (shouldUpdateStatus) {
      setStatus(config.has_key ? "Ready" : "Setup", config.has_key ? "ready" : "error");
    }
  } catch (error) {
    configBar.textContent = "Could not read server configuration.";

    if (shouldUpdateStatus) {
      setStatus("Error", "error");
    }
  }
}

async function askAssistant(question) {
  if (isBusy) {
    return;
  }

  setStatus("Thinking", "busy");
  setBusyState(true);
  showTyping();

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();

    if (!response.ok) {
      const prefix = data.provider && data.model ? `${data.provider} / ${data.model}: ` : "";
      throw new Error(`${prefix}${data.error || "Request failed."}`);
    }

    hideTyping();
    addMessage("assistant", data.answer, { refused: data.refused });
    setStatus(data.refused ? "Refused" : "Answered", data.refused ? "refused" : "ready");
  } catch (error) {
    hideTyping();
    addMessage("assistant", error.message, { error: true });
    setStatus("Error", "error");
  } finally {
    setBusyState(false);
    input.focus();
    loadConfig({ updateStatus: false });
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (isBusy) {
    return;
  }

  const question = input.value.trim();
  if (!question) {
    return;
  }

  addMessage("user", question);
  input.value = "";
  resizeInput();
  askAssistant(question);
});

input.addEventListener("input", resizeInput);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.question;
    resizeInput();
    input.focus();
    form.requestSubmit();
  });
});

resizeInput();
loadConfig();
