## 2025-10-31 - Local Command Injection in Update Launcher
**Vulnerability:** Found `subprocess.Popen` used with `shell=True` and an unsanitized path constructed from `__file__` in `main.py`. This could allow command injection if the application is installed in a path with shell metacharacters.
**Learning:** Even internal scripts or paths derived from `__file__` can be dangerous when used with `shell=True` on Windows, as the path itself becomes part of the command string.
**Prevention:** Avoid `shell=True`. Use `os.startfile` for launching files/scripts on Windows, or pass arguments as a list to `subprocess.Popen` with `shell=False`.
