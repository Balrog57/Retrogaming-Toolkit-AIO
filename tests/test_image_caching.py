
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock customtkinter and PIL before importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Define a real class for CTk to allow proper inheritance and attribute handling
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def title(self, *args): pass
    def geometry(self, *args): pass
    def iconbitmap(self, *args): pass
    def mainloop(self): pass
    def after(self, *args): pass
    def update_idletasks(self): pass
    def winfo_children(self): return []
    # Add other methods if needed

class MockCTkImage:
    def __init__(self, *args, **kwargs):
        pass

# Mock helpers that might be used
mock_ctk = sys.modules['customtkinter']
mock_ctk.CTk = MockCTk
# For other widgets, MagicMock is fine as they are usually instantiated but not inherited from in Application (except maybe frames?)
# Application instantiates CTkFrame, CTkLabel, etc.
# But we need them to be usable.
def create_mock_widget(*args, **kwargs):
    m = MagicMock()
    m.winfo_reqheight.return_value = 50
    return m

mock_ctk.CTkFrame = create_mock_widget
mock_ctk.CTkLabel = create_mock_widget
mock_ctk.CTkButton = create_mock_widget
mock_ctk.CTkEntry = create_mock_widget
mock_ctk.StringVar = MagicMock()
mock_ctk.CTkImage = MockCTkImage

# Setup Image mock
mock_image = sys.modules['PIL.Image']
# Ensure "from PIL import Image" works
sys.modules['PIL'].Image = mock_image

# Mock utils to avoid import error
sys.modules['utils'] = MagicMock()
sys.modules['utils'].resource_path = lambda x: x

# Now import main
import main

class TestImageCaching(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        mock_image.open.reset_mock()

        # Patch os.path.exists to always return True for icons
        self.patcher = patch('os.path.exists')
        self.mock_exists = self.patcher.start()
        self.mock_exists.return_value = True

    def tearDown(self):
        self.patcher.stop()

    def test_update_page_caches_images(self):
        # We need to ensure scripts are populated
        # Since we mocked utils, get_path returns the path as is.
        # main.scripts should be a list of dicts.

        # Instantiate App
        app = main.Application()

        # Mock widgets that act as containers
        app.search_frame = MagicMock()
        app.main_frame = MagicMock()
        app.nav_frame = MagicMock()
        app.bottom_frame = MagicMock()

        # Mock geometry methods
        app.search_frame.winfo_reqheight.return_value = 50
        app.main_frame.winfo_reqheight.return_value = 500
        app.nav_frame.winfo_reqheight.return_value = 50
        app.bottom_frame.winfo_reqheight.return_value = 50

        # Verify we have scripts
        # script[0] is "AssistedGamelist" with an icon

        # First call
        app.update_page()
        first_call_count = mock_image.open.call_count

        # Second call
        app.update_page()
        second_call_count = mock_image.open.call_count

        # Assert we have some calls initially (assuming >0 scripts)
        self.assertGreater(first_call_count, 0, "Should open images on first load")

        # Assert calls did NOT increase (proving cache works)
        self.assertEqual(second_call_count, first_call_count, "Images should be cached and not re-opened")

if __name__ == '__main__':
    unittest.main()
