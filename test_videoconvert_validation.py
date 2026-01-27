import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Define dummy classes for inheritance
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def after(self, *args, **kwargs): pass
    def mainloop(self): pass

class MockDnDWrapper:
    def drop_target_register(self, *args): pass
    def dnd_bind(self, *args): pass
    @staticmethod
    def _require(self): pass

# Mock libraries before importing VideoConvert
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.CTkComboBox = MagicMock
mock_ctk.CTkScrollableFrame = MagicMock
mock_ctk.CTkCheckBox = MagicMock
mock_ctk.CTkRadioButton = MagicMock
mock_ctk.StringVar = MagicMock
mock_ctk.set_appearance_mode = MagicMock()

sys.modules['customtkinter'] = mock_ctk

mock_dnd = MagicMock()
mock_dnd.TkinterDnD.DnDWrapper = MockDnDWrapper
sys.modules['tkinterdnd2'] = mock_dnd

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Add the directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'Retrogaming-Toolkit-AIO'))

import VideoConvert

class TestVideoConvertValidation(unittest.TestCase):
    def setUp(self):
        self.app = VideoConvert.VideoConvertApp.__new__(VideoConvert.VideoConvertApp)

        self.app.file_list = MagicMock()
        self.app.file_list.get_files.return_value = ["/path/to/video.mp4"]

        self.app.entry_start = MagicMock()
        self.app.entry_start.get.return_value = "00:00:00"

        self.app.entry_end = MagicMock()
        self.app.entry_end.get.return_value = "00:01:00"

        self.app.entry_v_bitrate = MagicMock()
        self.app.entry_a_bitrate = MagicMock()
        self.app.entry_fps = MagicMock()
        self.app.entry_res = MagicMock()

        self.app.combo_format = MagicMock()
        self.app.combo_format.get.return_value = "MP4"

        self.app.out_opt = MagicMock()
        self.app.out_opt.get.return_value = "folder"

        self.app.cap_no_rot = MagicMock()
        self.app.cap_no_rot.get.return_value = False

        self.app.cap_rot = MagicMock()
        self.app.cap_rot.get.return_value = False

    @patch('VideoConvert.convert_video')
    @patch('VideoConvert.check_and_download_ffmpeg')
    @patch('VideoConvert.messagebox')
    @patch('os.path.isfile')
    @patch('os.makedirs')
    def test_start_conversion_blocks_invalid_bitrate(self, mock_makedirs, mock_isfile, mock_mb, mock_check_ffmpeg, mock_convert):
        # SETUP: Mock file existence
        mock_isfile.return_value = True

        # SETUP: Invalid bitrate
        self.app.entry_v_bitrate.get.return_value = "invalid_bitrate"
        self.app.entry_a_bitrate.get.return_value = "128k"
        self.app.entry_fps.get.return_value = "30"
        self.app.entry_res.get.return_value = "1920x1080"

        mock_check_ffmpeg.return_value = "/bin/ffmpeg"

        # ACT
        self.app.start_conversion()

        # ASSERT
        mock_convert.assert_not_called()
        mock_mb.showerror.assert_called_with("Erreur", "Bitrate Vidéo invalide (ex: 8000k ou 8000)")

    @patch('VideoConvert.convert_video')
    @patch('VideoConvert.check_and_download_ffmpeg')
    @patch('VideoConvert.messagebox')
    @patch('os.path.isfile')
    @patch('os.makedirs')
    def test_start_conversion_blocks_invalid_fps(self, mock_makedirs, mock_isfile, mock_mb, mock_check_ffmpeg, mock_convert):
        # SETUP: Mock file existence
        mock_isfile.return_value = True

        # SETUP: Invalid FPS
        self.app.entry_v_bitrate.get.return_value = "8000k"
        self.app.entry_a_bitrate.get.return_value = "128k"
        self.app.entry_fps.get.return_value = "not_a_number"
        self.app.entry_res.get.return_value = "1920x1080"

        mock_check_ffmpeg.return_value = "/bin/ffmpeg"

        # ACT
        self.app.start_conversion()

        # ASSERT
        mock_convert.assert_not_called()
        mock_mb.showerror.assert_called_with("Erreur", "FPS invalide (ex: 30 ou 29.97)")

if __name__ == '__main__':
    unittest.main()
