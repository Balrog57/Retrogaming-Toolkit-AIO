# Module généré automatiquement à partir de media_orphan_detector.py

def main():
    import os
    import shutil
    import customtkinter as ctk
    from tkinter import messagebox
    from tkinter import filedialog

    # Configuration du thème sombre et de la couleur bleue
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    def detect_orphan_files(roms_dir):
        # Define the medium_artwork directory (same level as roms)
        medium_artwork_dir = os.path.join(os.path.dirname(roms_dir), "medium_artwork")

        # Check if medium_artwork directory exists
        if not os.path.exists(medium_artwork_dir):
            messagebox.showerror("Erreur", f"Le dossier 'medium_artwork' n'existe pas dans le même répertoire que 'roms'.")
            return

        # Get list of rom files once to avoid N+1 filesystem checks
        rom_files = set()
        valid_extensions = {".txt", ".png", ".jpg", ".zip", ".bin"}
        if os.path.exists(roms_dir):
            for f in os.listdir(roms_dir):
                name, ext = os.path.splitext(f)
                if ext.lower() in valid_extensions:
                    rom_files.add(os.path.normcase(name))

        # Iterate over each subdirectory in 'medium_artwork'
        for subdir in os.listdir(medium_artwork_dir):
            subdir_path = os.path.join(medium_artwork_dir, subdir)

            if os.path.isdir(subdir_path):
                # Create an 'orphan' directory inside the current subdirectory
                orphan_dir = os.path.join(subdir_path, "orphan")
                os.makedirs(orphan_dir, exist_ok=True)

                # Iterate over each file in the current subdirectory
                for file in os.listdir(subdir_path):
                    file_path = os.path.join(subdir_path, file)
                    file_name_without_ext = os.path.splitext(file)[0]

                    # Skip files named "default" and the 'orphan' directory itself
                    if file_name_without_ext.lower() == "default" or file == "orphan":
                        continue

                    # Check if a corresponding file exists in the 'roms' directory
                    if os.path.normcase(file_name_without_ext) not in rom_files:
                        # Move the file to the 'orphan' directory inside the current subdirectory
                        shutil.move(file_path, orphan_dir)

        messagebox.showinfo("Succès", "La détection des fichiers orphelins est terminée.")

    def select_roms_directory():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            roms_dir_var.set(folder_selected)

    def run_script():
        roms_dir = roms_dir_var.get()

        if not roms_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner le dossier 'roms'.")
            return

        detect_orphan_files(roms_dir)

    # Création de la fenêtre principale avec customtkinter
    root = ctk.CTk()
    root.title("Media Orphan Detector")

    # Variables de contrôle
    roms_dir_var = ctk.StringVar()

    # Interface utilisateur
    ctk.CTkLabel(root, text="Dossier 'roms' :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=roms_dir_var, width=300).grid(row=0, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_roms_directory, width=100).grid(row=0, column=2, padx=10, pady=10)

    ctk.CTkButton(root, text="Détecter les fichiers orphelins", command=run_script, width=200).grid(row=1, column=1, pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()