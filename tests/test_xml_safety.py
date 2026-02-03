import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrogaming-Toolkit-AIO')))

# Mock GUI and other dependencies to allow headless import
mock_ctk = MagicMock()
mock_tk = MagicMock()
mock_theme = MagicMock()
mock_utils = MagicMock()

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['theme'] = mock_theme
sys.modules['utils'] = mock_utils
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['vlc'] = MagicMock()

class TestXMLSafety(unittest.TestCase):
    def test_collection_builder_uses_lxml(self):
        import CollectionBuilder
        import lxml.etree

        # Check if ET is lxml.etree (after refactor)
        # Before refactor this will fail (it will be xml.etree.ElementTree)
        self.assertEqual(CollectionBuilder.ET, lxml.etree, "CollectionBuilder should use lxml.etree")

    def test_systems_extractor_uses_lxml(self):
        import SystemsExtractor
        import lxml.etree
        self.assertEqual(SystemsExtractor.ET, lxml.etree, "SystemsExtractor should use lxml.etree")

    def test_gamelist_hyperlist_uses_lxml(self):
        import GamelistHyperlist
        import lxml.etree
        self.assertEqual(GamelistHyperlist.ET, lxml.etree, "GamelistHyperlist should use lxml.etree")

    def test_story_hyperlist_uses_lxml(self):
        import StoryHyperlist
        import lxml.etree
        self.assertEqual(StoryHyperlist.ET, lxml.etree, "StoryHyperlist should use lxml.etree")

if __name__ == '__main__':
    unittest.main()
