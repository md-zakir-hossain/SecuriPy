# SecuriPy
SecuriPy — FastAPI Web Security Risk Checker.  SecuriPy is a lightweight FastAPI service that checks public websites for common security headers and cookie flags, then applies a tiny machine learning model to estimate risk. It’s non-intrusive (uses HEAD/GET requests only) and safe to run on sites you own or have permission to test.

Features
✅ FastAPI-powered REST service with /check and /healthz endpoints
✅ Detects key HTTP security headers: HSTS, CSP, X-Frame-Options, etc.
✅ Inspects cookies for Secure, HttpOnly, SameSite flags
✅ Tiny logistic regression model built-in for risk scoring
✅ Unit tests with pytest
✅ Ready for containerization with Docker
