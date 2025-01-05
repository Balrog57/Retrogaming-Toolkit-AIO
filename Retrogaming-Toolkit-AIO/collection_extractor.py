# Module généré automatiquement à partir de collection_extractor.py

def main():
    import os
    import shutil
    import customtkinter as ctk
    from tkinter import filedialog, messagebox, ttk

    class ScrollableCTkComboBox(ctk.CTkFrame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master)
            self.combobox = ctk.CTkComboBox(self, **kwargs)
            self.combobox.pack(fill="both", expand=True)
            self.combobox.bind("<MouseWheel>", self._on_mousewheel)
            
        def configure(self, **kwargs):
            if 'values' in kwargs:
                self.combobox.configure(values=kwargs['values'])
            else:
                super().configure(**kwargs)
                
        def cget(self, key):
            if key == 'values':
                return self.combobox.cget('values')
            return super().cget(key)
            
        def _on_mousewheel(self, event):
            # Récupérer la liste des valeurs
            values = self.cget("values")
            if not values:
                return
                
            # Calculer le décalage en fonction de la direction de la molette
            delta = -1 if event.delta > 0 else 1
            
            # Récupérer l'index actuel
            current_index = self.current()
            new_index = current_index + delta
            
            # Vérifier les limites
            if new_index < 0:
                new_index = 0
            elif new_index >= len(values):
                new_index = len(values) - 1
                
            # Mettre à jour la sélection si nécessaire
            if new_index != current_index:
                self.current(new_index)
                self.event_generate("<<ComboboxSelected>>")
                
            # Empêcher la propagation de l'événement
            return "break"

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    def afficher_fin():
        messagebox.showinfo("Terminé", "Merci d'avoir utilisé ce script.\nCTP - Collection Extractor par Balrog - v1")
    
    def list_parent_menus(base_path):
        path = os.path.join(base_path, "collections/Main/menu")
        parents = [os.path.splitext(f)[0] for f in os.listdir(path) if f.endswith(".txt")]
        return parents
    
    def list_collections(base_path, parent):
        path = os.path.join(base_path, f"collections/{parent}/menu")
        if not os.path.exists(path):
            return []
        collections = [os.path.splitext(f)[0] for f in os.listdir(path) if f.endswith(".txt")]
        return collections
    
    def parse_settings_file(base_path, collection_name):
        settings_path = os.path.join(base_path, f"collections/{collection_name}/settings.conf")
        if not os.path.exists(settings_path):
            return None
        with open(settings_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('launcher'):
                    return line.split('=')[1].strip()
    
    def parse_launcher_file(base_path, launcher_name):
        launcher_conf_path = os.path.join(base_path, f"launchers.windows/{launcher_name}.conf")
        if not os.path.exists(launcher_conf_path):
            return None
        with open(launcher_conf_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('executable'):
                    return line.split('=')[1].strip()
    
    def create_and_move_files(base_path, collection, parent, collection_type, emulator_type, launcher=None):
        filepath = f"CTP - {collection}"
        os.makedirs(filepath, exist_ok=True)
        errors = []
        try:
            menu_src = os.path.join(base_path, f"collections/{parent}/menu/{collection}.txt")
            menu_dest = os.path.join(filepath, f"collections/{parent}/menu/")
            if os.path.exists(menu_src):
                os.makedirs(menu_dest, exist_ok=True)
                shutil.move(menu_src, menu_dest)
            else:
                errors.append(f"Fichier menu introuvable : {menu_src}")
            
            if collection_type == "Système":
                if emulator_type == "RetroArch":
                    core_name = launcher.split('[lr-')[1].split(']')[0]
                    core_src = os.path.join(base_path, f"./emulators/retroarch/cores/{core_name}_libretro.dll")
                    core_dest = os.path.join(filepath, f"emulators/retroarch/cores/")
                    if os.path.exists(core_src):
                        os.makedirs(core_dest, exist_ok=True)
                        shutil.move(core_src, core_dest)
                    else:
                        errors.append(f"Core RetroArch introuvable : {core_src}")
                    
                    launcher_conf_name = f"{collection} [lr-{core_name}].conf"
                    launcher_conf_src = os.path.join(base_path, f"launchers.windows/{launcher_conf_name}")
                    launcher_conf_dest = os.path.join(filepath, f"launchers.windows/")
                    if os.path.exists(launcher_conf_src):
                        os.makedirs(launcher_conf_dest, exist_ok=True)
                        shutil.move(launcher_conf_src, launcher_conf_dest)
                    else:
                        errors.append(f"Fichier launcher introuvable : {launcher_conf_src}")
    
                elif emulator_type == "Autre":
                    executable_path = parse_launcher_file(base_path, collection)
                    if executable_path:
                        emulator_dir_name = executable_path.split('\\')[1]
                        emulator_dir_src = os.path.join(base_path, f"./emulators/{emulator_dir_name}")
                        emulator_dir_dest = os.path.join(filepath, f"emulators/{emulator_dir_name}")
                        if os.path.exists(emulator_dir_src):
                            shutil.move(emulator_dir_src, emulator_dir_dest)
                        else:
                            errors.append(f"Dossier émulateur introuvable : {emulator_dir_src}")
    
                        launcher_conf_name = f"{collection}.conf"
                        launcher_conf_src = os.path.join(base_path, f"launchers.windows/{launcher_conf_name}")
                        launcher_conf_dest = os.path.join(filepath, f"launchers.windows/")
                        if os.path.exists(launcher_conf_src):
                            os.makedirs(launcher_conf_dest, exist_ok=True)
                            shutil.move(launcher_conf_src, launcher_conf_dest)
                        else:
                            errors.append(f"Fichier launcher introuvable : {launcher_conf_src}")
    
                collection_dir_src = os.path.join(base_path, f"collections/{collection}")
                collection_dir_dest = os.path.join(filepath, f"collections/")
                if os.path.exists(collection_dir_src):
                    shutil.move(collection_dir_src, collection_dir_dest)
                else:
                    errors.append(f"Dossier collection introuvable : {collection_dir_src}")
    
                layout_src = os.path.join(base_path, f"layouts/TITAN/collections/{collection}")
                layout_dest = os.path.join(filepath, f"layouts/TITAN/collections/")
                if os.path.exists(layout_src):
                    shutil.move(layout_src, layout_dest)
                else:
                    errors.append(f"Dossier layout introuvable : {layout_src}")
                
                hyperlist_src = os.path.join(base_path, f"meta/hyperlist/{collection}.xml")
                hyperlist_dest = os.path.join(filepath, f"meta/hyperlist/")
                if os.path.exists(hyperlist_src):
                    os.makedirs(hyperlist_dest, exist_ok=True)
                    shutil.move(hyperlist_src, hyperlist_dest)
                else:
                    errors.append(f"Fichier hyperlist introuvable : {hyperlist_src}")
                
                readme_src = os.path.join(base_path, f"Readme/{collection}.txt")
                readme_dest = os.path.join(filepath, f"Readme/")
                if os.path.exists(readme_src):
                    os.makedirs(readme_dest, exist_ok=True)
                    shutil.move(readme_src, readme_dest)
                else:
                    errors.append(f"Fichier README introuvable : {readme_src}")
    
            elif collection_type == "Collections":
                collection_dir_src = os.path.join(base_path, f"collections/{collection}")
                collection_dir_dest = os.path.join(filepath, f"collections/{collection}")
                if os.path.exists(collection_dir_src):
                    shutil.move(collection_dir_src, collection_dir_dest)
                else:
                    errors.append(f"Dossier collection introuvable : {collection_dir_src}")
                
                logo_src = os.path.join(base_path, f"collections/COLLECTIONS/medium_artwork/logo/{collection}.png")
                logo_dest = os.path.join(filepath, f"collections/COLLECTIONS/medium_artwork/logo/")
                if os.path.exists(logo_src):
                    os.makedirs(logo_dest, exist_ok=True)
                    shutil.move(logo_src, logo_dest)
                else:
                    errors.append(f"Logo introuvable : {logo_src}")
                
                layout_collection_src = os.path.join(base_path, f"layouts/TITAN/collections/{collection}")
                layout_collection_dest = os.path.join(filepath, f"layouts/TITAN/collections/")
                if os.path.exists(layout_collection_src):
                    shutil.move(layout_collection_src, layout_collection_dest)
                else:
                    errors.append(f"Dossier layout introuvable : {layout_collection_src}")
    
            report_path = os.path.join(filepath, f"{collection}-rapport.txt")
            with open(report_path, "w") as report_file:
                report_file.write(f"Dossier créé pour la collection '{collection}':\n\n")
                if errors:
                    report_file.write("Erreurs rencontrées :\n")
                    for error in errors:
                        report_file.write(f"- {error}\n")
                report_file.write("\nOpérations terminées.\n")
            
            messagebox.showinfo("Succès", f"Dossier pour '{collection}' créé avec succès. Rapport généré.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur critique est survenue lors du déplacement des fichiers: {e}")
    
    def run_script():
        base_path = base_path_var.get()
        if not base_path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de base.")
            return
        
        parent_menu = parent_var.get()
        collection_name = collection_var.get()
        collection_type = collection_type_var.get()
        emulator_type = emulator_type_var.get() if collection_type == "Système" else None
        
        launcher_from_settings = parse_settings_file(base_path, collection_name)
        create_and_move_files(base_path, collection_name, parent_menu, collection_type, emulator_type, launcher_from_settings)
    
    def select_base_directory():
        folder_selected = filedialog.askdirectory()
        base_path_var.set(folder_selected)
        update_parent_menus()
    
    def update_parent_menus():
        base_path = base_path_var.get()
        if base_path:
            parents = list_parent_menus(base_path)
            parent_menu_dropdown.combobox.configure(values=parents)
            if parents:
                parent_var.set(parents[0])
                update_collections()
    
    def update_collections():
        base_path = base_path_var.get()
        parent_menu = parent_var.get()
        if base_path and parent_menu:
            collections = list_collections(base_path, parent_menu)
            collection_dropdown.combobox.configure(values=collections)
            if collections:
                collection_var.set(collections[0])
    
    # Création de la fenêtre principale
    root = ctk.CTk()
    root.title("CTP - Collection Extractor")
    
    # Variables de contrôle
    base_path_var = ctk.StringVar()
    parent_var = ctk.StringVar()
    collection_var = ctk.StringVar()
    collection_type_var = ctk.StringVar(value="Système")
    emulator_type_var = ctk.StringVar(value="RetroArch")
    
    # Frame principal
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(padx=20, pady=20)
    
    # Interface utilisateur
    ctk.CTkLabel(main_frame, text="Dossier de base :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", pady=(0, 5))
    ctk.CTkEntry(main_frame, textvariable=base_path_var, width=400).grid(row=0, column=1, pady=(0, 10))
    ctk.CTkButton(main_frame, text="Parcourir", command=select_base_directory, width=100).grid(row=0, column=2, padx=10)
    
    ctk.CTkLabel(main_frame, text="Système parent :", font=("Arial", 16)).grid(row=1, column=0, sticky="w", pady=(0, 5))
    parent_menu_dropdown = ScrollableCTkComboBox(
        main_frame, 
        variable=parent_var, 
        command=lambda _: update_collections(),
        dropdown_font=("Arial", 12),
        height=30,
        width=400
    )
    parent_menu_dropdown.grid(row=1, column=1, sticky="ew", pady=(0, 10))
    
    ctk.CTkLabel(main_frame, text="Collection :", font=("Arial", 16)).grid(row=2, column=0, sticky="w", pady=(0, 5))
    collection_dropdown = ScrollableCTkComboBox(
        main_frame, 
        variable=collection_var,
        dropdown_font=("Arial", 12),
        height=30,
        width=400
    )
    collection_dropdown.grid(row=2, column=1, sticky="ew", pady=(0, 10))
    
    ctk.CTkLabel(main_frame, text="Type de collection :", font=("Arial", 16)).grid(row=3, column=0, sticky="w", pady=(0, 5))
    ctk.CTkRadioButton(main_frame, text="Système", variable=collection_type_var, value="Système").grid(row=3, column=1, sticky="w", pady=(0, 5))
    ctk.CTkRadioButton(main_frame, text="Collections", variable=collection_type_var, value="Collections").grid(row=3, column=2, sticky="w", pady=(0, 5))
    
    ctk.CTkLabel(main_frame, text="Type d'émulateur :", font=("Arial", 16)).grid(row=4, column=0, sticky="w", pady=(0, 5))
    ctk.CTkRadioButton(main_frame, text="RetroArch", variable=emulator_type_var, value="RetroArch").grid(row=4, column=1, sticky="w", pady=(0, 5))
    ctk.CTkRadioButton(main_frame, text="Autre", variable=emulator_type_var, value="Autre").grid(row=4, column=2, sticky="w", pady=(0, 5))
    
    ctk.CTkButton(main_frame, text="Exécuter", command=run_script, width=200).grid(row=5, column=1, pady=20)
    
    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()
