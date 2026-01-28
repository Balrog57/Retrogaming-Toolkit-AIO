import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- Mocking Infrastructure ---

class MockCTk:
    def __init__(self, *args, **kwargs):
        self.tk = MagicMock()
    def mainloop(self): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def after(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def winfo_children(self): return []

class MockScrollableFrame:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def winfo_children(self): return []

class MockDnDWrapper:
    def drop_target_register(self, *args): pass
    def dnd_bind(self, *args): pass

class MockTkinterDnD:
    DnDWrapper = MockDnDWrapper
    @staticmethod
    def _require(*args): pass

# Apply Mocks
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkScrollableFrame = MockScrollableFrame
mock_ctk.set_appearance_mode = MagicMock()
sys.modules['customtkinter'] = mock_ctk

mock_dnd_module = MagicMock()
mock_dnd_module.TkinterDnD = MockTkinterDnD
sys.modules['tkinterdnd2'] = mock_dnd_module

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['requests'] = MagicMock()

# --- Import ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import VideoConvert

class TestVideoConvertCrash(unittest.TestCase):
    @patch('VideoConvert.convert_video')
    @patch('VideoConvert.shutil.move')
    @patch('VideoConvert.tempfile.NamedTemporaryFile')
    @patch('VideoConvert.os.remove')
    @patch('VideoConvert.os.path.isfile')
    @patch('VideoConvert.os.path.exists')
    @patch('VideoConvert.check_and_download_ffmpeg')
    @patch('VideoConvert.messagebox')
    def test_crash_and_leak_on_move_failure(self, mock_mb, mock_check, mock_exists, mock_isfile, mock_remove, mock_temp, mock_move, mock_convert):
        # Setup
        app = VideoConvert.VideoConvertApp()

        # Mocks
        app.file_list = MagicMock()
        app.file_list.get_files.return_value = ['/path/to/test_video.mp4']

        app.entry_start = MagicMock(); app.entry_start.get.return_value = "00:00:00"
        app.entry_end = MagicMock(); app.entry_end.get.return_value = "00:01:00"
        app.entry_v_bitrate = MagicMock(); app.entry_v_bitrate.get.return_value = "1000k"
        app.entry_a_bitrate = MagicMock(); app.entry_a_bitrate.get.return_value = "128k"
        app.entry_fps = MagicMock(); app.entry_fps.get.return_value = "30"
        app.entry_res = MagicMock(); app.entry_res.get.return_value = "1920x1080"
        app.combo_format = MagicMock(); app.combo_format.get.return_value = "Source" # .mp4 -> .mp4

        app.out_opt = MagicMock()
        app.out_opt.get.return_value = "replace"

        app.cap_no_rot = MagicMock(); app.cap_no_rot.get.return_value = False
        app.cap_rot = MagicMock(); app.cap_rot.get.return_value = False

        mock_isfile.return_value = True
        mock_exists.return_value = True
        mock_check.return_value = "/bin/ffmpeg"

        # Simulate Conversion Success
        mock_convert.return_value = True

        # Simulate Temp File Creation
        mock_temp_instance = MagicMock()
        mock_temp_instance.name = "/tmp/temp_file_123.mp4"
        mock_temp.return_value = mock_temp_instance

        # Simulate shutil.move FAILURE
        mock_move.side_effect = PermissionError("Access denied")

        # Run and Expect NO Crash (Handled by try/except/finally)
        app.start_conversion()

        # Verify Graceful Handling
        mock_mb.showerror.assert_called()
        args, _ = mock_mb.showerror.call_args
        self.assertIn("Erreur lors du remplacement", args[1])

        # Verify Cleanup: os.remove MUST be called for the temp file
        # Note: os.remove might be called multiple times if logic was different,
        # but here we ensure it was called at least once with the temp filename.
        mock_remove.assert_called_with(mock_temp_instance.name)

if __name__ == '__main__':
    unittest.main()
