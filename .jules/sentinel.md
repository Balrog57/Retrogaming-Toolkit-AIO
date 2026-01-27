## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.

## 2025-02-19 - Thread Safety in Temporary File Handling
**Vulnerability:** Race Condition in `CBZKiller.py` where multiple threads used a hardcoded temporary directory path ("temp_ext_cbr"), leading to data corruption or deletion of files being processed by other threads.
**Learning:** `subprocess` and external tools (like 7zip) don't provide thread isolation for file paths. Hardcoded paths in threaded workers are dangerous.
**Prevention:** Always use `tempfile.TemporaryDirectory()` or `tempfile.NamedTemporaryFile()` within the worker thread scope to ensure unique, isolated paths for each operation.
