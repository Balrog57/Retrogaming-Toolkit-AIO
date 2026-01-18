## 2026-01-18 - Batch Processing Optimization
**Learning:** The codebase relies heavily on `os.listdir` loops with synchronous `subprocess.run` calls for batch processing (ImageConvert, VideoConvert, CBZKiller). This creates significant bottlenecks on multi-core systems.
**Action:** Look for `for` loops iterating over files that call `subprocess.run` and refactor them to use `concurrent.futures.ThreadPoolExecutor` for immediate 4x+ gains on standard hardware.
