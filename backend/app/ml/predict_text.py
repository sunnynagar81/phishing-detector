import re
from pathlib import Path

import joblib

from app.ml.predict import predict_url

MODELS = Path(__file__).resolve().parents[1] / "models"
_sms = joblib.load(MODELS / "sms_model.joblib")
_email = joblib.load(MODELS / "email_model.joblib")

URL_RE = re.compile(r"https?://[^\s<>\"')]+|www\.[^\s<>\"')]+", re.I)
GENERIC_TOKENS = {"http", "https", "www", "com"}


def _status(prob: float) -> str:
    if prob >= 0.70:
        return "dangerous"
    if prob >= 0.40:
        return "suspicious"
    return "safe"


def _predict(pipe, text: str, top_n: int = 5):
    vec = pipe.named_steps["tfidfvectorizer"]
    clf = pipe.named_steps["logisticregression"]
    X = vec.transform([text])
    prob = float(clf.predict_proba(X)[0][1])

    row = X.tocoo()
    names = vec.get_feature_names_out()
    contribs = [
        (names[c], float(v), float(v * clf.coef_[0][c]))
        for c, v in zip(row.col, row.data)
    ]
    # Fix 2: hide generic tokens (the link has its own line in the result)
    contribs = [c for c in contribs if c[0] not in GENERIC_TOKENS]
    contribs = [c for c in contribs if c[2] > 0.01]
    contribs.sort(key=lambda c: c[2], reverse=True)
    explanation = [
        {"feature": w, "value": round(v, 3), "impact": round(i, 4)}
        for w, v, i in contribs[:top_n]
    ]
    return prob, explanation


def _scan_links(text: str, limit: int = 5):
    found = []
    for u in list(dict.fromkeys(URL_RE.findall(text)))[:limit]:
        r = predict_url(u.rstrip(".,;"))
        if r["status"] != "safe":
            found.append({"url": r["url"], "status": r["status"],
                          "probability": r["phishing_probability"]})
    return found


def _build(pipe, text: str, check_links: bool = True):
    prob, explanation = _predict(pipe, text)
    reasons = [f"Suspicious word or phrase: \"{e['feature']}\"" for e in explanation]
    links = _scan_links(text) if check_links else []

    # Fix 1: a message is at least as risky as its riskiest link (slightly discounted)
    if links:
        reasons.insert(0, f"Contains {len(links)} suspicious link(s)")
        worst = max(l["probability"] for l in links)
        prob = max(prob, worst * 0.9)
    status = _status(prob)

    return {
        "status": status,
        "phishing_probability": round(prob, 4),
        "reasons": reasons,
        "explanation": explanation,
        "flagged_urls": links,
    }


def predict_sms(text: str) -> dict:
    return _build(_sms, text)


def predict_email(subject: str, body: str) -> dict:
    return _build(_email, f"{subject} {body}")