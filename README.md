# SecuriPy — FastAPI Web Security Risk Checker
**SecuriPy** is a lightweight FastAPI service that checks public websites for common **security headers and cookie flags**, then applies a tiny **machine-learning (logistic regression)** model to estimate a risk score. It is non-intrusive (single *HEAD/GET* request) and intended for sites you **own or have permission** to test.

## Features
* FastAPI-powered REST service: */check*, */healthz* 
* Detects key headers: HSTS, CSP, X-Frame-Options, etc. 
* Inspects cookies for *Secure*, *HttpOnly*, *SameSite* flags 
* Built-in ML **risk scorer** (logistic regression)
* Unit tests with **pytest**

## Quickstart
**1. Clone the repo**

```bash
git clone https://github.com/md-zakir-hossain/SecuriPy.git
cd SecuriPy
```

**2. Create & activate venv**   

*Windows (PowerShell):*
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

*macOS/Linux:*
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3) Install dependencies**

```bash
pip install -r requirements.txt
```

**4) Run the server**

```bash
uvicorn app:app --reload    
```

Open: http://127.0.0.1:8000   
Docs (Swagger): http://127.0.0.1:8000/docs

## Try it

### Health check
```bash
curl http://127.0.0.1:8000/healthz
```

### Scan a website <br>
```bash
curl "http://127.0.0.1:8000/check?url=example.com" 
```

Or open http://127.0.0.1:8000/docs   
 for interactive Swagger UI.

 ### Example Response

```json
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
```

## Tests

```bash
   pytest -q
```

## Notes

* Use **only** on systems you own or where you have **explicit authorization**.   
* This tool **does not exploit** or brute-force. It performs a standard HTTP request and inspects response headers.
* The ML model is intentionally simple (fixed-weight logistic regression) to clearly demonstrate **model integration**.
* You can extend features or swap the model for a trained *scikit-learn* model (e.g., via *joblib*).

## Repository
https://github.com/md-zakir-hossain/SecuriPy
