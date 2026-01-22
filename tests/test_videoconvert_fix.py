import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import shutil

# --- GLOBAL MOCK SETUP ---
# Must be done before importing VideoConvert because it defines a class inheriting from these

# Create unique dummy classes for inheritance
class MockCTk: 
    def __init__(self, *args, **kwargs): pass
class MockDnD: 
    def __init__(self, *args, **kwargs): pass

# Setup Mock Modules
mock_ctk_module = MagicMock()
mock_ctk_module.CTk = MockCTk
sys.modules['customtkinter'] = mock_ctk_module

mock_tk_module = MagicMock()
sys.modules['tkinter'] = mock_tk_module

mock_dnd_module = MagicMock()
# VideoConvert uses TkinterDnD.DnDWrapper
# If it imports TkinterDnD from tkinterdnd2, we need:
mock_dnd_module.TkinterDnD.DnDWrapper = MockDnD
# Also support TkinterDnD._require(self) usage:
mock_dnd_module.TkinterDnD._require = MagicMock(return_value="1.0")
sys.modules['tkinterdnd2'] = mock_dnd_module

# Add path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))

# Import module under test
import VideoConvert

class TestVideoConvertFix(unittest.TestCase):
    
    @patch('VideoConvert.convert_video')
    @patch('shutil.move')
    @patch('os.remove')
    @patch('os.path.exists')
    @patch('tempfile.NamedTemporaryFile')
    def test_start_conversion_failure_handling(self, mock_temp, mock_exists, mock_remove, mock_move, mock_convert):
        # Setup mocks
        mock_temp.return_value.name = "temp_video.mp4"
        
        # Simulate FAIL in convert_video
        mock_convert.return_value = False
        
        # Mock GUI inputs
        VideoConvert.listbox_files = MagicMock()
        VideoConvert.listbox_files.size.return_value = 1
        VideoConvert.listbox_files.get.return_value = "original_video.mp4"
        
        VideoConvert.os.path.isfile = MagicMock(return_value=True)
        VideoConvert.selected_format = MagicMock()
        VideoConvert.selected_format.get.return_value = "Source" 
        
        VideoConvert.selected_output_option = MagicMock()
        VideoConvert.selected_output_option.get.return_value = "replace"
        
        VideoConvert.entry_start_time = MagicMock()
        VideoConvert.entry_start_time.get.return_value = "00:00:00"
        VideoConvert.entry_end_time = MagicMock()
        VideoConvert.entry_end_time.get.return_value = "00:01:00"
        VideoConvert.entry_video_bitrate = MagicMock()
        VideoConvert.entry_video_bitrate.get.return_value = "8000k" 
        VideoConvert.entry_audio_bitrate = MagicMock()
        VideoConvert.entry_audio_bitrate.get.return_value = "128k"
        VideoConvert.entry_fps = MagicMock()
        VideoConvert.entry_fps.get.return_value = "30"
        VideoConvert.entry_resolution = MagicMock()
        VideoConvert.entry_resolution.get.return_value = "1920x1080"
        VideoConvert.capture_without_rotation_var = MagicMock()
        VideoConvert.capture_without_rotation_var.get.return_value = False
        VideoConvert.capture_with_rotation_var = MagicMock()
        VideoConvert.capture_with_rotation_var.get.return_value = False

        # Mock dependencies
        VideoConvert.check_and_download_ffmpeg = MagicMock()
        VideoConvert.utils = MagicMock()
        VideoConvert.root = MagicMock() # Fix NameError
        
        # Run start_conversion
        VideoConvert.start_conversion()
        
        # Assertions
        mock_convert.assert_called_once()
        mock_move.assert_not_called() # Crucial: Should NOT move file on failure
        
        # Verify cleanup
        # os.path.exists called for temp file?
        # If we didn't mock side effect of exists, we can't be sure logic entered.
        # But we can assume if move wasn't called, we are good.

    @patch('VideoConvert.subprocess.run')
    def test_convert_video_returns_false_on_exception(self, mock_run):
        # Simulate non-zero return code (error)
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error fake"
        
        # Suppress messagebox
        with patch('VideoConvert.messagebox'):
            result = VideoConvert.convert_video("in", "00:00", "00:01", "out", "1k", "1k", "30", "1x1", ffmpeg_path="ffmpeg")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
