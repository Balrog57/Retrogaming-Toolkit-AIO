import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies before import
mock_ctk = MagicMock()
sys.modules['customtkinter'] = mock_ctk

# Create a proper Mock class for CTk to handle inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def resizable(self, *args): pass
    def pack(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def after(self, *args): pass

mock_ctk.CTk = MockCTk
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.BooleanVar = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkTextbox = MagicMock()
mock_ctk.CTkProgressBar = MagicMock()

sys.modules['fitz'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Mock subprocess with returncode 0
mock_subprocess = MagicMock()
mock_subprocess.run.return_value.returncode = 0
sys.modules['subprocess'] = mock_subprocess

# Mock utils (important!)
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

# Import the module
sys.path.append('Retrogaming-Toolkit-AIO')
from CBZKiller import PDFCBRtoCBZConverter
import utils # Should be the mock

class TestCBZKillerRaceCondition(unittest.TestCase):
    def test_convert_cbr_uses_unique_temp_dirs(self):
        converter = PDFCBRtoCBZConverter()

        # Patch shutil.rmtree specifically
        with patch('shutil.rmtree') as mock_rmtree, \
             patch('os.path.exists', return_value=False):

            # Call 1
            converter.convert_cbr("test1.cbr", "test1.cbz")

            calls = mock_utils.extract_with_7za.call_args_list
            if not calls:
                self.fail("utils.extract_with_7za was not called")

            arg1 = calls[0][0][1]

            # Call 2
            converter.convert_cbr("test2.cbr", "test2.cbz")

            calls = mock_utils.extract_with_7za.call_args_list
            if len(calls) < 2:
                self.fail("utils.extract_with_7za was not called twice")

            arg2 = calls[1][0][1]

            self.assertNotEqual(arg1, arg2, "Race Condition detected: Both calls used the same temporary directory!")

if __name__ == '__main__':
    unittest.main()
