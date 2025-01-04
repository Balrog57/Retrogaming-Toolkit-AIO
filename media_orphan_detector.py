import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def detect_orphan_files(roms_dir):
    # Define the medium_artwork directory (same level as roms)
    medium_artwork_dir = os.path.join(os.path.dirname(roms_dir), "medium_artwork")

    # Check if medium_artwork directory exists
    if not os.path.exists(medium_artwork_dir):
        messagebox.showerror("Erreur", f"Le dossier 'medium_artwork' n'existe pas dans le même répertoire que 'roms'.")
        return

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
                roms_file_path = os.path.join(roms_dir, f"{file_name_without_ext}.*")
                if not any([os.path.exists(roms_file_path.replace("*", ext)) for ext in ["txt", "png", "jpg", "zip", "bin"]]):
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

# Création de la fenêtre principale
root = tk.Tk()
root.title("Media Orphan Detector")

# Variables de contrôle
roms_dir_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Dossier 'roms' :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=roms_dir_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_roms_directory).grid(row=0, column=2)

tk.Button(root, text="Détecter les fichiers orphelins", command=run_script).grid(row=1, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()