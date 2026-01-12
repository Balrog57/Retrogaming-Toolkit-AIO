import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # PyInstaller --onedir
        # The data files are located relative to the executable
        # If we use --onefile, they are in sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
             base_path = sys._MEIPASS
        else:
             base_path = os.path.dirname(sys.executable)
    else:
        # Dev mode: assumes running from root
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_binary_path(binary_name):
    """ Get path to external binary """
    if getattr(sys, 'frozen', False):
        # Frozen: Binaries are expected to be next to the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Source: Binaries are in the root
        # utils.py is in Retrogaming-Toolkit-AIO/
        # We assume CWD is the root of the repo (where main.py is)
        base_path = os.getcwd()

    return os.path.join(base_path, binary_name)

def is_frozen():
    return getattr(sys, 'frozen', False)
