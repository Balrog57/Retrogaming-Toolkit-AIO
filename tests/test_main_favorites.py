import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json

# Mock modules BEFORE importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Mock CTk class for inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def mainloop(self):
        pass
    def geometry(self, *args):
        pass
    def title(self, *args):
        pass
    def iconbitmap(self, *args):
        pass
    def after(self, *args, **kwargs):
        pass
    def winfo_children(self):
        return []
    def update_idletasks(self):
        pass
    def pack(self, *args, **kwargs):
        pass
    def destroy(self):
        pass
    def winfo_reqheight(self):
        return 100

# Mock widgets to allow instantiation
class MockWidget:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def pack_forget(self, *args, **kwargs):
        pass
    def winfo_children(self):
        return []
    def winfo_reqheight(self):
        return 50
    def configure(self, *args, **kwargs):
        pass
    def focus_set(self):
        pass
    def bind(self, *args, **kwargs):
        pass

class MockStringVar:
    def __init__(self, *args, **kwargs):
        self._val = ""
    def trace(self, *args, **kwargs):
        pass
    def get(self):
        return self._val
    def set(self, val):
        self._val = val

# Setup the mock CTk module
mock_ctk = sys.modules['customtkinter']
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockWidget
mock_ctk.CTkLabel = MockWidget
mock_ctk.CTkEntry = MockWidget
# Use MagicMock for Button to easily track calls
mock_ctk.CTkButton = MagicMock()
mock_ctk.StringVar = MockStringVar

mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

# Ensure we can import main
sys.path.append(os.getcwd())
import main

class TestFavorites(unittest.TestCase):
    def setUp(self):
        # Patch json to verify saving
        self.json_patcher = patch('json.dump')
        self.mock_json_dump = self.json_patcher.start()

        self.json_load_patcher = patch('json.load')
        self.mock_json_load = self.json_load_patcher.start()
        self.mock_json_load.return_value = [] # Default empty list

        # Patch open
        self.open_patcher = patch('builtins.open', mock_open(read_data='[]'))
        self.mock_open = self.open_patcher.start()

        # Patch os.path.exists
        self.exists_patcher = patch('os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        self.mock_exists.return_value = True # File exists to trigger load

        # Patch makedirs
        self.makedirs_patcher = patch('os.makedirs')
        self.mock_makedirs = self.makedirs_patcher.start()

    def tearDown(self):
        self.json_patcher.stop()
        self.json_load_patcher.stop()
        self.open_patcher.stop()
        self.exists_patcher.stop()
        self.makedirs_patcher.stop()

    def test_logic(self):
        """Test the logic of favorites."""
        app = main.Application()

        # Initial state: Empty favorites (from mock_json_load)
        self.assertEqual(app.favorites, [])

        # Toggle favorite: Add
        script_name = "TestScript"
        app.toggle_favorite(script_name)

        # Check if added to list
        self.assertIn(script_name, app.favorites)

        # Check if saved
        self.mock_json_dump.assert_called_with([script_name], self.mock_open())

        # Toggle favorite: Remove
        app.toggle_favorite(script_name)

        # Check if removed from list
        self.assertNotIn(script_name, app.favorites)

        # Check if saved (empty list)
        self.mock_json_dump.assert_called_with([], self.mock_open())

    def test_sorting(self):
        """Test that favorites are sorted to the top."""
        app = main.Application()

        # We rely on scripts list from main.py
        # Initial state: sorted roughly by manual list (not strictly alphabetical in code, but filtered_scripts uses list(scripts))
        # Wait, if query is empty, filtered_scripts is list(scripts).
        # But filter_scripts is called by trace, which might be triggered?
        # Initialization does: self.filtered_scripts = list(self.scripts)
        # Then self.update_page().
        # self.favorites is empty.

        # Let's force filter_scripts call to ensure sort is applied
        app.filter_scripts()

        # Check that 'AssistedGamelist' is first (since it is first in scripts list and sorted alphabetically 'A' is good)
        # My sort key is (is_fav, name). So alphabetical sort IS applied even if no favorites.

        first_script_name = app.filtered_scripts[0]['name']

        # Pick the second script in the sorted list (likely BGBackup)
        second_script_name = app.filtered_scripts[1]['name']

        # Make the second script a favorite
        app.toggle_favorite(second_script_name)

        # Now it should be first
        self.assertEqual(app.filtered_scripts[0]['name'], second_script_name)

        # Toggle it off
        app.toggle_favorite(second_script_name)

        # Should be back to original order
        self.assertEqual(app.filtered_scripts[0]['name'], first_script_name)

    def test_ui_elements(self):
        """Test that UI elements are created correctly."""
        # Reset mocks
        mock_ctk.CTkButton.reset_mock()

        app = main.Application()

        # Initially, app.favorites is empty.
        # We expect calls to CTkButton.
        # Check args for one of the calls.

        # We have ~30 scripts.
        # For each script, we create a favorite button and a launch button and a readme button.
        # 3 buttons per script.

        # Let's find a call that has "★" or "☆"
        found_star = False
        for call in mock_ctk.CTkButton.call_args_list:
            args, kwargs = call
            if kwargs.get('text') in ["★", "☆"]:
                found_star = True
                break

        self.assertTrue(found_star, "Favorite button should be created")

if __name__ == '__main__':
    unittest.main()
