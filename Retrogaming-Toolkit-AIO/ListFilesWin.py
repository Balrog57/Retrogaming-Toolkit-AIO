# Module généré automatiquement à partir de liste_fichier_windows.py

def main():
    import os
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    
    # Configuration du thème
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
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
    root = ctk.CTk()
    root.title("Liste des fichiers et dossiers")
    
    # Variables de contrôle
    folder_path_var = ctk.StringVar()
    
    # Interface utilisateur
    ctk.CTkLabel(root, text="Dossier :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=folder_path_var, width=400).grid(row=0, column=1, padx=10)
    ctk.CTkButton(root, text="Parcourir", command=select_directory, width=200).grid(row=0, column=2, padx=10)
    
    ctk.CTkButton(root, text="Générer la liste", command=run_script, width=200).grid(row=1, column=1, pady=20)
    
    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()
