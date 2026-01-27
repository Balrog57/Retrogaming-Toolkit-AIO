import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

# Create a dummy CTk class to avoid MagicMock inheritance issues
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args, **kwargs): pass
    def geometry(self, *args, **kwargs): pass
    def resizable(self, *args, **kwargs): pass
    def iconbitmap(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def protocol(self, *args, **kwargs): pass
    def after(self, ms, func=None, *args, **kwargs): return "job_id"
    def after_cancel(self, *args, **kwargs): pass
    def mainloop(self): pass
    def winfo_exists(self): return True
    def winfo_width(self): return 1000
    def configure(self, **kwargs): pass

class MockCTkLabel:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def lower(self): pass
    def configure(self, **kwargs): pass

# Mock modules
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkLabel = MockCTkLabel
# We need to ensure other widgets are also mocks or classes if instantiated
mock_ctk.CTkFrame = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkEntry = MagicMock()
mock_ctk.CTkCanvas = MagicMock()
mock_ctk.CTkScrollbar = MagicMock()
mock_ctk.CTkOptionMenu = MagicMock()
mock_ctk.StringVar = MagicMock

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['module_runner'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Now import main
try:
    import main
except ImportError as e:
    raise ImportError(f"Failed to import main: {e}")

class TestBgOptimization(unittest.TestCase):
    def setUp(self):
        self.ApplicationClass = main.Application

    def test_setup_background_sets_cache(self):
        """Verify that setup_background stores the original image in self.original_bg_image."""

        with patch('main.Image.open') as MockImageOpen, \
             patch('main.CTkImage'), \
             patch('main.ImageTk.PhotoImage'), \
             patch('main.os.path.exists', return_value=True), \
             patch('main.get_path', side_effect=lambda p: p), \
             patch.object(main.Application, 'init_music'), \
             patch.object(main.Application, 'setup_sidebar'), \
             patch.object(main.Application, 'setup_content_area'), \
             patch.object(main.Application, 'check_updates'), \
             patch.object(main.Application, 'filter_and_display'), \
             patch.object(main.Application, 'play_radio'):

            mock_img = MagicMock()
            mock_img.height = 100
            mock_img.width = 200
            mock_img.resize.return_value = MagicMock()
            MockImageOpen.return_value = mock_img

            # Application() calls __init__ -> setup_background
            app = self.ApplicationClass()

            # Verify cache is explicitly set in instance dict
            if 'original_bg_image' not in app.__dict__:
                print("FAIL: app.original_bg_image not found in __dict__ (expected before optimization)")
                self.fail("original_bg_image should be cached in __dict__")
            else:
                self.assertEqual(app.original_bg_image, mock_img)

    def test_update_background_size_uses_cache(self):
        """Verify that update_background_size uses self.original_bg_image if available."""

        # Instantiate with minimal side effects
        with patch.object(main.Application, 'setup_background'), \
             patch.object(main.Application, 'init_music'), \
             patch.object(main.Application, 'setup_sidebar'), \
             patch.object(main.Application, 'setup_content_area'), \
             patch.object(main.Application, 'check_updates'), \
             patch.object(main.Application, 'filter_and_display'), \
             patch.object(main.Application, 'play_radio'):

            app = self.ApplicationClass()
            app.last_height = 500
            app.last_width = 800
            app.canvas = MagicMock()
            app.bg_label = MagicMock() # Mock label to avoid configure error

            # Mock cached image
            mock_cached_img = MagicMock()
            mock_cached_img.height = 100
            mock_cached_img.width = 200

            # Set the cache
            app.original_bg_image = mock_cached_img

            with patch('main.CTkImage') as MockCTkImage, \
                 patch('main.ImageTk.PhotoImage') as MockPhotoImage, \
                 patch('main.Image.open') as MockImageOpen, \
                 patch('main.os.path.exists', return_value=True), \
                 patch('main.get_path', side_effect=lambda p: p):

                app.update_background_size()

                # Verify Image.open was NOT called (Optimization Goal)
                MockImageOpen.assert_not_called()

                # Verify resize was called on cached image
                mock_cached_img.resize.assert_called()

if __name__ == '__main__':
    unittest.main()
