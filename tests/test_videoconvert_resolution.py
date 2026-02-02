import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Define Mock classes to avoid metaclass conflicts
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def after(self, *args, **kwargs): pass
    def mainloop(self): pass

class MockDnDWrapper:
    pass

class MockTkinterDnD:
    DnDWrapper = MockDnDWrapper
    @staticmethod
    def _require(self, *args): return "version"

# Setup mocks
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.CTkComboBox = MagicMock
mock_ctk.CTkCheckBox = MagicMock
mock_ctk.CTkScrollableFrame = MagicMock
mock_ctk.StringVar = MagicMock
mock_ctk.BooleanVar = MagicMock
sys.modules['customtkinter'] = mock_ctk

mock_dnd = MagicMock()
mock_dnd.TkinterDnD = MockTkinterDnD
mock_dnd.DND_FILES = 'DND_FILES'
sys.modules['tkinterdnd2'] = mock_dnd

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['utils'] = MagicMock()

# Add the source directory to path
sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

import VideoConvert

class TestVideoConvertResolution(unittest.TestCase):
    @patch('VideoConvert.subprocess.run')
    def test_convert_video_resolution_syntax(self, mock_run):
        # Setup mock return
        mock_run.return_value.returncode = 0

        # Call the function with the problematic resolution format "WxH"
        VideoConvert.convert_video(
            input_file="input.mp4",
            start_time="00:00:00",
            end_time="00:00:10",
            output_file="output.mp4",
            video_bitrate="1000k",
            audio_bitrate="128k",
            fps="30",
            resolution="1920x1080", # Input with 'x'
            root=None,
            ffmpeg_path="/bin/ffmpeg"
        )

        # Verify the call
        args, _ = mock_run.call_args
        command_list = args[0]

        # Check for incorrect syntax (which causes failure now)
        for arg in command_list:
            if "scale=1920x1080" in arg:
                self.fail(f"Found incorrect scale syntax: {arg}")

        # Check for correct syntax (which we want)
        found_correct = any("scale=1920:1080" in arg for arg in command_list)
        self.assertTrue(found_correct, f"Expected 'scale=1920:1080' not found. Command: {command_list}")

if __name__ == '__main__':
    unittest.main()
