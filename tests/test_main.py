import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Custom Mock classes need to be defined BEFORE import main
class MockCTk(object):
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def geometry(self, *args): pass
    def after(self, *args): pass
    def bind(self, *args): pass
    def update_idletasks(self): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 100
    def pack(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def mainloop(self): pass

class MockStringVar:
    def __init__(self, value="", **kwargs):
        self._val = value
    def trace(self, mode, callback):
        pass
    def get(self):
        return self._val
    def set(self, val):
        self._val = val

class MockWidget:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs): pass
    def pack_forget(self, *args, **kwargs): pass
    def winfo_reqheight(self): return 50
    def configure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def focus_set(self): pass
    def winfo_children(self): return []
    def destroy(self): pass
    def winfo_class(self): return "Frame" # Default

# Mock customtkinter and other dependencies
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkButton = MockWidget
mock_ctk.CTkEntry = MockWidget
mock_ctk.CTkComboBox = MockWidget
mock_ctk.StringVar = MockStringVar
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Mock utils which is imported in main
sys.modules['utils'] = MagicMock()

# Add root to sys.path
sys.path.append(os.getcwd())

import main

class TestApplication(unittest.TestCase):
    def setUp(self):
        # Create the app
        self.app = main.Application()
        self.app.favorites = set()

    def test_initial_scripts(self):
        self.assertEqual(len(self.app.filtered_scripts), len(main.scripts))

    def test_search_filtering(self):
        self.app.search_var.set("YTDownloader")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), 1)
        self.assertEqual(self.app.filtered_scripts[0]['name'], "YTDownloader")

    def test_search_case_insensitive(self):
        self.app.search_var.set("ytdownloader")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), 1)
        self.assertEqual(self.app.filtered_scripts[0]['name'], "YTDownloader")

    def test_search_clear(self):
        self.app.search_var.set("YTDownloader")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), 1)

        self.app.search_var.set("")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), len(main.scripts))

    def test_category_filtering(self):
        # We expect app to have category_var
        if not hasattr(self.app, 'category_var'):
            self.fail("category_var not implemented")

        self.app.category_var.set("Multimédia & Artworks")
        self.app.filter_scripts()

        # Check that filtered scripts are only from that category
        # YTDownloader is in Multimedia
        names = [s['name'] for s in self.app.filtered_scripts]
        self.assertIn("YTDownloader", names)
        # CollectionBuilder is NOT
        self.assertNotIn("CollectionBuilder", names)

        # Test "Toutes les catégories"
        self.app.category_var.set("Toutes les catégories")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), len(main.scripts))

if __name__ == '__main__':
    unittest.main()
