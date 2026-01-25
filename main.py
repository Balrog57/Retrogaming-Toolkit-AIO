import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import logging
import subprocess
import multiprocessing
import importlib
import tempfile
import zipfile
import traceback
from PIL import Image, ImageTk
from customtkinter import CTkImage
import requests
import urllib.request
import webbrowser
import threading
import json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

# Fix sys.path for bundled modules and data directory
if getattr(sys, 'frozen', False):
    # In frozen mode, we are in sys._MEIPASS
    # We add Retrogaming-Toolkit-AIO to sys.path to allow loading scripts that might be 
    # in the data directory (fallback or user-modified versions), 
    # even though bundled modules are already in the PYZ.
    base_path = sys._MEIPASS
    toolkit_path = os.path.join(base_path, "Retrogaming-Toolkit-AIO")
    if toolkit_path not in sys.path:
        sys.path.append(toolkit_path)
    # Also add base path just in case
    if base_path not in sys.path:
        sys.path.append(base_path)
else:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Retrogaming-Toolkit-AIO"))

try:
    import utils
    import theme
except ImportError:
    # Si utils n'est pas trouvé (devrait pas arriver si sys.path est correct)
    # logger might not be defined yet
    logger = logging.getLogger(__name__) # Safe to call
    logging.basicConfig() # Ensure basic logging
    logger.error("Impossible d'importer utils.py ou theme.py")
    utils = None
    theme = None

VERSION = "3.0.0"

# Configuration du logging
local_app_data = os.getenv('LOCALAPPDATA')
if not local_app_data:
    local_app_data = os.path.expanduser("~") # Fallback to user home if LOCALAPPDATA is missing

app_data_dir = os.path.join(local_app_data, 'RetrogamingToolkit')
if not os.path.exists(app_data_dir):
    try:
        os.makedirs(app_data_dir)
    except OSError:
        # Fallback to temp dir if permissions fail completely
        app_data_dir = tempfile.gettempdir()

