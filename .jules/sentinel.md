## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.

## 2025-02-21 - Standard Library XML Risks
**Vulnerability:** Python's standard `xml.etree.ElementTree` is vulnerable to Billion Laughs attacks (DoS) and potentially XXE in older environments.
**Learning:** While `xml.etree` is convenient, it lacks robust security controls for untrusted input. `lxml` allows explicit disabling of network and entity resolution.
**Prevention:** Replace `xml.etree.ElementTree` with `lxml.etree` using a configured `XMLParser(resolve_entities=False, no_network=True)` when handling external/untrusted XML.
