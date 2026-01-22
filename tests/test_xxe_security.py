import unittest
import os
from lxml import etree

class TestXXESecurity(unittest.TestCase):
    def setUp(self):
        # Create a dummy secret file
        self.secret_filename = "secret_xxe_test.txt"
        with open(self.secret_filename, "w") as f:
            f.write("SUPER_SECRET_DATA")

        # Create malicious XML payload
        self.payload_filename = "payload_xxe.xml"
        self.cwd = os.getcwd().replace("\\", "/")
        self.xxe_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///{self.cwd}/{self.secret_filename}">
]>
<root>
  <data>&xxe;</data>
</root>
"""
        with open(self.payload_filename, "w") as f:
            f.write(self.xxe_payload)

    def tearDown(self):
        if os.path.exists(self.secret_filename):
            os.remove(self.secret_filename)
        if os.path.exists(self.payload_filename):
            os.remove(self.payload_filename)

    def get_safe_parser(self):
        # This matches the implementation I intend to add to AssistedGamelist.py
        # resolve_entities=False prevents external entity resolution
        # no_network=True adds another layer of defense
        return etree.XMLParser(recover=True, encoding='utf-8', resolve_entities=False, no_network=True)

    def test_secure_parsing(self):
        parser = self.get_safe_parser()
        try:
            tree = etree.parse(self.payload_filename, parser)
            root = tree.getroot()
            content = root.find("data").text

            # Should be None (if entity ignored) or the literal "&xxe;" depending on behavior,
            # but definitely NOT "SUPER_SECRET_DATA"
            print(f"Parsed content: {content}")
            self.assertNotEqual(content, "SUPER_SECRET_DATA", "XXE Vulnerability detected! Secret was read.")
        except etree.XMLSyntaxError:
            # If it errors out on the entity, that is also secure
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_fromstring_secure(self):
        parser = self.get_safe_parser()
        try:
            # Note: lxml fromstring with resolve_entities=False might error or ignore
            root = etree.fromstring(self.xxe_payload.encode('utf-8'), parser=parser)
            content = root.find("data").text
            print(f"Parsed content (fromstring): {content}")
            self.assertNotEqual(content, "SUPER_SECRET_DATA", "XXE Vulnerability detected in fromstring!")
        except etree.XMLSyntaxError:
            pass

if __name__ == "__main__":
    unittest.main()
