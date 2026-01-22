## 2025-05-27 - Cross-Platform Subprocess & GUI Testing
**Learning:** `subprocess.STARTUPINFO` is not available on Linux, causing `AttributeError` in cross-platform CI/test environments for Windows-centric apps. Also, `customtkinter` imports require a display, crashing headless tests.
**Action:** Wrap `STARTUPINFO` usage in `if os.name == 'nt':` and mock GUI modules (`sys.modules['customtkinter'] = MagicMock()`) before importing logic from GUI files for testing.
