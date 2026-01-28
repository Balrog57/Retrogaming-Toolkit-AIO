
import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch, mock_open

# Proper Mock for CustomTkinter
class MockWidget:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def bind_all(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def cget(self, key): return ""
    def winfo_width(self): return 800
    def winfo_height(self): return 600
    def winfo_children(self): return []
    def delete(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass
    def create_image(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def create_window(self, *args, **kwargs): pass
    def yview_moveto(self, *args, **kwargs): pass
    def canvasy(self, *args, **kwargs): return 0
    def coords(self, *args, **kwargs): pass
    def tag_lower(self, *args, **kwargs): pass
    def destroy(self): pass
    def focus_set(self): pass
    def grid_propagate(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def set(self, *args, **kwargs): pass

class MockStringVar:
    def __init__(self, value="", *args, **kwargs): self.value = value
    def trace(self, *args, **kwargs): pass
    def trace_add(self, *args, **kwargs): pass
    def get(self): return self.value
    def set(self, val): self.value = val

class MockCTk:
    def __init__(self, **kwargs):
        pass
    def geometry(self, *args, **kwargs): pass
    def resizable(self, *args, **kwargs): pass
    def title(self, *args, **kwargs): pass
    def iconbitmap(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def after(self, ms, func=None, *args): return "job_id"
    def after_cancel(self, id): pass
    def bind(self, seq, func): pass
    def protocol(self, name, func): pass
    def mainloop(self): pass
    def winfo_width(self): return 800
    def winfo_height(self): return 600
    def update_idletasks(self): pass
    def withdraw(self): pass
    def deiconify(self): pass
    def winfo_exists(self): return True

# We need to set this up BEFORE importing main
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkEntry = MockWidget
mock_ctk.CTkButton = MockWidget
mock_ctk.CTkScrollbar = MockWidget
mock_ctk.CTkOptionMenu = MockWidget
mock_ctk.CTkCanvas = MockWidget
mock_ctk.StringVar = MockStringVar
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()
# Other widgets can be MagicMocks
sys.modules['customtkinter'] = mock_ctk

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['zipfile'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['radio'].run_radio_process = MagicMock()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

class TestFavoritesReal(unittest.TestCase):
    def setUp(self):
        # Patch Image stuff
        patch('main.Image').start()
        patch('main.CTkImage').start()
        patch('threading.Thread').start()
        patch('multiprocessing.Process').start()
        patch('multiprocessing.Queue').start()
        patch('main.pygame').start()

    def tearDown(self):
        patch.stopall()

    def test_logic(self):
        """Test the favorites logic implementation"""
        app = main.Application()

        # Now app is instance of Application(MockCTk)
        # It should have our methods
        self.assertTrue(hasattr(app, 'load_favorites'))

        # Mock app_data_dir usage
        favorites_path = os.path.join(main.app_data_dir, 'favorites.json')

        # --- Test load_favorites ---
        # Case 1: File doesn't exist
        with patch('os.path.exists', return_value=False):
             res = app.load_favorites()
             self.assertEqual(res, [])

        # Case 2: File exists
        mock_data = '["ScriptA", "ScriptB"]'
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_data)) as m:
                 res = app.load_favorites()
                 self.assertEqual(res, ["ScriptA", "ScriptB"])

        # --- Test toggle_favorite ---
        app.favorites = []
        app.filter_and_display = MagicMock()

        # We need to mock save_favorites or allow it to run with mocked open
        with patch('builtins.open', mock_open()) as m_save:
            # Add
            app.toggle_favorite("NewScript")
            self.assertIn("NewScript", app.favorites)
            app.filter_and_display.assert_called()

            # Verify write
            handle = m_save()
            handle.write.assert_called()

            # Remove
            app.toggle_favorite("NewScript")
            self.assertNotIn("NewScript", app.favorites)


if __name__ == '__main__':
    unittest.main()
