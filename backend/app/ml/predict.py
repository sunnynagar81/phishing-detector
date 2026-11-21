from pathlib import Path

import joblib
import pandas as pd
import shap
import tldextract

from app.ml.features import extract_features, FEATURE_NAMES

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "url_model.joblib"
_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_name = _bundle["name"]

# TreeExplainer works for random forest / gradient boosting
_explainer = shap.TreeExplainer(_model) if _name != "logistic_regression" else None

_ext = tldextract.TLDExtract(suffix_list_urls=())

TRUSTED_DOMAINS = {
    "google.com", "youtube.com", "github.com", "wikipedia.org", "microsoft.com",
    "apple.com", "amazon.com", "amazon.in", "facebook.com", "instagram.com",
    "linkedin.com", "twitter.com", "x.com", "reddit.com", "stackoverflow.com",
    "openai.com", "anthropic.com", "claude.ai", "netflix.com", "paypal.com",
    "gmail.com", "outlook.com", "live.com", "yahoo.com", "whatsapp.com",
    "flipkart.com", "irctc.co.in", "gov.in", "nic.in", "aktu.ac.in",
}

# Human-readable text for each feature
LABELS = {
    "url_length": "URL length",
    "host_length": "Domain name length",
    "path_length": "Path length",
    "query_length": "Query string length",
    "num_dots": "Number of dots",
    "num_hyphens": "Number of hyphens",
    "num_underscores": "Number of underscores",
    "num_digits": "Number of digits",
    "num_slashes": "Number of slashes",
    "num_at": "Contains '@' symbol",
    "num_question": "Number of '?' characters",
    "num_equals": "Number of '=' characters",
    "num_ampersand": "Number of '&' characters",
    "num_percent": "Encoded characters (%)",
    "digit_ratio": "Share of digits in URL",
    "letter_ratio": "Share of letters in URL",
    "has_ip": "Uses an IP address instead of a domain",
    "num_subdomains": "Number of subdomains",
    "domain_length": "Main domain length",
    "host_hyphens": "Hyphens in the domain",
    "host_digits": "Digits in the domain",
    "host_entropy": "Randomness of the domain name",
    "suspicious_words": "Suspicious words (login, verify, secure...)",
    "is_shortener": "Link shortener",
    "risky_tld": "Risky domain extension",
    "has_port": "Custom port number",
    "double_slash_in_path": "Double slash in path",
    "path_depth": "Path depth",
}


def _is_trusted(url: str) -> bool:
    if "://" not in url:
        url = "http://" + url
    e = _ext(url)
    return f"{e.domain}.{e.suffix}" in TRUSTED_DOMAINS


def _shap_reasons(X: pd.DataFrame, feats: dict, top_n: int = 4) -> list[dict]:
    """Return the features that pushed the score toward 'phishing'."""
    if _explainer is None:
        return []
    sv = _explainer.shap_values(X)
    # Handle the different output shapes across shap versions
    if isinstance(sv, list):
        vals = sv[1][0]
    else:
        vals = sv[0] if sv.ndim == 2 else sv[0]
        if vals.ndim == 2:
            vals = vals[:, 1]
    pairs = sorted(zip(FEATURE_NAMES, vals), key=lambda p: p[1], reverse=True)
    out = []
    for name, v in pairs[:top_n]:
        if v > 0.01:
            out.append({
                "feature": LABELS.get(name, name),
                "value": round(float(feats[name]), 3),
                "impact": round(float(v), 4),
            })
    return out


def predict_url(url: str) -> dict:
    if _is_trusted(url):
        return {
            "url": url,
            "status": "safe",
            "phishing_probability": 0.01,
            "reasons": ["Domain is on the trusted sites list"],
            "explanation": [],
        }

    feats = extract_features(url)
    X = pd.DataFrame([feats])[FEATURE_NAMES]
    prob = float(_model.predict_proba(X)[0][1])

    if prob >= 0.70:
        status = "dangerous"
    elif prob >= 0.40:
        status = "suspicious"
    else:
        status = "safe"

    explanation = _shap_reasons(X, feats) if status != "safe" else []
    reasons = [f"{e['feature']} (value: {e['value']})" for e in explanation]

    return {
        "url": url,
        "status": status,
        "phishing_probability": round(prob, 4),
        "reasons": reasons,
        "explanation": explanation,
    }