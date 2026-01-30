## 2025-05-27 - Cross-Platform Subprocess & GUI Testing
**Learning:** `subprocess.STARTUPINFO` is not available on Linux, causing `AttributeError` in cross-platform CI/test environments for Windows-centric apps. Also, `customtkinter` imports require a display, crashing headless tests.
**Action:** Wrap `STARTUPINFO` usage in `if os.name == 'nt':` and mock GUI modules (`sys.modules['customtkinter'] = MagicMock()`) before importing logic from GUI files for testing.

## 2025-05-27 - Removing Unused Heavy Imports
**Learning:** `main.py` imported `pygame` solely to call `quit()` in cleanup handlers, despite `pygame` never being initialized or used elsewhere. This added unnecessary startup overhead and dependency complexity.
**Action:** Audit imports for actual usage, especially large libraries like `pygame`. If only cleanup calls exist without initialization, they are likely dead code and should be removed.
