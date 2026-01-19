## 2024-05-22 - Non-blocking Startup
**Learning:** Initializing network requests (like update checks) in the main thread of a `customtkinter`/Tkinter app freezes the GUI launch, creating a poor first impression.
**Action:** Always wrap startup network calls in a `threading.Thread` and use `.after()` to update the UI.

## 2024-05-22 - Search Clear Pattern
**Learning:** `customtkinter` Entry widgets lack a built-in "clear" button. A separate button next to the input, toggled via `trace`, is a simple and effective workaround.
**Action:** Use this pattern for all search inputs in the toolkit.
