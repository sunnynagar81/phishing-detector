const API = "http://127.0.0.1:8000/api/scan/url";

const COLORS = { safe: "#2e7d32", suspicious: "#f9a825", dangerous: "#c62828" };
const TEXT = { safe: "OK", suspicious: "?", dangerous: "!" };

async function scanUrl(url) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error("API error " + res.status);
  return res.json();
}

function isLocal(url) {
  try {
    const h = new URL(url).hostname;
    return h === "localhost" || h === "127.0.0.1" || h === "::1" || h.endsWith(".local");
  } catch {
    return false;
  }
}

// Badge calls fail if the tab was closed in the meantime, so swallow that error
function setBadge(tabId, text, color) {
  chrome.action.setBadgeText({ tabId, text }).catch(() => {});
  if (color) chrome.action.setBadgeBackgroundColor({ tabId, color }).catch(() => {});
}

async function scanTab(tabId, url) {
  if (!/^https?:\/\//i.test(url) || isLocal(url)) {
    setBadge(tabId, "");
    return;
  }
  try {
    const result = await scanUrl(url);
    await chrome.storage.local.set({ ["tab_" + tabId]: result });
    setBadge(tabId, TEXT[result.status] || "", COLORS[result.status] || "#777777");
  } catch (err) {
    setBadge(tabId, "ERR", "#777777");
  }
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    scanTab(tabId, tab.url);
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  chrome.storage.local.remove("tab_" + tabId);
});