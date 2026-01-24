## 2024-05-22 - Keyboard Navigation Deficit
**Learning:** The application lacks standard keyboard shortcuts (e.g., Ctrl+F, Esc) across its custom UI components, forcing mouse usage.
**Action:** Systematically audit and add standard bindings to main interactive loops and list views.

## 2025-10-24 - Input Focus Guard for Shortcuts
**Learning:** Global keyboard shortcuts (like arrow keys for pagination) must include a guard clause to ignore events when the focus is on an input field (Entry), otherwise they hijack navigation while typing.
**Action:** Always check `event.widget.winfo_class() != 'Entry'` in global binding handlers.
