import sys
import os
import unittest
from unittest.mock import MagicMock
import fitz
import time
import zipfile

# Setup paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'Retrogaming-Toolkit-AIO'))

# Mock GUI modules BEFORE importing CBZKiller
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()

# Import the module
try:
    from CBZKiller import process_pdf_to_cbz
except ImportError:
    # Fallback if running from root without adding subfolder to path automatically
    from Retrogaming_Toolkit_AIO.CBZKiller import process_pdf_to_cbz

class TestCBZKiller(unittest.TestCase):
    def setUp(self):
        self.test_pdf = "test_doc.pdf"
        self.output_cbz = "output.cbz"

        # Create a dummy PDF with 5 pages
        doc = fitz.open()
        for i in range(5):
            page = doc.new_page()
            page.insert_text((50, 50), f"Page {i+1}", fontsize=50)
            # Add some content to make it non-trivial
            page.draw_rect((100, 100, 200, 200), color=(0, 0, 1))
        doc.save(self.test_pdf)
        doc.close()

    def tearDown(self):
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)
        if os.path.exists(self.output_cbz):
            os.remove(self.output_cbz)

    def test_process_pdf_to_cbz(self):
        print("\nStarting CBZ processing test...")
        start_time = time.time()
        success, msg = process_pdf_to_cbz(self.test_pdf, self.output_cbz)
        end_time = time.time()

        print(f"Execution time: {end_time - start_time:.4f}s")

        self.assertTrue(success, f"Processing failed: {msg}")
        self.assertTrue(os.path.exists(self.output_cbz))

        with zipfile.ZipFile(self.output_cbz, 'r') as z:
            files = z.namelist()
            self.assertEqual(len(files), 5)
            for i in range(5):
                self.assertIn(f"p_{i+1:03d}.jpg", files)
                # Verify file size is not zero
                info = z.getinfo(f"p_{i+1:03d}.jpg")
                self.assertGreater(info.file_size, 0)

if __name__ == '__main__':
    unittest.main()
