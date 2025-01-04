import os
import shutil
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
games_path = ""

def clear_console():
    # Check the operating system and clear the console accordingly
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def select_parent_menu():
    parent_menus = ["ARCADES", "CONSOLES", "HANDHELDS", "COMPUTERS", "PINBALL"]
    return parent_menus

def select_system(parent, base_dir):
    system_path = os.path.join(base_dir, "collections", parent, "menu")
    systems = [f[:-4] for f in os.listdir(system_path) if f.endswith(".txt")]
    return systems

def select_games(system, base_dir):
    global games_path
    games_path = os.path.join(base_dir, "collections", system, "roms")
    games = [f[:-4] for f in os.listdir(games_path) if os.path.isfile(os.path.join(games_path, f))]
    return games

def confirm_deletion(games):
    folders_to_delete = []
    for game in games:
        folder = os.path.join(games_path, game)
        if os.path.isdir(folder):
            folders_to_delete.append(folder)
    return folders_to_delete

def delete_games(system, games, folders, base_dir):
    games_path = os.path.join(base_dir, "collections", system, "roms")
    art_path = os.path.join(base_dir, "collections", system, "artwork")
    medium_art_path = os.path.join(base_dir, "collections", system, "medium_artwork")

    for game in games:
        game_files = glob.glob(os.path.join(games_path, game + ".*"))
        art_files = glob.glob(os.path.join(art_path, game + ".*"))
        medium_art_files = glob.glob(os.path.join(medium_art_path, "**", game + ".*"), recursive=True)

        for file in game_files:
            os.remove(file)
            print(f"Deleted game file: {file}")

        for file in art_files:
            os.remove(file)
            print(f"Deleted artwork file: {file}")

        for file in medium_art_files:
            os.remove(file)
            print(f"Deleted medium artwork file: {file}")

    for folder in folders:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
            print(f"Deleted folder: {folder}")

def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_var.set(folder_selected)
    update_parent_menus()

def update_parent_menus():
    base_dir = folder_path_var.get()
    if base_dir:
        parent_menus = select_parent_menu()
        parent_menu_dropdown['values'] = parent_menus
        if parent_menus:
            parent_var.set(parent_menus[0])
            update_systems()

def update_systems():
    base_dir = folder_path_var.get()
    parent_menu = parent_var.get()
    if base_dir and parent_menu:
        systems = select_system(parent_menu, base_dir)
        system_dropdown['values'] = systems
        if systems:
            system_var.set(systems[0])
            update_games()

def update_games():
    base_dir = folder_path_var.get()
    system = system_var.get()
    if base_dir and system:
        games = select_games(system, base_dir)
        game_listbox.delete(0, tk.END)
        for game in games:
            game_listbox.insert(tk.END, game)

def run_script():
    base_dir = folder_path_var.get()
    parent_menu = parent_var.get()
    system = system_var.get()
    selected_games = [game_listbox.get(idx) for idx in game_listbox.curselection()]
    
    if not base_dir:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier.")
        return
    if not parent_menu:
        messagebox.showerror("Erreur", "Veuillez sélectionner un menu parent.")
        return
    if not system:
        messagebox.showerror("Erreur", "Veuillez sélectionner un système.")
        return
    if not selected_games:
        messagebox.showerror("Erreur", "Veuillez sélectionner au moins un jeu.")
        return
    
    folders_to_delete = confirm_deletion(selected_games)
    confirm = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer les jeux sélectionnés ?")
    if confirm:
        delete_games(system, selected_games, folders_to_delete, base_dir)
        messagebox.showinfo("Succès", "Les jeux sélectionnés ont été supprimés avec succès.")
        update_games()

# Création de la fenêtre principale
root = tk.Tk()
root.title("CORE - TYPE R Game Deletion Script")

# Variables de contrôle
folder_path_var = tk.StringVar()
parent_var = tk.StringVar()
system_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Dossier de base :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_folder).grid(row=0, column=2)

tk.Label(root, text="Menu parent :").grid(row=1, column=0, sticky="w")
parent_menu_dropdown = ttk.Combobox(root, textvariable=parent_var)
parent_menu_dropdown.grid(row=1, column=1, sticky="ew")
parent_menu_dropdown.bind('<<ComboboxSelected>>', lambda _: update_systems())

tk.Label(root, text="Système :").grid(row=2, column=0, sticky="w")
system_dropdown = ttk.Combobox(root, textvariable=system_var)
system_dropdown.grid(row=2, column=1, sticky="ew")
system_dropdown.bind('<<ComboboxSelected>>', lambda _: update_games())

tk.Label(root, text="Jeux :").grid(row=3, column=0, sticky="w")
game_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
game_listbox.grid(row=3, column=1, sticky="ew")

tk.Button(root, text="Supprimer les jeux sélectionnés", command=run_script).grid(row=4, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()