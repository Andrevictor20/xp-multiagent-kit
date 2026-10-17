# Platform-Native First Policy (Zero Unnecessary Dependencies)

Before adding any JS/CSS/Python library, prefer native platform capabilities:
- **HTML/DOM:** `<dialog>`, `<details>/<summary>`, `<datalist>`, Popover API, native form validation.
- **CSS:** CSS Grid/Subgrid, Container Queries (`@container`), `:has()`, CSS Nesting, View Transitions, `clamp()`, Scroll-driven animations.
- **Web/JS APIs:** `fetch`, `AbortController`, `structuredClone`, `Intl.*`, `crypto.randomUUID()`, `IntersectionObserver`, `URLSearchParams`.
- **Python Stdlib:** `pathlib`, `dataclasses`, `unittest`, `sqlite3`, `urllib.request`, `concurrent.futures`, `functools.lru_cache`.
