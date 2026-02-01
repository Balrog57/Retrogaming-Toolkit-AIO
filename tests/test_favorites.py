import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Mock customtkinter properly (Class, not MagicMock instance)
mock_ctk = MagicMock()

class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def iconbitmap(self, *args): pass
    def title(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def after(self, ms, func, *args): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def mainloop(self): pass
    def winfo_width(self): return 800

class MockCTkToplevel:
    def __init__(self, *args, **kwargs):
        pass

mock_ctk.CTk = MockCTk
mock_ctk.CTkToplevel = MockCTkToplevel
mock_ctk.CTkFrame = MagicMock
mock_ctk.CTkLabel = MagicMock
mock_ctk.CTkButton = MagicMock
mock_ctk.CTkEntry = MagicMock
mock_ctk.StringVar = MagicMock
sys.modules['customtkinter'] = mock_ctk

# Mock other dependencies that might cause issues during import
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Add root to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Create a temp dir for app_data_dir
        self.test_dir = tempfile.mkdtemp()
        self.favorites_file = os.path.join(self.test_dir, 'favorites.json')

        # Patch app_data_dir in main module
        self.patcher = patch('main.app_data_dir', self.test_dir)
        self.patcher.start()

        # Instantiate Application with mocked init
        with patch('main.Application.__init__', return_value=None):
            self.app = main.Application()
            # Initialize attributes normally set in __init__
            self.app.favorites = []
            self.app.scripts = [{"name": "Tool1"}, {"name": "Tool2"}]
            # Mock UI methods
            self.app.filter_and_display = MagicMock()
            self.app.draw_card = MagicMock()
            self.app.current_lang = "FR" # Needed for translations if used

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_load_favorites_empty(self):
        favs = self.app.load_favorites()
        self.assertEqual(favs, [])

    def test_load_favorites_existing(self):
        # Create file
        data = ["Tool1"]
        with open(self.favorites_file, 'w') as f:
            json.dump(data, f)

        favs = self.app.load_favorites()
        self.assertEqual(favs, ["Tool1"])

    def test_save_favorites(self):
        self.app.favorites = ["Tool2"]
        self.app.save_favorites()

        with open(self.favorites_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, ["Tool2"])

    def test_toggle_favorite(self):
        self.app.favorites = []
        # Mock save_favorites to avoid disk I/O in this specific test (optional)
        self.app.save_favorites = MagicMock()

        # Toggle On
        self.app.toggle_favorite("Tool1")
        self.assertIn("Tool1", self.app.favorites)
        self.app.save_favorites.assert_called()
        self.app.filter_and_display.assert_called()

        # Toggle Off
        self.app.toggle_favorite("Tool1")
        self.assertNotIn("Tool1", self.app.favorites)

if __name__ == '__main__':
    unittest.main()
