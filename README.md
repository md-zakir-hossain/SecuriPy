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

3. Run the server <br>

```bash
uvicorn app:app --reload <br>
```
Server runs at: http://127.0.0.1:8000

4. Try it

* Health check <br>
```bash
curl http://127.0.0.1:8000/healthz <br> <br>
```

* Scan a website <br>
```bash
curl "http://127.0.0.1:8000/check?url=example.com" <br>
```

Or open http://127.0.0.1:8000/docs <br>
 for interactive Swagger UI.

## Run Tests

```bash
   pytest -q
```

## Docker Support

```bash
docker build -t securipy . <br>
docker run -p 8000:8000 securipy
```

## Example Response

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

## Notes

* For **educational/demo use only**. Do not scan websites you don’t control. <br>
* The ML model is intentionally simple (logistic regression with fixed weights).
* Extendable: swap out the feature extractor and model with a production-ready one.

## GitHub Link
👉 https://github.com/md-zakir-hossain/SecuriPy
