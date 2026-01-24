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
from PIL import Image
from customtkinter import CTkImage
import requests
import webbrowser
import threading
import json

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
except ImportError:
    # Si utils n'est pas trouvé (devrait pas arriver si sys.path est correct)
    # logger might not be defined yet
    logger = logging.getLogger(__name__) # Safe to call
    logging.basicConfig() # Ensure basic logging
    logger.error("Impossible d'importer utils.py")
    utils = None

VERSION = "2.0.38"

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
    {"name": "AssistedGamelist", "description": "(Retrobat) Gère et enrichit les listes de jeux XML.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "AssistedGamelist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "AssistedGamelist.txt"))},
    {"name": "BGBackup", "description": "(Retrobat) Sauvegarde les fichiers gamelist.xml.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "BGBackup.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "BGBackup.txt"))},
    {"name": "CHDManager", "description": "Convertit et vérifie les fichiers CHD (MAME).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "CHDManager.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CHDManager.txt"))},
    {"name": "CollectionBuilder", "description": "(Core) Crée des collections de jeux par mots-clés.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "CollectionBuilder.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CollectionBuilder.txt"))},
    {"name": "CollectionExtractor", "description": "(Core) Extrait des collections de jeux spécifiques.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "CollectionExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CollectionExtractor.txt"))},
    {"name": "LongPaths", "description": "Active les chemins longs sur Windows (Registry).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "LongPaths.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "LongPaths.txt"))},
    {"name": "FolderToTxt", "description": "Crée des fichiers TXT à partir des noms de dossiers.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "FolderToTxt.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderToTxt.txt"))},
    {"name": "FolderToZip", "description": "Compresse des fichiers de jeux en ZIP.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "FolderToZip.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderToZip.txt"))},
    {"name": "GameBatch", "description": "Génère des fichiers batch pour lancer des jeux PC.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "GameBatch.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GameBatch.txt"))},
    {"name": "EmptyGen", "description": "Génère des fichiers vides dans des sous-dossiers.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "EmptyGen.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "EmptyGen.txt"))},
    {"name": "GameRemoval", "description": "(Core) Supprime des jeux et leurs médias associés.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "GameRemoval.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GameRemoval.txt"))},
    {"name": "GamelistHyperlist", "description": "(Core) Convertit gamelist.xml en hyperlist.xml.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "GamelistHyperlist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "GamelistHyperlist.txt"))},
    {"name": "HyperlistGamelist", "description": "(Retrobat) Convertit hyperlist.xml en gamelist.xml.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "HyperlistGamelist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "HyperlistGamelist.txt"))},
    {"name": "InstallDeps", "description": "Installe les dépendances système (DirectX, VC++).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "InstallDeps.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "InstallDeps.txt"))},
    {"name": "ListFilesSimple", "description": "Liste les fichiers d'un répertoire (Simple).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "ListFilesSimple.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ListFilesSimple.txt"))},
    {"name": "ListFilesWin", "description": "Liste fichiers et dossiers (Détails Windows).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "ListFilesWin.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ListFilesWin.txt"))},
    {"name": "MaxCSO", "description": "Compresse des fichiers ISO en CSO (MaxCSO).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "MaxCSO.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "MaxCSO.txt"))},
    {"name": "MediaOrphans", "description": "(Core) Détecte et déplace les médias orphelins.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "MediaOrphans.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "MediaOrphans.txt"))},
    {"name": "FolderCleaner", "description": "Supprime les dossiers vides récursivement.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "FolderCleaner.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "FolderCleaner.txt"))},
    {"name": "StoryHyperlist", "description": "(Core) Intègre des story dans des hyperlist.xml.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "StoryHyperlist.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "StoryHyperlist.txt"))},
    {"name": "DolphinConvert", "description": "Convertit entre formats RVZ et ISO (Dolphin).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "DolphinConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "DolphinConvert.txt"))},
    {"name": "StoryCleaner", "description": "Nettoie les fichiers texte non ASCII.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "StoryCleaner.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "StoryCleaner.txt"))},
    {"name": "M3UCreator", "description": "Crée des playlists M3U pour le multi-disque.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "M3UCreator.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "M3UCreator.txt"))},
    {"name": "CoverExtractor", "description": "Extrait la première image des CBZ, CBR, PDF.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "CoverExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CoverExtractor.txt"))},
    {"name": "CBZKiller", "description": "Convertisseur PDF/CBR vers CBZ.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "CBZKiller.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CBZKiller.txt"))},
    {"name": "VideoConvert", "description": "Convertit/Rogne des vidéos par lot (FFmpeg).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "VideoConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "VideoConvert.txt"))},
    {"name": "YTDownloader", "description": "Télécharge des vidéos/audio Youtube (yt-dlp).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "YTDownloader.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "YTDownloader.txt"))},
    {"name": "ImageConvert", "description": "Convertit des images par lot.", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "ImageConvert.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "ImageConvert.txt"))},
    {"name": "SystemsExtractor", "description": "Extrait les systèmes uniques (EmulationStation).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "SystemsExtractor.ico")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "SystemsExtractor.txt"))},
    {"name": "UniversalRomCleaner", "description": "Nettoie et trie vos ROMs (1G1R, Régions).", "icon": get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "UniversalRomCleaner.png")), "readme": get_path(os.path.join("Retrogaming-Toolkit-AIO", "read_me", "UniversalRomCleaner.txt"))},
]

