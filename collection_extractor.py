import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def afficher_fin():
    messagebox.showinfo("Terminé", "Merci d'avoir utilisé ce script.\nCTP - Collection Extractor par Balrog - v1")

def list_parent_menus(base_path):
    path = os.path.join(base_path, "collections/Main/menu")
    parents = [os.path.splitext(f)[0] for f in os.listdir(path) if f.endswith(".txt")]
    return parents

def list_collections(base_path, parent):
    path = os.path.join(base_path, f"collections/{parent}/menu")
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
        parent_menu_dropdown['values'] = parents
        if parents:
            parent_var.set(parents[0])
            update_collections()

def update_collections():
    base_path = base_path_var.get()
    parent_menu = parent_var.get()
    if base_path and parent_menu:
        collections = list_collections(base_path, parent_menu)
        collection_dropdown['values'] = collections
        if collections:
            collection_var.set(collections[0])

# Création de la fenêtre principale
root = tk.Tk()
root.title("CTP - Collection Extractor")

# Variables de contrôle
base_path_var = tk.StringVar()
parent_var = tk.StringVar()
collection_var = tk.StringVar()
collection_type_var = tk.StringVar(value="Système")
emulator_type_var = tk.StringVar(value="RetroArch")

# Interface utilisateur
tk.Label(root, text="Dossier de base :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=base_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_base_directory).grid(row=0, column=2)

tk.Label(root, text="Système parent :").grid(row=1, column=0, sticky="w")
parent_menu_dropdown = ttk.Combobox(root, textvariable=parent_var)
parent_menu_dropdown.grid(row=1, column=1, sticky="ew")
parent_menu_dropdown.bind('<<ComboboxSelected>>', lambda _: update_collections())

tk.Label(root, text="Collection :").grid(row=2, column=0, sticky="w")
collection_dropdown = ttk.Combobox(root, textvariable=collection_var)
collection_dropdown.grid(row=2, column=1, sticky="ew")

tk.Label(root, text="Type de collection :").grid(row=3, column=0, sticky="w")
ttk.Radiobutton(root, text="Système", variable=collection_type_var, value="Système").grid(row=3, column=1, sticky="w")
ttk.Radiobutton(root, text="Collections", variable=collection_type_var, value="Collections").grid(row=3, column=2, sticky="w")

tk.Label(root, text="Type d'émulateur :").grid(row=4, column=0, sticky="w")
ttk.Radiobutton(root, text="RetroArch", variable=emulator_type_var, value="RetroArch").grid(row=4, column=1, sticky="w")
ttk.Radiobutton(root, text="Autre", variable=emulator_type_var, value="Autre").grid(row=4, column=2, sticky="w")

tk.Button(root, text="Exécuter", command=run_script).grid(row=5, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()