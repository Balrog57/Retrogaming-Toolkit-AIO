import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from PIL import Image

# Mock ctk and tk
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()

# Import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

class TestIconCaching(unittest.TestCase):
    def setUp(self):
        # Patch load_favorites because Application.__init__ calls it
        patcher = patch('main.Application.load_favorites', return_value=set())
        patcher.start()
        self.addCleanup(patcher.stop)

        self.app = main.Application()
        # Mock script list
        self.app.filtered_scripts = [{"name": "Tool A", "description": "desc", "icon": "fake_icon.ico", "readme": "fake.txt"}]
        self.app.scripts_per_page = 10
        self.app.page = 0
        self.app.main_frame = MagicMock()
        
        # Mock widgets creation
        self.app.icon_cache = {}

    @patch('os.path.exists')
    @patch('PIL.Image.open')
    @patch('main.CTkImage')
    def test_icon_caching(self, mock_ctk_image, mock_img_open, mock_exists):
        mock_exists.return_value = True
        mock_img_open.return_value = MagicMock() # PIL Image mock
        
        # First call: Should load image
        self.app.update_page()
        self.assertEqual(mock_img_open.call_count, 1)
        self.assertIn("fake_icon.ico", self.app.icon_cache)
        
        # Second call: Should use cache (no new open)
        self.app.update_page()
        self.assertEqual(mock_img_open.call_count, 1) # Count remains 1

if __name__ == '__main__':
    unittest.main()
