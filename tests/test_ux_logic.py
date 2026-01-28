import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# 1. Mock dependencies BEFORE importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['multiprocessing'] = MagicMock()
sys.modules['threading'] = MagicMock()

# Mock specific ctk classes used in inheritance
class MockCTk(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind_calls = {}

    def bind(self, sequence, func, add=None):
        self.bind_calls[sequence] = func

    def bind_all(self, sequence, func, add=None):
        pass

    def protocol(self, *args):
        pass

    def geometry(self, *args):
        pass

    def resizable(self, *args):
        pass

    def grid_columnconfigure(self, *args, **kwargs):
        pass

    def grid_rowconfigure(self, *args, **kwargs):
        pass

    def after(self, ms, func=None, *args):
        # Return a dummy id
        return "after_id"

sys.modules['customtkinter'].CTk = MockCTk

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import main
import main

class TestUXKeyboard(unittest.TestCase):
    def test_keyboard_navigation_bindings_exist(self):
        # We need to instantiate Application
        # We must mock out the heavy lifting methods to avoid errors

        with patch.object(main.Application, 'setup_background'), \
             patch.object(main.Application, 'init_music'), \
             patch.object(main.Application, 'setup_sidebar'), \
             patch.object(main.Application, 'setup_content_area'), \
             patch.object(main.Application, 'check_updates'), \
             patch.object(main.Application, 'filter_and_display'), \
             patch.object(main.Application, 'play_radio'), \
             patch.object(main.Application, 'load_favorites', create=True, return_value=[]):

            app = main.Application()

            # Check for bindings
            bindings = app.bind_calls
            print("Registered bindings:", bindings.keys())

            # These are the ones we EXPECT (based on my plan)
            required_keys = ['<Up>', '<Down>', '<Prior>', '<Next>', '<Home>', '<End>']

            for key in required_keys:
                self.assertIn(key, bindings, f"Binding for {key} is missing")

if __name__ == '__main__':
    unittest.main()
