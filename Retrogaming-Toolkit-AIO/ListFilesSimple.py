# Module généré automatiquement à partir de liste_fichier_simple.py

def main():
    import os
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
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
    root = ctk.CTk()
    root.title("Liste des fichiers")
    
    # Variables de contrôle
    folder_path_var = ctk.StringVar()
    
    # Interface utilisateur
    ctk.CTkLabel(root, text="Dossier :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=folder_path_var, width=400).grid(row=0, column=1, padx=10)
    ctk.CTkButton(root, text="Parcourir", command=select_directory, width=100).grid(row=0, column=2, padx=10)
    
    ctk.CTkButton(root, 
                 text="Générer la liste des fichiers", 
                 command=run_script,
                 width=200,
                 font=("Arial", 16)).grid(row=1, column=1, pady=20)
    
    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()
