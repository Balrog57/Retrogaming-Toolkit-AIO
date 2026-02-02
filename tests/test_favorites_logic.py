import unittest
import json
import os
import tempfile
import shutil

class ApplicationWithFavorites:
    """Mock Application class with the Favorites logic we want to implement."""
    def __init__(self, app_data_dir):
        self.app_data_dir = app_data_dir
        self.favorites = self.load_favorites()
        self.scripts = [
            {"name": "ToolA", "category": "Cat1"},
            {"name": "ToolB", "category": "Cat1"},
            {"name": "ToolC", "category": "Cat2"}
        ]
        self.filtered_scripts = []

    def load_favorites(self):
        """Charge les favoris depuis le JSON."""
        fav_file = os.path.join(self.app_data_dir, "favorites.json")
        if os.path.exists(fav_file):
            try:
                with open(fav_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_favorites(self):
        """Sauvegarde les favoris."""
        fav_file = os.path.join(self.app_data_dir, "favorites.json")
        try:
            with open(fav_file, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f)
        except Exception:
            pass

    def toggle_favorite(self, script_name):
        """Basculer l'état favori d'un script."""
        if script_name in self.favorites:
            self.favorites.remove(script_name)
        else:
            self.favorites.append(script_name)
        self.save_favorites()
        self.filter_and_display() # Simulate refresh

    def filter_and_display(self):
        """Simulate sorting logic."""
        # Logic to be implemented in main.py
        filtered = list(self.scripts)

        # Sort: Favorites first, then Name
        # x["name"] not in self.favorites returns True (1) for non-favorites, False (0) for favorites.
        # Sort order (0, Name) -> Favorites first.
        filtered.sort(key=lambda x: (x["name"] not in self.favorites, x["name"]))
        self.filtered_scripts = filtered


class TestFavoritesLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app = ApplicationWithFavorites(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_empty(self):
        self.assertEqual(self.app.favorites, [])

    def test_toggle_save_load(self):
        self.app.toggle_favorite("ToolA")
        self.assertIn("ToolA", self.app.favorites)

        # Check file
        fav_file = os.path.join(self.test_dir, "favorites.json")
        self.assertTrue(os.path.exists(fav_file))

        # Create new app to test persistence
        app2 = ApplicationWithFavorites(self.test_dir)
        self.assertIn("ToolA", app2.favorites)

        # Toggle off
        self.app.toggle_favorite("ToolA")
        self.assertNotIn("ToolA", self.app.favorites)

        app3 = ApplicationWithFavorites(self.test_dir)
        self.assertNotIn("ToolA", app3.favorites)

    def test_sorting(self):
        # Default: A, B, C
        self.app.filter_and_display()
        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertEqual(names, ["ToolA", "ToolB", "ToolC"])

        # Favorite ToolB -> B, A, C
        self.app.toggle_favorite("ToolB")
        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertEqual(names, ["ToolB", "ToolA", "ToolC"])

        # Favorite ToolC -> B, C, A (Alphabetical among favorites)
        self.app.toggle_favorite("ToolC")
        names = [s["name"] for s in self.app.filtered_scripts]
        self.assertEqual(names, ["ToolB", "ToolC", "ToolA"])

if __name__ == '__main__':
    unittest.main()
