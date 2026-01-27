import sys
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# 1. Mock libraries BEFORE import
mock_ctk = MagicMock()
mock_tk = MagicMock()
mock_dnd = MagicMock()

# Define standard classes to avoid metaclass conflicts
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def resizable(self, *args): pass
    def configure(self, *args, **kwargs): pass
    def mainloop(self): pass
    def after(self, *args): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass

class MockDnDWrapper:
    def drop_target_register(self, *args): pass
    def dnd_bind(self, *args): pass

class MockTkinterDnD:
    DnDWrapper = MockDnDWrapper
    def _require(self, *args): return "version"

mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.CTkScrollableFrame = MagicMock
mock_ctk.CTkComboBox = MagicMock
mock_ctk.CTkRadioButton = MagicMock
mock_ctk.CTkCheckBox = MagicMock
mock_ctk.StringVar = MagicMock

mock_dnd.TkinterDnD = MockTkinterDnD
mock_dnd.DND_FILES = 'DND_Files'

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinterdnd2'] = mock_dnd

# Mock utils and theme
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# 2. Import module
sys.path.append('Retrogaming-Toolkit-AIO')
import VideoConvert

class TestVideoConvertLeak(unittest.TestCase):
    def setUp(self):
        # Create a dummy file to convert
        self.test_file = "test_video.mp4"
        with open(self.test_file, 'w') as f:
            f.write("dummy content")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch('VideoConvert.convert_video')
    @patch('tempfile.NamedTemporaryFile')
    @patch('VideoConvert.check_and_download_ffmpeg')
    def test_leak_on_failure(self, mock_check_ffmpeg, mock_named_temp, mock_convert):
        # Setup mocks
        mock_convert.return_value = False # Simulate failure
        mock_check_ffmpeg.return_value = "/usr/bin/ffmpeg"

        # Mock temp file creation
        temp_file_path = "leaked_temp_file.tmp"
        with open(temp_file_path, 'w') as f:
            f.write("I should be deleted")

        mock_temp_obj = MagicMock()
        mock_temp_obj.name = temp_file_path
        mock_named_temp.return_value = mock_temp_obj

        # Mock app instance
        app = MagicMock()
        app.file_list.get_files.return_value = [self.test_file]

        # Mock inputs
        app.entry_start.get.return_value = "00:00:00"
        app.entry_end.get.return_value = "00:00:10"
        app.entry_v_bitrate.get.return_value = "1000k"
        app.entry_a_bitrate.get.return_value = "128k"
        app.entry_fps.get.return_value = "30"
        app.entry_res.get.return_value = "1920x1080"
        app.combo_format.get.return_value = "Source"

        # Set option to "replace"
        app.out_opt.get.return_value = "replace"
        app.cap_no_rot.get.return_value = False
        app.cap_rot.get.return_value = False

        # Run logic
        VideoConvert.VideoConvertApp.start_conversion(app)

        # Assertions
        mock_convert.assert_called()

        exists = os.path.exists(temp_file_path)

        # Cleanup if exists (to avoid pollution if we run multiple times)
        if exists:
            os.remove(temp_file_path)

        self.assertFalse(exists, "Temp file still exists! Memory leak detected.")

if __name__ == '__main__':
    unittest.main()
