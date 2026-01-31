import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Mock libraries BEFORE importing the module under test
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Add project root to path
# Assuming this script is in tests/ and Retrogaming-Toolkit-AIO/ is in root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))

import SystemsExtractor

class TestSystemsExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cust_cfg = os.path.join(self.test_dir, "custom_es_systems.cfg")
        self.out_dir = os.path.join(self.test_dir, "output")

        # Create a dummy custom cfg
        with open(self.cust_cfg, "w", encoding="utf-8") as f:
            f.write('<systemList><system><name>custom_sys</name><fullname>Custom System</fullname></system></systemList>')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('SystemsExtractor.requests.get')
    @patch('SystemsExtractor.messagebox')
    def test_process(self, mock_mb, mock_get):
        # Mock download of official cfg
        mock_response = MagicMock()
        mock_response.content = b'<systemList><system><name>nes</name><fullname>Nintendo Entertainment System</fullname></system></systemList>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Run process
        SystemsExtractor.process(self.cust_cfg, self.out_dir)

        # Verify output
        expected_file = os.path.join(self.out_dir, "es_systems_custom_sys.cfg")
        self.assertTrue(os.path.exists(expected_file))

        with open(expected_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("custom_sys", content)
            self.assertIn("Custom System", content)

if __name__ == '__main__':
    unittest.main()
