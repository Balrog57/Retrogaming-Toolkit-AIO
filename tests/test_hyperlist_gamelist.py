import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
import sys

# Mock customtkinter and theme before importing the module
sys.modules['customtkinter'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# Add path to find the module.
# Assuming tests are run from repo root or tests/ folder.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also need to add Retrogaming-Toolkit-AIO to path if it's not a package
toolkit_dir = os.path.join(project_root, 'Retrogaming-Toolkit-AIO')
if toolkit_dir not in sys.path:
    sys.path.insert(0, toolkit_dir)

try:
    import HyperlistGamelist
except ImportError:
    # If run from root without setup, might fail.
    pass

class TestHyperlistGamelist(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_output")
        os.makedirs(self.test_dir, exist_ok=True)
        self.src_xml = os.path.join(self.test_dir, "hyperlist.xml")
        with open(self.src_xml, "w", encoding="utf-8") as f:
            f.write("""<?xml version="1.0"?>
<menu>
    <game name="Test Game 1">
        <description>Test Game 1</description>
        <manufacturer>Test Dev</manufacturer>
        <year>2000</year>
        <genre>Action</genre>
        <story>A great story about testing.</story>
    </game>
    <game name="Test Game 2">
        <story>Another story.</story>
    </game>
</menu>""")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_convert(self):
        out_dir = self.test_dir
        ext = ".zip"

        # We need to patch the object that HyperlistGamelist imported
        # Check if HyperlistGamelist was imported successfully
        if 'HyperlistGamelist' not in sys.modules:
            self.fail("Could not import HyperlistGamelist")

        with patch.object(HyperlistGamelist.messagebox, 'showinfo') as mock_info, \
             patch.object(HyperlistGamelist.messagebox, 'showerror') as mock_error:

             HyperlistGamelist.convert(self.src_xml, ext, out_dir)

             if mock_error.called:
                 print(f"ERROR CALLED: {mock_error.call_args}")

             mock_info.assert_called()

        expected_output = os.path.join(out_dir, "gamelist_hyperlist.xml")
        self.assertTrue(os.path.exists(expected_output))

        with open(expected_output, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("<game>", content)
            self.assertIn("<name>Test Game 1</name>", content)
            self.assertIn("<desc>A great story about testing.</desc>", content)
            self.assertIn("<developer>Test Dev</developer>", content)
            self.assertIn("<releasedate>20000101</releasedate>", content)
            self.assertIn("<path>./Test Game 1.zip</path>", content)

    def test_xxe_resilience(self):
        # Create XXE payload
        secret_file = os.path.join(self.test_dir, "secret.txt")
        with open(secret_file, "w") as f:
            f.write("SECRET_DATA")

        xxe_xml = os.path.join(self.test_dir, "xxe.xml")
        with open(xxe_xml, "w") as f:
            f.write(f"""<!DOCTYPE foo [
<!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "file://{os.path.abspath(secret_file)}" >]>
<menu>
    <game name="XXE Game">
        <description>&xxe;</description>
    </game>
</menu>""")

        out_dir = self.test_dir
        ext = ".zip"

        # Run conversion
        with patch.object(HyperlistGamelist.messagebox, 'showinfo') as mock_info, \
             patch.object(HyperlistGamelist.messagebox, 'showerror') as mock_error:

             HyperlistGamelist.convert(xxe_xml, ext, out_dir)

             # With secure parser, it might not error, but just not expand.
             # Or it might error if 'resolve_entities=False' causes it to complain about undefined entity?
             # No, lxml with recover=True usually just ignores it or keeps it as entity ref.
             pass

        expected_output = os.path.join(out_dir, "gamelist_xxe.xml")

        # If conversion succeeded, check if secret was leaked
        if os.path.exists(expected_output):
            with open(expected_output, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertNotIn("SECRET_DATA", content)

if __name__ == '__main__':
    unittest.main()
