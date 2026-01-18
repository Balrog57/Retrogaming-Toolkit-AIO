# .Jules/palette.md

## 2024-05-23 - Search Bar Implementation in Tkinter Launcher
**Learning:** In a `customtkinter` (or Tkinter) app with a long, paginated list of items, implementing a client-side search/filter is surprisingly simple and high-impact.
-   Key pattern: Maintain two lists, `self.all_items` (source of truth) and `self.displayed_items` (filtered view).
-   Use `StringVar.trace_add("write", callback)` to trigger real-time filtering as the user types.
-   Always reset pagination (`page = 0`) when the search query changes to avoid "empty page" states.
**Action:** When working on legacy GUI launchers or lists, always check if a simple text filter can be added to reduce navigation friction. It requires minimal code but drastically improves discoverability.
