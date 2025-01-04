import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, ImageTk
import win32ui
import win32gui
import win32con
import win32api

# Liste des scripts avec descriptions et fichiers "Lisez-moi"
scripts = [
    {"name": "Assisted GameList Creator", "file": os.path.join(os.getcwd(), "_internal/assisted_gamelist_creator.exe"), "description": "Gère et enrichit les listes de jeux XML.", "readme": os.path.join(os.getcwd(), "_internal/assisted_gamelist_creator.txt")},
    {"name": "CHD Converter Tool", "file": os.path.join(os.getcwd(), "_internal/CHD_Converter_Tool.exe"), "description": "Convertit et vérifie les fichiers CHD.", "readme": os.path.join(os.getcwd(), "_internal/CHD_Converter_Tool.txt")},
    {"name": "Collection Builder", "file": os.path.join(os.getcwd(), "_internal/collection_builder.exe"), "description": "(Core) Crée des collections de jeux par mots-clés.", "readme": os.path.join(os.getcwd(), "_internal/collection_builder.txt")},
    {"name": "Collection Extractor", "file": os.path.join(os.getcwd(), "_internal/collection_extractor.exe"), "description": "(Core) Extrait des collections de jeux spécifiques.", "readme": os.path.join(os.getcwd(), "_internal/collection_extractor.txt")},
    {"name": "Enable Long Paths", "file": os.path.join(os.getcwd(), "_internal/enable_long_paths.exe"), "description": "Active les chemins longs sur Windows.", "readme": os.path.join(os.getcwd(), "_internal/enable_long_paths.txt")},
    {"name": "Folder Name to TXT", "file": os.path.join(os.getcwd(), "_internal/folder_name_to_txt.exe"), "description": "Crée des fichiers TXT à partir des noms de dossiers.", "readme": os.path.join(os.getcwd(), "_internal/folder_name_to_txt.txt")},
    {"name": "Folder to ZIP", "file": os.path.join(os.getcwd(), "_internal/folder_to_zip.exe"), "description": "Compresse des fichiers de jeux en ZIP.", "readme": os.path.join(os.getcwd(), "_internal/folder_to_zip.txt")},
    {"name": "Game Batch Creator", "file": os.path.join(os.getcwd(), "_internal/game_batch_creator.exe"), "description": "Génère des fichiers batch pour lancer des jeux.", "readme": os.path.join(os.getcwd(), "_internal/game_batch_creator.txt")},
    {"name": "Game Removal Tool", "file": os.path.join(os.getcwd(), "_internal/game_removal.exe"), "description": "(Core) Supprime des jeux et leurs artworks.", "readme": os.path.join(os.getcwd(), "_internal/game_removal.txt")},
    {"name": "Gamelist to Hyperlist", "file": os.path.join(os.getcwd(), "_internal/gamelist_to_hyperlist.exe"), "description": "Convertit gamelist.xml en hyperlist.xml.", "readme": os.path.join(os.getcwd(), "_internal/gamelist_to_hyperlist.txt")},
    {"name": "Hyperlist to Gamelist", "file": os.path.join(os.getcwd(), "_internal/hyperlist_to_gamelist.exe"), "description": "Convertit hyperlist.xml en gamelist.xml.", "readme": os.path.join(os.getcwd(), "_internal/hyperlist_to_gamelist.txt")},
    {"name": "Install Dependencies", "file": os.path.join(os.getcwd(), "_internal/install_dependencies.exe"), "description": "Installe les dépendances système pour Windows.", "readme": os.path.join(os.getcwd(), "_internal/install_dependencies.txt")},
    {"name": "Liste Fichier Simple", "file": os.path.join(os.getcwd(), "_internal/liste_fichier_simple.exe"), "description": "Liste les fichiers dans un répertoire.", "readme": os.path.join(os.getcwd(), "_internal/liste_fichier_simple.txt")},
    {"name": "Liste Fichier Windows", "file": os.path.join(os.getcwd(), "_internal/liste_fichier_windows.exe"), "description": "Liste fichiers et dossiers sous Windows.", "readme": os.path.join(os.getcwd(), "_internal/liste_fichier_windows.txt")},
    {"name": "MaxCSO Compression Script", "file": os.path.join(os.getcwd(), "_internal/MaxCSO_Compression_Script.exe"), "description": "Compresse des fichiers ISO en CSO.", "readme": os.path.join(os.getcwd(), "_internal/MaxCSO_Compression_Script.txt")},
    {"name": "Media Orphan Detector", "file": os.path.join(os.getcwd(), "_internal/media_orphan_detector.exe"), "description": "(Core) Détecte et déplace les fichiers multimédias orphelins.", "readme": os.path.join(os.getcwd(), "_internal/media_orphan_detector.txt")},
    {"name": "Merge Story Hyperlist", "file": os.path.join(os.getcwd(), "_internal/merge_story_hyperlist.exe"), "description": "Intègre des histoires dans des hyperlistes XML.", "readme": os.path.join(os.getcwd(), "_internal/merge_story_hyperlist.txt")},
    {"name": "RVZ ISO Convert", "file": os.path.join(os.getcwd(), "_internal/rvz_iso_convert.exe"), "description": "Convertit entre formats RVZ et ISO.", "readme": os.path.join(os.getcwd(), "_internal/rvz_iso_convert.txt")},
    {"name": "Story Format Cleaner", "file": os.path.join(os.getcwd(), "_internal/story_format_cleaner.exe"), "description": "Nettoie les fichiers texte pour XML.", "readme": os.path.join(os.getcwd(), "_internal/story_format_cleaner.txt")},
    {"name": "Video Converter", "file": os.path.join(os.getcwd(), "_internal/video_converter.exe"), "description": "Convertit et rogne des vidéos par lot.", "readme": os.path.join(os.getcwd(), "_internal/video_converter.txt")},
]

