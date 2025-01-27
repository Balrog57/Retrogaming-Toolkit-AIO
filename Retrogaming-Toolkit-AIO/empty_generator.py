import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

class EmptyFileCreatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.title("Empty File Creator")
        self.geometry("600x400")

        # Variables pour stocker le dossier et l'extension
        self.folder_path = None
        self.selected_extension = ctk.StringVar(value="scummvm")  # Extension par défaut
        self.custom_extension = None  # Pour stocker l'extension personnalisée

        # Setup de l'interface
        self.setup_ui()

    def setup_ui(self):
        # Label principal
        label = ctk.CTkLabel(self, text="Empty File Creator", font=("Arial", 16))
        label.pack(pady=10)

        # Options d'extension (verrouillées)
        extensions_frame = ctk.CTkFrame(self)
        extensions_frame.pack(pady=10)

        # Boutons radio pour les extensions prédéfinies
        self.scummvm_radio = ctk.CTkRadioButton(extensions_frame, text=".scummvm", variable=self.selected_extension, value="scummvm")
        self.scummvm_radio.pack(pady=5, anchor="w")

        self.singe_radio = ctk.CTkRadioButton(extensions_frame, text=".singe", variable=self.selected_extension, value="singe")
        self.singe_radio.pack(pady=5, anchor="w")

        self.cgenius_radio = ctk.CTkRadioButton(extensions_frame, text=".cgenius", variable=self.selected_extension, value="cgenius")
        self.cgenius_radio.pack(pady=5, anchor="w")

        # Option "Autre" avec un champ de saisie
        self.autre_radio = ctk.CTkRadioButton(extensions_frame, text="Autre", variable=self.selected_extension, value="autre")
        self.autre_radio.pack(pady=5, anchor="w")

        # Champ de saisie pour une extension personnalisée
        self.custom_extension_entry = ctk.CTkEntry(extensions_frame, placeholder_text="Entrez une extension personnalisée")
        self.custom_extension_entry.pack(pady=5)
        self.custom_extension_entry.pack_forget()  # Masqué par défaut

        # Gestion du changement de sélection des boutons radio
        self.selected_extension.trace_add("write", self.on_extension_change)

        # Bouton pour choisir le dossier
        folder_button = ctk.CTkButton(self, text="Choisir un dossier", command=self.choose_folder)
        folder_button.pack(pady=10)

        # Bouton pour créer les fichiers
        create_button = ctk.CTkButton(self, text="Créer les fichiers", command=self.create_files)
        create_button.pack(pady=10)

    def on_extension_change(self, *args):
        """Affiche ou masque le champ de saisie pour une extension personnalisée."""
        if self.selected_extension.get() == "autre":
            self.custom_extension_entry.pack(pady=5)  # Affiche le champ de saisie
        else:
            self.custom_extension_entry.pack_forget()  # Masque le champ de saisie

    def choose_folder(self):
        """Ouvre une boîte de dialogue pour choisir un dossier."""
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("Dossier sélectionné", f"Dossier choisi : {self.folder_path}")

    def create_files(self):
        """Crée les fichiers dans les sous-dossiers avec l'extension choisie."""
        if not self.folder_path:
            messagebox.showerror("Erreur", "Veuillez choisir un dossier.")
            return

        # Détermine l'extension à utiliser
        if self.selected_extension.get() == "autre":
            extension = self.custom_extension_entry.get().strip()
            if not extension:
                messagebox.showerror("Erreur", "Veuillez entrer une extension personnalisée.")
                return
        else:
            extension = self.selected_extension.get()

        # Parcourt les sous-dossiers et crée les fichiers
        for folder_name in os.listdir(self.folder_path):
            folder_full_path = os.path.join(self.folder_path, folder_name)
            if os.path.isdir(folder_full_path):
                file_name = f"{folder_name}.{extension}"
                file_path = os.path.join(folder_full_path, file_name)
                with open(file_path, 'w'):
                    pass
                print(f"Created {file_name} in {folder_full_path}")

        messagebox.showinfo("Succès", f"Les fichiers .{extension} ont été créés avec succès.")

if __name__ == "__main__":
    app = EmptyFileCreatorApp()
    app.mainloop()