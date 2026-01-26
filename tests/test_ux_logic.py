import unittest
from unittest.mock import MagicMock

class TestUXLogic(unittest.TestCase):
    def test_arrow_navigation_logic(self):
        """
        Verifies that scroll commands are issued only when focus is NOT in an Entry widget.
        """
        # Mock the Application instance
        app = MagicMock()

        # Define the logic we intend to implement in main.py
        # This mirrors the planned implementation of on_arrow_up/down
        def on_arrow_up(event):
            if event.widget.winfo_class() != "Entry":
                app.scroll_relative(120)

        def on_arrow_down(event):
            if event.widget.winfo_class() != "Entry":
                app.scroll_relative(-120)

        # Case 1: Focus is in an Entry widget (e.g., search bar)
        event_entry = MagicMock()
        event_entry.widget.winfo_class.return_value = "Entry"

        on_arrow_up(event_entry)
        app.scroll_relative.assert_not_called()

        on_arrow_down(event_entry)
        app.scroll_relative.assert_not_called()

        # Case 2: Focus is on something else (e.g., Canvas, Frame)
        event_other = MagicMock()
        event_other.widget.winfo_class.return_value = "Canvas"

        on_arrow_up(event_other)
        app.scroll_relative.assert_called_with(120)
        app.scroll_relative.reset_mock()

        on_arrow_down(event_other)
        app.scroll_relative.assert_called_with(-120)

if __name__ == "__main__":
    unittest.main()
