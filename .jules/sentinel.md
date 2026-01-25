## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.

## 2025-02-19 - Concurrent File Handling Race Condition
**Vulnerability:** Race Condition and Data Integrity risk in `CBZKiller.py` where a hardcoded temporary directory path (`temp_ext_cbr`) was shared across concurrent worker threads.
**Learning:** Using `ThreadPoolExecutor` with a shared filesystem resource (hardcoded path) leads to collisions (TOCTOU), causing data corruption (archives containing wrong files) or crashes.
**Prevention:** Always use `tempfile.TemporaryDirectory` (Context Manager) for temporary file operations. It creates a unique, secure, and auto-cleaned directory for each thread/process, ensuring isolation.
