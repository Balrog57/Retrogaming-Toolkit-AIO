import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def load_gamelist(file_path):
    try:
        tree = ET.parse(file_path)
    except ET.ParseError:
        messagebox.showerror("Erreur", f"Erreur de format dans le fichier {file_path}. Le fichier sera ignoré.")
        return []

    root = tree.getroot()
    games = []

    for game_elem in root.findall('game'):
        name = game_elem.find('name').text if game_elem.find('name') is not None else ""
        path = game_elem.find('path').text if game_elem.find('path') is not None else ""
        desc = game_elem.find('desc').text if game_elem.find('desc') is not None else ""
        releasedate = game_elem.find('releasedate').text if game_elem.find('releasedate') is not None else ""
        developer = game_elem.find('developer').text if game_elem.find('developer') is not None else ""
        publisher = game_elem.find('publisher').text if game_elem.find('publisher') is not None else ""
        genre = game_elem.find('genre').text if game_elem.find('genre') is not None else ""
        rating = game_elem.find('rating').text if game_elem.find('rating') is not None else "0"
        players = game_elem.find('players').text if game_elem.find('players') is not None else "1"

        year = releasedate[:4] if releasedate and len(releasedate) >= 4 else ""

        games.append({
            'name': name,
            'path': path,
            'desc': desc,
            'year': year,
            'manufacturer': developer,
            'publisher': publisher,
            'genre': genre,
            'score': str(round(float(rating) * 5, 2)),
            'players': players
        })

    return games

def write_hyperlist(games, output_file, desc_dir):
    root = ET.Element('menu')

    # Créer un dossier pour les descriptions
    os.makedirs(desc_dir, exist_ok=True)

    for game in games:
        game_elem = ET.SubElement(root, 'game', name=game['name'])
        ET.SubElement(game_elem, 'manufacturer').text = game['manufacturer']
        ET.SubElement(game_elem, 'year').text = game['year']
        ET.SubElement(game_elem, 'publisher').text = game['publisher']
        ET.SubElement(game_elem, 'genre').text = game['genre']
        ET.SubElement(game_elem, 'score').text = game['score']
        ET.SubElement(game_elem, 'players').text = game['players']

        # Ajouter une balise <description> avec le nom du jeu
        ET.SubElement(game_elem, 'description').text = game['name']

        # Créer un fichier texte pour la description
        rom_name = os.path.splitext(os.path.basename(game['path']))[0]
        desc_file_path = os.path.join(desc_dir, f"{rom_name}.txt")
        with open(desc_file_path, "w", encoding="utf-8") as desc_file:
            desc_file.write(game['desc'])

    # Enregistrer l'hyperlist XML formatée
    tree = ET.ElementTree(root)
    format_xml(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def format_xml(elem, level=0):
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        for child in elem:
            format_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent + "  "
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent

def convert_gamelist_to_hyperlist(gamelist_file, output_dir):
    hyperlist_name = os.path.splitext(os.path.basename(gamelist_file))[0]
    output_hyperlist_file = os.path.join(output_dir, f"{hyperlist_name}_hyperlist.xml")
    desc_dir = os.path.join(output_dir, hyperlist_name)

    games = load_gamelist(gamelist_file)
    if games:
        write_hyperlist(games, output_hyperlist_file, desc_dir)
        messagebox.showinfo("Succès", f"Conversion terminée. Fichier HyperList généré : {output_hyperlist_file}\nDescriptions extraites dans le dossier : {desc_dir}")

def select_gamelist_file():
    file_selected = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    gamelist_file_var.set(file_selected)

def select_output_directory():
    folder_selected = filedialog.askdirectory()
    output_dir_var.set(folder_selected)

def run_conversion():
    gamelist_file = gamelist_file_var.get()
    output_dir = output_dir_var.get()
    
    if not gamelist_file:
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier gamelist.xml.")
        return
    if not output_dir:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie.")
        return
    
    convert_gamelist_to_hyperlist(gamelist_file, output_dir)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Gamelist to HyperList Converter")

# Variables de contrôle
gamelist_file_var = tk.StringVar()
output_dir_var = tk.StringVar()

# Interface utilisateur
tk.Label(root, text="Fichier gamelist.xml :").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=gamelist_file_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Parcourir", command=select_gamelist_file).grid(row=0, column=2)

tk.Label(root, text="Dossier de sortie :").grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=output_dir_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Parcourir", command=select_output_directory).grid(row=1, column=2)

tk.Button(root, text="Convertir", command=run_conversion).grid(row=2, column=1, pady=10)

# Démarrer la boucle principale de l'interface graphique
root.mainloop()