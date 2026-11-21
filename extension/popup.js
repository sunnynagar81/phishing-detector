const BASE = "http://127.0.0.1:8000/api/scan";

const LABEL = {
  safe: "🟢 Safe",
  suspicious: "🟡 Suspicious",
  dangerous: "🔴 Dangerous",
};

const card = document.getElementById("card");
const statusEl = document.getElementById("status");
const probEl = document.getElementById("prob");
const urlEl = document.getElementById("url");
const reasonsBox = document.getElementById("reasonsBox");
const reasonsEl = document.getElementById("reasons");
const urlPane = document.getElementById("urlPane");
const textPane = document.getElementById("textPane");
const subjectEl = document.getElementById("subject");
const textInput = document.getElementById("textInput");

let mode = "url";

async function post(path, payload) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("API error " + res.status);
  return res.json();
}

function showLoading() {
  card.className = "card loading";
  statusEl.textContent = "Checking...";
  probEl.textContent = "";
  reasonsBox.hidden = true;
}

function showMessage(title, sub) {
  card.className = "card";
  statusEl.textContent = title;
  probEl.textContent = sub || "";
  urlEl.textContent = "";
  reasonsBox.hidden = true;
}

function showError(msg) {
  showMessage("⚠️ Cannot check", msg);
}

function render(r) {
  card.className = "card " + r.status;
  statusEl.textContent = LABEL[r.status] || r.status;
  probEl.textContent = "Phishing probability: " + Math.round(r.phishing_probability * 100) + "%";
  urlEl.textContent = r.url || "";

  reasonsEl.textContent = "";
  (r.reasons || []).forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text; // textContent keeps untrusted text from running as HTML
    reasonsEl.appendChild(li);
  });
  reasonsBox.hidden = !(r.reasons && r.reasons.length);
}

async function checkUrl(url) {
  showLoading();
  try {
    render(await post("/url", { url }));
  } catch (e) {
    showError("Is the backend running on 127.0.0.1:8000?");
  }
}

async function analyzeText() {
  const text = textInput.value.trim();
  if (!text) return;
  showLoading();
  try {
    const payload = mode === "email"
      ? { text, subject: subjectEl.value.trim() }
      : { text };
    render(await post("/" + mode, payload));
  } catch (e) {
    showError("Is the backend running on 127.0.0.1:8000?");
  }
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function initUrl() {
  const tab = await getActiveTab();
  if (!tab || !/^https?:\/\//i.test(tab.url || "")) {
    showError("This page type can't be scanned.");
    return;
  }
  const key = "tab_" + tab.id;
  const cached = (await chrome.storage.local.get(key))[key];
  if (cached && cached.url === tab.url) {
    render(cached);
  } else {
    checkUrl(tab.url);
  }
}

function setMode(next) {
  mode = next;
  document.querySelectorAll(".tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.mode === next));
  urlPane.hidden = next !== "url";
  textPane.hidden = next === "url";
  subjectEl.hidden = next !== "email";
  if (next === "url") {
    initUrl();
  } else {
    showMessage(next === "sms" ? "Paste an SMS" : "Paste an email",
                "Then click Analyze");
  }
}

document.querySelectorAll(".tab").forEach((b) =>
  b.addEventListener("click", () => setMode(b.dataset.mode)));

document.getElementById("rescanBtn").addEventListener("click", async () => {
  const tab = await getActiveTab();
  if (tab && tab.url) checkUrl(tab.url);
});

document.getElementById("checkBtn").addEventListener("click", () => {
  const v = document.getElementById("manualUrl").value.trim();
  if (v) checkUrl(v);
});

document.getElementById("manualUrl").addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("checkBtn").click();
});

document.getElementById("analyzeBtn").addEventListener("click", analyzeText);

initUrl();