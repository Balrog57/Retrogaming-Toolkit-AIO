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
    possible_paths = []
    
    # 1. Check AppData (User downloaded updates)
    app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', binary_name)
    possible_paths.append(app_data_path)

    if getattr(sys, 'frozen', False):
        # Frozen: Binaries are expected to be next to the executable OR in _internal
        base_path = os.path.dirname(sys.executable)
        possible_paths.append(os.path.join(base_path, binary_name))
        possible_paths.append(os.path.join(base_path, "_internal", binary_name))
    else:
        # Source: Binaries are in the root
        base_path = os.getcwd()
        possible_paths.append(os.path.join(base_path, binary_name))

    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    # Default return (even if not exists, so code can check generic path)
    if getattr(sys, 'frozen', False):
         return os.path.join(os.path.dirname(sys.executable), binary_name)
    return os.path.join(os.getcwd(), binary_name)

def is_frozen():
    return getattr(sys, 'frozen', False)
