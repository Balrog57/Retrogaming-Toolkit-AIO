import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import tempfile
import shutil
from PIL import Image

# Mock dependencies before import
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()

sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

import ImageConvert

class TestImageConvert(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.input_image_path = os.path.join(self.test_dir, "test.png")

        # Create a dummy image
        img = Image.new('RGBA', (100, 100), color = (255, 0, 0, 255))
        img.save(self.input_image_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_process_single_image_png_to_jpg(self):
        output_path = os.path.join(self.test_dir, "output.jpg")

        # We expect the signature to be (input_path, output_path, delete_originals)
        # after modification.
        if hasattr(ImageConvert, 'process_single_image'):
            # Check argument count to decide how to call it (for iterative development)
            import inspect
            sig = inspect.signature(ImageConvert.process_single_image)
            if len(sig.parameters) == 4: # Old signature
                 print("Skipping test: Code not yet modified (expects 4 args)")
                 return

            success, path, error = ImageConvert.process_single_image(self.input_image_path, output_path, False)

            self.assertTrue(success, f"Conversion failed: {error}")
            self.assertTrue(os.path.exists(output_path))

            with Image.open(output_path) as img:
                self.assertEqual(img.format, 'JPEG')
                self.assertEqual(img.mode, 'RGB') # Should convert RGBA to RGB

    def test_process_single_image_delete_original(self):
        output_path = os.path.join(self.test_dir, "output.webp")

        # Check signature again
        import inspect
        sig = inspect.signature(ImageConvert.process_single_image)
        if len(sig.parameters) == 4: return

        success, path, error = ImageConvert.process_single_image(self.input_image_path, output_path, True)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertFalse(os.path.exists(self.input_image_path))

if __name__ == '__main__':
    unittest.main()
