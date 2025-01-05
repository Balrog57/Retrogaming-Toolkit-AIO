import customtkinter as ctk
from tkinter import messagebox  # messagebox est toujours utilisé depuis tkinter
import os
import logging
import subprocess
from PIL import Image
from customtkinter import CTkImage

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='retrogaming_toolkit.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Configuration du thème
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

# Liste des scripts avec descriptions, chemins des icônes et fichiers "Lisez-moi"
scripts = [
    {"name": "assisted_gamelist_creator", "description": "Gère et enrichit les listes de jeux XML.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "assisted_gamelist_creator.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "assisted_gamelist_creator.txt")},
    {"name": "CHD_Converter_Tool", "description": "Convertit et vérifie les fichiers CHD.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "CHD_Converter_Tool.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "CHD_Converter_Tool.txt")},
    {"name": "collection_builder", "description": "(Core) Crée des collections de jeux par mots-clés.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "collection_builder.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "collection_builder.txt")},
    {"name": "collection_extractor", "description": "(Core) Extrait des collections de jeux spécifiques.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "collection_extractor.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "collection_extractor.txt")},
    {"name": "enable_long_paths", "description": "Active les chemins longs sur Windows.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "enable_long_paths.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "enable_long_paths.txt")},
    {"name": "folder_name_to_txt", "description": "Crée des fichiers TXT à partir des noms de dossiers.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "folder_name_to_txt.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "folder_name_to_txt.txt")},
    {"name": "folder_to_zip", "description": "Compresse des fichiers de jeux en ZIP.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "folder_to_zip.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "folder_to_zip.txt")},
    {"name": "game_batch_creator", "description": "Génère des fichiers batch pour lancer des jeux.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "game_batch_creator.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "game_batch_creator.txt")},
    {"name": "game_removal", "description": "(Core) Supprime des jeux et leurs artworks.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "game_removal.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "game_removal.txt")},
    {"name": "gamelist_to_hyperlist", "description": "Convertit gamelist.xml en hyperlist.xml.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "gamelist_to_hyperlist.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "gamelist_to_hyperlist.txt")},
    {"name": "hyperlist_to_gamelist", "description": "Convertit hyperlist.xml en gamelist.xml.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "hyperlist_to_gamelist.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "hyperlist_to_gamelist.txt")},
    {"name": "install_dependencies", "description": "Installe les dépendances système pour Windows.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "install_dependencies.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "install_dependencies.txt")},
    {"name": "liste_fichier_simple", "description": "Liste les fichiers dans un répertoire.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "liste_fichier_simple.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "liste_fichier_simple.txt")},
    {"name": "liste_fichier_windows", "description": "Liste fichiers et dossiers sous Windows.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "liste_fichier_windows.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "liste_fichier_windows.txt")},
    {"name": "MaxCSO_Compression_Script", "description": "Compresse des fichiers ISO en CSO.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "MaxCSO_Compression_Script.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "MaxCSO_Compression_Script.txt")},
    {"name": "media_orphan_detector", "description": "(Core) Détecte et déplace les fichiers multimédias orphelins.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "media_orphan_detector.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "media_orphan_detector.txt")},
    {"name": "merge_story_hyperlist", "description": "Intègre des histoires dans des hyperlistes XML.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "merge_story_hyperlist.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "merge_story_hyperlist.txt")},
    {"name": "rvz_iso_convert", "description": "Convertit entre formats RVZ et ISO.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "rvz_iso_convert.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "rvz_iso_convert.txt")},
    {"name": "story_format_cleaner", "description": "Nettoie les fichiers texte pour XML.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "story_format_cleaner.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "story_format_cleaner.txt")},
    {"name": "video_converter", "description": "Convertit et rogne des vidéos par lot.", "icon": os.path.join("Retrogaming-Toolkit-AIO", "icons", "video_converter.ico"), "readme": os.path.join("Retrogaming-Toolkit-AIO", "read_me", "video_converter.txt")},
]

