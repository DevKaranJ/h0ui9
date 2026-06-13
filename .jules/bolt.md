## 2023-10-27 - High Frequency Rendering
**Learning:** The backend broadcasts state updates to the React frontend (`Terminal.tsx`) up to 10 times per second. This causes rapid component re-renders. Operations that are typically cheap, like instantiating `Intl.NumberFormat`, become measurable performance bottlenecks if left inside the render cycle under this load.
**Action:** Always extract static configurations, heavy formatting objects (like `Intl`), and complex static calculations outside the render cycle of WebSocket-driven terminal components.
## 2023-10-27 - [Instantiating Intl.NumberFormat inside render loops is a performance bottleneck]
**Learning:** Instantiating `Intl.NumberFormat` is a computationally expensive operation in JavaScript. Creating it inside a React component's render loop (especially one that updates up to 10x/sec like the Terminal component) causes significant unnecessary overhead.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat` or `Intl.DateTimeFormat`) outside of the component render function and cache them as module-level constants.
