import math
import re
from urllib.parse import urlparse

import tldextract

# Use the bundled suffix list so no internet is needed
_extract = tldextract.TLDExtract(suffix_list_urls=())

SUSPICIOUS_WORDS = [
    "login", "signin", "verify", "update", "secure", "account", "bank",
    "confirm", "password", "paypal", "ebay", "amazon", "wallet", "free",
    "bonus", "webscr", "support", "billing",
]
SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "cutt.ly", "rb.gy"}
RISKY_TLDS = {"tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "work", "zip", "country"}
IP_REGEX = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

FEATURE_NAMES = [
    "url_length", "host_length", "path_length", "query_length",
    "num_dots", "num_hyphens", "num_underscores", "num_digits", "num_slashes",
    "num_at", "num_question", "num_equals", "num_ampersand", "num_percent",
    "digit_ratio", "letter_ratio", "has_ip", "num_subdomains", "domain_length",
    "host_hyphens", "host_digits", "host_entropy", "suspicious_words",
    "is_shortener", "risky_tld", "has_port", "double_slash_in_path", "path_depth",
]


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = {c: text.count(c) for c in set(text)}
    n = len(text)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def normalize(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", url):
        url = "http://" + url
    return url


def extract_features(raw_url: str) -> dict:
    url = normalize(raw_url)
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        parsed = urlparse("http://invalid")
        host, port = "", None

    path, query = parsed.path or "", parsed.query or ""
    ext = _extract(host)
    subs = [s for s in ext.subdomain.split(".") if s and s != "www"]
    lowered = url.lower()
    n = max(len(url), 1)
    digits = sum(c.isdigit() for c in url)
    letters = sum(c.isalpha() for c in url)

    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_digits": digits,
        "num_slashes": url.count("/"),
        "num_at": url.count("@"),
        "num_question": url.count("?"),
        "num_equals": url.count("="),
        "num_ampersand": url.count("&"),
        "num_percent": url.count("%"),
        "digit_ratio": digits / n,
        "letter_ratio": letters / n,
        "has_ip": int(bool(IP_REGEX.match(host))),
        "num_subdomains": len(subs),
        "domain_length": len(ext.domain),
        "host_hyphens": host.count("-"),
        "host_digits": sum(c.isdigit() for c in host),
        "host_entropy": _entropy(host),
        "suspicious_words": sum(w in lowered for w in SUSPICIOUS_WORDS),
        "is_shortener": int(host in SHORTENERS),
        "risky_tld": int(ext.suffix.split(".")[-1] in RISKY_TLDS),
        "has_port": int(port is not None),
        "double_slash_in_path": int("//" in path),
        "path_depth": len([p for p in path.split("/") if p]),
    }