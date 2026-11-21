import { ShieldAlert, ShieldCheck, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { scan } from "../api";

const VERDICT = {
  safe: { text: "Safe", Icon: ShieldCheck },
  suspicious: { text: "Suspicious", Icon: TriangleAlert },
  dangerous: { text: "Dangerous", Icon: ShieldAlert },
};

const EXAMPLES = {
  url: "http://paypal-secure-login.verify-account.tk/signin/update.php",
  sms: "URGENT: Your bank account is blocked. Verify now at http://secure-bank-login.tk/verify",
  email: "Dear customer, your account has been suspended. Click here to verify your password immediately.",
};

export default function ScanBox({ onDone }) {
  const [type, setType] = useState("url");
  const [text, setText] = useState("");
  const [subject, setSubject] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    if (!text.trim()) return;
    setBusy(true);
    setError("");
    try {
      let payload = { text };
      if (type === "url") payload = { url: text.trim() };
      if (type === "email") payload = { text, subject };
      setResult(await scan(type, payload));
      onDone();
    } catch (e) {
      setError("Could not reach the backend. Is it running on 127.0.0.1:8000?");
    } finally {
      setBusy(false);
    }
  }

  function example() {
    setText(EXAMPLES[type]);
    if (type === "email") setSubject("Account suspended");
  }

  const v = result && VERDICT[result.status];
  const pct = result ? Math.round(result.phishing_probability * 100) : 0;

  return (
    <div>
      <div className="segmented">
        {["url", "sms", "email"].map((t) => (
          <button key={t} className={t === type ? "active" : ""}
                  onClick={() => { setType(t); setResult(null); setText(""); }}>
            {t.toUpperCase()}
          </button>
        ))}
      </div>

      {type === "email" && (
        <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Email subject" />
      )}
      {type === "url" ? (
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="https://example.com/login"
               onKeyDown={(e) => e.key === "Enter" && run()} />
      ) : (
        <textarea rows={5} value={text} onChange={(e) => setText(e.target.value)}
                  placeholder={type === "sms" ? "Paste the SMS..." : "Paste the email body..."} />
      )}

      <button className="primary" onClick={run} disabled={busy}>
        {busy ? "Scanning..." : "Scan now"}
      </button>
      <div style={{ textAlign: "center", marginTop: 8 }}>
        <button className="ghost" onClick={example}>Try an example</button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className={"result " + result.status}>
          <div className="result-head">
            <div className="verdict"><v.Icon size={22} />{v.text}</div>
            <div className="score">{pct}%</div>
          </div>
          <div className="meter"><div style={{ width: pct + "%" }} /></div>
          {result.reasons?.length > 0 && (
            <ul>{result.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
          )}
        </div>
      )}
    </div>
  );
}