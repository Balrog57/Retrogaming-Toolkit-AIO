import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Mock modules before import
mock_ctk = MagicMock()
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def after(self, *args, **kwargs): return "job_id"
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def mainloop(self): pass
    def destroy(self): pass
    def grid_propagate(self, *args): pass
    def pack_propagate(self, *args): pass
    def update(self): pass
    def winfo_width(self): return 800
    def winfo_height(self): return 600

mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.StringVar = MagicMock
mock_ctk.CTkCanvas = MagicMock
mock_ctk.CTkScrollbar = MagicMock
mock_ctk.CTkOptionMenu = MagicMock
mock_ctk.CTkImage = MagicMock

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinterdnd2'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['urllib.request'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['radio'] = MagicMock()

# utils and theme might be imported by main
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Patch app_data_dir in main to a temp dir
        self.test_dir = os.path.join(os.getcwd(), "test_data_fav")
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        main.app_data_dir = self.test_dir
        self.fav_file = os.path.join(self.test_dir, "favorites.json")
        if os.path.exists(self.fav_file):
            os.remove(self.fav_file)

        # Instantiate App
        # We need to mock methods that do UI setup in __init__ if they fail
        with patch.object(main.Application, 'setup_background'), \
             patch.object(main.Application, 'init_music'), \
             patch.object(main.Application, 'setup_sidebar'), \
             patch.object(main.Application, 'setup_content_area'), \
             patch.object(main.Application, 'check_updates'), \
             patch.object(main.Application, 'filter_and_display'), \
             patch.object(main.Application, 'play_radio'):
            self.app = main.Application()
            # Restore filter_and_display for testing if needed, or mock it separately
            self.app.filter_and_display = MagicMock()
            self.app.favorites = []

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        self.app.favorites = ["ToolA", "ToolB"]
        self.app.save_favorites()

        self.assertTrue(os.path.exists(self.fav_file))

        # Reset and load
        self.app.favorites = []
        loaded = self.app.load_favorites()
        self.assertEqual(loaded, ["ToolA", "ToolB"])

    def test_toggle_favorite(self):
        # Initial state
        self.assertEqual(self.app.favorites, [])

        # Toggle ON
        self.app.toggle_favorite("TestScript")
        self.assertIn("TestScript", self.app.favorites)
        self.app.filter_and_display.assert_called()

        # Verify file
        loaded = self.app.load_favorites()
        self.assertIn("TestScript", loaded)

        # Toggle OFF
        self.app.toggle_favorite("TestScript")
        self.assertNotIn("TestScript", self.app.favorites)

        # Verify file empty
        loaded = self.app.load_favorites()
        self.assertEqual(loaded, [])

if __name__ == '__main__':
    unittest.main()
