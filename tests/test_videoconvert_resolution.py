import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 1. Mock modules that might not exist or are GUI related
sys.modules['requests'] = MagicMock()

# Mock CustomTkinter properly for inheritance
mock_ctk = MagicMock()
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def mainloop(self):
        pass
    def after(self, *args):
        pass
    def geometry(self, *args):
        pass
    def title(self, *args):
        pass
mock_ctk.CTk = MockCTk
mock_ctk.CTkScrollableFrame = MockCTk
mock_ctk.CTkFrame = MockCTk
mock_ctk.CTkLabel = MockCTk
mock_ctk.CTkButton = MockCTk
mock_ctk.CTkEntry = MockCTk
mock_ctk.CTkComboBox = MockCTk
mock_ctk.CTkRadioButton = MockCTk
mock_ctk.CTkCheckBox = MockCTk
mock_ctk.StringVar = MagicMock
sys.modules['customtkinter'] = mock_ctk

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# Mock TkinterDnD properly for inheritance
class MockDnDWrapper:
    def drop_target_register(self, *args):
        pass
    def dnd_bind(self, *args):
        pass

mock_tkinter_dnd_class = MagicMock()
mock_tkinter_dnd_class.DnDWrapper = MockDnDWrapper
mock_tkinter_dnd_class._require = MagicMock()

mock_dnd_module = MagicMock()
mock_dnd_module.TkinterDnD = mock_tkinter_dnd_class
sys.modules['tkinterdnd2'] = mock_dnd_module
# Mocking utils and theme which are local modules but we want to isolate VideoConvert
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# 2. Add the source directory to path
source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Retrogaming-Toolkit-AIO'))
sys.path.insert(0, source_dir)

# 3. Import the module under test
import VideoConvert

class TestVideoConvertResolution(unittest.TestCase):
    @patch('subprocess.run')
    def test_convert_video_resolution_syntax(self, mock_subprocess_run):
        """
        Verifies that the resolution passed to ffmpeg scale filter uses colon syntax (e.g. 1920:1080)
        instead of 'x' syntax (e.g. 1920x1080) which causes errors in some ffmpeg versions.
        """
        # Setup mock return
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        # Define inputs
        input_file = "test_input.mp4"
        output_file = "test_output.mp4"
        start_time = "00:00:00"
        end_time = "00:00:10"
        video_bitrate = "1000k"
        audio_bitrate = "128k"
        fps = "30"
        resolution_input = "1920x1080" # User input format
        ffmpeg_path = "ffmpeg"

        # Execute
        VideoConvert.convert_video(
            input_file, start_time, end_time, output_file,
            video_bitrate, audio_bitrate, fps, resolution_input,
            root=None, ffmpeg_path=ffmpeg_path
        )

        # Verify
        self.assertTrue(mock_subprocess_run.called)
        args, _ = mock_subprocess_run.call_args
        command = args[0]

        # Look for the scale argument
        scale_arg = None
        for item in command:
            if item.startswith("scale="):
                scale_arg = item
                break

        self.assertIsNotNone(scale_arg, "Scale argument not found in ffmpeg command")

        # Assert it uses colons. This will FAIL if the bug is present.
        self.assertEqual(scale_arg, "scale=1920:1080",
                         f"Expected 'scale=1920:1080' but got '{scale_arg}'. The 'x' separator causes FFmpeg errors.")

if __name__ == '__main__':
    unittest.main()
