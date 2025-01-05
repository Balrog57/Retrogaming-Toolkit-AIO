import os
import glob
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GameDeletionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CORE-TYPE R Game Deletion Script")
        self.root.geometry("800x600")

        self.base_dir = ""
        self.selected_main = ""
        self.selected_system = ""
        self.selected_games = []

        self.create_widgets()

    def create_widgets(self):
        # Frame principale pour organiser les champs de sélection
        self.frame_selection = ctk.CTkFrame(self.root)
        self.frame_selection.pack(pady=10, fill="x", padx=20)

        # Sélection du dossier de base
        self.label_base_dir = ctk.CTkLabel(self.frame_selection, text="Sélectionnez le dossier de base :", font=("Arial", 14))
        self.label_base_dir.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.button_base_dir = ctk.CTkButton(self.frame_selection, text="Parcourir", command=self.select_base_dir, width=100)
        self.button_base_dir.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Sélection dans Main
        self.label_main = ctk.CTkLabel(self.frame_selection, text="Sélectionnez un fichier dans Main :", font=("Arial", 14))
        self.label_main.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.combo_main = ctk.CTkOptionMenu(self.frame_selection, values=[], width=200)
        self.combo_main.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.button_confirm_main = ctk.CTkButton(self.frame_selection, text="→", width=30, command=self.confirm_main)
        self.button_confirm_main.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Sélection du système
        self.label_system = ctk.CTkLabel(self.frame_selection, text="Sélectionnez un système :", font=("Arial", 14))
        self.label_system.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.combo_system = ctk.CTkOptionMenu(self.frame_selection, values=[], width=200)
        self.combo_system.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.button_confirm_system = ctk.CTkButton(self.frame_selection, text="→", width=30, command=self.confirm_system)
        self.button_confirm_system.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        # Frame pour la sélection des jeux
        self.frame_games = ctk.CTkFrame(self.root)
        self.frame_games.pack(pady=10, fill="both", expand=True, padx=20)

        self.label_games = ctk.CTkLabel(self.frame_games, text="Sélectionnez un ou plusieurs jeux :", font=("Arial", 14))
        self.label_games.pack(pady=10)

        self.canvas_games = ctk.CTkCanvas(self.frame_games, bg="gray20")
        self.canvas_games.pack(side="left", fill="both", expand=True)

        self.scrollbar_games = ctk.CTkScrollbar(self.frame_games, orientation="vertical", command=self.canvas_games.yview)
        self.scrollbar_games.pack(side="right", fill="y")

        self.canvas_games.configure(yscrollcommand=self.scrollbar_games.set)
        self.canvas_games.bind("<Configure>", lambda e: self.canvas_games.configure(scrollregion=self.canvas_games.bbox("all")))

        self.frame_checkboxes = ctk.CTkFrame(self.canvas_games, fg_color="gray20")
        self.canvas_games.create_window((0, 0), window=self.frame_checkboxes, anchor="nw")

        # Bouton de suppression
        self.button_delete = ctk.CTkButton(self.root, text="Supprimer les jeux sélectionnés", command=self.delete_games, width=200)
        self.button_delete.pack(pady=20)

        # Verrouillage des étapes
        self.lock_steps()

    def lock_steps(self):
        """Verrouille les étapes suivantes jusqu'à ce que la sélection soit confirmée."""
        self.combo_system.configure(state="disabled")
        self.button_confirm_system.configure(state="disabled")
        self.canvas_games.configure(state="disabled")
        self.button_delete.configure(state="disabled")

    def unlock_system_selection(self):
        """Déverrouille la sélection du système."""
        self.combo_system.configure(state="normal")
        self.button_confirm_system.configure(state="normal")

    def unlock_games_selection(self):
        """Déverrouille la sélection des jeux."""
        self.canvas_games.configure(state="normal")
        self.button_delete.configure(state="normal")

    def select_base_dir(self):
        self.base_dir = filedialog.askdirectory()
        print(f"[LOG] Dossier de base sélectionné : {self.base_dir}")
        if self.base_dir:
            self.load_main_files()

    def load_main_files(self):
        main_dir = os.path.join(self.base_dir, "collections", "Main", "menu")
        print(f"[LOG] Chargement des fichiers dans Main/menu : {main_dir}")
        if os.path.exists(main_dir):
            main_files = [f[:-4] for f in os.listdir(main_dir) if f.endswith(".txt")]
            print(f"[LOG] Fichiers trouvés dans Main/menu : {main_files}")
            self.combo_main.configure(values=main_files)
            self.combo_main.set("")  # Réinitialiser la sélection
        else:
            print(f"[ERREUR] Le dossier {main_dir} n'existe pas.")

    def confirm_main(self):
        self.selected_main = self.combo_main.get()
        print(f"[LOG] Fichier Main sélectionné : {self.selected_main}")
        if self.selected_main:
            self.load_systems()
            self.unlock_system_selection()  # Déverrouille la sélection du système
        else:
            print("[ERREUR] Aucun fichier Main sélectionné.")

    def load_systems(self):
        systems_dir = os.path.join(self.base_dir, "collections", self.selected_main, "menu")
        print(f"[LOG] Chargement des systèmes depuis : {systems_dir}")
        if os.path.exists(systems_dir):
            systems = [f[:-4] for f in os.listdir(systems_dir) if f.endswith(".txt")]
            print(f"[LOG] Systèmes trouvés : {systems}")
            self.combo_system.configure(values=systems)
            self.combo_system.set("")  # Réinitialiser la sélection
        else:
            print(f"[ERREUR] Le dossier {systems_dir} n'existe pas.")

    def confirm_system(self):
        self.selected_system = self.combo_system.get()
        print(f"[LOG] Système sélectionné : {self.selected_system}")
        if self.selected_system:
            self.load_games()
            self.unlock_games_selection()  # Déverrouille la sélection des jeux
        else:
            print("[ERREUR] Aucun système sélectionné.")

    def load_games(self):
        games_dir = os.path.join(self.base_dir, "collections", self.selected_system, "roms")
        print(f"[LOG] Chargement des jeux depuis : {games_dir}")
        if os.path.exists(games_dir):
            # Liste uniquement les fichiers (pas les dossiers)
            games = [f for f in os.listdir(games_dir) if os.path.isfile(os.path.join(games_dir, f))]
            print(f"[LOG] Jeux trouvés : {games}")

            # Effacer les anciennes cases à cocher
            for widget in self.frame_checkboxes.winfo_children():
                widget.destroy()

            # Ajouter des cases à cocher pour chaque jeu
            for game in games:
                checkbox = ctk.CTkCheckBox(self.frame_checkboxes, text=game)
                checkbox.pack(anchor="w")

            # Ajuster la taille de la fenêtre des jeux
            self.canvas_games.update_idletasks()
            self.canvas_games.configure(scrollregion=self.canvas_games.bbox("all"))

        else:
            print(f"[ERREUR] Le dossier {games_dir} n'existe pas.")

    def delete_games(self):
        selected_games = [checkbox.cget("text") for checkbox in self.frame_checkboxes.winfo_children() if checkbox.get() == 1]
        if not selected_games:
            messagebox.showwarning("Aucun jeu sélectionné", "Veuillez sélectionner au moins un jeu à supprimer.")
            return

        confirm = messagebox.askyesno("Confirmer la suppression", "Êtes-vous sûr de vouloir supprimer les jeux sélectionnés ?")
        if confirm:
            for game in selected_games:
                self.delete_game_files(game)
            messagebox.showinfo("Suppression terminée", "Les jeux sélectionnés ont été supprimés avec succès.")
            self.load_games()  # Rafraîchir la liste des jeux après la suppression

    def delete_game_files(self, game):
        games_path = os.path.join(self.base_dir, "collections", self.selected_system, "roms")
        medium_art_path = os.path.join(self.base_dir, "collections", self.selected_system, "medium_artwork")

        # Supprimer les fichiers de jeu
        game_files = glob.glob(os.path.join(games_path, game))
        if not game_files:
            print(f"[ERREUR] Aucun fichier trouvé pour le jeu : {game}")
        else:
            for file in game_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"[LOG] Fichier de jeu supprimé : {file}")
                else:
                    print(f"[ERREUR] Fichier de jeu introuvable : {file}")

        # Supprimer les fichiers média associés
        medium_art_files = glob.glob(os.path.join(medium_art_path, "**", os.path.splitext(game)[0] + ".*"), recursive=True)
        if not medium_art_files:
            print(f"[ERREUR] Aucun fichier média trouvé pour le jeu : {game}")
        else:
            for file in medium_art_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"[LOG] Fichier média supprimé : {file}")
                else:
                    print(f"[ERREUR] Fichier média introuvable : {file}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = GameDeletionApp(root)
    root.mainloop()