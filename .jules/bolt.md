## 2023-10-27 - High Frequency Rendering
**Learning:** The backend broadcasts state updates to the React frontend (`Terminal.tsx`) up to 10 times per second. This causes rapid component re-renders. Operations that are typically cheap, like instantiating `Intl.NumberFormat`, become measurable performance bottlenecks if left inside the render cycle under this load.
**Action:** Always extract static configurations, heavy formatting objects (like `Intl`), and complex static calculations outside the render cycle of WebSocket-driven terminal components.
