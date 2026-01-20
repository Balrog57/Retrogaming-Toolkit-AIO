import sys
import os
import unittest
from unittest.mock import MagicMock

# Define a Mock class for CTk that captures bind calls
class MockCTk:
    def __init__(self, **kwargs):
        self.bind_calls = []
        self.after_calls = []

    def bind(self, event, command=None):
        self.bind_calls.append((event, command))

    def after(self, ms, func=None):
        self.after_calls.append((ms, func))

    def title(self, *args): pass
    def geometry(self, *args): pass
    def iconbitmap(self, *args): pass
    def update_idletasks(self): pass
    def mainloop(self): pass
    def configure(self, **kwargs): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 100
    def focus_set(self): pass

# Setup ctk mock module
ctk_module = MagicMock()
ctk_module.CTk = MockCTk

# Configure CTkFrame to return an object with winfo_reqheight returning an int
frame_mock = MagicMock()
frame_mock.winfo_reqheight.return_value = 50
ctk_module.CTkFrame.return_value = frame_mock

# Same for other widgets if they are queried (unlikely for reqheight in main loop)
ctk_module.CTkLabel = MagicMock()
ctk_module.CTkEntry = MagicMock()
ctk_module.CTkButton = MagicMock()
ctk_module.StringVar = MagicMock()
ctk_module.set_appearance_mode = MagicMock()
ctk_module.set_default_color_theme = MagicMock()

sys.modules["customtkinter"] = ctk_module

tk_mock = MagicMock()
sys.modules["tkinter"] = tk_mock
sys.modules["tkinter.messagebox"] = MagicMock()

pil_mock = MagicMock()
sys.modules["PIL"] = pil_mock
sys.modules["PIL.Image"] = MagicMock()

requests_mock = MagicMock()
sys.modules["requests"] = requests_mock

utils_mock = MagicMock()
utils_mock.resource_path = lambda x: x
sys.modules["utils"] = utils_mock

sys.path.append(os.getcwd())
import main

class TestMainUX(unittest.TestCase):
    def test_keyboard_shortcuts_bound(self):
        """Test that Ctrl+F and Escape are bound in Application.__init__"""
        app = main.Application()

        print("Bind calls:", app.bind_calls)

        bound_events = [call[0] for call in app.bind_calls]

        self.assertIn("<Control-f>", bound_events, "Ctrl+F should be bound")
        self.assertIn("<Escape>", bound_events, "Escape should be bound")

        for event, command in app.bind_calls:
            if event == "<Escape>":
                self.assertEqual(command, app.clear_search_or_focus)

    def test_clear_search_or_focus(self):
        """Test the logic of clear_search_or_focus"""
        app = main.Application()

        # Mock search_var
        app.search_var = MagicMock()

        # Case 1: Text present -> should clear
        app.search_var.get.return_value = "something"
        app.clear_search = MagicMock()

        app.clear_search_or_focus()

        app.clear_search.assert_called_once()

        # Case 2: No text -> should focus window (blur entry)
        app.search_var.get.return_value = ""
        app.clear_search.reset_mock()
        # We can't check focus_set call easily as MockCTk doesn't record it
        # But we ensure it doesn't crash
        app.clear_search_or_focus()
        app.clear_search.assert_not_called()

if __name__ == "__main__":
    unittest.main()
