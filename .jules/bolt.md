## 2023-10-27 - [Instantiating Intl.NumberFormat inside render loops is a performance bottleneck]
**Learning:** Instantiating `Intl.NumberFormat` is a computationally expensive operation in JavaScript. Creating it inside a React component's render loop (especially one that updates up to 10x/sec like the Terminal component) causes significant unnecessary overhead.
**Action:** Extract expensive instantiations (like `Intl.NumberFormat` or `Intl.DateTimeFormat`) outside of the component render function and cache them as module-level constants.
