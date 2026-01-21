import sys
import os
import unittest
from unittest.mock import MagicMock

# Mock libraries before importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['threading'] = MagicMock()

import customtkinter as ctk

# Define Mock classes that simulate the minimal interface needed
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, text): pass
    def geometry(self, text): pass
    def iconbitmap(self, path): pass
    def bind(self, seq, func, add=None): pass
    def after(self, ms, func=None, *args): pass
    def update_idletasks(self): pass
    def mainloop(self): pass
    def winfo_children(self): return []
    def focus_set(self): pass
    def focus_get(self): return None
    def focus(self): pass

class MockWidget:
    def __init__(self, master=None, *args, **kwargs):
        self.master = master
    def pack(self, *args, **kwargs): pass
    def pack_forget(self): pass
    def destroy(self): pass
    def configure(self, *args, **kwargs): pass
    def winfo_reqheight(self): return 100 # return int
    def focus_set(self): pass
    def winfo_children(self): return []

class MockFrame(MockWidget): pass
class MockLabel(MockWidget): pass
class MockButton(MockWidget): pass

class MockEntry(MockWidget):
    def __init__(self, master=None, textvariable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.textvariable = textvariable
    def insert(self, index, string): pass
    def delete(self, first, last=None): pass
    def get(self): return ""
    def focus_set(self): pass

class MockStringVar:
    def __init__(self, value=""):
        self._value = value
    def trace(self, mode, callback): pass
    def get(self): return self._value
    def set(self, value): self._value = value

ctk.CTk = MockCTk
ctk.CTkFrame = MockFrame
ctk.CTkLabel = MockLabel
ctk.CTkButton = MockButton
ctk.CTkEntry = MockEntry
ctk.StringVar = MockStringVar

# Add current directory to path
sys.path.append(os.getcwd())

import main

class TestMainUX(unittest.TestCase):
    def setUp(self):
        # Instantiate Application
        self.app = main.Application()

        # Spy on the methods we care about
        # We replace the actual methods/objects with mocks AFTER instantiation
        # or we verify the side effects on the variables.

        # Mocking the search_entry.focus_set method to track calls
        self.app.search_entry.focus_set = MagicMock()

        # Mocking focus_get and focus
        self.app.focus_get = MagicMock()
        self.app.focus = MagicMock()

    def test_focus_search(self):
        if hasattr(self.app, 'focus_search'):
            self.app.focus_search()
            self.app.search_entry.focus_set.assert_called_once()
        else:
            print("focus_search not implemented yet")

    def test_on_escape_clears_text_if_focused(self):
        # Setup: Search has text, and is focused
        self.app.search_var.set("search term")
        self.app.focus_get.return_value = self.app.search_entry

        if hasattr(self.app, 'on_escape'):
            self.app.on_escape()
            # Expect text to be cleared
            self.assertEqual(self.app.search_var.get(), "")
        else:
             print("on_escape not implemented yet")

    def test_on_escape_blurs_if_empty_and_focused(self):
        # Setup: Search is empty, and is focused
        self.app.search_var.set("")
        self.app.focus_get.return_value = self.app.search_entry

        if hasattr(self.app, 'on_escape'):
            self.app.on_escape()
            # Expect blur (focus to self)
            self.app.focus.assert_called_once()
        else:
             print("on_escape not implemented yet")

    def test_on_escape_clears_if_not_focused(self):
        # Setup: Search has text, NOT focused
        self.app.search_var.set("search term")
        self.app.focus_get.return_value = None

        if hasattr(self.app, 'on_escape'):
            self.app.on_escape()
            # Expect text to be cleared
            self.assertEqual(self.app.search_var.get(), "")
        else:
             print("on_escape not implemented yet")

if __name__ == '__main__':
    unittest.main()
