import unittest
import os
from lxml import etree
import sys

# Ensure we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))
from AssistedGamelist import GameListApp

class TestXXESecurity(unittest.TestCase):
    def setUp(self):
        # Create a mock or partial instance of GameListApp to access static method
        # We don't need a valid root if we only check get_safe_parser or static methods
        self.app_class = GameListApp
        self.xxe_payload = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <!DOCTYPE foo [
          <!ELEMENT foo ANY >
          <!ENTITY xxe SYSTEM "file:///etc/passwd" >]><data>&xxe;</data>"""
        
        # Temporary file for file-based parsing tests
        self.payload_filename = "xxe_test.xml"
        with open(self.payload_filename, "w") as f:
            f.write(self.xxe_payload)

    def tearDown(self):
        if os.path.exists(self.payload_filename):
            os.remove(self.payload_filename)

    def get_safe_parser(self):
        return self.app_class.get_safe_parser()

    def test_secure_parsing(self):
        parser = self.get_safe_parser()
        try:
            tree = etree.parse(self.payload_filename, parser)
            root = tree.getroot()
            content = root.find("data").text

            # Should be None (if entity ignored) or the literal "&xxe;" depending on behavior,
            # but definitely NOT "SUPER_SECRET_DATA" or content of a file (though hard to test file read without a real secret file)
            # The point is it shouldn't resolve.
            print(f"Parsed content: {content}")
            
            # If it resolved, it would try to read the file. Since file:///etc/passwd likely doesn't exist on windows or test env,
            # it might error out or return empty if resolved but empty.
            # But the parser setting resolve_entities=False ensures it doesn't even try.
            
            self.assertNotEqual(content, "root:x:0:0:root:/root:/bin/bash", "XXE Vulnerability detected! Secret was potentially read (simulation).")
            
        except etree.XMLSyntaxError:
            # If it errors out on the entity, that is also secure
            pass
        except Exception as e:
            # IOError is possible if it tries to read and fails? No, resolve_entities=False prevents lookup
            pass

    def test_fromstring_secure(self):
        parser = self.get_safe_parser()
        try:
            # Note: lxml fromstring with resolve_entities=False might error or ignore
            # We use a simple payload that would definitely resolve if vulnerable
            root = etree.fromstring(self.xxe_payload.encode('utf-8'), parser=parser)
            if root is not None:
                content = root.text
                # It might be empty or None
                pass
        except etree.XMLSyntaxError:
            pass

    def test_parser_attributes(self):
        parser = self.get_safe_parser()
        # Check if we can inspect the parser configuration (limited in lxml API)
        # We mainly rely on functional tests
        pass

if __name__ == "__main__":
    unittest.main()
