import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock modules BEFORE importing main
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['radio'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['theme'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Setup customtkinter mocks
import customtkinter as ctk

# Mock CTk class to support inheritance
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def geometry(self, *args): pass
    def resizable(self, *args): pass
    def title(self, *args): pass
    def iconbitmap(self, *args): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def bind(self, *args): pass
    def protocol(self, *args): pass
    def after(self, ms, func, *args): return "job_id"
    def after_cancel(self, *args): pass
    def winfo_width(self): return 1000
    def update_idletasks(self): pass
    def lower(self, *args): pass
    def mainloop(self): pass
    def wm_attributes(self, *args): pass
    def wm_withdraw(self): pass
    def lift(self): pass

ctk.CTk = MockCTk
ctk.CTkFrame = MagicMock()
ctk.CTkLabel = MagicMock()
ctk.CTkButton = MagicMock()
ctk.CTkEntry = MagicMock()
ctk.CTkScrollbar = MagicMock()
ctk.CTkImage = MagicMock()
ctk.StringVar = MagicMock()
ctk.CTkOptionMenu = MagicMock()
ctk.CTkToplevel = MockCTk

# Configure CTkCanvas mock
mock_canvas_instance = MagicMock()
mock_canvas_instance.winfo_width.return_value = 1000
# Also need to handle create_image, create_text, create_window, create_rectangle without crashing
ctk.CTkCanvas = MagicMock(return_value=mock_canvas_instance)


# Import main
with patch('os.getenv', return_value='/tmp'):
    import main

class TestMemoryLeak(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        main.ctk.CTkButton.reset_mock()

    def test_widget_cleanup(self):
        # Initialize app
        # This will call __init__ -> filter_and_display -> canvas.winfo_width()
        app = main.Application()

        # Override canvas again just in case, but the one from __init__ is what matters initially
        # app.canvas is already mock_canvas_instance

        # Track destroyed widgets
        destroyed_widgets = []

        # Custom side effect for CTkButton to track instances
        def create_mock_button(*args, **kwargs):
            btn = MagicMock()
            def destroy_side_effect():
                destroyed_widgets.append(btn)
            btn.destroy.side_effect = destroy_side_effect
            return btn

        main.ctk.CTkButton.side_effect = create_mock_button

        # First Pass
        print("Running first pass...")
        app.filter_and_display()

        # Second Pass
        print("Running second pass...")
        app.filter_and_display()

        # Verification
        if hasattr(app, 'card_widgets'):
            print(f"Fix detected. Destroyed widgets count: {len(destroyed_widgets)}")
            self.assertTrue(len(destroyed_widgets) > 0, "Widgets should be destroyed with the fix")
        else:
            print("No fix detected.")
            self.assertEqual(len(destroyed_widgets), 0, "Widgets are NOT destroyed without the fix")

if __name__ == '__main__':
    unittest.main()
