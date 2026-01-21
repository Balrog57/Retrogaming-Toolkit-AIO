import sys
import unittest
from unittest.mock import MagicMock, patch
import subprocess
import os

# Define TWO MockBase classes to avoid "duplicate base class" error
class MockBase1:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def mainloop(self): pass

class MockBase2:
    @staticmethod
    def _require(self): pass

# Mock modules before importing VideoConvert
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.Listbox'] = MagicMock()
sys.modules['tkinter.Checkbutton'] = MagicMock()
sys.modules['tkinter.BooleanVar'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['utils'] = MagicMock()

# Configure the specific mocks needed for inheritance
sys.modules['customtkinter'].CTk = MockBase1

# Fix tkinterdnd2 structure
mock_tkinterdnd2 = MagicMock()
mock_TkinterDnD = MagicMock()
mock_TkinterDnD.DnDWrapper = MockBase2
mock_tkinterdnd2.TkinterDnD = mock_TkinterDnD
sys.modules['tkinterdnd2'] = mock_tkinterdnd2

# Adjust path to import VideoConvert
sys.path.insert(0, os.path.abspath('Retrogaming-Toolkit-AIO'))
import VideoConvert

class TestVideoConvertBug(unittest.TestCase):
    @patch('VideoConvert.subprocess.run')
    @patch('VideoConvert.shutil.move')
    @patch('VideoConvert.os.remove')
    @patch('VideoConvert.tempfile.NamedTemporaryFile')
    @patch('VideoConvert.messagebox.showerror')
    def test_start_conversion_prevents_overwrite_on_failure(self, mock_showerror, mock_tempfile, mock_remove, mock_move, mock_run):
        # Setup mocks

        # Mock subprocess to fail
        # This simulates ffmpeg returning a non-zero exit code
        mock_run.side_effect = subprocess.CalledProcessError(1, ['ffmpeg'], stderr="Simulated FFmpeg error")

        # Mock global variables in VideoConvert
        VideoConvert.listbox_files = MagicMock()
        VideoConvert.listbox_files.size.return_value = 1
        VideoConvert.listbox_files.get.return_value = "video.mp4"

        VideoConvert.entry_start_time = MagicMock()
        VideoConvert.entry_start_time.get.return_value = "00:00:00"

        VideoConvert.entry_end_time = MagicMock()
        VideoConvert.entry_end_time.get.return_value = "00:01:00"

        VideoConvert.entry_video_bitrate = MagicMock()
        VideoConvert.entry_video_bitrate.get.return_value = "1000k"

        VideoConvert.entry_audio_bitrate = MagicMock()
        VideoConvert.entry_audio_bitrate.get.return_value = "128k"

        VideoConvert.entry_fps = MagicMock()
        VideoConvert.entry_fps.get.return_value = "30"

        VideoConvert.entry_resolution = MagicMock()
        VideoConvert.entry_resolution.get.return_value = "1920x1080"

        VideoConvert.selected_format = MagicMock()
        VideoConvert.selected_format.get.return_value = "Source"

        # Crucial: Select "Replace" mode
        VideoConvert.selected_output_option = MagicMock()
        VideoConvert.selected_output_option.get.return_value = "replace"

        # Mock other vars used in start_conversion
        VideoConvert.capture_without_rotation_var = MagicMock()
        VideoConvert.capture_without_rotation_var.get.return_value = False
        VideoConvert.capture_with_rotation_var = MagicMock()
        VideoConvert.capture_with_rotation_var.get.return_value = False

        VideoConvert.root = MagicMock()

        # Mock tempfile
        mock_temp = MagicMock()
        mock_temp.name = "temp_video.mp4"
        mock_tempfile.return_value = mock_temp

        # Mock os.path.isfile to return True for input file
        with patch('VideoConvert.os.path.isfile', return_value=True):
             with patch('VideoConvert.os.path.exists', return_value=True): # For ffmpeg check
                # Call start_conversion
                VideoConvert.start_conversion()

        # Assertions
        # We expect shutil.move NOT to be called because conversion failed
        mock_move.assert_not_called()

        # Also ensure os.remove(temp_file) WAS called to clean up
        mock_remove.assert_called_with(mock_temp.name)

if __name__ == '__main__':
    unittest.main()
