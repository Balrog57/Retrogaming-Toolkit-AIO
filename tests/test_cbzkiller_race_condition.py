import sys
import unittest
from unittest.mock import MagicMock, patch
import os
import threading
import time
import shutil # Needed for side effects if we want, but we patch it

# Create a proper class for CTk to avoid MagicMock inheritance weirdness
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, ms, func=None, *args):
        if func:
            func(*args)

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkCheckBox = MagicMock()
mock_ctk.CTkProgressBar = MagicMock()
mock_ctk.BooleanVar = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['fitz'] = MagicMock() # PyMuPDF

# We also need to mock utils because CBZKiller imports it inside methods
mock_utils = MagicMock()
sys.modules['utils'] = mock_utils

sys.path.append(os.path.join(os.getcwd(), 'Retrogaming-Toolkit-AIO'))

try:
    from CBZKiller import PDFCBRtoCBZConverter
except ImportError as e:
    print(f"Failed to import CBZKiller: {e}")
    sys.exit(1)

class TestCBZKillerRaceCondition(unittest.TestCase):
    def test_concurrent_extraction_race_condition(self):
        """
        Verifies that running convert_cbr_to_cbz in parallel uses unique extraction directories.
        Fails if they share the same directory (current bug).
        """
        converter = PDFCBRtoCBZConverter()
        converter.log = MagicMock()

        captured_dirs = []
        lock = threading.Lock()

        def mock_extract(archive_path, output_dir, file_to_extract=None, root=None):
            with lock:
                captured_dirs.append(output_dir)
            time.sleep(0.05)

        mock_utils.extract_with_7za.side_effect = mock_extract

        mock_manager = MagicMock()
        mock_manager.seven_za_path = "7za.exe"
        mock_utils.DependencyManager.return_value = mock_manager

        # Patch shutil.rmtree globally so imports inside functions pick it up
        with patch('shutil.rmtree') as mock_rmtree, \
             patch('CBZKiller.subprocess.run') as mock_run, \
             patch('CBZKiller.os.path.exists') as mock_exists, \
             patch('CBZKiller.os.remove') as mock_remove:

             mock_exists.return_value = False # Avoid initial deletion check
             mock_run.return_value.returncode = 0

             threads = []
             files = ["file1.cbr", "file2.cbr"]
             for f in files:
                 t = threading.Thread(target=converter.convert_cbr_to_cbz, args=(f, f.replace(".cbr", ".cbz")))
                 threads.append(t)
                 t.start()

             for t in threads:
                 t.join()

        print(f"Captured dirs: {captured_dirs}")

        self.assertEqual(len(captured_dirs), 2, "Should have attempted extraction twice")
        self.assertNotEqual(captured_dirs[0], captured_dirs[1],
                            f"Race Condition Detected: Both threads used the same extraction directory '{captured_dirs[0]}'")

if __name__ == '__main__':
    unittest.main()
