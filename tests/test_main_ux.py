import unittest
from unittest.mock import MagicMock
import sys
import os

# Mock customtkinter as it requires a display and we might run in headless env
sys.modules['customtkinter'] = MagicMock()
import tkinter as tk
sys.modules['tkinter'] = MagicMock()

# Add path to import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

class TestMainUX(unittest.TestCase):
    def setUp(self):
        # Prevent main.Application from initializing full UI which calls ctk methods
        # relying on tk.Tk() which isn't fully mocked by just MagicMock() sometimes
        # So we mock the Application class parts we need or just instantiate if mocks hold up
        self.app = main.Application()
        self.app.bind_calls = []
        
        # Monkey patch bind to capture calls
        def mock_bind(event, command=None):
            self.app.bind_calls.append((event, command))
        self.app.bind = mock_bind
        
        # Manually run the init logic parts responsible for bindings if we can't run full init
        # But since we instantiated it, and CTk is mocked, it should have run init.
        # However, our replace_file_content put bindings in __init__.
        # If MagicMock works for CTk(), __init__ runs.
        
        # Re-apply bindings manually if __init__ failed to register because of mocks
        # Actually, let's just test logic of clear_search_or_focus individually
        # and assume variables are setup.

    def test_clear_search_or_focus(self):
        """Test the logic of clear_search_or_focus"""
        # Setup mocks
        self.app.search_var = MagicMock()
        self.app.clear_search = MagicMock()
        self.app.focus_set = MagicMock()

        # Case 1: Text present -> should clear
        self.app.search_var.get.return_value = "something"
        self.app.clear_search_or_focus()
        self.app.clear_search.assert_called_once()
        self.app.focus_set.assert_not_called()

        # Case 2: No text -> should focus window (blur entry)
        self.app.clear_search.reset_mock()
        self.app.search_var.get.return_value = ""
        self.app.clear_search_or_focus()
        self.app.clear_search.assert_not_called()
        self.app.focus_set.assert_called_once()

if __name__ == "__main__":
    unittest.main()
