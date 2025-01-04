import os
import tkinter as tk
from tkinter import filedialog, messagebox

def list_files_and_directories(directory):
    # Get the list of files and directories in the selected directory
    entries = os.listdir(directory)
    output_file = os.path.join(directory, "Liste.txt")
    
    # Write the list to 'Liste.txt'
    with open(output_file, "w", encoding="utf-8") as file:
        for entry in entries:
            file.write(f"{entry}\n")
    
    messagebox.showinfo("Succès", f"La liste des fichiers et dossiers a été sauvegardée dans : {output_file}")

def select_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)

def run_script():
    directory = folder_path_var.get()
    if not directory:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier.")
        return
    
    list_files_and_directories(directory)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Liste des fichiers et dossiers")

# Variables de contrôle
folder_path_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Dossier :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_directory).grid(row=0, column=2)

tk.Button(root, text="Générer la liste", command=run_script).grid(row=1, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()