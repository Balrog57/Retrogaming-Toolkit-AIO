## 2025-02-19 - Safe XML Parsing
**Vulnerability:** XXE (XML External Entity) injection in `lxml` due to implicit or default `resolve_entities=True` configuration (or environment-dependent defaults).
**Learning:** Even if `lxml` defaults change, explicit configuration is required for robust security. `etree.parse()` uses the default parser which may be vulnerable.
**Prevention:** Always use `etree.XMLParser(resolve_entities=False, no_network=True)` and pass this parser to `etree.parse` or `etree.fromstring`.