# Interface graphique
class Application(ttk.Window):
    def __init__(self, scripts):
        super().__init__(themename="cosmo")
        self.title("Menu des Scripts")
        self.geometry("700x400")  # Taille par défaut
        
        self.scripts = scripts
        self.page = 0
        self.scripts_per_page = 5

        # Conteneur principal
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(expand=True, fill="both")

        # Créer les boutons de navigation
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill="x", pady=10)

        self.previous_button = ttk.Button(self.nav_frame, text="◀ Précédent", command=self.previous_page, bootstyle="secondary")
        self.previous_button.pack(side="left", padx=10)

        self.page_label = ttk.Label(self.nav_frame, text="Page 1", font=("Arial", 12))
        self.page_label.pack(side="left", expand=True)

        self.next_button = ttk.Button(self.nav_frame, text="Suivant ▶", command=self.next_page, bootstyle="secondary")
        self.next_button.pack(side="right", padx=10)

        # Afficher les scripts de la première page
        self.update_page()

    def update_page(self):
        # Efface les widgets existants
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Afficher les scripts de la page courante
        start_index = self.page * self.scripts_per_page
        end_index = start_index + self.scripts_per_page
        for script in self.scripts[start_index:end_index]:
            frame = ttk.Frame(self.main_frame, padding=5)
            frame.pack(fill="x", pady=5)

            # Charger l'icône directement depuis l'exécutable
            try:
                ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
                
                large, small = win32gui.ExtractIconEx(script["file"], 0)
                win32gui.DestroyIcon(small[0])
                
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                hdc.DrawIcon((0,0), large[0])
                
                bmpinfo = hbmp.GetInfo()
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                img = img.resize((32, 32), Image.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                
                icon_label = ttk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side="left", padx=10)
                
                win32gui.DestroyIcon(large[0])
            except Exception as e:
                print(f"Erreur lors du chargement de l'icône : {e}")
                # Utiliser une icône par défaut en cas d'erreur
                default_icon = ImageTk.PhotoImage(Image.new('RGBA', (32, 32), (0, 0, 0, 0)))
                icon_label = ttk.Label(frame, image=default_icon)
                icon_label.image = default_icon
                icon_label.pack(side="left", padx=10)

            # Bouton pour exécuter le script
            button = ttk.Button(frame, text=script["name"], command=lambda s=script["file"]: self.execute_script(s), bootstyle="primary")
            button.pack(side="left", padx=10)

            # Description du script
            label = ttk.Label(frame, text=script["description"], anchor="w", justify="left", font=("Arial", 10))
            label.pack(side="left", expand=True, fill="x")

            # Bouton "Lisez-moi"
            readme_button = ttk.Button(frame, text="Lisez-moi", command=lambda r=script["readme"]: self.open_readme(r), bootstyle="info")
            readme_button.pack(side="right", padx=10)

        # Mettre à jour l'indicateur de page
        total_pages = (len(self.scripts) - 1) // self.scripts_per_page + 1
        self.page_label.config(text=f"Page {self.page + 1} sur {total_pages}")

        # Activer/Désactiver les boutons de navigation
        self.previous_button.config(state="normal" if self.page > 0 else "disabled")
        self.next_button.config(state="normal" if end_index < len(self.scripts) else "disabled")

        # Ajuster la taille de la fenêtre
        self.update_idletasks()  # Applique les changements visuels
        self.geometry(f"700x{self.main_frame.winfo_reqheight() + 100}")  # Ajuste la hauteur

    def next_page(self):
        if (self.page + 1) * self.scripts_per_page < len(self.scripts):
            self.page += 1
            self.update_page()

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.update_page()

    def execute_script(self, script_file):
        try:
            import subprocess
            subprocess.run([script_file], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erreur", f"Le script {script_file} a échoué avec le code {e.returncode}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution de {script_file} : {e}")

    def open_readme(self, readme_file):
        try:
            if os.path.exists(readme_file):
                with open(readme_file, "r", encoding="utf-8") as file:
                    content = file.read()
                messagebox.showinfo("Lisez-moi", content)
            else:
                messagebox.showwarning("Lisez-moi", f"Le fichier {readme_file} n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier {readme_file} : {e}")

# Lancer l'application
if __name__ == "__main__":
    app = Application(scripts)
    app.mainloop()
