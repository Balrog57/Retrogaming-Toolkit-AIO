import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock customtkinter before importing CBZKiller
# We need a class that can be inherited from
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def after(self, delay, callback=None, *args):
        if callback:
            callback(*args)
    def mainloop(self): pass

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.BooleanVar = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkProgressBar = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['fitz'] = MagicMock() # PyMuPDF

# Mock utils
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

# Add repo to sys.path
sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

import CBZKiller

class TestCBZKiller(unittest.TestCase):

    @patch('CBZKiller.subprocess.run')
    @patch('CBZKiller.tempfile.TemporaryDirectory')
    @patch('CBZKiller.shutil.rmtree') # To avoid actual deletion if test runs against old code
    def test_convert_cbr_to_cbz_concurrency_safe(self, mock_rmtree, mock_tempdir, mock_run):
        """
        Verifies that convert_cbr_to_cbz uses a unique temporary directory
        and executes the archiving command within that directory.
        """
        # Setup mocks
        converter = CBZKiller.PDFCBRtoCBZConverter()
        converter.log = MagicMock()

        # Mock DependencyManager
        mock_manager = MagicMock()
        mock_manager.seven_za_path = "/path/to/7za.exe"
        # We access sys.modules['utils'] because CBZKiller imports utils inside the function
        sys.modules['utils'].DependencyManager.return_value = mock_manager

        # Mock TemporaryDirectory context manager
        mock_temp_dir_obj = MagicMock()
        mock_temp_dir_path = "/tmp/unique_random_dir"
        mock_temp_dir_obj.__enter__.return_value = mock_temp_dir_path
        mock_tempdir.return_value = mock_temp_dir_obj

        cbr_path = "/path/to/comic.cbr"
        cbz_path = "/path/to/comic.cbz"

        # Execute
        converter.convert_cbr_to_cbz(cbr_path, cbz_path)

        # Verify TemporaryDirectory was used
        mock_tempdir.assert_called_once()

        # Verify extract called with unique temp dir
        sys.modules['utils'].extract_with_7za.assert_called_once_with(cbr_path, mock_temp_dir_path, root=converter)

        # Verify subprocess run called correctly
        # We expect cwd=mock_temp_dir_path and args to include '*'
        args, kwargs = mock_run.call_args
        cmd = args[0]

        self.assertEqual(kwargs.get('cwd'), mock_temp_dir_path, "Subprocess must run in the temp directory")
        self.assertIn('*', cmd, "Command must use wildcard '*'")

        # Ensure we are using absolute paths for 7za (mocked)
        # Note: In the test setup, we provided an absolute path /path/to/7za.exe, so it should be used.
        # Check that the first argument ends with 7za.exe
        self.assertTrue(str(cmd[0]).endswith('7za.exe'), "Command must use 7za path")

if __name__ == '__main__':
    unittest.main()
