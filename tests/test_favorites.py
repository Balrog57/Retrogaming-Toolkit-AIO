import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

# Define a real class for CTk to avoid Application becoming a Mock
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def after(self, *args): return "job_id"
    def mainloop(self): pass
    def configure(self, *args, **kwargs): pass

# 1. Mock dependencies BEFORE importing main
ctk_mock = MagicMock()
ctk_mock.CTk = MockCTk
# Other widgets can be Mocks, that's fine as long as they are callable
sys.modules['customtkinter'] = ctk_mock

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['urllib.request'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['module_runner'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Add root to path
sys.path.append(os.getcwd())

# Import main after mocking
import main

class TestFavorites(unittest.TestCase):

    def setUp(self):
        # Patch app_data_dir to a temp location or mock it
        self.patcher = patch('main.app_data_dir', '/tmp/retrogaming_test')
        self.mock_app_dir = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_logic_real_methods(self):
        """Test the ACTUAL methods from main.Application."""

        # Verify main.Application is a real class
        self.assertIsInstance(main.Application, type)

        # Create a mock instance
        app = MagicMock()
        app.favorites = []

        # Bind the REAL methods to our mock instance
        app.load_favorites = main.Application.load_favorites.__get__(app, main.Application)
        app.save_favorites = main.Application.save_favorites.__get__(app, main.Application)
        app.toggle_favorite = main.Application.toggle_favorite.__get__(app, main.Application)
        app.filter_and_display = MagicMock()

        # Mock file operations
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data='["Tool1", "Tool2"]')) as mock_file, \
             patch('json.dump') as mock_json_dump:

            mock_exists.return_value = True

            # Test Load
            favs = app.load_favorites()
            self.assertEqual(favs, ["Tool1", "Tool2"])

            # Test Save logic via Toggle
            app.favorites = ["Tool1"]

            # Toggle OFF
            app.toggle_favorite("Tool1")
            self.assertEqual(app.favorites, [])
            mock_json_dump.assert_called()

            # Toggle ON
            app.toggle_favorite("Tool3")
            self.assertEqual(app.favorites, ["Tool3"])

    def test_sorting_logic(self):
        """Verify the sorting logic prioritizes favorites."""
        scripts = [{"name": "C"}, {"name": "A"}, {"name": "B"}]
        favorites = ["B"]

        # Sort logic
        scripts.sort(key=lambda x: (0 if x["name"] not in favorites else -1, x["name"]))

        expected = [{"name": "B"}, {"name": "A"}, {"name": "C"}]
        self.assertEqual(scripts, expected)

if __name__ == '__main__':
    unittest.main()
