import os
import zipfile
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

class BGBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGBackup")
        self.root.geometry("400x200")

        # En-tête de la GUI
        self.header_label = ctk.CTkLabel(root, text="BGBackup", font=("Arial", 24))
        self.header_label.pack(pady=20)

        # Bouton pour sélectionner le dossier roms
        self.select_button = ctk.CTkButton(root, text="Sélectionner le dossier roms", command=self.select_roms_folder, width=200)
        self.select_button.pack(pady=10)

        # Bouton pour créer le backup
        self.backup_button = ctk.CTkButton(root, text="Créer le backup", command=self.create_backup, width=200, state="disabled")
        self.backup_button.pack(pady=10)

        # Variable pour stocker le chemin du dossier roms
        self.roms_folder = None

    def select_roms_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier roms."""
        self.roms_folder = filedialog.askdirectory(title="Sélectionnez le dossier roms")
        if self.roms_folder:
            self.backup_button.configure(state="normal")  # Active le bouton de backup

    def create_backup(self):
        """Parcourt les sous-dossiers, récupère les fichiers gamelist.xml et les compresse dans un ZIP en conservant la structure des dossiers."""
        if not self.roms_folder:
            messagebox.showerror("Erreur", "Aucun dossier roms sélectionné.")
            return

        # Création du fichier ZIP
        zip_filename = "gamelist_backup.zip"
        try:
            with zipfile.ZipFile(zip_filename, "w") as zipf:
                # Parcours des sous-dossiers sur 2 niveaux
                for root_dir, dirs, files in os.walk(self.roms_folder):
                    if "gamelist.xml" in files:
                        gamelist_path = os.path.join(root_dir, "gamelist.xml")
                        # Calcul du chemin relatif pour conserver la structure des dossiers
                        relative_path = os.path.relpath(gamelist_path, self.roms_folder)
                        # Ajout du fichier au ZIP avec le chemin relatif
                        zipf.write(gamelist_path, relative_path)

                    # Limite la profondeur de recherche à 2 niveaux
                    if os.path.relpath(root_dir, self.roms_folder).count(os.sep) >= 2:
                        dirs.clear()

            messagebox.showinfo("Succès", f"Backup créé avec succès : {zip_filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du ZIP : {e}")

def main():
    root = ctk.CTk()
    app = BGBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()