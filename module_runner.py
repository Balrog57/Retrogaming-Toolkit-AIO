import os
import sys
import logging
import importlib
import traceback
import tempfile
from PIL import Image, ImageTk
import customtkinter as ctk

def run_module_process(module_name, icon_path):
    """Fonction exécutée dans le processus enfant pour lancer le module."""
    app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit')
    if not os.path.exists(app_data_dir):
        try:
            os.makedirs(app_data_dir)
        except OSError:
            app_data_dir = tempfile.gettempdir()
    log_file = os.path.join(app_data_dir, 'retrogaming_toolkit.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )
    logger = logging.getLogger(__name__)

    # Ensure sys.path is correct in child process
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        toolkit_path = os.path.join(base_path, "Retrogaming-Toolkit-AIO")
        if toolkit_path not in sys.path:
            sys.path.append(toolkit_path)
    else:
        # Not frozen, source mode. 
        # module_runner is in root.
        # We need to add Retrogaming-Toolkit-AIO to sys.path
        root_dir = os.path.dirname(os.path.abspath(__file__))
        toolkit_path = os.path.join(root_dir, "Retrogaming-Toolkit-AIO")
        if toolkit_path not in sys.path:
            sys.path.append(toolkit_path)

    try:
        logger.info(f"Child process started for module: {module_name}")
        
        # --- Monkeypatch CTk to inject Icon ---
        if icon_path:
            icon_path = os.path.abspath(icon_path) # Force absolute
            
        if icon_path and os.path.exists(icon_path):
            OriginalCTk = ctk.CTk
            class IconizedCTk(OriginalCTk):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.after(10, self.set_icon_safe)

                def set_icon_safe(self):
                    try:
                        # Apply icon
                        if icon_path.lower().endswith(".ico"):
                            self.wm_iconbitmap(icon_path)
                        else:
                            # Try PNG/Image
                            icon_img = Image.open(icon_path)
                            self.iconphoto(False, ImageTk.PhotoImage(icon_img))
                        logger.info(f"Icon applied from {icon_path}")
                    except Exception as e:
                        logger.error(f"Failed to set icon in child process: {e}")
            
            # Apply the patch
            ctk.CTk = IconizedCTk
        
        # Import dynamique du module
        module = importlib.import_module(module_name)
        # Exécution de la fonction main() du module
        if hasattr(module, 'main'):
            module.main()
        else:
            logger.error(f"Erreur : Le module {module_name} n'a pas de fonction main()")
    except Exception as e:
        logger.error(f"Erreur dans le processus enfant pour {module_name}: {e}")
        logger.error(traceback.format_exc())
