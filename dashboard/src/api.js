const BASE = "http://127.0.0.1:8000/api";

async function req(path, options) {
  const res = await fetch(BASE + path, options);
  if (!res.ok) throw new Error("API error " + res.status);
  return res.json();
}

export const getStats = () => req("/stats");

export const getHistory = ({ scan_type, status, limit = 50 } = {}) => {
  const p = new URLSearchParams({ limit });
  if (scan_type) p.set("scan_type", scan_type);
  if (status) p.set("status", status);
  return req("/history?" + p.toString());
};

export const scan = (type, payload) =>
  req("/scan/" + type, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

export const clearHistory = () => req("/history", { method: "DELETE" });