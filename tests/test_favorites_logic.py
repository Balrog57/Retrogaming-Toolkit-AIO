import unittest
import sys
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

# Mock modules before import
sys.modules['customtkinter'] = MagicMock()
# Mock CTk class to support inheritance
class MockCTk:
    def __init__(self, **kwargs): pass
    def mainloop(self): pass
    def title(self, t): pass
    def geometry(self, g): pass
    def resizable(self, w, h): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def protocol(self, *args, **kwargs): pass
    def after(self, *args, **kwargs): return "job_id"
    def after_cancel(self, *args, **kwargs): pass
    def iconbitmap(self, *args, **kwargs): pass

class MockWidget:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def cget(self, key): return ""
    def destroy(self): pass
    def winfo_width(self): return 100
    def winfo_height(self): return 100
    # Methods for Canvas
    def delete(self, *args): pass
    def create_image(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass
    def create_window(self, *args, **kwargs): pass
    def yview_moveto(self, *args): pass
    def canvasy(self, y): return y

sys.modules['customtkinter'].CTk = MockCTk
sys.modules['customtkinter'].CTkFrame = MockWidget
sys.modules['customtkinter'].CTkLabel = MockWidget
sys.modules['customtkinter'].CTkButton = MockWidget
sys.modules['customtkinter'].CTkEntry = MockWidget
sys.modules['customtkinter'].StringVar = MagicMock
sys.modules['customtkinter'].CTkImage = MagicMock
sys.modules['customtkinter'].CTkCanvas = MockWidget
sys.modules['customtkinter'].CTkScrollbar = MockWidget
sys.modules['customtkinter'].CTkOptionMenu = MockWidget
sys.modules['customtkinter'].CTkToplevel = MockWidget
sys.modules['customtkinter'].CTkTextbox = MockWidget

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()

sys.modules['requests'] = MagicMock()
sys.modules['urllib.request'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['pygame'] = MagicMock()

# Mock radio logic
sys.modules['radio'] = MagicMock()

# Mock utils and theme
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Mock multiprocessing
sys.modules['multiprocessing'] = MagicMock()

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import main
import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Setup a temp directory for favorites.json
        self.test_dir = tempfile.TemporaryDirectory()
        self.app_data_patch = patch('main.app_data_dir', self.test_dir.name)
        self.app_data_patch.start()

        # Instantiate App (mocking what's needed)
        with patch('main.Application.setup_background'), \
             patch('main.Application.init_music'), \
             patch('main.Application.setup_sidebar'), \
             patch('main.Application.setup_content_area'), \
             patch('main.Application.check_updates'), \
             patch('main.Application.filter_and_display'), \
             patch('main.Application.play_radio'):

            self.app = main.Application()
            self.app.canvas = MockWidget() # Mock canvas to avoid UI errors in filter_and_display

            # Use 'Favoris' as category for testing
            self.app.category_buttons = {"Favoris": MagicMock()}
            self.app.current_category = "Tout"

    def tearDown(self):
        self.app_data_patch.stop()
        self.test_dir.cleanup()

    def test_methods_exist(self):
        self.assertTrue(hasattr(self.app, 'load_favorites'), "load_favorites missing")
        self.assertTrue(hasattr(self.app, 'save_favorites'), "save_favorites missing")
        self.assertTrue(hasattr(self.app, 'toggle_favorite'), "toggle_favorite missing")

    def test_load_favorites(self):
        if not hasattr(self.app, 'load_favorites'): return

        # Create a dummy favorites file
        fav_file = os.path.join(self.test_dir.name, 'favorites.json')
        initial_data = ["ScriptA", "ScriptB"]
        with open(fav_file, 'w') as f:
            json.dump(initial_data, f)

        loaded = self.app.load_favorites()
        self.assertEqual(loaded, initial_data)

    def test_save_favorites(self):
        if not hasattr(self.app, 'save_favorites'): return

        fav_file = os.path.join(self.test_dir.name, 'favorites.json')
        self.app.favorites = ["ScriptC"]
        self.app.save_favorites()

        self.assertTrue(os.path.exists(fav_file))
        with open(fav_file, 'r') as f:
            saved = json.load(f)
        self.assertEqual(saved, ["ScriptC"])

    def test_toggle_favorite(self):
        if not hasattr(self.app, 'toggle_favorite'): return

        # Ensure favorites list exists
        self.app.favorites = []

        # Add
        self.app.toggle_favorite("TestScript")
        self.assertIn("TestScript", self.app.favorites)

        # Remove
        self.app.toggle_favorite("TestScript")
        self.assertNotIn("TestScript", self.app.favorites)

if __name__ == '__main__':
    unittest.main()
