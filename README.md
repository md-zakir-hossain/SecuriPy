# SecuriPy
**SecuriPy — FastAPI Web Security Risk Checker**. It is a lightweight FastAPI service that checks public websites for common security headers and cookie flags, then applies a tiny machine learning model to estimate risk. It’s non-intrusive (uses HEAD/GET requests only) and safe to run on sites you own or have permission to test.

## Features
* FastAPI-powered REST service with /check and /healthz endpoints <br>
* Detects key HTTP security headers: HSTS, CSP, X-Frame-Options, etc. <br>
* Inspects cookies for Secure, HttpOnly, SameSite flags <br>
* Tiny logistic regression model built-in for risk scoring <br>
* Unit tests with pytest <br>
* Ready for containerization with Docker <br>

## Quickstart
1. Clone the repo <br>
git clone https://github.com/md-zakir-hossain/SecuriPy.git <br>
cd SecuriPy

2. Install dependencies (Python 3.11+) <br>
python -m venv .venv <br>
source .venv/bin/activate   # on Linux/macOS <br>
.venv\Scripts\activate      # on Windows PowerShell

pip install -r requirements.txt

3. Run the server
uvicorn app:app --reload

Server runs at: http://127.0.0.1:8000

4. Try it

Health check

curl http://127.0.0.1:8000/healthz


Scan a website

curl "http://127.0.0.1:8000/check?url=example.com"


Or open http://127.0.0.1:8000/docs
 for interactive Swagger UI.

🧪 Run Tests
pytest -q

🐳 Docker Support
docker build -t securipy .
docker run -p 8000:8000 securipy

📊 Example Response
{
  "url": "https://example.com/",
  "status": 200,
  "headers_present": {
    "strict-transport-security": true,
    "content-security-policy": false,
    "x-content-type-options": true,
    "x-frame-options": false,
    "referrer-policy": true,
    "permissions-policy": false
  },
  "cookie_flags_found": {
    "secure": true,
    "httponly": true,
    "samesite": false
  },
  "uses_https": true,
  "risk_score": 0.42
}

📌 Notes

For educational/demo use only. Do not scan websites you don’t control.

The ML model is intentionally simple (logistic regression with fixed weights).

Extendable: swap out the feature extractor and model with a production-ready one.

🔗 GitHub Link

👉 https://github.com/md-zakir-hossain/SecuriPy
