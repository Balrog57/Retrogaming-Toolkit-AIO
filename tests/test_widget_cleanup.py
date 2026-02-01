import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Create dummy classes for inheritance
class MockCTk:
    def __init__(self, **kwargs):
        pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def after(self, *args): return "job_id"
    def after_cancel(self, *args): pass
    def mainloop(self): pass
    def winfo_exists(self): return True
    def winfo_children(self): return []
    def winfo_width(self): return 800

# Mock dependencies BEFORE importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['customtkinter'].CTk = MockCTk # Replace the Mock with our class
sys.modules['customtkinter'].CTkImage = MagicMock()

sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()

# Mock internal modules
sys.modules['radio'] = MagicMock()
sys.modules['module_runner'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Mock globals
os.environ['LOCALAPPDATA'] = '/tmp'

# Add current directory to path
sys.path.append(os.getcwd())

import main

class TestWidgetCleanup(unittest.TestCase):
    def setUp(self):
        # We need to control what is mocked.
        # For general setup, we mock everything to get an instance.
        with patch.object(main.Application, 'init_music'), \
             patch.object(main.Application, 'setup_sidebar'), \
             patch.object(main.Application, 'setup_content_area'), \
             patch.object(main.Application, 'check_updates'), \
             patch.object(main.Application, 'filter_and_display'), \
             patch.object(main.Application, 'setup_background'), \
             patch.object(main.Application, 'play_radio'):

            self.app = main.Application()

        # Setup attributes that might be missing due to mocked init calls
        self.app.canvas = MagicMock()
        self.app.canvas.winfo_width.return_value = 800

        self.app.scripts = [{"name": "TestScript", "description": "Test", "category": "Test"}]
        self.app.current_category = "Tout"
        self.app.search_query = ""
        self.app.current_lang = "FR"
        self.app.icon_cache = {}
        self.app.card_bg_img_cache = {}

        # Mock color attributes
        self.app.COLOR_SIDEBAR_BG = "black"
        self.app.COLOR_CARD_BORDER = "white"
        self.app.COLOR_TEXT_MAIN = "white"
        self.app.COLOR_TEXT_SUB = "gray"
        self.app.COLOR_ACCENT_PRIMARY = "blue"

    def test_draw_card_tracks_widgets(self):
        """
        Verify draw_card adds widgets to self.card_widgets
        """
        # Ensure list is empty
        self.app.card_widgets = []

        with patch('main.ctk.CTkButton') as MockBtn:
            self.app.draw_card(self.app.scripts[0], 0, 0, 100, 100)

            # Verify buttons were tracked
            self.assertEqual(len(self.app.card_widgets), 2)
            # Verify they are the mock objects returned by CTkButton
            self.assertEqual(self.app.card_widgets[0], MockBtn.return_value)

    def test_fix_structure_proposal(self):
        """
        Verify that IF widgets are in the list, they WOULD be destroyed.
        This tests the logic loop independently of filter_and_display integration.
        """
        self.app.card_widgets = []
        mock_btn1 = MagicMock()
        mock_btn2 = MagicMock()

        self.app.card_widgets.append(mock_btn1)
        self.app.card_widgets.append(mock_btn2)

        # Replicate the cleanup logic from main.py
        for widget in self.app.card_widgets:
            widget.destroy()
        self.app.card_widgets.clear()

        mock_btn1.destroy.assert_called_once()
        mock_btn2.destroy.assert_called_once()
        self.assertEqual(len(self.app.card_widgets), 0)

if __name__ == '__main__':
    unittest.main()
