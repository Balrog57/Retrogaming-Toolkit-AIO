import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def create_txt_files(folder_path, input_ext):
    """
    Create an empty .txt file for each file with the specified input extension in the selected directory.
    """
    # Ensure the input extension starts with a dot
    if not input_ext.startswith("."):
        input_ext = f".{input_ext}"

    # Process files in the selected directory
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(input_ext):
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(folder_path, f"{base_name}.txt")
                # Create an empty .txt file
                with open(output_file, 'w') as file:
                    pass
                print(f"Created: {output_file}")
        messagebox.showinfo("Succès", "Les fichiers .txt ont été créés avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_var.set(folder_selected)

def run_script():
    folder_path = folder_path_var.get()
    input_ext = input_extension_var.get().strip()
    
    if not folder_path:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier.")
        return
    if not input_ext:
        messagebox.showerror("Erreur", "Veuillez entrer une extension de fichier.")
        return
    
    create_txt_files(folder_path, input_ext)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Créateur de fichiers .txt")

# Variables de contrôle
folder_path_var = tk.StringVar()
input_extension_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Dossier :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_folder).grid(row=0, column=2)

tk.Label(root, text="Extension des fichiers (ex: 'mp4') :").grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=input_extension_var, width=50).grid(row=1, column=1)

tk.Button(root, text="Créer les fichiers .txt", command=run_script).grid(row=2, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()