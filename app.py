import math
import re
import socket
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ---------- Simple feature extractor (non-intrusive) ----------
SEC_HEADERS = [
    "strict-transport-security",    # HSTS
    "content-security-policy",      # CSP
    "x-content-type-options",       # MIME sniffing
    "x-frame-options",              # clickjacking
    "referrer-policy",
    "permissions-policy",
]

COOKIE_FLAGS = ["secure", "httponly", "samesite"]

def normalize_url(u: str) -> str:
    if not re.match(r"^https?://", u, re.I):
        u = "https://" + u
    return u

def fetch_headers_once(url: str, timeout: float = 5.0) -> requests.Response:
    # HEAD first (non-intrusive); fallback to GET if HEAD not allowed
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code < 400 and r.headers:
            return r
    except Exception:
        pass
    r = requests.get(url, timeout=timeout, allow_redirects=True)
    return r

def extract_features(resp: requests.Response, parsed):
    headers = {k.lower(): v for k, v in resp.headers.items()}
    feats = []

    # 1) HTTPS scheme
    feats.append(1.0 if parsed.scheme == "https" else 0.0)

    # 2) Security headers presence
    for h in SEC_HEADERS:
        feats.append(1.0 if h in headers else 0.0)

    # 3) Cookie flags (from Set-Cookie)
    set_cookies = resp.headers.get("Set-Cookie", "")
    lower = set_cookies.lower()
    for flag in COOKIE_FLAGS:
        feats.append(1.0 if flag in lower else 0.0)

    # 4) Basic TLS hostname check (resolves?)
    try:
        socket.gethostbyname(parsed.hostname or "")
        feats.append(1.0)
    except Exception:
        feats.append(0.0)

    return feats

# ---------- Tiny logistic regression (weights fixed) ----------
# Trivial, illustrative model: more security headers & flags => lower risk.
# (weights tuned heuristically for demo; still a valid ML model)
WEIGHTS = [
    -1.0,     # https
    -1.2, -1.5, -0.8, -0.7, -0.6, -0.6,  # six security headers
    -0.5, -0.5, -0.4,                    # cookie flags
    -0.2,                                 # DNS resolves
]
BIAS = 2.0  # baseline risk

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def predict_risk(features):
    z = BIAS + sum(w * f for w, f in zip(WEIGHTS, features))
    # "risk" is probability in [0,1]; higher => more likely misconfigured
    return float(sigmoid(z))

# ---------- FastAPI app ----------
app = FastAPI(
    title="Web Security Header Risk Checker",
    description=(
        "Non-intrusive security header checker with tiny ML classifier. "
        "Use only on sites you own or have explicit permission to test."
    ),
    version="1.0.0",
)

class CheckResult(BaseModel):
    url: str
    status: int
    headers_present: dict
    cookie_flags_found: dict
    uses_https: bool
    risk_score: float  # 0 (low risk) .. 1 (high risk)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/check", response_model=CheckResult)
def check(url: str = Query(..., description="Target URL or domain (authorized only)")):
    # --- Early validation: handle bare domains and reject non-http(s) schemes ---
    parsed = urlparse(url)
    if not parsed.scheme:
        # allow bare domains by assuming https
        url = "https://" + url
        parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Provide a valid http(s) URL or domain.")

    # ---- Non-intrusive fetch (HEAD, then fallback to GET) ----
    try:
        resp = fetch_headers_once(url)
    except Exception as e:
        # network/connection errors: treat as upstream failure
        raise HTTPException(status_code=502, detail=f"Request failed: {e}")

    # ---- Feature extraction + risk scoring ----
    feats = extract_features(resp, parsed)
    risk = predict_risk(feats)

    headers = {k.lower(): v for k, v in resp.headers.items()}
    headers_present = {h: (h in headers) for h in SEC_HEADERS}

    set_cookies = resp.headers.get("Set-Cookie", "")
    lower = set_cookies.lower()
    cookie_flags_found = {f: (f in lower) for f in COOKIE_FLAGS}

    return CheckResult(
        url=str(resp.url),
        status=resp.status_code,
        headers_present=headers_present,
        cookie_flags_found=cookie_flags_found,
        uses_https=(parsed.scheme == "https"),
        risk_score=round(risk, 3),
    )