log_file = os.path.join(app_data_dir, 'retrogaming_toolkit.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)
logger = logging.getLogger(__name__)

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_path(p):
    if utils:
        return utils.resource_path(p)
    return p

# Liste des scripts avec descriptions, chemins des icônes et fichiers "Lisez-moi"
scripts = [
    {"name": "AssistedGamelist", "description": "(Retrobat) Gère et enrichit les listes de jeux XML.", "icon": get_path(os.path.join("assets", "AssistedGamelist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "AssistedGamelist.txt"))},
    {"name": "BGBackup", "description": "(Retrobat) Sauvegarde les fichiers gamelist.xml.", "icon": get_path(os.path.join("assets", "BGBackup.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "BGBackup.txt"))},
    {"name": "CHDManager", "description": "Convertit et vérifie les fichiers CHD (MAME).", "icon": get_path(os.path.join("assets", "CHDManager.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CHDManager.txt"))},
    {"name": "CollectionBuilder", "description": "(Core) Crée des collections de jeux par mots-clés.", "icon": get_path(os.path.join("assets", "CollectionBuilder.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CollectionBuilder.txt"))},
    {"name": "CollectionExtractor", "description": "(Core) Extrait des collections de jeux spécifiques.", "icon": get_path(os.path.join("assets", "CollectionExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CollectionExtractor.txt"))},
    {"name": "LongPaths", "description": "Active les chemins longs sur Windows (Registry).", "icon": get_path(os.path.join("assets", "LongPaths.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "LongPaths.txt"))},
    {"name": "FolderToTxt", "description": "Crée des fichiers TXT à partir des noms de dossiers.", "icon": get_path(os.path.join("assets", "FolderToTxt.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderToTxt.txt"))},
    {"name": "FolderToZip", "description": "Compresse des fichiers de jeux en ZIP.", "icon": get_path(os.path.join("assets", "FolderToZip.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderToZip.txt"))},
    {"name": "GameBatch", "description": "Génère des fichiers batch pour lancer des jeux PC.", "icon": get_path(os.path.join("assets", "GameBatch.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GameBatch.txt"))},
    {"name": "EmptyGen", "description": "Génère des fichiers vides dans des sous-dossiers.", "icon": get_path(os.path.join("assets", "EmptyGen.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "EmptyGen.txt"))},
    {"name": "GameRemoval", "description": "(Core) Supprime des jeux et leurs médias associés.", "icon": get_path(os.path.join("assets", "GameRemoval.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GameRemoval.txt"))},
    {"name": "GamelistHyperlist", "description": "(Core) Convertit gamelist.xml en hyperlist.xml.", "icon": get_path(os.path.join("assets", "GamelistHyperlist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GamelistHyperlist.txt"))},
    {"name": "HyperlistGamelist", "description": "(Retrobat) Convertit hyperlist.xml en gamelist.xml.", "icon": get_path(os.path.join("assets", "HyperlistGamelist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "HyperlistGamelist.txt"))},
    {"name": "InstallDeps", "description": "Installe les dépendances système (DirectX, VC++).", "icon": get_path(os.path.join("assets", "InstallDeps.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "InstallDeps.txt"))},
    {"name": "ListFilesSimple", "description": "Liste les fichiers d'un répertoire (Simple).", "icon": get_path(os.path.join("assets", "ListFilesSimple.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ListFilesSimple.txt"))},
    {"name": "ListFilesWin", "description": "Liste fichiers et dossiers (Détails Windows).", "icon": get_path(os.path.join("assets", "ListFilesWin.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ListFilesWin.txt"))},
    {"name": "MaxCSO", "description": "Compresse des fichiers ISO en CSO (MaxCSO).", "icon": get_path(os.path.join("assets", "MaxCSO.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "MaxCSO.txt"))},
    {"name": "MediaOrphans", "description": "(Core) Détecte et déplace les médias orphelins.", "icon": get_path(os.path.join("assets", "MediaOrphans.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "MediaOrphans.txt"))},
    {"name": "FolderCleaner", "description": "Supprime les dossiers vides récursivement.", "icon": get_path(os.path.join("assets", "FolderCleaner.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderCleaner.txt"))},
    {"name": "StoryHyperlist", "description": "(Core) Intègre des story dans des hyperlist.xml.", "icon": get_path(os.path.join("assets", "StoryHyperlist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "StoryHyperlist.txt"))},
    {"name": "DolphinConvert", "description": "Convertit entre formats RVZ et ISO (Dolphin).", "icon": get_path(os.path.join("assets", "DolphinConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "DolphinConvert.txt"))},
    {"name": "StoryCleaner", "description": "Nettoie les fichiers texte non ASCII.", "icon": get_path(os.path.join("assets", "StoryCleaner.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "StoryCleaner.txt"))},
    {"name": "M3UCreator", "description": "Crée des playlists M3U pour le multi-disque.", "icon": get_path(os.path.join("assets", "M3UCreator.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "M3UCreator.txt"))},
    {"name": "CoverExtractor", "description": "Extrait la première image des CBZ, CBR, PDF.", "icon": get_path(os.path.join("assets", "CoverExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CoverExtractor.txt"))},
    {"name": "CBZKiller", "description": "Convertisseur PDF/CBR vers CBZ.", "icon": get_path(os.path.join("assets", "CBZKiller.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CBZKiller.txt"))},
    {"name": "VideoConvert", "description": "Convertit/Rogne des vidéos par lot (FFmpeg).", "icon": get_path(os.path.join("assets", "VideoConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "VideoConvert.txt"))},
    {"name": "YTDownloader", "description": "Télécharge des vidéos/audio Youtube (yt-dlp).", "icon": get_path(os.path.join("assets", "YTDownloader.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "YTDownloader.txt"))},
    {"name": "ImageConvert", "description": "Convertit des images par lot.", "icon": get_path(os.path.join("assets", "ImageConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ImageConvert.txt"))},
    {"name": "SystemsExtractor", "description": "Extrait les systèmes uniques (EmulationStation).", "icon": get_path(os.path.join("assets", "SystemsExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "SystemsExtractor.txt"))},
    {"name": "UniversalRomCleaner", "description": "Nettoie et trie vos ROMs (1G1R, Régions).", "icon": get_path(os.path.join("assets", "UniversalRomCleaner.png")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "UniversalRomCleaner.txt"))},
]

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

    # Ensure sys.path is correct in child process for frozen imports
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        toolkit_path = os.path.join(base_path, "Retrogaming-Toolkit-AIO")
        if toolkit_path not in sys.path:
            sys.path.append(toolkit_path)

    try:
        logger.info(f"Child process started for module: {module_name}")
        
        # --- Monkeypatch CTk to inject Icon ---
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

def lancer_module(module_name):
    """Charge et exécute un module Python dans un processus séparé via multiprocessing."""
    try:
        logger.info(f"Lancement du module: {module_name}")
        
        # Trouver l'icône correspondante
        icon_path = None
        for s in scripts:
            if s["name"] == module_name:
                icon_path = s["icon"]
                break
        
        # Fallback icon determination
        if not icon_path:
             icon_path = get_path(os.path.join("assets", f"{module_name}.ico"))

        # On lance le module dans un nouveau processus
        # Cela permet d'isoler les boucles principales Tkinter
        p = multiprocessing.Process(target=run_module_process, args=(module_name, icon_path))
        p.daemon = True # Kill child process if main process exits
        p.start()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du module {module_name}: {str(e)}")
        messagebox.showerror("Erreur", f"Erreur lors de l'exécution du module {module_name}: {str(e)}")

def open_readme(readme_file):
    """Ouvre et affiche le contenu d'un fichier Lisez-moi."""
    try:
        if os.path.exists(readme_file):
            with open(readme_file, "r", encoding="utf-8") as file:
                content = file.read()
            # Utiliser messagebox directement si le custom modal n'est pas dispo dans ce scope,
            # mais ici on est dans main.py, donc on a accès à ReadmeWindow si on le déplace ou le rend global?
            # En réalité, on appelle Application.open_custom_readme depuis l'instance. 
            # Cette fonction open_readme est utilisée par legacy ou buttons ? 
            # Dans Application.create_card, on utilise self.open_custom_readme.
            # Cette fonction globale reste pour compatibilité ou fallback.
            messagebox.showinfo("Lisez-moi", content)
        else:
            messagebox.showwarning("Lisez-moi", f"Le fichier {readme_file} n'existe pas.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier {readme_file} : {e}")

def check_for_updates():
    """Vérifie si une nouvelle version est disponible sur GitHub."""
    try:
        url = "https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest"
        response = requests.get(url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release["tag_name"]

        # Fonction pour convertir une version en tuple de nombres
        def version_to_tuple(version):
            return tuple(map(int, version.lstrip('v').split('.')))

        # Convertir les versions en tuples de nombres
        current_version_tuple = version_to_tuple(VERSION)
        latest_version_tuple = version_to_tuple(latest_version)

        # Comparer les versions
        if latest_version_tuple > current_version_tuple:
            return True, latest_version
        else:
            return False, latest_version

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des mises à jour : {e}")
        return False, VERSION

def download_and_run_installer(download_url):
    """Télécharge et exécute l'installateur."""
    try:
        # Créer un fichier temporaire pour l'installateur
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp_file:
            installer_path = tmp_file.name

        # Télécharger
        logger.info(f"Téléchargement de la mise à jour depuis {download_url}...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info("Téléchargement terminé. Lancement de l'installateur...")

        # Lancer l'installateur et fermer l'application actuelle
        subprocess.Popen([installer_path, "/SILENT"]) # Ou sans /SILENT pour voir l'UI
        sys.exit(0)

    except Exception as e:
        messagebox.showerror("Erreur Mise à jour", f"Erreur lors du téléchargement : {e}")
        logger.error(f"Erreur update: {e}")

def launch_update():
    """Lance le processus de mise à jour."""
    if utils and utils.is_frozen():
        # Mode EXE : Télécharger l'installateur
        try:
            url = "https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest"
            response = requests.get(url)
            data = response.json()
            assets = data.get("assets", [])

            # Chercher un fichier .exe dans les assets (Setup.exe ou autre)
            installer_url = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    installer_url = asset["browser_download_url"]
                    break

            if installer_url:
                if messagebox.askyesno("Mise à jour", "Une nouvelle version est disponible. Voulez-vous la télécharger et l'installer maintenant ?"):
                    download_and_run_installer(installer_url)
            else:
                messagebox.showerror("Erreur", "Aucun fichier d'installation trouvé dans la dernière release.")

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")

    else:
        # Mode Source : Utiliser update.bat (legacy)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            update_script = os.path.join(current_dir, "update.bat")
            if os.path.exists(update_script):
                logger.info(f"Fichier update.bat trouvé : {update_script}")
                subprocess.Popen(["start", "cmd.exe", "/c", update_script], shell=True)
                logger.info("update.bat lancé dans une nouvelle fenêtre")
            else:
                logger.error("Le fichier update.bat n'existe pas.")
                messagebox.showerror("Erreur", "Le fichier update.bat n'existe pas.")
        except Exception as e:
            logger.error(f"Erreur lors du lancement de la mise à jour : {e}")
            messagebox.showerror("Erreur", f"Erreur lors du lancement de la mise à jour : {e}")

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lanceur de Modules - Retrogaming-Toolkit-AIO")
        try:
            icon_path = get_path(os.path.join("assets", "Retrogaming-Toolkit-AIO.ico"))
            self.iconbitmap(icon_path)
        except Exception as e:
            logger.error(f"Erreur lors de la définition de l'icône de l'application : {e}")
        self.geometry("800x400")  # Taille initiale

        self.scripts = scripts
        self.filtered_scripts = list(self.scripts)  # Initialiser avec tous les scripts
        self.page = 0
        self.scripts_per_page = 10
        self.min_window_height = 400
        self.preferred_width = 800

        self.icon_cache = {}
        self.favorites = self.load_favorites()

        # Barre de recherche
        self.search_frame = ctk.CTkFrame(self, corner_radius=10)
        self.search_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.search_label = ctk.CTkLabel(self.search_frame, text="Rechercher :", font=("Arial", 14))
        self.search_label.pack(side="left", padx=10)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_scripts)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, width=300, placeholder_text="Nom ou description... (Ctrl+F)")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.clear_button = ctk.CTkButton(self.search_frame, text="✕", width=25, height=25, 
                                          command=self.clear_search, 
                                          fg_color="transparent", hover_color=("gray70", "gray30"), text_color="gray")


# Mapping des scripts par catégorie (Nouvelle classification)
# Mapping des scripts par catégorie (Nouvelle classification complète)
# Mapping des scripts par catégorie (Refonte Complète)
SCRIPT_CATEGORIES = {
    # Gestion des Jeux & ROMs
    "CHDManager": "Gestion des Jeux & ROMs",
    "MaxCSO": "Gestion des Jeux & ROMs",
    "DolphinConvert": "Gestion des Jeux & ROMs",
    "FolderToZip": "Gestion des Jeux & ROMs",
    "GameBatch": "Gestion des Jeux & ROMs",
    "GameRemoval": "Gestion des Jeux & ROMs",
    "UniversalRomCleaner": "Gestion des Jeux & ROMs",

    # Métadonnées & Gamelists
    "AssistedGamelist": "Métadonnées & Gamelists",
    "GamelistHyperlist": "Métadonnées & Gamelists",
    "HyperlistGamelist": "Métadonnées & Gamelists",
    "BGBackup": "Métadonnées & Gamelists",
    "StoryHyperlist": "Métadonnées & Gamelists",
    "StoryCleaner": "Métadonnées & Gamelists",
    "SystemsExtractor": "Métadonnées & Gamelists",

    # Multimédia & Artworks
    "YTDownloader": "Multimédia & Artworks",
    "VideoConvert": "Multimédia & Artworks",
    "ImageConvert": "Multimédia & Artworks",
    "CoverExtractor": "Multimédia & Artworks",
    "MediaOrphans": "Multimédia & Artworks",
    "CBZKiller": "Multimédia & Artworks",

    # Organisation & Collections
    "CollectionBuilder": "Organisation & Collections",
    "CollectionExtractor": "Organisation & Collections",
    "M3UCreator": "Organisation & Collections",
    "FolderCleaner": "Organisation & Collections",
    "FolderToTxt": "Organisation & Collections",
    "EmptyGen": "Organisation & Collections",

    # Maintenance Système
    "LongPaths": "Maintenance Système",
    "InstallDeps": "Maintenance Système",
    "ListFilesSimple": "Maintenance Système",
    "ListFilesWin": "Maintenance Système",
}

class ReadmeWindow(ctk.CTkToplevel):
    def __init__(self, parent, title, content, fg_color, text_color, accent_color, icon_path=None):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=fg_color)
        
        # Close Button - Pack FIRST to ensure it reserves space at the bottom
        close_btn = ctk.CTkButton(self, text="Fermer", fg_color="transparent", 
                                border_width=1, border_color=accent_color,
                                text_color=accent_color, hover_color="#333",
                                command=self.destroy)
        close_btn.pack(side="bottom", pady=20)

        # Estimate height based on character count (approximate)
        # 600px width -> approx 90 chars per line
        lines = content.count('\n') + (len(content) / 90) 
        
        # Height calculation
        # Base = 150 (padding + button)
        # Line height = 20
        calculated_height = int(lines * 20) + 150
        
        # Constraints for 1080p screen comfort
        max_h = 800 
        min_h = 200
        
        height = min(max_h, max(min_h, calculated_height))
        
        self.geometry(f"600x{height}")
        self.minsize(300, 200)

        # Content (Scrollable Text) - Pack SECOND to fill remaining space
        textbox = ctk.CTkTextbox(self, text_color=text_color, fg_color="transparent", 
                               wrap="word", font=("Roboto", 13))
        # Keep button at bottom visible
        textbox.pack(side="top", fill="both", expand=True, padx=30, pady=(25, 10))
        textbox.insert("0.0", content)
        textbox.configure(state="disabled") # Read-only
        
        # Set Icon - Use delay to ensure window is created
        if icon_path and os.path.exists(icon_path):
            self.after(200, lambda: self._apply_icon(icon_path))

        self.focus_set()
        self.grab_set() # Modal

    def _apply_icon(self, path):
         try:
            path = os.path.abspath(path)
            # Try bitmap first if ico
            if path.lower().endswith(".ico"):
                try:
                    self.wm_iconbitmap(path)
                except:
                    # Fallback to photoimage if bitmap fails
                    img = Image.open(path)
                    self.icon_ref = ImageTk.PhotoImage(img)
                    self.wm_iconphoto(False, self.icon_ref)
            else:
                img = Image.open(path)
                self.icon_ref = ImageTk.PhotoImage(img) # Keep reference!
                self.wm_iconphoto(False, self.icon_ref)
         except Exception as e:
             logger.error(f"Failed to apply icon to readme: {e}")

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Theme Application ---
        if theme:
            theme.apply_theme(self, "Retrogaming Toolkit - Sakura Night Edition")
            self.COLOR_ACCENT_PRIMARY = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_ACCENT_HOVER = theme.COLOR_ACCENT_HOVER
            self.COLOR_SIDEBAR_BG = theme.COLOR_BG
            self.COLOR_CONTENT_BG = "transparent"
            self.COLOR_SIDEBAR_HOVER = theme.COLOR_GHOST_HOVER
            self.COLOR_CARD_BORDER = theme.COLOR_CARD_BORDER
            self.COLOR_TEXT_MAIN = theme.COLOR_TEXT_MAIN
            self.COLOR_TEXT_SUB = theme.COLOR_TEXT_SUB
            self.app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Retrogaming-Toolkit-AIO.ico")
        else:
             # Fallback if theme import fails
            self.title("Retrogaming Toolkit - Sakura Night Edition")
            self.COLOR_ACCENT_PRIMARY = "#ff6699"
            self.COLOR_ACCENT_HOVER = "#ff3385"
            self.COLOR_SIDEBAR_BG = "#151515"
            self.COLOR_CONTENT_BG = "transparent"
            self.COLOR_SIDEBAR_HOVER = "#2a2a2a"
            self.COLOR_CARD_BORDER = "#444"
            self.COLOR_TEXT_MAIN = "#ffffff"
            self.COLOR_TEXT_SUB = "#b0bec5"
            self.app_icon_path = None

        self.geometry("1100x720")
        self.resizable(False, False) 

        # --- Données ---
        self.scripts = scripts
        # Enrichir les scripts avec leur catégorie
        for s in self.scripts:
            # Sécurité
            s["category"] = SCRIPT_CATEGORIES.get(s["name"], "Organisation & Collections")
            
        self.icon_cache = {}
        self.current_category = "Tout"
        self.search_query = ""

        # --- Layout Principal ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Arrière-plan (Sakura) Main Window ---
        self.setup_background()

        # --- Logic ---
        self.init_music()
        self.setup_sidebar()
        self.setup_content_area()
        self.check_updates()
        self.filter_and_display()

        # Shortcuts
        self.bind("<Control-f>", lambda event: self.search_entry.focus_set())
        self.bind("<Escape>", lambda event: self.clear_search())
        
        self.last_width = 1100
        self.last_height = 720

    def on_window_resize(self, event):
        if event.widget == self:
            # Check for significant change to avoid jitter
            if abs(event.width - self.last_width) > 5 or abs(event.height - self.last_height) > 5:
                self.last_width = event.width
                self.last_height = event.height
                
                # Debounce/Delay update
                if hasattr(self, '_resize_job'):
                    self.after_cancel(self._resize_job)
                self._resize_job = self.after(100, self.perform_resize_updates)

    def perform_resize_updates(self):
        self.update_background_size()
        self.filter_and_display()

    def update_background_size(self):
        try:
            bg_path = get_path(os.path.join("assets", "sakura_bg.png"))
            if os.path.exists(bg_path):
                # Utiliser la HAUTEUR actuelle de la fenêtre comme référence
                target_h = self.last_height
                
                # Ouvrir l'image originale
                original_img = Image.open(bg_path)
                
                # Calculer le ratio basé sur la HAUTEUR pour ne pas déborder
                ratio = target_h / original_img.height
                
                target_w = int(original_img.width * ratio)
                # target_h est déjà self.last_height
                
                # Redimensionner en gardant le ratio
                pil_image = original_img.resize((target_w, target_h), Image.LANCZOS)
                
                # Update References
                self.bg_image_ref = CTkImage(pil_image, size=(target_w, target_h))
                self.pil_bg_image = pil_image
                self.canvas_bg_photo = ImageTk.PhotoImage(pil_image)

                # Update Label
                self.bg_label.configure(image=self.bg_image_ref, anchor="ne")
                
                # Update Canvas BG (redraw)
                self.draw_background_on_canvas()
        except Exception as e:
            logger.error(f"BG Resize Error: {e}")
        except Exception as e:
            logger.error(f"BG Resize Error: {e}")

    # ... setup_background ...

    def filter_and_display(self):
        self.canvas.delete("content") # Only delete scrollable content
        
        # Reset Scroll
        self.scroll_y = 0
        self.canvas.yview_moveto(0) 
        
        filtered = []
        for s in self.scripts:
            cat_match = (self.current_category == "Tout") or (s.get("category") == self.current_category)
            search_match = True
            if self.search_query:
                tags = f"{s['name']} {s['description']} {s.get('category','')}".lower()
                if self.search_query not in tags: search_match = False
            if cat_match and search_match: filtered.append(s)
        
        filtered.sort(key=lambda x: x["name"])

        # Layout sorting - FLUID 2 COLUMNS
        # Force 2 columns always
        col_count = 2
        
        # Determine available width
        pad_x = 20
        pad_y = 20
        start_y = 20
        
        # Width available for content is Window Width - Sidebar (200)
        # OR self.canvas.winfo_width()
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100: canvas_w = self.last_width - 200 # Fallback
        
        # Adjust calculations
        # content_width = canvas_w
        # margins (left/right) = pad_x
        # gap between cols = pad_x
        # total_width = 2 * card_width + 1 * pad_x + 2 * pad_x (margins)
        # card_width = (canvas_w - 3 * pad_x) / 2
        
        available_w = canvas_w - (3 * pad_x) # 2 outer margins + 1 inner gap
        card_width = int(available_w // 2)
        
        # Safety min width
        if card_width < 200: card_width = 200
        
        card_height = 140 # Keep height fixed for consistency

        # Centrage / Padding
        start_x = pad_x # Left margin
        
        if not filtered:
            msg = f"Aucun résultat pour '{self.search_query}'" if self.search_query else "Aucun outil dans cette catégorie."
            self.canvas.create_text(canvas_w // 2, 100, text=msg, fill="white", font=("Arial", 16), tags="content")
            return

        for idx, script in enumerate(filtered):
            row = idx // col_count
            col = idx % col_count
            
            x = start_x + col * (card_width + pad_x)
            y = start_y + row * (card_height + pad_y)
            
            self.draw_card(script, x, y, card_width, card_height)

        # Calculate Total Height
        total_rows = (len(filtered) + col_count - 1) // col_count
        content_total_h = start_y + total_rows * (card_height + pad_y) + 50 # padding bottom
        self.update_content_height(content_total_h)

    def setup_background(self):
        """Configure l'image de fond Sakura (Globale)."""
        try:
            bg_path = get_path(os.path.join("assets", "sakura_bg.png"))
            if os.path.exists(bg_path):
                # Init with default size 720 (height logic)
                target_h = 720
                
                original_img = Image.open(bg_path)
                
                # Logic "Fit Height"
                ratio = target_h / original_img.height
                
                new_w = int(original_img.width * ratio)
                new_h = target_h

                pil_image = original_img.resize((new_w, new_h), Image.LANCZOS)
                
                self.bg_image_ref = CTkImage(pil_image, size=(new_w, new_h)) 
                self.pil_bg_image = pil_image 
                self.canvas_bg_photo = ImageTk.PhotoImage(pil_image) 

                # anchor="ne" : aligné en haut à droite
                self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image_ref, anchor="ne")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower() 
            else:
                logger.warning(f"Background image not found at {bg_path}")
        except Exception as e:
            logger.error(f"Erreur background setup: {e}")

    def setup_sidebar(self):
        """Crée la barre latérale avec les catégories."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="transparent")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        


        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🌸 Retrogaming 🌸\nToolkit", 
                                     font=("Roboto Medium", 20), text_color=self.COLOR_ACCENT_PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.category_buttons = {}
        # Ordre spécifique demandé
        categories = [
            "Tout",
            "Gestion des Jeux & ROMs",
            "Métadonnées & Gamelists",
            "Multimédia & Artworks",
            "Organisation & Collections",
            "Maintenance Système"
        ]
        
        for i, cat in enumerate(categories):
            btn = ctk.CTkButton(self.sidebar_frame, text=cat, anchor="w",
                                fg_color="transparent", text_color=self.COLOR_TEXT_MAIN,
                                hover_color=self.COLOR_SIDEBAR_HOVER,
                                font=("Roboto", 13),
                                height=35,
                                command=lambda c=cat: self.change_category(c))
            btn.grid(row=i+1, column=0, sticky="ew", padx=10, pady=2)
            self.category_buttons[cat] = btn

        # GIF Animation
        self.gif_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.gif_label.grid(row=10, column=0, padx=20, pady=(10, 0), sticky="s")
        self.start_gif_rotation()

        # Track Info Label
        self.track_label = ctk.CTkLabel(self.sidebar_frame, text="Loading...", 
                                      font=("Roboto", 10), text_color="gray70",
                                      wraplength=180, justify="center")
        self.track_label.grid(row=11, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.start_track_updater()
            
        self.bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_frame.grid(row=12, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.version_label = ctk.CTkLabel(self.bottom_frame, text=f"v{VERSION}", text_color=self.COLOR_TEXT_SUB)
        self.version_label.pack(side="left")
        
        self.update_status_label = ctk.CTkLabel(self.sidebar_frame, text="...", text_color=self.COLOR_TEXT_SUB, font=("Arial", 10))
        self.update_status_label.grid(row=12, column=0, padx=20, pady=(0, 20), sticky="w")

        # Music Controls
        self.setup_music_controls()


    def setup_content_area(self):
        """Crée la zone principale de contenu avec Canvas et Scroll Manuel pour un fond fixe parfait."""
        self.content_container = ctk.CTkFrame(self, fg_color="transparent") 
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # --- Header : Recherche ---
        self.header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent", height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 10), padx=20)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(self.header_frame, textvariable=self.search_var, 
                                       placeholder_text="Rechercher...",
                                       border_color=self.COLOR_ACCENT_PRIMARY, border_width=1,
                                       fg_color="#1a1a1a")
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True, ipady=5)
        
        self.clear_btn = ctk.CTkButton(self.header_frame, text="✕", width=40, fg_color="#1a1a1a", 
                                         border_width=1, border_color=self.COLOR_TEXT_SUB,
                                         hover_color="#333",
                                         command=self.clear_search)
        self.clear_btn.pack(side="right")

        # --- Canvas ---
        # bg="#1e1e1e" for the "Fond Opaque" requested
        self.canvas = ctk.CTkCanvas(self.content_container, bg="#1e1e1e", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        
        self.scrollbar = ctk.CTkScrollbar(self.content_container, orientation="vertical", command=self.on_scrollbar_drag)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Scroll State
        self.scroll_y = 0.0 # Current pixel offset (0 to -content_height)
        self.content_height = 0
        self.visible_height = 0
        
        # Bindings
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_canvas_configure(self, event):
        self.visible_height = event.height
        self.draw_background_on_canvas()
        self.update_scrollbar()

    def update_content_height(self, height):
        self.content_height = max(height, self.visible_height)
        self.update_scrollbar()

    def update_scrollbar(self):
        # Update scrollbar thumb based on self.scroll_y and self.content_height
        if self.content_height <= self.visible_height:
            self.scrollbar.set(0, 1)
        else:
            # Fraction visible
            ratio = self.visible_height / self.content_height
            # Start position (inverted logic because scroll_y is negative)
            start = -self.scroll_y / self.content_height
            end = start + ratio
            self.scrollbar.set(start, end)

    def on_scrollbar_drag(self, *args):
        # args can be ('moveto', 'float') or ('scroll', 'int', 'units')
        if not self.content_height: return
        
        if args[0] == 'moveto':
            target_ratio = float(args[1])
            # Target Y position
            target_y = -1 * target_ratio * self.content_height
            self.scroll_absolute(target_y)
            
        elif args[0] == 'scroll':
            amount = int(args[1])
            # Scroll step
            step = 30 * -amount # inverted
            self.scroll_relative(step)

    def on_mousewheel(self, event):
        # Windows: delta is usually +-120
        delta = event.delta
        self.scroll_relative(delta)

    def scroll_relative(self, delta):
        new_y = self.scroll_y + delta
        self.scroll_absolute(new_y)
        
    def scroll_absolute(self, target_y):
        # Clamp target_y
        # Max scroll (negative) is visible_height - content_height
        min_y = min(0, self.visible_height - self.content_height)
        max_y = 0
        
        target_y = max(min_y, min(target_y, max_y))
        
        diff = target_y - self.scroll_y
        if diff != 0:
            self.canvas.move("content", 0, diff)
            self.scroll_y = target_y
            self.update_scrollbar()

    def draw_background_on_canvas(self):
        # Dessine le fond sur le Canvas, aligné à DROITE (NE)
        self.canvas.delete("bg")
        try:
            if hasattr(self, 'canvas_bg_photo') and self.canvas_bg_photo:
                # La fenêtre fait self.last_width de large
                # Le sidebar fait 200.
                # Le Canvas commence à x=200.
                # La largeur du Canvas est donc window_width - 200.
                # On veut que le bord droit de l'image (anchor=ne) soit au bord droit du Canvas.
                
                canvas_width = self.last_width - 200
                if canvas_width > 0:
                    self.canvas.create_image(canvas_width, 0, image=self.canvas_bg_photo, anchor="ne", tags="bg")
                    self.canvas.tag_lower("bg")
        except Exception as e:
            logger.error(f"Canvas BG Error: {e}")

    def change_category(self, category):
        if self.current_category in self.category_buttons:
             self.category_buttons[self.current_category].configure(text_color=self.COLOR_TEXT_MAIN, fg_color="transparent")
        self.current_category = category
        self.category_buttons[category].configure(text_color=self.COLOR_ACCENT_PRIMARY, fg_color="#333333")
        self.filter_and_display()

    def on_search_change(self, *args):
        self.search_query = self.search_var.get().lower().strip()
        self.filter_and_display()

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()

    def open_custom_readme(self, title, readme_path, icon_path=None):
        try:
            content = "Fichier non trouvé."
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
            ReadmeWindow(self, title, content, self.COLOR_SIDEBAR_BG, self.COLOR_TEXT_MAIN, self.COLOR_ACCENT_PRIMARY, icon_path=icon_path)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def filter_and_display(self):
        self.canvas.delete("content") # Only delete scrollable content
        # self.draw_background_on_canvas() # No need to redraw BG every filter
        
        # Reset Scroll
        self.scroll_y = 0
        self.canvas.yview_moveto(0) # Reset native just in case
        
        filtered = []
        for s in self.scripts:
            cat_match = (self.current_category == "Tout") or (s.get("category") == self.current_category)
            search_match = True
            if self.search_query:
                tags = f"{s['name']} {s['description']} {s.get('category','')}".lower()
                if self.search_query not in tags: search_match = False
            if cat_match and search_match: filtered.append(s)
        
        filtered.sort(key=lambda x: x["name"])

        # Layout sorting
        col_count = 2
        card_width = 400
        card_height = 140
        pad_x = 20
        pad_y = 20
        
        # Obtenir la largeur visible dynamique du Canvas
        # Fallback à 900 (taille min fenêtre - sidebar) si canvas pas encore affiché
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100: canvas_w = 900 
        
        total_content_width = (col_count * card_width) + ((col_count - 1) * pad_x)
        
        # Centrage horizontal
        start_x = (canvas_w - total_content_width) // 2
        if start_x < 20: start_x = 20 # Minimum padding left
        
        start_y = 20
        
        if not filtered:
            msg = f"Aucun résultat pour '{self.search_query}'" if self.search_query else "Aucun outil dans cette catégorie."
            self.canvas.create_text(400, 100, text=msg, fill="white", font=("Arial", 16), tags="content")
            return

        for idx, script in enumerate(filtered):
            row = idx // col_count
            col = idx % col_count
            x = start_x + col * (card_width + pad_x)
            y = start_y + row * (card_height + pad_y)
            self.draw_card(script, x, y, card_width, card_height)

        # Calculate Total Height
        total_rows = (len(filtered) + col_count - 1) // col_count
        content_total_h = start_y + total_rows * (card_height + pad_y) + 50 # padding bottom
        self.update_content_height(content_total_h)

    def draw_card(self, script, x, y, w, h):
        # Add tags="content" to EVERYTHING that should scroll
        
        # Semi-transparent background for readability
        # Create a semi-transparent image on the fly (cached)
        if not hasattr(self, 'card_bg_img_cache') or (w, h) not in self.card_bg_img_cache:
            if not hasattr(self, 'card_bg_img_cache'):
                self.card_bg_img_cache = {}
            # Black with 70% opacity (approx 180/255)
            pil_bg = Image.new('RGBA', (w, h), (30, 30, 30, 200)) 
            self.card_bg_img_cache[(w, h)] = ImageTk.PhotoImage(pil_bg)
            
        self.canvas.create_image(x, y, image=self.card_bg_img_cache[(w, h)], anchor="nw", tags="content")

        # Border
        self.canvas.create_rectangle(x, y, x+w, y+h, outline=self.COLOR_CARD_BORDER, width=1, tags="content")
        
        # Icon
        icon_path = script.get("icon", "")
        if icon_path not in self.icon_cache:
             try:
                 if os.path.exists(icon_path):
                     img = Image.open(icon_path).resize((40, 40), Image.LANCZOS)
                     self.icon_cache[icon_path] = ImageTk.PhotoImage(img)
             except: pass
        if icon_path in self.icon_cache:
            self.canvas.create_image(x + 20, y + 20, image=self.icon_cache[icon_path], anchor="nw", tags="content")

        # Title
        self.canvas.create_text(x + 70, y + 20, text=script["name"], fill=self.COLOR_TEXT_MAIN, 
                                font=("Roboto Medium", 16), anchor="nw", tags="content")
        
        # Description
        self.canvas.create_text(x + 70, y + 50, text=script["description"], fill=self.COLOR_TEXT_SUB,
                                font=("Roboto", 12), anchor="nw", width=w-90, tags="content")
        
        # Buttons
        # Note: Canvas windows move with canvas.move if they are on the canvas!
        # But we need to make sure we create_window with tags="content"? 
        # Tkinter create_window accepts tags!
        
        readme_btn = ctk.CTkButton(self.canvas, text="?", width=30, height=30,
                                 fg_color="transparent", text_color=self.COLOR_ACCENT_PRIMARY, 
                                 border_width=1, border_color=self.COLOR_ACCENT_PRIMARY, 
                                 hover_color="#333",
                                 command=lambda r=script.get("readme", ""), n=script["name"], i=script.get("icon", ""): self.open_custom_readme(f"Aide - {n}", r, icon_path=i))
        
        self.canvas.create_window(x + 20, y + h - 45, window=readme_btn, anchor="nw", tags="content")
        
        launch_btn = ctk.CTkButton(self.canvas, text="Ouvrir", height=30, width=w-70,
                                 fg_color="transparent", text_color=self.COLOR_ACCENT_PRIMARY,
                                 border_width=1, border_color=self.COLOR_ACCENT_PRIMARY,
                                 hover_color="#333333",
                                 font=("Roboto Medium", 13),
                                 command=lambda n=script["name"]: self.execute_module(n))
        
        self.canvas.create_window(x + 60, y + h - 45, window=launch_btn, anchor="nw", tags="content")

    def get_icon(self, path):
        if path in self.icon_cache:
            return self.icon_cache[path]
        try:
            if os.path.exists(path):
                img = Image.open(path).resize((40, 40), Image.LANCZOS)
                ctk_img = CTkImage(img, size=(40, 40))
                self.icon_cache[path] = ctk_img
                return ctk_img
        except: pass
        return CTkImage(Image.new("RGBA", (40, 40), (100, 100, 100, 0)), size=(40, 40))

    def execute_module(self, module_name):
        lancer_module(module_name)

    def check_updates(self):
        def update_worker():
             try:
                 update_available, latest_version = check_for_updates()
                 # Check if the window still exists before scheduling callback
                 if self.winfo_exists():
                     self.after(0, lambda: self.update_update_ui(update_available, latest_version))
             except Exception as e:
                 logger.debug(f"Update check thread ignored: {e}")
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()

    def update_update_ui(self, update_available, latest_version):
        if update_available:
            self.update_status_label.configure(text=f"Update: {latest_version}", text_color=self.COLOR_ACCENT_PRIMARY)
        else:
            self.update_status_label.configure(text=f"À jour", text_color="green")

    def init_music(self):
        """Initialise et lance la musique de fond (Web Radio)."""
        try:
            # Increase buffer size to handle streaming better
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=8192)
            pygame.mixer.init()
            
            # 8Beats Radio Stream (HTTP for compatibility)
            stream_url = "http://stream.radiojar.com/2fa4wbch308uv"
            
            self.music_playing = False
            self.music_muted = False
            self.gif_paused = False
            
            def load_stream():
                try:
                    logger.info(f"Connecting to Web Radio: {stream_url}")
                    
                    # Add headers to mimic a browser/player
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Icy-MetaData': '1' 
                    }
                    
                    r = requests.get(stream_url, headers=headers, stream=True, timeout=15)
                    
                    if r.status_code == 200:
                        class StreamWrapper:
                            def __init__(self, raw):
                                self.raw = raw
                            def read(self, n=-1):
                                if n == -1: n = 8192 # Read standard chunk if undefined
                                return self.raw.read(n)
                            def seek(self, offset, whence=0):
                                pass 
                            def tell(self):
                                return 0
                            def close(self):
                                self.raw.close()

                        # Load wrapped stream
                        pygame.mixer.music.load(StreamWrapper(r.raw))
                        pygame.mixer.music.play()
                        self.music_playing = True
                        pygame.mixer.music.set_volume(0.5)
                        logger.info("Web Radio playback started.")
                    else:
                        logger.error(f"Web Radio connection failed: {r.status_code}")

                except Exception as e:
                    logger.error(f"Error loading Web Radio: {e}")

            # Lancer le chargement dans un thread pour ne pas bloquer l'interface au démarrage
            threading.Thread(target=load_stream, daemon=True).start()

        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")

    def setup_music_controls(self):
        """Ajoute les contrôles de musique dans la sidebar."""
        # Seulementsi pygame a bien démarré
        if not pygame.mixer.get_init():
            return

        # Play/Pause Button
        self.play_btn = ctk.CTkButton(self.bottom_frame, text="⏸️", width=30, height=30,
                                      fg_color="transparent", border_width=0, 
                                      text_color=self.COLOR_TEXT_MAIN,
                                      font=("Segoe UI Emoji", 20),
                                      hover_color=self.COLOR_SIDEBAR_HOVER,
                                      command=self.toggle_music)
        self.play_btn.pack(side="left", padx=(15, 5))
        
        # Mute Button
        self.mute_btn = ctk.CTkButton(self.bottom_frame, text="🔊", width=30, height=30,
                                      fg_color="transparent", border_width=0,
                                      text_color=self.COLOR_TEXT_MAIN,
                                      font=("Segoe UI Emoji", 20),
                                      hover_color=self.COLOR_SIDEBAR_HOVER,
                                      command=self.toggle_mute)
        self.mute_btn.pack(side="left", padx=0)

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
            self.play_btn.configure(text="▶️")
            self.music_playing = False
            self.gif_paused = True # Pause GIF
        else:
            pygame.mixer.music.unpause()
            # Cas où la musique a été stoppée ou non démarrée
            if not pygame.mixer.music.get_busy():
                 try:
                    pygame.mixer.music.play(-1)
                 except: pass
            self.play_btn.configure(text="⏸️")
            self.music_playing = True
            
            # Resume GIF if it was paused
            if self.gif_paused:
                self.gif_paused = False
                self.animate_gif()

    def toggle_mute(self):
        if self.music_muted:
            pygame.mixer.music.set_volume(0.5) # Retour au volume par défaut
            self.mute_btn.configure(text="🔊")
            self.music_muted = False
        else:
            pygame.mixer.music.set_volume(0.0)
            self.mute_btn.configure(text="🔇")
            self.music_muted = True

    def start_gif_rotation(self):
        """Charge les deux GIFs et lance la rotation."""
        self.gif_list = []
        
        # Charger dance.gif
        g1 = self.load_gif_data(os.path.join("assets", "dance.gif"))
        if g1: self.gif_list.append(g1)
        
        # Charger dance2.gif
        g2 = self.load_gif_data(os.path.join("assets", "dance2.gif"))
        if g2: self.gif_list.append(g2)
        
        if not self.gif_list:
            return

        self.current_gif_index = 0
        self.set_active_gif(self.gif_list[0])
        self.animate_gif()
        
        # Rotation timer (60s) seulement si on a plus d'un GIF
        if len(self.gif_list) > 1:
            self.rotate_gif()

    def load_gif_data(self, path):
        """Charge les frames et le délai d'un GIF."""
        try:
            full_path = get_path(path)
            if not os.path.exists(full_path):
                return None

            gif = Image.open(full_path)
            duration = gif.info.get('duration', 100)
            if duration < 20: duration = 100
            
            frames = []
            try:
                while True:
                    frame = gif.copy().convert("RGBA")
                    target_w = 150
                    ratio = target_w / frame.width
                    target_h = int(frame.height * ratio)
                    frame = frame.resize((target_w, target_h), Image.LANCZOS)
                    frames.append(CTkImage(frame, size=(target_w, target_h)))
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
                
            if frames:
                return {'frames': frames, 'delay': duration}
        except Exception as e:
            logger.error(f"GIF Load Error {path}: {e}")
        return None

    def set_active_gif(self, gif_data):
        """Définit le GIF actif."""
        self.gif_frames = gif_data['frames']
        self.gif_delay = gif_data['delay']
        self.current_frame_idx = 0

    def rotate_gif(self):
        """Change de GIF toutes les 60 secondes."""
        self.current_gif_index = (self.current_gif_index + 1) % len(self.gif_list)
        new_gif = self.gif_list[self.current_gif_index]
        self.set_active_gif(new_gif)
        
        # Re-planifier dans 60s
        self.after(60000, self.rotate_gif)

    def animate_gif(self):
        """Boucle d'animation du GIF."""
        if self.gif_paused:
            return

        if hasattr(self, 'gif_frames') and self.gif_frames:
            frame = self.gif_frames[self.current_frame_idx]
            self.gif_label.configure(image=frame)
            
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.gif_frames)
            
            self.after(self.gif_delay, self.animate_gif)


    def start_track_updater(self):
        """Lance le thread de mise à jour des infos musique."""
        threading.Thread(target=self.track_updater_loop, daemon=True).start()

    def track_updater_loop(self):
        """Boucle de mise à jour du titre en cours."""
        api_url = "https://www.radiojar.com/api/stations/2fa4wbch308uv/now_playing/"
        while True:
            try:
                r = requests.get(api_url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    artist = data.get('artist', '')
                    title = data.get('title', '')
                    
                    track_text = f"{artist} - {title}" if artist else title
                    if not track_text: track_text = "8Beats Radio"
                    
                    # Update UI in main thread safely (ctk is often thread safe for config, but be careful)
                    self.track_label.configure(text=track_text)
                
            except Exception as e:
                pass # Silent fail, retry later
            
            # Wait 20 seconds before next update
            threading.Event().wait(20)

def main():
    """Point d'entrée principal de l'application"""
    multiprocessing.freeze_support()

    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
