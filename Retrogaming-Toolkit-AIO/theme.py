import customtkinter as ctk
import os
import sys

# --- Sakura Night Palette ---
COLOR_ACCENT_PRIMARY = "#ff6699"  # Neon Sakura
COLOR_ACCENT_HOVER = "#ff3385"    # Hover Pink
COLOR_BG = "#151515"              # Deep Night (Sidebar, Main BG)
COLOR_CARD_BG = "#1e1e1e"         # Card Glass approximation (Solid for performance/tkinter limits)
COLOR_CARD_BORDER = "#444444"     # Card Border
COLOR_TEXT_MAIN = "#ffffff"       # Text White
COLOR_TEXT_SUB = "#aaaaaa"        # Text Grey
COLOR_GHOST_HOVER = "#333333"     # Ghost/Transparent Button Hover

# Status Colors
COLOR_SUCCESS = "#2ecc71"         # Green
COLOR_ERROR = "#e74c3c"           # Red
COLOR_WARNING = "#f39c12"         # Orange

# Fonts
FONT_FAMILY = "Roboto"

def get_font_main(size=13, weight="normal"):
    """Returns the standard font tuple/CTKFont."""
    return (FONT_FAMILY, size, weight)

def get_font_title(size=20, weight="bold"):
    """Returns the title font."""
    return (FONT_FAMILY, size, weight)

def apply_theme(app, title_prefix="Retrogaming Toolkit"):
    """
    Applies the base theme to a CTk window.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue") # Default backing, we override most things
    
    app.title(title_prefix)
    try:
        app.configure(fg_color=COLOR_BG)
    except Exception:
        pass # In case it's not a CTk window (but it should be)
    
    # Try setting icon
    try:
        if getattr(sys, 'frozen', False):
             base_path = sys._MEIPASS
        else:
             # Assumes running from 'Python - Module' root or similar
             # If we are in Retrogaming-Toolkit-AIO, we might need to go up if assets are in root
             # Based on list_dir:
             # root/
             #   assets/
             #   Retrogaming-Toolkit-AIO/
             #     theme.py
             
             # So from theme.py, we go up two levels to get to root assets
             current_dir = os.path.dirname(os.path.abspath(__file__))
             base_path = os.path.dirname(current_dir) # Python - Module

        icon_path = os.path.join(base_path, "assets", "Retrogaming-Toolkit-AIO.ico")
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
    except Exception:
        pass

class CTkToolTip:
    """
    Simple ToolTip for CustomTkinter.
    Shows text on hover.
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.id = None
        self.tip_window = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = None

    def show(self, event=None):
        if self.tip_window: return

        # Position logic
        try:
            x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except:
            return

        self.tip_window = ctk.CTkToplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        # Avoid stealing focus
        self.tip_window.wm_attributes("-topmost", True)

        # Styling matches theme
        label = ctk.CTkLabel(self.tip_window, text=self.text, text_color=COLOR_TEXT_MAIN,
                             fg_color="#2b2b2b", corner_radius=6,
                             font=("Roboto", 11))
        label.pack(padx=8, pady=4)

        # Windows specifics for border if possible, otherwise simple label
        try:
             # Add a thin border using a frame if needed, but label is fine for micro-ux
             pass
        except: pass

    def hide(self, event=None):
        self.unschedule()
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
