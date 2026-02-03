## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.

## 2025-02-21 - Standard Library XML Risks
**Vulnerability:** Python's standard `xml.etree.ElementTree` is vulnerable to Billion Laughs attacks (DoS) and potentially XXE in older environments.
**Learning:** While `xml.etree` is convenient, it lacks robust security controls for untrusted input. `lxml` allows explicit disabling of network and entity resolution.
**Prevention:** Replace `xml.etree.ElementTree` with `lxml.etree` using a configured `XMLParser(resolve_entities=False, no_network=True)` when handling external/untrusted XML.

## 2025-02-23 - Secure Windows Subprocess Launch
**Vulnerability:** Usage of `shell=True` with `start` command to launch detached processes on Windows introduces command injection risks.
**Learning:** `start` is a shell built-in, forcing `shell=True`. To launch a detached console window safely without shell injection, use `creationflags=subprocess.CREATE_NEW_CONSOLE` with direct executable invocation (e.g. `cmd.exe /c path`).
**Prevention:** Avoid `shell=True`. Use `subprocess.Popen([cmd, arg], creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0x10))` for detached windows on Windows.
