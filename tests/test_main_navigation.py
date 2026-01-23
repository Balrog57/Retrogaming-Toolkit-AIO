import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock libraries before importing main
mock_ctk = MagicMock()
sys.modules["customtkinter"] = mock_ctk
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["webbrowser"] = MagicMock()

# Mock utils if it exists/imported
sys.modules["utils"] = MagicMock()

# Need to handle CTk inheritance
class MockCTk:
    def __init__(self, **kwargs):
        pass
    def title(self, t): pass
    def geometry(self, g): pass
    def iconbitmap(self, p): pass
    def bind(self, k, c): pass
    def after(self, t, c): pass
    def mainloop(self): pass
    def update_idletasks(self): pass
    def winfo_children(self): return []
    def winfo_reqheight(self): return 100

mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MagicMock()
mock_ctk.CTkLabel = MagicMock()
mock_ctk.CTkButton = MagicMock()
mock_ctk.CTkEntry = MagicMock()
mock_ctk.StringVar = MagicMock()

# Import the module under test
import main

class TestNavigation(unittest.TestCase):
    def setUp(self):
        # Patch Application methods to avoid side effects and allow verification
        self.original_bind = main.Application.bind
        self.bind_calls = {}

        # Capture bindings
        def mock_bind(self_app, key, command):
            self.bind_calls[key] = command

        main.Application.bind = mock_bind

        # Mock other methods
        main.Application.update_page = MagicMock()
        main.Application.previous_page = MagicMock()
        main.Application.next_page = MagicMock()
        main.Application.load_favorites = MagicMock(return_value=set())
        main.Application.check_updates = MagicMock()

        # Instantiate
        self.app = main.Application()

    def tearDown(self):
        main.Application.bind = self.original_bind

    def test_left_arrow_on_entry_should_not_navigate(self):
        """Test that Left arrow does NOT trigger previous_page when focus is on an Entry"""
        # Get the callback for Left arrow
        callback = self.bind_calls.get("<Left>")
        self.assertIsNotNone(callback, "Left arrow binding not found")

        # Create a mock event from an Entry widget
        mock_event = MagicMock()
        mock_event.widget.winfo_class.return_value = "Entry"

        # Call the callback
        callback(mock_event)

        # Assert previous_page was NOT called
        self.app.previous_page.assert_not_called()

    def test_left_arrow_on_other_should_navigate(self):
        """Test that Left arrow triggers previous_page when focus is NOT on an Entry"""
        callback = self.bind_calls.get("<Left>")
        self.assertIsNotNone(callback)

        # Create a mock event from a Button (or anything else)
        mock_event = MagicMock()
        mock_event.widget.winfo_class.return_value = "Button"

        # Call the callback
        callback(mock_event)

        # Assert previous_page WAS called
        self.app.previous_page.assert_called_once()

    def test_right_arrow_on_entry_should_not_navigate(self):
        """Test that Right arrow does NOT trigger next_page when focus is on an Entry"""
        callback = self.bind_calls.get("<Right>")
        self.assertIsNotNone(callback, "Right arrow binding not found")

        mock_event = MagicMock()
        mock_event.widget.winfo_class.return_value = "Entry"

        callback(mock_event)

        self.app.next_page.assert_not_called()

    def test_right_arrow_on_other_should_navigate(self):
        """Test that Right arrow triggers next_page when focus is NOT on an Entry"""
        callback = self.bind_calls.get("<Right>")
        self.assertIsNotNone(callback)

        mock_event = MagicMock()
        mock_event.widget.winfo_class.return_value = "Frame"

        callback(mock_event)

        self.app.next_page.assert_called_once()

if __name__ == "__main__":
    unittest.main()
