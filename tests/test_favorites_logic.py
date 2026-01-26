import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json

# --- MOCKING DEPENDENCIES BEFORE IMPORTING main ---
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['urllib.request'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['module_runner'] = MagicMock()

# Mock CTk class to support inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def after(self, ms, func=None, *args):
        # Do NOT call func immediately to avoid infinite recursion loops (like marquee)
        return "job_id"
    def after_cancel(self, *args): pass
    def mainloop(self, *args): pass
    def iconbitmap(self, *args): pass
    def withdraw(self): pass
    def deiconify(self): pass
    def overrideredirect(self, *args): pass
    def update_idletasks(self): pass
    def destroy(self): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def winfo_width(self): return 800
    def winfo_height(self): return 600
    def wm_attributes(self, *args, **kwargs): pass
    def wm_iconbitmap(self, *args): pass
    def wm_iconphoto(self, *args): pass
    def focus_set(self): pass
    def grab_set(self): pass
    def minsize(self, *args): pass

# Setup customtkinter mocks
ctk_mock = sys.modules['customtkinter']
ctk_mock.CTk = MockCTk
ctk_mock.CTkToplevel = MockCTk # ReadmeWindow inherits from this
ctk_mock.CTkFrame = MagicMock()
ctk_mock.CTkLabel = MagicMock()
ctk_mock.CTkButton = MagicMock()
ctk_mock.CTkEntry = MagicMock()

# Configure CTkCanvas to return an object with winfo_width returning int
canvas_mock_instance = MagicMock()
canvas_mock_instance.winfo_width.return_value = 800
canvas_mock_instance.create_text.return_value = 1
canvas_mock_instance.create_image.return_value = 2
canvas_mock_instance.create_rectangle.return_value = 3
canvas_mock_instance.create_window.return_value = 4
ctk_mock.CTkCanvas = MagicMock(return_value=canvas_mock_instance)

ctk_mock.CTkScrollbar = MagicMock()
ctk_mock.CTkOptionMenu = MagicMock()
ctk_mock.CTkTextbox = MagicMock() # For ReadmeWindow
ctk_mock.CTkImage = MagicMock()
ctk_mock.StringVar = MagicMock

# Mock stringvar behavior a bit better if needed
class MockStringVar:
    def __init__(self, value="", *args, **kwargs):
        self._val = value
    def get(self): return self._val
    def set(self, val): self._val = val
    def trace(self, *args): pass
    def trace_add(self, *args): pass

ctk_mock.StringVar = MockStringVar

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Import main
import main

class TestFavoritesLogic(unittest.TestCase):

    def setUp(self):
        # Prevent threading in check_updates
        self.check_updates_patch = patch('main.check_for_updates', return_value=(False, "1.0", None))
        self.check_updates_patch.start()

        # Patch load_favorites to avoid reading real file during init (unless we want to test that)
        # We can patch os.path.exists to False to simulate no favorites file by default
        self.exists_patcher = patch('os.path.exists', return_value=False)
        self.exists_patcher.start()

    def tearDown(self):
        self.check_updates_patch.stop()
        self.exists_patcher.stop()

    def test_methods_existence(self):
        """Test that the new methods exist in Application class."""
        app = main.Application()
        self.assertTrue(hasattr(app, 'load_favorites'), "Application should have load_favorites")
        self.assertTrue(hasattr(app, 'save_favorites'), "Application should have save_favorites")
        self.assertTrue(hasattr(app, 'toggle_favorite'), "Application should have toggle_favorite")
        self.assertTrue(hasattr(app, 'favorites'), "Application should have favorites attribute")

    def test_load_favorites(self):
        """Test loading favorites from JSON."""
        mock_data = json.dumps(["ScriptA", "ScriptB"])

        # We need to stop the global exists patcher to apply a new one or just override it
        self.exists_patcher.stop()

        with patch("builtins.open", mock_open(read_data=mock_data)):
            with patch("os.path.exists", return_value=True):
                app = main.Application()
                # If load_favorites is called in __init__, app.favorites should be set
                self.assertEqual(app.favorites, ["ScriptA", "ScriptB"])

    def test_save_favorites(self):
        """Test saving favorites to JSON."""
        app = main.Application()
        app.favorites = ["ScriptX"]

        m = mock_open()
        with patch("builtins.open", m):
            app.save_favorites()

        m.assert_called_with(os.path.join(main.app_data_dir, 'favorites.json'), 'w')
        handle = m()
        # Join the write calls to check the full JSON
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('"ScriptX"', written_content)

    def test_toggle_favorite(self):
        """Test toggling a favorite."""
        # Mock save_favorites to avoid file I/O errors during toggle
        # Note: We need to patch the method on the INSTANCE or Class
        # Since we create app inside, better patch on Class
        with patch.object(main.Application, 'save_favorites') as mock_save:
            with patch.object(main.Application, 'filter_and_display') as mock_filter:
                app = main.Application()
                app.favorites = []

                # Add
                app.toggle_favorite("ScriptA")
                self.assertIn("ScriptA", app.favorites)
                mock_save.assert_called()
                mock_filter.assert_called()

                # Remove
                app.toggle_favorite("ScriptA")
                self.assertNotIn("ScriptA", app.favorites)

    def test_category_setup(self):
        """Test that 'Favoris' category is added."""
        app = main.Application()
        # Check if 'Favoris' is in the category buttons keys
        # Note: setup_sidebar uses "Favoris" string
        self.assertIn("Favoris", app.category_buttons.keys())

if __name__ == '__main__':
    unittest.main()
