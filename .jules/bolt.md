## 2025-05-27 - Cross-Platform Subprocess & GUI Testing
**Learning:** `subprocess.STARTUPINFO` is not available on Linux, causing `AttributeError` in cross-platform CI/test environments for Windows-centric apps. Also, `customtkinter` imports require a display, crashing headless tests.
**Action:** Wrap `STARTUPINFO` usage in `if os.name == 'nt':` and mock GUI modules (`sys.modules['customtkinter'] = MagicMock()`) before importing logic from GUI files for testing.

## 2025-05-27 - Tkinter Canvas Widget Leak
**Learning:** `canvas.delete()` removes visual items but DOES NOT destroy widgets embedded via `create_window`. These widgets persist as hidden children, causing memory leaks in dynamic lists.
**Action:** Explicitly track embedded widgets in a list and call `.destroy()` on them before clearing the canvas.
