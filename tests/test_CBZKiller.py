import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Adjust path to find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))

# Mock dependencies BEFORE importing CBZKiller
mock_ctk = MagicMock()
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def pack(self, *args, **kwargs): pass
    def after(self, *args, **kwargs): pass
    def mainloop(self): pass
    def configure(self, *args, **kwargs): pass

mock_ctk.CTk = MockCTk
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkCheckBox = MagicMock
mock_ctk.CTkTextbox = MagicMock
# Configure ProgressBar mock to explicitly allow .set()
mock_progressbar_instance = MagicMock()
mock_ctk.CTkProgressBar = MagicMock(return_value=mock_progressbar_instance)
mock_ctk.BooleanVar = MagicMock
mock_ctk.set_appearance_mode = MagicMock

sys.modules['customtkinter'] = mock_ctk
sys.modules['theme'] = MagicMock()
sys.modules['fitz'] = MagicMock()

# Mock utils globally
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

import subprocess
if not hasattr(subprocess, 'STARTUPINFO'):
    subprocess.STARTUPINFO = MagicMock
if not hasattr(subprocess, 'STARTF_USESHOWWINDOW'):
    subprocess.STARTF_USESHOWWINDOW = 1

# Now import the module under test
import CBZKiller

class TestCBZKiller(unittest.TestCase):
    def setUp(self):
        self.app = CBZKiller.PDFCBRtoCBZConverter()

    @patch('CBZKiller.tempfile.TemporaryDirectory')
    @patch('CBZKiller.zipfile.ZipFile')
    @patch('CBZKiller.os.walk')
    @patch('CBZKiller.subprocess.run')
    def test_convert_cbr_uses_secure_temp_dir(self, mock_run, mock_walk, mock_zipfile, mock_tempdir):
        # Setup mocks
        mock_ctx = MagicMock()
        mock_tempdir.return_value.__enter__.return_value = "/tmp/unique_dir"
        mock_walk.return_value = [("/tmp/unique_dir", [], ["page1.jpg"])]

        cbr_path = "comic.cbr"
        cbz_path = "comic.cbz"

        # Call the method
        self.app.convert_cbr(cbr_path, cbz_path)

        # Check if TemporaryDirectory was used (Security/Concurrency Fix)
        mock_tempdir.assert_called_once()

        # Check if extract was called with the temp dir
        mock_utils.extract_with_7za.assert_called_with(cbr_path, "/tmp/unique_dir", root=self.app)

        # Check if ZipFile was used (Replacement for 7za subprocess)
        mock_zipfile.assert_called()

        # Verify NO subprocess calls (we replaced 7za packing with zipfile)
        # Note: mocking subprocess.run ensures we don't actually run anything,
        # but we also want to ensure we removed the old logic.
        mock_run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
