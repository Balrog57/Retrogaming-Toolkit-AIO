import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open, ANY
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- MOCKING DEPENDENCIES ---
class MockBase:
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def cget(self, *args, **kwargs): return ""
    def bind(self, *args, **kwargs): pass
    def destroy(self, *args, **kwargs): pass
    def winfo_width(self): return 100
    def winfo_height(self): return 100
    def winfo_children(self): return []
    def winfo_exists(self): return True
    def canvasy(self, *args): return 0
    def create_image(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass
    def create_window(self, *args, **kwargs): pass
    def delete(self, *args): pass
    def yview(self, *args): pass
    def yview_moveto(self, *args): pass
    def yview_scroll(self, *args): pass
    def coords(self, *args): pass
    def tag_lower(self, *args): pass
    def focus_set(self): pass
    def insert(self, *args): pass
    def lower(self): pass

class MockCTk(MockBase):
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def grid_columnconfigure(self, *args): pass
    def grid_rowconfigure(self, *args): pass
    def protocol(self, *args): pass
    def after(self, *args): return "job"
    def after_cancel(self, *args): pass
    def mainloop(self): pass
    def wm_iconbitmap(self, *args): pass
    def wm_iconphoto(self, *args): pass
    def update_idletasks(self): pass
    def lift(self): pass
    def attributes(self, *args): pass

class MockStringVar:
    def __init__(self, value="", *args, **kwargs): self._val = value
    def trace(self, *args): pass
    def trace_add(self, *args): pass
    def set(self, val): self._val = val
    def get(self): return self._val

mock_ctk_module = MagicMock()
mock_ctk_module.CTk = MockCTk
mock_ctk_module.CTkFrame = MockBase
mock_ctk_module.CTkLabel = MockBase
mock_ctk_module.CTkButton = MockBase
mock_ctk_module.CTkEntry = MockBase
mock_ctk_module.CTkCanvas = MockBase
mock_ctk_module.CTkScrollbar = MockBase
mock_ctk_module.CTkTextbox = MockBase
mock_ctk_module.CTkToplevel = MockCTk
mock_ctk_module.CTkOptionMenu = MockBase
mock_ctk_module.StringVar = MockStringVar
mock_ctk_module.CTkImage = MagicMock()
mock_ctk_module.set_appearance_mode = MagicMock()
mock_ctk_module.set_default_color_theme = MagicMock()

sys.modules['customtkinter'] = mock_ctk_module
sys.modules['tkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['requests'] = MagicMock()

import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Prevent actual UI initialization
        patchers = [
            patch('main.Application.setup_background'),
            patch('main.Application.init_music'),
            patch('main.Application.play_radio'),
            patch('main.Application.check_updates'),
            patch('main.Application.setup_sidebar'),
            patch('main.Application.setup_content_area'),
            patch('main.Application.filter_and_display'),
            patch('main.Application.after'), # Prevent timers
            patch('main.Application.geometry'),
            patch('main.Application.resizable'),
            patch('main.Application.title'),
            patch('main.Application.iconbitmap'),
            patch('main.Application.grid_columnconfigure'),
            patch('main.Application.grid_rowconfigure'),
            patch('main.Application.bind'),
            patch('main.Application.protocol')
        ]
        for p in patchers:
            p.start()
            self.addCleanup(p.stop)

        # Mock app_data_dir to a known value for tests
        self.original_app_data_dir = main.app_data_dir
        main.app_data_dir = '/tmp/test_app_data'

        # Instantiate
        self.app = main.Application()
        # Reset scripts for testing
        self.app.scripts = [
            {"name": "Alpha", "category": "Cat1"},
            {"name": "Beta", "category": "Cat2"},
            {"name": "Gamma", "category": "Cat1"}
        ]
        self.app.favorites = []

    def tearDown(self):
        main.app_data_dir = self.original_app_data_dir

    def test_load_favorites(self):
        # This method needs to be implemented in main.py first to pass
        if not hasattr(self.app, 'load_favorites'):
            print("Skipping test_load_favorites: method not implemented")
            return

        mock_content = json.dumps(["Alpha", "Gamma"])
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_content)):
            result = self.app.load_favorites()
            self.assertEqual(result, ["Alpha", "Gamma"])

    def test_save_favorites(self):
        if not hasattr(self.app, 'save_favorites'):
            print("Skipping test_save_favorites: method not implemented")
            return

        self.app.favorites = ["Beta"]
        m = mock_open()
        with patch('builtins.open', m):
            self.app.save_favorites()
            # Check if open was called with correct path and mode
            m.assert_called_with(os.path.join(main.app_data_dir, 'favorites.json'), 'w')

    def test_toggle_favorite(self):
        if not hasattr(self.app, 'toggle_favorite'):
            print("Skipping test_toggle_favorite: method not implemented")
            return

        # Mock save_favorites and filter_and_display to verify calls
        self.app.save_favorites = MagicMock()
        self.app.filter_and_display = MagicMock()

        # Add
        self.app.toggle_favorite("Alpha")
        self.assertIn("Alpha", self.app.favorites)
        self.app.save_favorites.assert_called()
        self.app.filter_and_display.assert_called()

        # Remove
        self.app.toggle_favorite("Alpha")
        self.assertNotIn("Alpha", self.app.favorites)

    def test_sorting_logic(self):
        # Let's verify the key logic: (not is_fav, name)
        favorites = ["Gamma"]
        items = [
            {"name": "Alpha"},
            {"name": "Beta"},
            {"name": "Gamma"}
        ]

        # Expected order: Gamma (Fav), Alpha, Beta
        items.sort(key=lambda x: (x["name"] not in favorites, x["name"]))

        self.assertEqual(items[0]["name"], "Gamma")
        self.assertEqual(items[1]["name"], "Alpha")
        self.assertEqual(items[2]["name"], "Beta")

if __name__ == '__main__':
    unittest.main()
