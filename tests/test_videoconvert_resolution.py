import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Define mock classes to support inheritance
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def after(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def mainloop(self): pass
    def drop_target_register(self, *args): pass
    def dnd_bind(self, *args): pass

class MockDnDWrapper:
    pass

class MockTkinterDnD:
    DnDWrapper = MockDnDWrapper
    @staticmethod
    def _require(self): return "1.0"

# Setup mocks in sys.modules
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkScrollableFrame = MagicMock
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.CTkComboBox = MagicMock
mock_ctk.CTkRadioButton = MagicMock
mock_ctk.CTkCheckBox = MagicMock
mock_ctk.StringVar = MagicMock
mock_ctk.set_appearance_mode = MagicMock()

sys.modules['customtkinter'] = mock_ctk

sys.modules['tkinterdnd2'] = MagicMock()
sys.modules['tkinterdnd2'].TkinterDnD = MockTkinterDnD
sys.modules['tkinterdnd2'].DND_FILES = 'files'

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Add package path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Retrogaming-Toolkit-AIO')))

import VideoConvert

class TestVideoConvertResolution(unittest.TestCase):
    @patch('subprocess.run')
    def test_convert_video_scale_arg(self, mock_run):
        # Setup
        input_file = "input.mp4"
        output_file = "output.mp4"
        start_time = "00:00:00"
        end_time = "00:00:10"
        video_bitrate = "1000k"
        audio_bitrate = "128k"
        fps = "30"
        resolution = "1920x1080" # User input with 'x'

        # Mock successful run
        mock_run.return_value.returncode = 0

        # Call function
        VideoConvert.convert_video(
            input_file, start_time, end_time, output_file,
            video_bitrate, audio_bitrate, fps, resolution,
            root=None, ffmpeg_path="ffmpeg"
        )

        # Verify args
        args, _ = mock_run.call_args
        command = args[0]

        # We expect one of the args to be "scale=1920:1080"
        # The bug currently produces "scale=1920x1080"

        scale_cmd = None
        for arg in command:
            if arg.startswith("scale="):
                scale_cmd = arg
                break

        self.assertIsNotNone(scale_cmd, "Scale argument not found in command")
        self.assertEqual(scale_cmd, "scale=1920:1080", f"Expected scale=1920:1080 but got {scale_cmd}")

if __name__ == '__main__':
    unittest.main()
