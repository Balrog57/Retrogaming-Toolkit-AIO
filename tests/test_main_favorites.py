import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

# Mock customtkinter before importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Define a non-MagicMock base class for CTk
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, text): pass
    def iconbitmap(self, path): pass
    def geometry(self, size): pass
    def after(self, ms, func): pass
    def mainloop(self): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 100
    def update_idletasks(self): pass

sys.modules['customtkinter'].CTk = MockCTk
# Ensure CTkFrame returns a mock that can be packed
MockFrame = MagicMock()
MockFrame.winfo_children.return_value = []
MockFrame.winfo_reqheight.return_value = 100
sys.modules['customtkinter'].CTkFrame = MagicMock(return_value=MockFrame)
sys.modules['customtkinter'].CTkLabel = MagicMock()
sys.modules['customtkinter'].CTkButton = MagicMock()
sys.modules['customtkinter'].CTkEntry = MagicMock()
sys.modules['customtkinter'].StringVar = MagicMock()

# Now import main
import main

class TestMainFavorites(unittest.TestCase):
    def setUp(self):
        # Patch threading to avoid threads starting in __init__
        with patch("threading.Thread"):
             with patch("os.path.exists", return_value=False):
                self.app = main.Application()

        # Disable side effects for tests
        self.app.update_page = MagicMock()

    @patch("builtins.open", new_callable=mock_open, read_data='["Tool A"]')
    @patch("os.path.exists", return_value=True)
    def test_load_favorites(self, mock_exists, mock_file):
        favs = self.app.load_favorites()
        self.assertEqual(favs, {"Tool A"})

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_favorites(self, mock_json_dump, mock_file):
        self.app.favorites = {"Tool B"}
        self.app.save_favorites()

        args, _ = mock_file.call_args
        self.assertIn("favorites.json", args[0])

        args, _ = mock_json_dump.call_args
        self.assertEqual(set(args[0]), {"Tool B"})

    @patch("main.Application.save_favorites")
    @patch("main.Application.filter_scripts")
    def test_toggle_favorite(self, mock_filter, mock_save):
        self.app.favorites = set()

        # Add
        self.app.toggle_favorite("Tool A")
        self.assertIn("Tool A", self.app.favorites)
        mock_save.assert_called()
        mock_filter.assert_called()

        # Remove
        self.app.toggle_favorite("Tool A")
        self.assertNotIn("Tool A", self.app.favorites)

    def test_sorting_integration(self):
        # Test that filter_scripts actually sorts using favorites
        self.app.favorites = {"Tool B"}
        self.app.scripts = [
            {"name": "Tool A", "description": "desc", "icon": "", "readme": ""},
            {"name": "Tool B", "description": "desc", "icon": "", "readme": ""},
            {"name": "Tool C", "description": "desc", "icon": "", "readme": ""},
        ]
        # Mock search_var.get()
        self.app.search_var.get.return_value = ""

        self.app.filter_scripts()

        # Tool B should be first
        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertEqual(names, ["Tool B", "Tool A", "Tool C"])

if __name__ == '__main__':
    unittest.main()
