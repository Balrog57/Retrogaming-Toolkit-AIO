import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Adjust path to allow importing from Retrogaming-Toolkit-AIO
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
aio_path = os.path.join(repo_root, 'Retrogaming-Toolkit-AIO')
if aio_path not in sys.path:
    sys.path.insert(0, aio_path)

# Mock modules before import
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['concurrent.futures'] = MagicMock()

# Mock utils specifically because ImageConvert imports it
utils_mock = MagicMock()
utils_mock.get_binary_path.return_value = "dummy_ffmpeg.exe"
sys.modules['utils'] = utils_mock

# Import the target module
import ImageConvert

class TestSparkFeature(unittest.TestCase):
    def test_open_button_exists(self):
        """Test that a button for opening the output folder exists."""
        print("\nScanning for Open Folder button...")

        with patch('ImageConvert.ctk.CTkButton') as mock_button:
            with patch('ImageConvert.ctk.CTkFrame'):
                with patch('ImageConvert.ctk.CTkEntry'):
                    with patch('ImageConvert.ctk.CTkLabel'):
                        with patch('ImageConvert.ctk.CTkCheckBox'): # ImageConvert uses CheckBox
                             ImageConvert.create_gui()

            # Check if a button with text="📂" or similar was created
            found = False
            for call in mock_button.call_args_list:
                text = call.kwargs.get('text', '')
                print(f"Found button: {text}")
                if text == "📂" or "Ouvrir" in text:
                    found = True
                    break

            if not found:
                print("FAIL: Open Folder button not found.")
            else:
                print("SUCCESS: Open Folder button found.")

            self.assertTrue(found, "Open Output Folder button (📂) not found in GUI.")

if __name__ == '__main__':
    unittest.main()
