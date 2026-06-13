## 2025-06-11 - [CORS Configuration]
**Vulnerability:** Overly permissive CORS policy (`allow_origins=["*"]`) combined with `allow_credentials=True`.
**Learning:** This is not only a significant security risk (exposing the API to CSRF and data leakage from malicious origins) but also invalid in modern FastAPI/Starlette versions, which throw an error on startup for this exact combination.
**Prevention:** Always restrict CORS origins to trusted domains (e.g., local development environments) and avoid using `allow_origins=["*"]` with `allow_credentials=True`.

## 2024-06-12 - WebSocket Connection Leak DoS
**Vulnerability:** Fast-broadcasting endpoints did not appropriately disconnect failed WebSocket connections, and `websocket_endpoint` only handled `WebSocketDisconnect` exceptions.
**Learning:** High-frequency data streams (like Order Flow engines) paired with unhandled connection errors can very quickly cause memory exhaustion, as stale connection objects pool in memory indefinitely.
**Prevention:** In async WebSockets: 1. use `try/except` inside broadcast loops to collect and remove dead clients. 2. use a `finally` block in the endpoint generator to ensure cleanup happens irrespective of the disconnection reason.
