import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock customtkinter with a real class to support inheritance properly
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, ms, func=None, *args):
        # We can execute the function immediately for testing
        if func:
            func(*args)
        return "after_id"
    def pack(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
# Mock other widgets as MagicMock, they are just instantiated
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkProgressBar = MagicMock()
mock_ctk.BooleanVar = MagicMock
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

sys.modules["customtkinter"] = mock_ctk
sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()
sys.modules["tkinter.filedialog"] = MagicMock()
sys.modules["tkinter.scrolledtext"] = MagicMock()
sys.modules["fitz"] = MagicMock()

# Mock utils
mock_utils = MagicMock()
sys.modules["utils"] = mock_utils

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Retrogaming-Toolkit-AIO")))

# Now import CBZKiller
import CBZKiller

class TestCBZSecurity(unittest.TestCase):
    @patch("CBZKiller.subprocess.run")
    @patch("CBZKiller.os.path.exists")
    @patch("CBZKiller.shutil.rmtree")
    def test_convert_cbr_to_cbz_secure_temp(self, mock_rmtree, mock_exists, mock_run):
        # Setup
        converter = CBZKiller.PDFCBRtoCBZConverter()
        converter.log = MagicMock() # Capture logs

        # Configure utils mock
        mock_utils.reset_mock()
        mock_utils.DependencyManager.return_value.seven_za_path = "7za.exe"
        mock_utils.extract_with_7za = MagicMock()

        cbr_path = "/path/to/comic.cbr"
        cbz_path = "/path/to/comic.cbz"

        # Execute (should not raise exception)
        converter.convert_cbr_to_cbz(cbr_path, cbz_path)

        # Verification

        # 1. Verify extract_with_7za was called
        self.assertTrue(mock_utils.extract_with_7za.called, "utils.extract_with_7za should be called")

        # 2. Check the temp_dir passed to extract_with_7za
        _, args, _ = mock_utils.extract_with_7za.mock_calls[0]
        temp_dir_arg = args[1]

        # The VULNERABLE code uses "temp_extract"
        self.assertNotEqual(temp_dir_arg, "temp_extract", "Vulnerability detected: Hardcoded 'temp_extract' directory used!")

        # 3. Verify subprocess.run (7za a)
        self.assertTrue(mock_run.called, "subprocess.run should be called for archiving")
        _, run_args, run_kwargs = mock_run.mock_calls[0]

        # If secure: cwd=temp_dir is passed
        cwd = run_kwargs.get("cwd")
        if cwd:
             self.assertEqual(cwd, temp_dir_arg, "subprocess cwd should match the temp dir")
        else:
             # The old code used absolute path in command line like "./temp_extract/*" which is insecure relative path
             pass

        # 4. Verify rmtree was NOT called on "temp_extract" explicitly
        for call in mock_rmtree.mock_calls:
            args = call.args
            if args and args[0] == "temp_extract":
                self.fail("Vulnerability detected: explicitly removing 'temp_extract' implies its usage.")

if __name__ == "__main__":
    unittest.main()
