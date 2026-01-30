import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Adjust path to import modules from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Define a proper Mock Class for CTk
class MockCTk:
    def __init__(self, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, *args): pass
    def configure(self, **kwargs): pass
    def pack(self, **kwargs): pass

    # Add other methods if needed by CBZKiller init
    # It calls ctk.CTkLabel(self, ...) which expects self to be widget-like
    # But ctk.CTkLabel is mocked below, so it receives this instance.

# Mock dependencies
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.set_appearance_mode = MagicMock()
sys.modules['customtkinter'] = mock_ctk

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['fitz'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Mock utils globally
utils_mock = MagicMock()
sys.modules['utils'] = utils_mock

import CBZKiller

class TestCBZKillerEmptyBug(unittest.TestCase):
    def test_convert_cbr_empty_extraction_should_fail(self):
        """
        If extraction yields no files, convert_cbr should fail (raise Exception).
        """
        # Instantiate without GUI side effects
        converter = CBZKiller.PDFCBRtoCBZConverter()

        # Mock extract_with_7za to return None (success)
        utils_mock.extract_with_7za.return_value = None

        cbr_path = "dummy.cbr"
        cbz_path = "dummy.cbz"

        # Mock tempfile to provide an empty directory
        with patch('tempfile.TemporaryDirectory') as mock_temp_dir:
            # The context manager returns a path string
            mock_temp_dir.return_value.__enter__.return_value = "/tmp/dummy_empty_dir"

            # Mock os.walk to simulate empty directory
            with patch('os.walk') as mock_walk:
                mock_walk.return_value = [("/tmp/dummy_empty_dir", [], [])]

                with patch('zipfile.ZipFile') as mock_zip:
                    mock_zip_instance = MagicMock()
                    mock_zip.return_value.__enter__.return_value = mock_zip_instance

                    # Expect an exception because empty extraction means data loss
                    with self.assertRaises(Exception) as cm:
                        converter.convert_cbr(cbr_path, cbz_path)

                    self.assertIn("Extraction produced no files", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