def lancer_module(module_name):
    """Charge et exécute un module Python dans un processus séparé."""
    try:
        # Vérification du chemin du module
        current_dir = os.path.dirname(os.path.abspath(__file__))
        module_file = os.path.join(current_dir, "Retrogaming-Toolkit-AIO", f"{module_name}.py")
        
        if not os.path.exists(module_file):
            error_msg = f"Le fichier module '{module_file}' n'existe pas"
            logger.error(error_msg)
            messagebox.showerror("Erreur", error_msg)
            return
        
        # Exécution du module dans un processus séparé
        subprocess.Popen(["python", module_file])
        logger.info(f"Module {module_name} exécuté avec succès")
    
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

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lanceur de Modules - Retrogaming-Toolkit-AIO")
        self.geometry("800x400")  # Taille initiale

        self.scripts = scripts
        self.page = 0
        self.scripts_per_page = 10
        self.min_window_height = 400
        self.preferred_width = 800

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

        # Afficher les scripts de la première page
        self.update_page()

    def update_page(self):
        """Met à jour l'affichage des scripts pour la page courante."""
        # Efface les widgets existants
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Afficher les scripts de la page courante
        start_index = self.page * self.scripts_per_page
        end_index = start_index + self.scripts_per_page
        for script in self.scripts[start_index:end_index]:
            frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
            frame.pack(fill="x", pady=5, padx=10)

            # Charger l'icône
            try:
                if os.path.exists(script["icon"]):
                    img = Image.open(script["icon"])
                    img = img.resize((32, 32), Image.LANCZOS)
                    icon = CTkImage(img)
                else:
                    raise FileNotFoundError("Icon file not found")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'icône {script['icon']}: {e}")
                icon = CTkImage(Image.new('RGBA', (32, 32), (0, 0, 0, 0)))
            icon_label = ctk.CTkLabel(frame, image=icon, text="")
            icon_label.image = icon
            icon_label.pack(side="left", padx=10)

            # Bouton pour lancer le module
            button = ctk.CTkButton(
                frame, 
                text=script["name"], 
                command=lambda name=script["name"]: self.execute_module(name), 
                width=200
            )
            button.pack(side="left", padx=10)

            # Description du script
            label = ctk.CTkLabel(frame, text=script["description"], anchor="w", justify="left", font=("Arial", 12))
            label.pack(side="left", expand=True, fill="x")

            # Bouton "Lisez-moi"
            readme_button = ctk.CTkButton(frame, text="Lisez-moi", command=lambda r=script["readme"]: open_readme(r), width=100)
            readme_button.pack(side="right", padx=10)

        # Mettre à jour l'indicateur de page
        total_pages = (len(self.scripts) - 1) // self.scripts_per_page + 1
        self.page_label.configure(text=f"Page {self.page + 1} sur {total_pages}")

        # Activer/Désactiver les boutons de navigation
        self.previous_button.configure(state="normal" if self.page > 0 else "disabled")
        self.next_button.configure(state="normal" if end_index < len(self.scripts) else "disabled")

        # Ajuster la taille de la fenêtre
        self.update_idletasks()
        new_height = max(self.min_window_height, self.main_frame.winfo_reqheight() + 150)
        self.geometry(f"{self.preferred_width}x{new_height}")

    def execute_module(self, module_name):
        """Exécute un module dans un processus séparé."""
        logger.info(f"Lancement du module depuis l'interface: {module_name}")
        lancer_module(module_name)

    def next_page(self):
        """Passe à la page suivante."""
        if (self.page + 1) * self.scripts_per_page < len(self.scripts):
            self.page += 1
            self.update_page()

    def previous_page(self):
        """Revient à la page précédente."""
        if self.page > 0:
            self.page -= 1
            self.update_page()

if __name__ == '__main__':
    app = Application()
    app.mainloop()