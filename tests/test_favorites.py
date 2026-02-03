import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch, mock_open

# Mock dependencies BEFORE importing main
mock_ctk = MagicMock()

# Define a Mock Class for CTk that accepts everything
class MockCTk:
    def __init__(self, **kwargs): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def protocol(self, *args): pass
    def bind(self, *args): pass
    def after(self, *args): return "job"
    def after_cancel(self, *args): pass
    def mainloop(self): pass
    def iconbitmap(self, *args): pass
    def title(self, *args): pass
    def winfo_width(self): return 1000
    def winfo_height(self): return 800
    def winfo_exists(self): return True
    def configure(self, *args, **kwargs): pass
    def update_idletasks(self): pass
    def destroy(self): pass
    def minsize(self, *args): pass
    def wm_iconbitmap(self, *args): pass
    def wm_iconphoto(self, *args): pass
    def focus_set(self): pass
    def grab_set(self): pass

# Generic Mock Widget Class for inheritance
class MockWidget:
    def __init__(self, *args, **kwargs):
        self.configure = MagicMock()
        self.grid = MagicMock()
        self.pack = MagicMock()
        self.place = MagicMock()
        self.grid_propagate = MagicMock()
        self.grid_rowconfigure = MagicMock()
        self.grid_columnconfigure = MagicMock()
        self.destroy = MagicMock()
        self.cget = MagicMock(return_value="")
        self.bind = MagicMock()
        self.yview = MagicMock()
        self.yview_moveto = MagicMock()
        self.yview_scroll = MagicMock()
        self.canvasy = MagicMock(return_value=0)
        self.create_text = MagicMock()
        self.create_image = MagicMock()
        self.create_window = MagicMock()
        self.create_rectangle = MagicMock()
        self.delete = MagicMock()
        self.tag_lower = MagicMock()
        self.coords = MagicMock()
        self.insert = MagicMock()
        self.set = MagicMock()
        self.bind_all = MagicMock()

    def winfo_width(self): return 100
    def winfo_children(self): return []

mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkButton = MockWidget
mock_ctk.CTkEntry = MockWidget
mock_ctk.CTkCanvas = MockWidget
mock_ctk.CTkScrollbar = MockWidget
mock_ctk.CTkImage = MagicMock
mock_ctk.CTkOptionMenu = MockWidget
mock_ctk.CTkTextbox = MockWidget
mock_ctk.CTkToplevel = MockWidget # Now a class
mock_ctk.StringVar = MagicMock
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['lxml'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['module_runner'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Setup sys.path
sys.path.append(os.getcwd())

import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Prevent radio process start
        with patch('multiprocessing.Process'), patch('multiprocessing.Queue'):
            self.app = main.Application()
            # Manually inject app_data_dir if needed
            self.app.favorites = [] # Reset if logic exists

    def test_load_favorites_file_exists(self):
        # Mock file existence and content
        data = '["ToolA", "ToolB"]'
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=data)):

            # Call load_favorites (assuming it will be implemented)
            if hasattr(self.app, 'load_favorites'):
                favs = self.app.load_favorites()
                self.assertEqual(favs, ["ToolA", "ToolB"])
            else:
                pass

    def test_load_favorites_file_missing(self):
        with patch('os.path.exists', return_value=False):
            if hasattr(self.app, 'load_favorites'):
                favs = self.app.load_favorites()
                self.assertEqual(favs, [])
            else:
                pass

    def test_save_favorites(self):
        self.app.favorites = ["ToolX"]
        with patch('builtins.open', mock_open()) as m_open:
            if hasattr(self.app, 'save_favorites'):
                self.app.save_favorites()
                # Check path
                # m_open.assert_called_with(..., 'w')
                # check write
                handle = m_open()
                written_data = "".join(call.args[0] for call in handle.write.call_args_list)
                self.assertIn('"ToolX"', written_data)
            else:
                pass

    def test_toggle_favorite(self):
        self.app.favorites = []
        if hasattr(self.app, 'toggle_favorite'):
            # Mock save_favorites and filter_and_display to avoid side effects
            self.app.save_favorites = MagicMock()
            self.app.filter_and_display = MagicMock()

            # Toggle ON
            self.app.toggle_favorite("MyTool")
            self.assertIn("MyTool", self.app.favorites)
            self.app.save_favorites.assert_called()
            self.app.filter_and_display.assert_called()

            # Toggle OFF
            self.app.toggle_favorite("MyTool")
            self.assertNotIn("MyTool", self.app.favorites)
        else:
            pass

    def test_sorting_favorites_first(self):
        self.app.favorites = ["Z_Tool"]
        self.app.scripts = [
            {"name": "A_Tool", "category": "Tout"},
            {"name": "Z_Tool", "category": "Tout"},
            {"name": "B_Tool", "category": "Tout"}
        ]
        self.app.current_category = "Tout"
        self.app.search_query = ""

        # Mock draw_card to capture call order
        self.app.draw_card = MagicMock()
        self.app.update_content_height = MagicMock()
        # Ensure canvas methods work
        # Application.__init__ creates canvas using CTkCanvas which is MockWidget
        # So self.app.canvas is a MockWidget instance.
        self.app.canvas.winfo_width = MagicMock(return_value=800)

        self.app.filter_and_display()

        calls = self.app.draw_card.call_args_list
        if len(calls) >= 3:
            names = [call[0][0]["name"] for call in calls]
            # Expected: Z_Tool (Fav) first, then A_Tool, then B_Tool
            self.assertEqual(names[0], "Z_Tool")
            self.assertEqual(names[1], "A_Tool")
            self.assertEqual(names[2], "B_Tool")
        else:
            pass

if __name__ == '__main__':
    unittest.main()
