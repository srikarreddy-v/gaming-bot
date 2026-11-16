const form = document.getElementById("chatForm");
const input = document.getElementById("promptInput");
const chatArea = document.getElementById("chatArea");
const welcome = document.getElementById("welcome");
const sendBtn = document.getElementById("sendBtn");
let history = [];

function addMessage(role, text, isError = false) {
  welcome.style.display = "none";
  const row = document.createElement("div");
  row.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "Y" : "E";
  const bubble = document.createElement("div");
  bubble.className = "bubble" + (isError ? " error" : "");
  bubble.textContent = text;
  row.append(avatar, bubble);
  chatArea.appendChild(row);
  row.scrollIntoView({ behavior: "smooth", block: "end" });
  return bubble;
}

function setPrompt(text) {
  input.value = text;
  input.focus();
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
}
document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => setPrompt(button.dataset.prompt));
});
document.getElementById("newChat").addEventListener("click", () => {
  history = [];
  chatArea.innerHTML = "";
  welcome.style.display = "";
  setPrompt("");
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
});
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendBtn.disabled) return;
  addMessage("user", message);
  history.push({ role: "user", content: message });
  input.value = "";
  input.style.height = "auto";
  sendBtn.disabled = true;
  const typing = addMessage("assistant", "Thinking…");
  typing.classList.add("typing");
  try {
    const response = await fetch("/.netlify/functions/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The AI request failed.");
    typing.textContent = data.reply || "I couldn't generate a response. Please try again.";
    typing.classList.remove("typing");
    history.push({ role: "assistant", content: data.reply || "" });
  } catch (error) {
    typing.textContent = error.message + " Check your Netlify environment variables and API provider setup.";
    typing.classList.remove("typing");
    typing.classList.add("error");
    history.pop();
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});
