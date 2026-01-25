import unittest
from unittest.mock import MagicMock, patch, mock_open, call
import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

# Define a proper Mock Class for CTk and Widgets
class MockWidget:
    def __init__(self, *args, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def place(self, **kwargs):
        pass
    def grid_propagate(self, flag):
        pass
    def grid_rowconfigure(self, idx, weight=1):
        pass
    def grid_columnconfigure(self, idx, weight=1):
        pass
    def configure(self, **kwargs):
        pass
    def destroy(self):
        pass
    def winfo_children(self):
        return []
    def winfo_width(self):
        return 800
    def cget(self, key):
        return ""
    def bind(self, seq, func):
        pass
    def bind_all(self, seq, func):
        pass
    def focus_set(self):
        pass
    def delete(self, *args):
        pass
    def insert(self, *args):
        pass
    def yview_moveto(self, *args):
        pass
    def create_text(self, *args, **kwargs):
        pass
    def create_image(self, *args, **kwargs):
        pass
    def create_rectangle(self, *args, **kwargs):
        pass
    def create_window(self, *args, **kwargs):
        pass
    def set(self, *args):
        pass
    def lower(self):
        pass

class MockCTk:
    def __init__(self, **kwargs):
        pass
    def title(self, t):
        pass
    def geometry(self, g):
        pass
    def resizable(self, w, h):
        pass
    def grid_columnconfigure(self, idx, weight=1):
        pass
    def grid_rowconfigure(self, idx, weight=1):
        pass
    def iconbitmap(self, path):
        pass
    def after(self, ms, func=None, *args):
        return "job_id"
    def after_cancel(self, job_id):
        pass
    def bind(self, seq, func):
        pass
    def bind_all(self, seq, func):
        pass
    def protocol(self, name, func):
        pass
    def mainloop(self):
        pass
    def winfo_exists(self):
        return True
    def winfo_width(self):
        return 800
    def configure(self, **kwargs):
        pass
    def withdraw(self):
        pass
    def deiconify(self):
        pass

# Mock customtkinter and tkinter BEFORE importing main
sys.modules['tkinter'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()

# Set the class mock
sys.modules['customtkinter'].CTk = MockCTk
sys.modules['customtkinter'].CTkFrame = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkLabel = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkButton = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkEntry = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkCanvas = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkScrollbar = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].CTkTextbox = MagicMock(return_value=MockWidget())

# CTkImage needs to be callable but return something useful?
# CTkImage(pil_image, size)
sys.modules['customtkinter'].CTkImage = MagicMock()
sys.modules['customtkinter'].CTkToplevel = MagicMock(return_value=MockWidget())
sys.modules['customtkinter'].StringVar = MagicMock()

# Import main after mocking
import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Side effect to simulate init_music setting attributes
        def mock_init_music(app_instance):
            app_instance.music_playing = False
            app_instance.music_muted = False
            app_instance.gif_paused = False

        # Prevent load_favorites from actually running during init
        with patch.object(main.Application, 'load_favorites', return_value=[]):
            with patch('theme.apply_theme'):
                with patch('main.Application.init_music', side_effect=mock_init_music, autospec=True):
                    with patch('main.Application.play_radio'):
                         self.app = main.Application()

        # Mock methods that might be called
        self.app.filter_and_display = MagicMock()
        self.app.draw_card = MagicMock()
        self.app.canvas = MagicMock() # Replace the MockWidget with MagicMock for easier assertions
        self.app.scripts = [
            {"name": "Alpha", "description": "desc", "category": "Tout"},
            {"name": "Beta", "description": "desc", "category": "Tout"},
            {"name": "Gamma", "description": "desc", "category": "Tout"}
        ]
        self.app.favorites = []
        self.app.current_category = "Tout"
        self.app.search_query = ""
        self.app.last_width = 1000
        self.app.icon_cache = {}

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='["Alpha"]')
    def test_load_favorites(self, mock_file, mock_exists):
        mock_exists.return_value = True
        favorites = main.Application.load_favorites(self.app)
        self.assertEqual(favorites, ["Alpha"])
        mock_file.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_save_favorites(self, mock_file):
        self.app.favorites = ["Beta"]
        main.Application.save_favorites(self.app)

        # Check all write calls
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('"Beta"', written_content)

    def test_toggle_favorite(self):
        self.app.save_favorites = MagicMock()
        self.app.filter_and_display = MagicMock()
        self.app.favorites = []

        # Add
        main.Application.toggle_favorite(self.app, "Alpha")
        self.assertIn("Alpha", self.app.favorites)
        self.app.save_favorites.assert_called_once()
        self.app.filter_and_display.assert_called_once()

        # Remove
        main.Application.toggle_favorite(self.app, "Alpha")
        self.assertNotIn("Alpha", self.app.favorites)

    def test_sorting_favorites_first(self):
        def mock_init_music(app_instance):
            app_instance.music_playing = False
            app_instance.music_muted = False
            app_instance.gif_paused = False

        with patch.object(main.Application, 'load_favorites', return_value=[]):
             with patch('theme.apply_theme'):
                 with patch('main.Application.init_music', side_effect=mock_init_music, autospec=True):
                     with patch('main.Application.play_radio'):
                        app = main.Application()

        app.canvas = MagicMock()
        app.draw_card = MagicMock()
        app.scripts = [
            {"name": "Zebra", "description": "desc", "category": "Tout"},
            {"name": "Alpha", "description": "desc", "category": "Tout"},
            {"name": "Beta", "description": "desc", "category": "Tout"}
        ]
        app.favorites = ["Beta"]
        app.current_category = "Tout"
        app.search_query = ""
        app.last_width = 1000
        app.icon_cache = {}
        app.scripts_per_page = 100
        app.card_bg_img_cache = {}

        app.canvas.winfo_width.return_value = 1000

        main.Application.filter_and_display(app)

        calls = app.draw_card.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0][0][0]["name"], "Beta")
        self.assertEqual(calls[1][0][0]["name"], "Alpha")
        self.assertEqual(calls[2][0][0]["name"], "Zebra")

if __name__ == '__main__':
    unittest.main()
