import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- MOCKS START ---

class MockCTk:
    def __init__(self, *args, **kwargs):
        self.bind_calls = []
        self.children = []

    def title(self, t): pass
    def geometry(self, g): pass
    def iconbitmap(self, p): pass
    def after(self, ms, func=None):
        # Don't run immediately if it's the recursive focus set, otherwise infinite loop
        # But for simple lambdas it might be fine.
        # Ideally we mock after to just register callbacks.
        pass
    def mainloop(self): pass
    def update_idletasks(self): pass

    def bind(self, event, command, add=None):
        self.bind_calls.append(event)

    def winfo_children(self):
        return self.children

    def pack(self, *args, **kwargs): pass

    def winfo_reqheight(self): return 100

class MockWidget:
    def __init__(self, master=None, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs): pass
    def pack_forget(self): pass
    def grid(self, *args, **kwargs): pass
    def grid_forget(self): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 50
    def destroy(self): pass
    def focus_set(self): pass
    def configure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    # Add fake image property since labels use it
    @property
    def image(self): return None
    @image.setter
    def image(self, value): pass

class MockCTkImage:
    def __init__(self, *args, **kwargs):
        pass

# Setup sys.modules
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkButton = MockWidget
mock_ctk.CTkEntry = MockWidget
mock_ctk.StringVar = MagicMock
mock_ctk.CTkImage = MockCTkImage
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# --- MOCKS END ---

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patching os and logging before import
with patch('os.getenv', return_value='/tmp'), \
     patch('os.makedirs'), \
     patch('os.path.exists', return_value=True), \
     patch('builtins.open', MagicMock()), \
     patch('logging.basicConfig'), \
     patch('logging.getLogger'):

    import main

class TestMainUX(unittest.TestCase):
    def test_shortcuts(self):
        # Instantiate app
        app = main.Application()

        print(f"Captured bindings: {app.bind_calls}")

        # We handle case sensitivity by lowercasing for check if needed, but Tkinter events are specific.
        # <Control-f> is standard. <Escape> is standard.

        required_bindings = ['<Control-f>', '<Escape>', '<Left>', '<Right>']
        # Also check for variations like <Control-F> just in case

        normalized_binds = [b.lower() for b in app.bind_calls]

        missing = []
        for req in required_bindings:
            if req.lower() not in normalized_binds:
                missing.append(req)

        if missing:
            self.fail(f"Missing bindings: {missing}")

    def test_arrow_keys_logic(self):
        app = main.Application()

        # Mocking page navigation methods
        app.previous_page = MagicMock()
        app.next_page = MagicMock()

        # 1. Test from generic widget (should navigate)
        mock_event_generic = MagicMock()
        mock_event_generic.widget.winfo_class.return_value = 'Frame'

        app.handle_arrow_key(mock_event_generic, 'left')
        app.previous_page.assert_called_once()
        app.next_page.assert_not_called()

        app.previous_page.reset_mock()
        app.handle_arrow_key(mock_event_generic, 'right')
        app.next_page.assert_called_once()

        # 2. Test from Entry widget (should NOT navigate)
        mock_event_entry = MagicMock()
        mock_event_entry.widget.winfo_class.return_value = 'Entry'

        app.previous_page.reset_mock()
        app.next_page.reset_mock()

        app.handle_arrow_key(mock_event_entry, 'left')
        app.previous_page.assert_not_called()
        app.next_page.assert_not_called()

if __name__ == '__main__':
    unittest.main()
