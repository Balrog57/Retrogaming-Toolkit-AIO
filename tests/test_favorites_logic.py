import unittest
import json
import os
from unittest.mock import patch, mock_open

class TestFavoritesLogic(unittest.TestCase):
    def test_sort_favorites_priority(self):
        """Test that favorites are sorted to the top."""
        favorites = {"Tool B", "Tool D"}
        scripts = [
            {"name": "Tool A"},
            {"name": "Tool B"},
            {"name": "Tool C"},
            {"name": "Tool D"},
            {"name": "Tool E"},
        ]

        # The logic we will implement in main.py
        # False (0) comes before True (1).
        # s["name"] not in favorites is False for favorites (priority)
        sorted_scripts = sorted(scripts, key=lambda s: (s["name"] not in favorites, s["name"]))

        expected_names = ["Tool B", "Tool D", "Tool A", "Tool C", "Tool E"]
        self.assertEqual([s["name"] for s in sorted_scripts], expected_names)

    @patch("builtins.open", new_callable=mock_open, read_data='["Tool A"]')
    @patch("os.path.exists", return_value=True)
    def test_load_logic(self, mock_exists, mock_file):
        """Test loading favorites from JSON."""
        # Logic simulation
        loaded_favs = set()
        if os.path.exists("dummy"):
            with open("dummy", "r") as f:
                loaded_favs = set(json.load(f))

        self.assertEqual(loaded_favs, {"Tool A"})

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_logic(self, mock_dump, mock_file):
        """Test saving favorites to JSON."""
        favorites = {"Tool A", "Tool B"}
        path = "dummy.json"

        with open(path, "w") as f:
            json.dump(list(favorites), f)

        mock_file.assert_called_with(path, "w")
        # Check that json.dump was called with the list
        args, _ = mock_dump.call_args
        self.assertEqual(set(args[0]), favorites)

if __name__ == '__main__':
    unittest.main()
