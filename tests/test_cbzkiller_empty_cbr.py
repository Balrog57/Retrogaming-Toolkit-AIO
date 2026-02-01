import sys
import unittest
from unittest.mock import MagicMock
import os
import tempfile
import zipfile

# Create a dummy class for CTk to avoid Mock inheritance issues
class DummyCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, *args): pass
    def pack(self, *args): pass

mock_ctk = MagicMock()
mock_ctk.CTk = DummyCTk

# Setup widget mocks
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkTextbox = MagicMock()

# ProgressBar needs explicit set
mock_prog = MagicMock()
mock_prog.set = MagicMock()
mock_ctk.CTkProgressBar = MagicMock(return_value=mock_prog)

# BooleanVar
mock_bool = MagicMock()
mock_bool.get.return_value = False
mock_ctk.BooleanVar = MagicMock(return_value=mock_bool)

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['fitz'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Mock utils globally
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO'))
if repo_root not in sys.path:
    sys.path.append(repo_root)

# Force reload
if 'CBZKiller' in sys.modules:
    del sys.modules['CBZKiller']

import CBZKiller

class TestCBZKiller(unittest.TestCase):
    def test_convert_cbr_raises_on_empty_result(self):
        # Setup
        converter = CBZKiller.PDFCBRtoCBZConverter()

        # Mock extract_with_7za to do nothing
        mock_utils.extract_with_7za = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cbr_path = os.path.join(tmpdir, "test.cbr")
            cbz_path = os.path.join(tmpdir, "test.cbz")

            # Create a dummy cbr file
            with open(cbr_path, "w") as f:
                f.write("dummy")

            # Run conversion - EXPECT Exception
            with self.assertRaises(Exception) as cm:
                converter.convert_cbr(cbr_path, cbz_path)

            self.assertIn("Conversion produced empty archive", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
