## 2025-06-11 - [CORS Configuration]
**Vulnerability:** Overly permissive CORS policy (`allow_origins=["*"]`) combined with `allow_credentials=True`.
**Learning:** This is not only a significant security risk (exposing the API to CSRF and data leakage from malicious origins) but also invalid in modern FastAPI/Starlette versions, which throw an error on startup for this exact combination.
**Prevention:** Always restrict CORS origins to trusted domains (e.g., local development environments) and avoid using `allow_origins=["*"]` with `allow_credentials=True`.
