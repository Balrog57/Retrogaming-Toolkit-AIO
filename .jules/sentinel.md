## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.

## 2025-02-21 - Standard Library XML Risks
**Vulnerability:** Python's standard `xml.etree.ElementTree` is vulnerable to Billion Laughs attacks (DoS) and potentially XXE in older environments.
**Learning:** While `xml.etree` is convenient, it lacks robust security controls for untrusted input. `lxml` allows explicit disabling of network and entity resolution.
**Prevention:** Replace `xml.etree.ElementTree` with `lxml.etree` using a configured `XMLParser(resolve_entities=False, no_network=True)` when handling external/untrusted XML.

## 2025-10-26 - Inconsistent XML Parsing Libraries
**Vulnerability:** `SystemsExtractor.py` used `xml.etree.ElementTree` and `minidom` while other modules used `lxml` with security flags. This inconsistency leaves some vectors exposed to DoS/XXE.
**Learning:** Checking one file is not enough; related modules (handling similar data types like gamelists) often copy-paste insecure patterns or legacy code.
**Prevention:** Audit all files importing `xml` or `lxml` to ensure they all use the standardized `get_safe_parser` pattern.