CATEGORY_MAPPING = {
    "Gestion des Jeux & ROMs": ["CHDManager", "MaxCSO", "DolphinConvert", "FolderToZip", "GameBatch", "GameRemoval", "UniversalRomCleaner"],
    "Métadonnées & Gamelists": ["AssistedGamelist", "GamelistHyperlist", "HyperlistGamelist", "BGBackup", "StoryHyperlist", "StoryCleaner", "SystemsExtractor"],
    "Multimédia & Artworks": ["YTDownloader", "VideoConvert", "ImageConvert", "CoverExtractor", "MediaOrphans", "CBZKiller"],
    "Organisation & Collections": ["CollectionBuilder", "CollectionExtractor", "M3UCreator", "FolderCleaner", "FolderToTxt", "EmptyGen"],
    "Maintenance Système": ["LongPaths", "InstallDeps", "ListFilesSimple", "ListFilesWin"]
}

def run_module_process(module_name):
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
        
        # On lance le module dans un nouveau processus
        # Cela permet d'isoler les boucles principales Tkinter
        p = multiprocessing.Process(target=run_module_process, args=(module_name,))
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
            icon_path = get_path(os.path.join("Retrogaming-Toolkit-AIO", "icons", "Retrogaming-Toolkit-AIO.ico"))
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

        # Filtre par catégorie
        self.category_var = ctk.StringVar(value="Toutes les catégories")
        self.category_combo = ctk.CTkComboBox(
            self.search_frame,
            values=["Toutes les catégories"] + list(CATEGORY_MAPPING.keys()),
            command=self.filter_scripts,
            variable=self.category_var,
            width=200,
            state="readonly"
        )
        self.category_combo.pack(side="left", padx=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_scripts)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, width=300, placeholder_text="Nom ou description... (Ctrl+F)")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.clear_button = ctk.CTkButton(self.search_frame, text="✕", width=25, height=25, 
                                          command=self.clear_search, 
                                          fg_color="transparent", hover_color=("gray70", "gray30"), text_color="gray")

        # Conteneur principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Boutons de navigation
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(fill="x", pady=10)

        self.previous_button = ctk.CTkButton(self.nav_frame, text="◀ Précédent", command=self.previous_page, width=100)
        self.previous_button.pack(side="left", padx=10)

        self.page_label = ctk.CTkLabel(self.nav_frame, text="Page 1", font=("Arial", 16))
        self.page_label.pack(side="left", expand=True)

        self.next_button = ctk.CTkButton(self.nav_frame, text="Suivant ▶", command=self.next_page, width=100)
        self.next_button.pack(side="right", padx=10)



        # Ajouter une zone en bas pour la version et les mises à jour
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(fill="x", pady=10)

        self.version_label = ctk.CTkLabel(self.bottom_frame, text=f"Version actuelle : {VERSION}", font=("Arial", 12))
        self.version_label.pack(side="left", padx=10)

        self.update_label = ctk.CTkLabel(self.bottom_frame, text="Vérification des mises à jour...", font=("Arial", 12))
        self.update_label.pack(side="left", padx=10)

        # Vérifier les mises à jour
        self.check_updates()

        # Afficher les scripts de la première page (APRÈS l'initialisation de tous les frames)
        self.update_page()
        
        # Auto-focus search bar
        self.after(100, lambda: self.search_entry.focus_set())

        # Keyboard shortcuts
        self.bind("<Control-f>", lambda event: self.search_entry.focus_set())
        self.bind("<Escape>", self.clear_search_or_focus)
        self.bind("<Left>", lambda e: self.previous_page())
        self.bind("<Right>", lambda e: self.next_page())

    def clear_search_or_focus(self, event=None):
        """Efface la recherche ou enlève le focus."""
        if self.search_var.get():
            self.clear_search()
        else:
            self.focus_set()

    def check_updates(self):
        """Vérifie les mises à jour de manière asynchrone (non-bloquant)."""
        self.update_label.configure(text="Vérification des mises à jour...", text_color="gray")
        
        def update_worker():
             update_available, latest_version = check_for_updates()
             # Schedule UI update on main thread
             self.after(0, lambda: self.update_update_ui(update_available, latest_version))
        
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()

    def load_favorites(self):
        """Charge les favoris depuis le fichier JSON."""
        fav_file = os.path.join(app_data_dir, 'favorites.json')
        if os.path.exists(fav_file):
            try:
                with open(fav_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception as e:
                logger.error(f"Erreur lors du chargement des favoris: {e}")
        return set()

    def save_favorites(self):
        """Sauvegarde les favoris dans le fichier JSON."""
        fav_file = os.path.join(app_data_dir, 'favorites.json')
        try:
            with open(fav_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.favorites), f)
        except Exception as e:
            logger.error(f"Erreur lors du sauvegarde des favoris: {e}")

    def toggle_favorite(self, script_name):
        """Bascule l'état favori d'un script."""
        if script_name in self.favorites:
            self.favorites.remove(script_name)
        else:
            self.favorites.add(script_name)
        self.save_favorites()
        self.filter_scripts() # Refresh list

    def update_update_ui(self, update_available, latest_version):
        """Met à jour l'UI avec le résultat de la vérification de mise à jour."""
        if update_available:
            self.update_label.configure(text=f"Mise à jour disponible : {latest_version}", text_color="green")
            if not hasattr(self, 'update_button'):
                self.update_button = ctk.CTkButton(self.bottom_frame, text="Mettre à jour", command=launch_update, fg_color="green")
                self.update_button.pack(side="right", padx=10)
        else:
            self.update_label.configure(text=f"Version à jour ({VERSION})", text_color="gray")

    def filter_scripts(self, *args):
        """Filtre la liste des scripts en fonction de la recherche et de la catégorie."""
        query = self.search_var.get().lower()
        category = self.category_var.get()

        # Toggle clear button visibility
        if query:
            self.clear_button.pack(side="right", padx=(0, 10))
        else:
            self.clear_button.pack_forget()

        # Filter by category first
        if category and category != "Toutes les catégories":
            allowed_scripts = CATEGORY_MAPPING.get(category, [])
            temp_scripts = [s for s in self.scripts if s["name"] in allowed_scripts]
        else:
            temp_scripts = list(self.scripts)

        # Filter by query
        if query:
            self.filtered_scripts = [
                s for s in temp_scripts
                if query in s["name"].lower() or query in s["description"].lower()
            ]
        else:
            self.filtered_scripts = temp_scripts
        
        # Sort by favorites
        self.filtered_scripts.sort(key=lambda s: (s["name"] not in self.favorites, s["name"]))

        self.page = 0 # Réinitialiser à la première page
        self.update_page()

    def clear_search(self):
        """Efface la recherche."""
        self.search_var.set("")
        self.search_entry.focus_set()

    def update_page(self):
        """Met à jour l'affichage des scripts pour la page courante."""
        # Efface les widgets existants
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Afficher les scripts de la page courante
        start_index = self.page * self.scripts_per_page
        end_index = start_index + self.scripts_per_page
        
        current_scripts = self.filtered_scripts[start_index:end_index]
        
        if not current_scripts:
            no_result_label = ctk.CTkLabel(self.main_frame, text="Aucun outil trouvé.", font=("Arial", 14))
            no_result_label.pack(pady=20)
        
        for script in current_scripts:
            frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
            frame.pack(fill="x", pady=5, padx=10)

            # Charger l'icône (avec Cache)
            if script["icon"] in self.icon_cache:
                icon = self.icon_cache[script["icon"]]
            else:
                try:
                    if os.path.exists(script["icon"]):
                        img = Image.open(script["icon"])
                        img = img.resize((32, 32), Image.LANCZOS)
                        icon = CTkImage(img)
                        self.icon_cache[script["icon"]] = icon
                    else:
                        raise FileNotFoundError("Icon file not found")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de l'icône {script['icon']}: {e}")
                    icon = CTkImage(Image.new('RGBA', (32, 32), (0, 0, 0, 0)))
                    self.icon_cache[script["icon"]] = icon

            icon_label = ctk.CTkLabel(frame, image=icon, text="")
            icon_label.image = icon
            icon_label.pack(side="left", padx=10)

            # Bouton pour lancer le module
            btn_text = "★ " + script["name"] if script["name"] in self.favorites else script["name"]
            btn_color = "#D4AF37" if script["name"] in self.favorites else None # Gold for favorite
            
            button = ctk.CTkButton(
                frame, 
                text=btn_text,
                fg_color=btn_color if btn_color else ["#3B8ED0", "#1F6AA5"], # Default colors
                command=lambda name=script["name"]: self.execute_module(name), 
                width=200
            )
            # Right click to separate favorite toggle
            button.bind("<Button-3>", lambda event, s=script["name"]: self.toggle_favorite(s))
            button.pack(side="left", padx=10)

            # Description du script
            label = ctk.CTkLabel(frame, text=script["description"], anchor="w", justify="left", font=("Arial", 12))
            label.pack(side="left", expand=True, fill="x")

            # Bouton "Lisez-moi"
            readme_button = ctk.CTkButton(frame, text="Lisez-moi", command=lambda r=script["readme"]: open_readme(r), width=100)
            readme_button.pack(side="right", padx=10)

        # Mettre à jour l'indicateur de page
        total_pages = (len(self.filtered_scripts) - 1) // self.scripts_per_page + 1
        page_display = self.page + 1 if total_pages > 0 else 0
        self.page_label.configure(text=f"Page {page_display} sur {max(1, total_pages)}")

        # Activer/Désactiver les boutons de navigation
        self.previous_button.configure(state="normal" if self.page > 0 else "disabled")
        self.next_button.configure(state="normal" if end_index < len(self.filtered_scripts) else "disabled")

        # Ajuster la taille de la fenêtre
        self.update_idletasks()
        
        # Calculer la hauteur totale nécessaire
        total_height = 0
        total_height += self.search_frame.winfo_reqheight() + 10 # + pady
        total_height += self.main_frame.winfo_reqheight() + 20   # + pady top/bottom
        total_height += self.nav_frame.winfo_reqheight() + 10    # + pady
        total_height += self.bottom_frame.winfo_reqheight() + 10 # + pady
        
        # Ajouter une marge de sécurité
        total_height += 20 

        new_height = max(self.min_window_height, total_height)
        self.geometry(f"{self.preferred_width}x{new_height}")

    def execute_module(self, module_name):
        """Exécute un module dans un processus séparé."""
        logger.info(f"Lancement du module depuis l'interface: {module_name}")
        lancer_module(module_name)

    def next_page(self):
        """Passe à la page suivante."""
        if (self.page + 1) * self.scripts_per_page < len(self.filtered_scripts):
            self.page += 1
            self.update_page()

    def previous_page(self):
        """Revient à la page précédente."""
        if self.page > 0:
            self.page -= 1
            self.update_page()

def main():
    """Point d'entrée principal de l'application"""
    multiprocessing.freeze_support()

    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
