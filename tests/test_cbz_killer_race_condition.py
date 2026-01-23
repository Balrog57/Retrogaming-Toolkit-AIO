import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Define a real class for CTk to avoid inheritance issues with MagicMock
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, *args):
        # Simple immediate execution for testing
        if len(args) > 1 and callable(args[1]):
            args[1](*args[2:])

# 1. Mock external dependencies
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkProgressBar = MagicMock()
mock_ctk.BooleanVar = MagicMock

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['fitz'] = MagicMock()

# 2. Add source directory to path
repo_root = os.path.abspath(".")
src_dir = os.path.join(repo_root, "Retrogaming-Toolkit-AIO")
sys.path.insert(0, src_dir)

# 3. Mock utils
sys.modules['utils'] = MagicMock()

import CBZKiller

class TestRaceCondition(unittest.TestCase):
    @patch('CBZKiller.tempfile.TemporaryDirectory')
    @patch('subprocess.run')
    def test_convert_cbr_to_cbz_uses_dynamic_path(self, mock_run, mock_temp_dir):
        # Setup
        converter = CBZKiller.PDFCBRtoCBZConverter()

        # Capture logs
        converter.log = MagicMock()

        mock_utils = sys.modules['utils']
        mock_utils.extract_with_7za = MagicMock()
        mock_utils.DependencyManager = MagicMock()
        mock_utils.DependencyManager.return_value.seven_za_path = "7za.exe"

        # Setup mock context manager for TemporaryDirectory
        mock_context = MagicMock()
        mock_temp_dir.return_value = mock_context
        mock_context.__enter__.return_value = "/tmp/unique_random_dir"

        # Run
        try:
            converter.convert_cbr_to_cbz("fake_input.cbr", "fake_output.cbz")
        except Exception as e:
            pass

        # Verification

        # 1. Verify TemporaryDirectory was used
        if mock_temp_dir.called:
             print("SUCCESS: TemporaryDirectory was used.")
        else:
             print("FAILURE: TemporaryDirectory was NOT used.")
        self.assertTrue(mock_temp_dir.called, "Should use TemporaryDirectory")

        # 2. Verify extract_with_7za used the dynamic path
        if mock_utils.extract_with_7za.called:
             args, _ = mock_utils.extract_with_7za.call_args
             path_arg = args[1]
             print(f"DEBUG: extract_with_7za path: {path_arg}")
             self.assertEqual(path_arg, "/tmp/unique_random_dir", "Should use the dynamic path from TemporaryDirectory")
        else:
             self.fail("extract_with_7za was not called")

if __name__ == '__main__':
    unittest.main()
