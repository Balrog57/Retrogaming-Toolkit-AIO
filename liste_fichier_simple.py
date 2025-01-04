import os
import tkinter as tk
from tkinter import filedialog, messagebox

def list_files_with_structure_and_save(root_dir, script_name):
    file_structure = []
    output_file = os.path.join(root_dir, "Liste.txt")
    
    # Parcourir les fichiers et sous-dossiers
    for root, dirs, files in os.walk(root_dir):
        relative_path = os.path.relpath(root, root_dir)
        if relative_path == '.':
            relative_path = ''
        
        for file in files:
            # Ignorer le script et le fichier de sortie
            if file not in {script_name, "Liste.txt"}:
                file_structure.append(os.path.join(relative_path, file))
    
    # Écrire la liste dans Liste.txt
    with open(output_file, 'w', encoding='utf-8') as f:
        for file in file_structure:
            f.write(file + '\n')
    
    messagebox.showinfo("Succès", f"Liste des fichiers sauvegardée dans : {output_file}")

def select_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)

def run_script():
    root_dir = folder_path_var.get()
    if not root_dir:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier.")
        return
    
    script_name = os.path.basename(__file__)
    list_files_with_structure_and_save(root_dir, script_name)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Liste des fichiers")

# Variables de contrôle
folder_path_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Dossier :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_directory).grid(row=0, column=2)

tk.Button(root, text="Générer la liste des fichiers", command=run_script).grid(row=1, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()