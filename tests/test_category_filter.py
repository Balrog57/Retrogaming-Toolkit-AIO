import unittest
import sys
import os

# Add parent directory to sys.path to find main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch

# --- Mocks Setup BEFORE importing main ---

# Mock tkinter
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# Mock PIL
mock_pil = MagicMock()
mock_image = MagicMock()
# Setup Image.open to return a mock that has resize method
mock_img_instance = MagicMock()
mock_img_instance.resize.return_value = mock_img_instance
mock_image.open.return_value = mock_img_instance
mock_image.new.return_value = mock_img_instance
mock_image.LANCZOS = 1

mock_pil.Image = mock_image
sys.modules['PIL'] = mock_pil

# Mock CustomTkinter
# We need to define classes for inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def mainloop(self): pass
    def geometry(self, *args): pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def after(self, *args): pass
    def bind(self, *args): pass
    def update_idletasks(self): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 100
    def configure(self, *args, **kwargs): pass
    def destroy(self): pass

class MockWidget:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs): pass
    def pack_forget(self): pass
    def configure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def winfo_reqheight(self): return 20
    def winfo_children(self): return []
    def destroy(self): pass
    def focus_set(self): pass

class MockCTkFrame(MockWidget): pass
class MockCTkLabel(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = None
class MockCTkButton(MockWidget): pass
class MockCTkEntry(MockWidget): pass

# Mock StringVar
class MockStringVar:
    def __init__(self, value="", *args, **kwargs):
        self._value = value
        self._callbacks = []

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def trace(self, mode, callback):
        self._callbacks.append(callback)

# Mock CTkComboBox
class MockCTkComboBox(MockWidget):
    def __init__(self, master, values=None, command=None, variable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.values = values or []
        self._command = command
        self._variable = variable

    def configure(self, **kwargs):
        pass

# Mock CTkImage
class MockCTkImage:
    def __init__(self, light_image=None, dark_image=None, size=None):
        pass

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockCTkFrame
mock_ctk.CTkLabel = MockCTkLabel
mock_ctk.CTkButton = MockCTkButton
mock_ctk.CTkEntry = MockCTkEntry
mock_ctk.CTkComboBox = MockCTkComboBox
mock_ctk.StringVar = MockStringVar
mock_ctk.CTkImage = MockCTkImage
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

sys.modules['customtkinter'] = mock_ctk

# Mock utils
sys.modules['utils'] = MagicMock()

# Mock requests and webbrowser
sys.modules['requests'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Now import main
import main

class TestCategoryFilter(unittest.TestCase):
    def setUp(self):
        # Prevent threading.Thread.start from actually starting threads (updates check)
        self.thread_patcher = patch('threading.Thread')
        self.mock_thread = self.thread_patcher.start()

        # Prevent actual file operations if any (favorites loading)
        self.open_patcher = patch('builtins.open', new_callable=MagicMock)
        self.mock_open = self.open_patcher.start()
        # Mock json load to return empty list for favorites
        self.json_patcher = patch('json.load', return_value=[])
        self.mock_json = self.json_patcher.start()

        # Mock os.path.exists to avoid checking real icons
        self.exists_patcher = patch('os.path.exists', return_value=True)
        self.mock_exists = self.exists_patcher.start()

        # Initialize App
        self.app = main.Application()

    def tearDown(self):
        self.thread_patcher.stop()
        self.open_patcher.stop()
        self.json_patcher.stop()
        self.exists_patcher.stop()

    def test_scripts_have_categories(self):
        """Test that scripts are correctly assigned a category."""
        # Check a few known scripts
        script_dict = {s["name"]: s for s in self.app.scripts}

        self.assertEqual(script_dict["CHDManager"]["category"], "Gestion des Jeux & ROMs")
        self.assertEqual(script_dict["AssistedGamelist"]["category"], "Métadonnées & Gamelists")
        self.assertEqual(script_dict["YTDownloader"]["category"], "Multimédia & Artworks")
        self.assertEqual(script_dict["CollectionBuilder"]["category"], "Organisation & Collections")
        self.assertEqual(script_dict["LongPaths"]["category"], "Maintenance Système")

        # Check that UniversalRomCleaner got mapped correctly
        self.assertEqual(script_dict["UniversalRomCleaner"]["category"], "Gestion des Jeux & ROMs")

    def test_filter_by_category(self):
        """Test filtering by category."""
        # Initial state: "Tout" selected, all scripts shown
        self.app.category_var.set("Tout")
        self.app.filter_scripts()
        self.assertEqual(len(self.app.filtered_scripts), len(self.app.scripts))

        # Filter "Gestion des Jeux & ROMs"
        self.app.category_var.set("Gestion des Jeux & ROMs")
        self.app.filter_scripts()

        # Check that only scripts in that category are shown
        for script in self.app.filtered_scripts:
            self.assertEqual(script["category"], "Gestion des Jeux & ROMs")

        # Check specific presence
        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertIn("CHDManager", names)
        self.assertNotIn("YTDownloader", names)

    def test_filter_by_category_and_search(self):
        """Test combined filtering."""
        self.app.category_var.set("Multimédia & Artworks")
        self.app.search_var.set("Convert") # Should match VideoConvert and ImageConvert

        self.app.filter_scripts()

        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertIn("VideoConvert", names)
        self.assertIn("ImageConvert", names)
        self.assertNotIn("CHDManager", names) # Wrong category

if __name__ == '__main__':
    unittest.main()
