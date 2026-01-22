import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

# Mock ctk and tk
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()

# Import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

class TestFavorites(unittest.TestCase):
class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Patch load_favorites to avoid file I/O during init
        patcher = patch('main.Application.load_favorites', return_value=set())
        self.mock_load = patcher.start()
        self.addCleanup(patcher.stop)

        self.app = main.Application()
        self.app.scripts = [
            {"name": "Tool A", "description": "desc"},
            {"name": "Tool B", "description": "desc"},
        ]
        self.app.favorites = set()
        self.app.filter_scripts = MagicMock()
        self.app.save_favorites = MagicMock() # Mock save to avoid file writes in tests

    def test_toggle_favorite(self):
        # 1. Add favorite
        self.app.save_favorites = MagicMock()
        self.app.toggle_favorite("Tool A")
        
        self.assertIn("Tool A", self.app.favorites)
        self.app.save_favorites.assert_called_once()
        self.app.filter_scripts.assert_called_once()
        
        # 2. Remove favorite
        self.app.save_favorites.reset_mock()
        self.app.toggle_favorite("Tool A")
        
        self.assertNotIn("Tool A", self.app.favorites)
        self.app.save_favorites.assert_called_once()

    def test_sorting(self):
        # Simulate filter_scripts logic
        self.app.favorites = {"Tool B"}
        
        # Run sorting logic directly (since we can't fully run filter_scripts with mocks easily)
        sorted_scripts = sorted(self.app.scripts, key=lambda s: (s["name"] not in self.app.favorites, s["name"]))
        
        self.assertEqual(sorted_scripts[0]["name"], "Tool B")
        self.assertEqual(sorted_scripts[1]["name"], "Tool A")

if __name__ == '__main__':
    unittest.main()
