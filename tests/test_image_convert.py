import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
from PIL import Image

# Mock dependencies
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

# Add path
sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

# Import module
import ImageConvert

class TestImageConvert(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.input_path = os.path.join(self.test_dir.name, "test.png")
        self.output_path = os.path.join(self.test_dir.name, "test.jpg")

        # Create a test image
        img = Image.new('RGBA', (100, 100), color = (255, 0, 0, 255))
        img.save(self.input_path)

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('subprocess.run')
    def test_process_single_image_pillow(self, mock_subprocess):
        # We test the NEW signature: (input_path, output_path, delete_originals, output_fmt)

        try:
            # Note: We pass "jpeg" as output_fmt to trigger the RGBA->RGB logic
            success, _, error = ImageConvert.process_single_image(self.input_path, self.output_path, False, "jpeg")
        except TypeError:
            self.fail("Function signature mismatch. Did you update process_single_image?")

        if not success:
            self.fail(f"Conversion failed: {error}")

        self.assertTrue(os.path.exists(self.output_path), "Output file was not created")

        # Verify subprocess was NOT called
        mock_subprocess.assert_not_called()

        # Verify content (it should be a valid JPEG)
        with Image.open(self.output_path) as img:
            self.assertEqual(img.format, 'JPEG')
            self.assertEqual(img.mode, 'RGB') # Check RGBA -> RGB conversion

if __name__ == '__main__':
    unittest.main()
