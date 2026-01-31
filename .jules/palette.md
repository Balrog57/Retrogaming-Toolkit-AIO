## 2024-05-22 - Keyboard Navigation Deficit
**Learning:** The application lacks standard keyboard shortcuts (e.g., Ctrl+F, Esc) across its custom UI components, forcing mouse usage.
**Action:** Systematically audit and add standard bindings to main interactive loops and list views.

## 2026-01-31 - Scroll Navigation Consistency
**Learning:** Custom canvas implementations often break standard scroll keys (Up/Down/PgUp/PgDn). Users expect these to work globally unless a text input is focused.
**Action:** Always implement a `scroll_canvas` handler with an explicit focus check (`winfo_class() != 'Entry'`) for any scrollable content area.
