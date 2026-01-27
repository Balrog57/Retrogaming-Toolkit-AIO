import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Mock libraries before importing main
mock_ctk = MagicMock()
mock_tkdnd = MagicMock()
mock_pil = MagicMock()
mock_requests = MagicMock()
mock_pygame = MagicMock()
mock_radio = MagicMock()
mock_utils = MagicMock()
mock_theme = MagicMock()
mock_threading = MagicMock()
mock_multiprocessing = MagicMock()

# Mock widget class to avoid AttributeErrors
class MockWidget:
    def __init__(self, *args, **kwargs):
        self._w = "widget"
        self.bind_calls = {}
        self.yview_scroll = MagicMock()
        self.yview_moveto = MagicMock()
        self.set = MagicMock()

    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def bind(self, sequence=None, func=None, add=None):
        if sequence: self.bind_calls[sequence] = func
    def bind_all(self, sequence=None, func=None, add=None): pass
    def destroy(self): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_propagate(self, *args): pass
    def winfo_children(self): return []
    def cget(self, key): return ""
    def focus_set(self): pass
    def delete(self, *args): pass
    def canvasy(self, *args): return 0
    def create_image(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def create_window(self, *args, **kwargs): pass
    def coords(self, *args): pass
    def tag_lower(self, *args): pass
    def yview(self, *args): pass
    def winfo_width(self): return 800

# Configure specific mocks
mock_ctk.CTkCanvas = MockWidget
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkButton = MockWidget
mock_ctk.CTkEntry = MockWidget
mock_ctk.CTkTextbox = MockWidget
mock_ctk.CTkOptionMenu = MockWidget
mock_ctk.CTkScrollbar = MockWidget
mock_ctk.StringVar = MagicMock
mock_ctk.CTkImage = MagicMock
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

# Mock CTk class to support inheritance and capture bind calls
class MockCTkClass:
    def __init__(self, *args, **kwargs):
        self.tk = MagicMock()
        self.bind_calls = {}
        self._w = "root"

    def bind(self, sequence=None, func=None, add=None):
        if sequence:
            self.bind_calls[sequence] = func

    def geometry(self, *args): pass
    def title(self, *args): pass
    def resizable(self, *args): pass
    def iconbitmap(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def after(self, ms, func=None, *args): return "job_id"
    def after_cancel(self, id): pass
    def protocol(self, *args): pass
    def mainloop(self): pass
    def winfo_exists(self): return True
    def winfo_width(self): return 1200
    def update_idletasks(self): pass

mock_ctk.CTk = MockCTkClass
mock_ctk.CTkImage = MagicMock() # Needs to be callable or class

# Apply mocks
sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinterdnd2'] = mock_tkdnd
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['requests'] = mock_requests
sys.modules['pygame'] = mock_pygame
sys.modules['radio'] = mock_radio
sys.modules['utils'] = mock_utils
sys.modules['theme'] = mock_theme
sys.modules['threading'] = mock_threading
sys.modules['multiprocessing'] = mock_multiprocessing

# Setup path for internal imports in main.py
sys.path.append(os.getcwd())

# Import main after mocking
import main

class TestKeyboardNavigation(unittest.TestCase):
    def setUp(self):
        # Prevent scripts form trying to load icons
        main.scripts = []
        # Prevent init_music from spawning processes
        with patch('main.radio.run_radio_process'):
             self.app = main.Application()

        # Mock the canvas manually since we mocked CTkCanvas class, but instances are MagicMocks usually
        # But wait, self.canvas is created via ctk.CTkCanvas(self.content_container, ...)
        # In our mock setup, ctk.CTkCanvas is a MagicMock class, so the instance is a MagicMock.
        # We need to ensure we can check calls on it.
        self.app.canvas = MagicMock()
        self.app.update_background_position = MagicMock()

    def test_scroll_bindings_exist(self):
        """Test that scroll keys are bound to the application."""
        bindings = self.app.bind_calls

        expected_keys = ["<Up>", "<Down>", "<Prior>", "<Next>", "<Home>", "<End>"]
        for key in expected_keys:
            self.assertIn(key, bindings, f"Binding for {key} is missing")

    def test_scroll_logic(self):
        """Test that the callback performs the correct scroll action."""
        bindings = self.app.bind_calls

        # Helper to invoke callback
        def invoke(key, widget_class="Frame"):
            callback = bindings.get(key)
            if callback:
                mock_event = MagicMock()
                mock_event.widget.winfo_class.return_value = widget_class
                callback(mock_event)
            return callback

        # Up -> yview_scroll(-1, "units")
        if "<Up>" in bindings:
            invoke("<Up>")
            self.app.canvas.yview_scroll.assert_called_with(-1, "units")

        # Down -> yview_scroll(1, "units")
        if "<Down>" in bindings:
            self.app.canvas.reset_mock()
            invoke("<Down>")
            self.app.canvas.yview_scroll.assert_called_with(1, "units")

        # PageUp -> yview_scroll(-1, "pages")
        if "<Prior>" in bindings:
            self.app.canvas.reset_mock()
            invoke("<Prior>")
            self.app.canvas.yview_scroll.assert_called_with(-1, "pages")

        # PageDown -> yview_scroll(1, "pages")
        if "<Next>" in bindings:
            self.app.canvas.reset_mock()
            invoke("<Next>")
            self.app.canvas.yview_scroll.assert_called_with(1, "pages")

        # Home -> yview_moveto(0)
        if "<Home>" in bindings:
            self.app.canvas.reset_mock()
            invoke("<Home>")
            self.app.canvas.yview_moveto.assert_called_with(0)

        # End -> yview_moveto(1)
        if "<End>" in bindings:
            self.app.canvas.reset_mock()
            invoke("<End>")
            self.app.canvas.yview_moveto.assert_called_with(1)

    def test_no_scroll_on_entry_focus(self):
        """Test that scrolling is disabled when an Entry widget is focused."""
        bindings = self.app.bind_calls

        callback = bindings.get("<Down>")
        if not callback:
            return # Skip if not implemented yet

        mock_event = MagicMock()
        mock_event.widget.winfo_class.return_value = "Entry"

        self.app.canvas.reset_mock()
        callback(mock_event)

        self.app.canvas.yview_scroll.assert_not_called()

if __name__ == '__main__':
    unittest.main()
