import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import subprocess

# 1. Mock external GUI and heavy dependencies BEFORE importing the module under test
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['fitz'] = MagicMock() # PyMuPDF
sys.modules['concurrent.futures'] = MagicMock()
sys.modules['PIL'] = MagicMock()

# Mock ctk.CTk class specifically to allow inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def pack(self, *args): pass
    def configure(self, *args): pass
    def after(self, *args): pass
    def mainloop(self): pass

sys.modules['customtkinter'].CTk = MockCTk
sys.modules['customtkinter'].CTkLabel = MagicMock()
sys.modules['customtkinter'].CTkButton = MagicMock()
sys.modules['customtkinter'].BooleanVar = MagicMock()
sys.modules['customtkinter'].CTkCheckBox = MagicMock()
sys.modules['customtkinter'].CTkTextbox = MagicMock()
sys.modules['customtkinter'].CTkProgressBar = MagicMock()
sys.modules['customtkinter'].set_appearance_mode = MagicMock()

# Mock utils module which is imported inside the function
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

# Add the source directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))

# Now import the module under test
import CBZKiller

class TestCBZRaceCondition(unittest.TestCase):
    @patch('subprocess.run')
    def test_race_condition_fix(self, mock_subprocess):
        # Mock Windows-specific subprocess attributes if on Linux
        if not hasattr(subprocess, 'STARTUPINFO'):
            subprocess.STARTUPINFO = MagicMock()
            subprocess.STARTF_USESHOWWINDOW = 1

        # Setup
        app = CBZKiller.PDFCBRtoCBZConverter()

        # Mock DependencyManager inside utils
        mock_manager = MagicMock()
        mock_manager.seven_za_path = "7za.exe"
        mock_utils.DependencyManager.return_value = mock_manager

        # Mock extract_with_7za
        mock_utils.extract_with_7za = MagicMock()

        # Execute
        # We allow exceptions to propagate. If convert_cbr fails (e.g. NameError), the test will error out.
        app.convert_cbr("input.cbr", "output.cbz")

        # Assert
        # Check if extract_with_7za was called with a dynamic path
        if not mock_utils.extract_with_7za.called:
            self.fail("utils.extract_with_7za was not called.")

        args, _ = mock_utils.extract_with_7za.call_args
        output_dir = args[1]

        print(f"\n[DEBUG] extract_with_7za called with output_dir: {output_dir}")

        self.assertNotEqual(output_dir, "temp_ext_cbr", "Fix Failed: Still using hardcoded temporary directory.")
        # Check if it looks like a temporary directory (e.g., contains 'tmp' or system temp prefix)
        self.assertTrue(os.path.isabs(output_dir) or output_dir.startswith(tempfile.gettempdir()) or "tmp" in output_dir,
                       f"Path '{output_dir}' does not look like a temporary directory.")

if __name__ == '__main__':
    unittest.main()
