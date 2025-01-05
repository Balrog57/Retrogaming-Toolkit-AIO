import os
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog

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

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

# Création de la fenêtre principale
root = ctk.CTk()
root.title("Créateur de fichiers .txt")

# Variables de contrôle
folder_path_var = ctk.StringVar()
input_extension_var = ctk.StringVar()

# Interface utilisateur
ctk.CTkLabel(root, text="Dossier :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
ctk.CTkEntry(root, textvariable=folder_path_var, width=300).grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(root, text="Parcourir", command=select_folder, width=100).grid(row=0, column=2, padx=10, pady=10)

ctk.CTkLabel(root, text="Extension des fichiers (ex: 'mp4') :", font=("Arial", 16)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
ctk.CTkEntry(root, textvariable=input_extension_var, width=300).grid(row=1, column=1, padx=10, pady=10)

ctk.CTkButton(root, text="Créer les fichiers .txt", command=run_script, width=200).grid(row=2, column=1, pady=20)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()