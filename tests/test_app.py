# ----- make project root importable -----
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ---------------------------------------

import types
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

import app  # your FastAPI service (must expose `app = FastAPI(...)`)


def make_resp(url: str, status: int, headers: Dict[str, str]) -> Any:
    """Create a minimal response-like object matching what app.extract_features expects."""
    r = types.SimpleNamespace()
    r.url = url
    r.status_code = status
    # Case-insensitive behavior emulated by normalizing in app.extract_features
    r.headers = headers
    return r


def test_healthz_returns_ok():
    client = TestClient(app.app)
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_check_secure_site_low_risk(monkeypatch):
    """HEAD succeeds with strong security headers and secure cookie flags → lower risk."""
    headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=()",
        "Set-Cookie": "session=abc; Secure; HttpOnly; SameSite=Strict",
    }
    fake_head = lambda url, timeout=5.0, allow_redirects=True: make_resp(url, 200, headers)
    fake_get = lambda url, timeout=5.0, allow_redirects=True: make_resp(url, 200, headers)

    monkeypatch.setattr(app.requests, "head", fake_head)
    monkeypatch.setattr(app.requests, "get", fake_get)

    client = TestClient(app.app)
    res = client.get("/check", params={"url": "https://example.com"})
    assert res.status_code == 200
    data = res.json()

    for k, present in data["headers_present"].items():
        assert present is True, f"Expected {k} to be present"

    assert all(data["cookie_flags_found"].values())
    assert 0.0 <= data["risk_score"] <= 0.6


def test_check_head_falls_back_to_get(monkeypatch):
    """If HEAD fails, app should fall back to GET."""
    def fake_head(url, timeout=5.0, allow_redirects=True):
        raise RuntimeError("HEAD not allowed")

    headers_get = {
        "X-Content-Type-Options": "nosniff",
        "Set-Cookie": "id=1; HttpOnly",
    }
    fake_get = lambda url, timeout=5.0, allow_redirects=True: make_resp(url, 200, headers_get)

    monkeypatch.setattr(app.requests, "head", fake_head)
    monkeypatch.setattr(app.requests, "get", fake_get)

    client = TestClient(app.app)
    res = client.get("/check", params={"url": "example.com"})  # scheme-less; app will normalize
    assert res.status_code == 200
    data = res.json()

    assert data["headers_present"]["x-content-type-options"] is True
    assert data["headers_present"]["content-security-policy"] is False


def test_check_rejects_bad_url():
    client = TestClient(app.app)
    res = client.get("/check", params={"url": "ftp://example.com"})
    assert res.status_code == 400
    assert "valid http(s) URL" in res.json()["detail"]