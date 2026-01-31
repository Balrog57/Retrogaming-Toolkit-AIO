import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- MOCKING DEPENDENCIES BEFORE IMPORT ---
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['ctypes'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['zipfile'] = MagicMock()

# Define Mock Classes to simulate ctk widgets
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def protocol(self, *args): pass
    def after(self, *args): return "job_id"
    def after_cancel(self, *args): pass
    def mainloop(self): pass
    def iconbitmap(self, *args): pass
    def winfo_exists(self): return True
    def winfo_width(self): return 1000
    def winfo_height(self): return 800
    def update_idletasks(self): pass
    def title(self, *args): pass
    def configure(self, *args, **kwargs): pass

class MockWidget:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def destroy(self): pass
    def winfo_children(self): return []
    def grid_propagate(self, *args): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def cget(self, key): return ""
    def focus_set(self): pass

class MockCanvas(MockWidget):
    def delete(self, *args): pass
    def yview_moveto(self, *args): pass
    def create_text(self, *args, **kwargs): pass
    def create_image(self, *args, **kwargs): pass
    def create_window(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def canvasy(self, val): return val
    def coords(self, *args): pass
    def tag_lower(self, *args): pass
    def bind_all(self, *args): pass

class MockScrollbar(MockWidget):
    def set(self, *args): pass

# Patch sys.modules with our mock classes structure
sys.modules['customtkinter'].CTk = MockCTk
sys.modules['customtkinter'].CTkFrame = MockWidget
sys.modules['customtkinter'].CTkLabel = MockWidget
sys.modules['customtkinter'].CTkButton = MockWidget
sys.modules['customtkinter'].CTkEntry = MockWidget
sys.modules['customtkinter'].CTkCanvas = MockCanvas
sys.modules['customtkinter'].CTkScrollbar = MockScrollbar
sys.modules['customtkinter'].CTkImage = MagicMock()
sys.modules['customtkinter'].StringVar = MagicMock
sys.modules['customtkinter'].CTkOptionMenu = MockWidget
sys.modules['customtkinter'].CTkToplevel = MockWidget
sys.modules['customtkinter'].CTkTextbox = MockWidget

# Now import main
import main

class TestUXLogic(unittest.TestCase):
    def setUp(self):
        # Suppress logging
        main.logger = MagicMock()

    def test_keyboard_bindings(self):
        bind_calls = []

        # Intercept bind calls
        def side_effect_bind(self, key, command):
            bind_calls.append(key)

        # Side effect for init_music to set attributes
        def side_effect_init_music(self):
            self.music_playing = False
            self.music_muted = False
            self.gif_paused = False
            self.radio_queue = MagicMock()
            self.radio_process = MagicMock()
            self.radio_process.is_alive.return_value = True

        # Prepare environment
        with patch.object(main.Application, 'bind', autospec=True, side_effect=side_effect_bind) as mock_bind, \
             patch('main.get_path', return_value="assets/icon.ico"), \
             patch('os.path.exists', return_value=True), \
             patch('main.scripts', []), \
             patch('main.theme', MagicMock()), \
             patch('main.utils', MagicMock()), \
             patch.object(main.Application, 'init_music', autospec=True, side_effect=side_effect_init_music), \
             patch.object(main.Application, 'setup_background', return_value=None), \
             patch.object(main.Application, 'filter_and_display', return_value=None), \
             patch.object(main.Application, 'check_updates', return_value=None):

            # Instantiate
            app = main.Application()

            # Check existing binds (from memory/code reading)
            self.assertIn('<Control-f>', bind_calls, "Ctrl+F should be bound")
            self.assertIn('<Escape>', bind_calls, "Escape should be bound")

            # Check for NEW binds (should fail initially)
            self.assertIn('<Up>', bind_calls, "Up arrow should be bound")
            self.assertIn('<Down>', bind_calls, "Down arrow should be bound")
            self.assertIn('<Prior>', bind_calls, "PageUp should be bound")
            self.assertIn('<Next>', bind_calls, "PageDown should be bound")
            self.assertIn('<Home>', bind_calls, "Home should be bound")
            self.assertIn('<End>', bind_calls, "End should be bound")

if __name__ == '__main__':
    unittest.main()
