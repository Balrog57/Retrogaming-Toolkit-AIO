# Module généré automatiquement à partir de hyperlist_to_gamelist.py

def main():
    import xml.etree.ElementTree as ET
    import os
    import customtkinter as ctk
    from tkinter import messagebox

    # Configuration du thème
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème bleu

    def load_hyperlist(file_path, rom_extension):
        try:
            tree = ET.parse(file_path)
        except ET.ParseError:
            messagebox.showerror("Erreur", f"Erreur de format dans le fichier {file_path}. Le fichier sera ignoré.")
            return []

        root = tree.getroot()
        games = []

        for game in root.findall('game'):
            name = game.get('name')
            description = game.find('story').text if game.find('story') is not None else ""
            
            year = game.find('year').text if game.find('year') is not None else None
            manufacturer = game.find('manufacturer').text if game.find('manufacturer') is not None else ""
            publisher = game.find('publisher').text if game.find('publisher') is not None else ""
            genre = game.find('genre').text if game.find('genre') is not None else ""
            score = game.find('score').text if game.find('score') is not None else "0"
            players = game.find('players').text if game.find('players') is not None else "1"

            if year and year.isdigit() and len(year) == 4:
                releasedate = year + "0101"
            else:
                releasedate = ""

            score = score if score else "0"
            try:
                rating = str(round(float(score) / 5.0, 2))
            except ValueError:
                rating = "0.00"

            games.append({
                'name': name,
                'desc': description,
                'releasedate': releasedate,
                'developer': manufacturer,
                'publisher': publisher,
                'genre': genre,
                'rating': rating,
                'players': players,
                'rompath': name + rom_extension
            })

        return games

    def write_gamelist(games, output_file):
        root = ET.Element('gameList')

        for game in games:
            game_elem = ET.SubElement(root, 'game')
            ET.SubElement(game_elem, 'path').text = "./" + game['rompath']
            ET.SubElement(game_elem, 'name').text = game['name']
            
            # Nettoyage de desc avec une vérification pour éviter les erreurs NoneType
            desc_text = game['desc'] if game['desc'] else ""
            desc_elem = ET.SubElement(game_elem, 'desc')
            desc_elem.text = " ".join(desc_text.split())
            
            ET.SubElement(game_elem, 'releasedate').text = game['releasedate']
            ET.SubElement(game_elem, 'developer').text = game['developer']
            ET.SubElement(game_elem, 'publisher').text = game['publisher']
            ET.SubElement(game_elem, 'genre').text = game['genre']
            ET.SubElement(game_elem, 'rating').text = game['rating']
            ET.SubElement(game_elem, 'players').text = game['players']

        tree = ET.ElementTree(root)
        format_xml(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

    def format_xml(elem, level=0):
        # Nettoyer les espaces et ajouter un retour à la ligne après chaque balise
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

    def convert_hyperlist_to_gamelist(hyperlist_file, rom_extension, output_dir):
        output_file = os.path.join(output_dir, f"gamelist_{os.path.basename(hyperlist_file)}")
        games = load_hyperlist(hyperlist_file, rom_extension)
        if games:
            write_gamelist(games, output_file)
            messagebox.showinfo("Succès", f"Conversion terminée. Fichier généré : {output_file}")

    def select_hyperlist_file():
        file_selected = ctk.filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        hyperlist_file_var.set(file_selected)

    def select_output_directory():
        folder_selected = ctk.filedialog.askdirectory()
        output_dir_var.set(folder_selected)

    def run_conversion():
        hyperlist_file = hyperlist_file_var.get()
        rom_extension = rom_extension_var.get().strip()
        output_dir = output_dir_var.get()
        
        if not hyperlist_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier HyperList.")
            return
        if not rom_extension.startswith("."):
            messagebox.showerror("Erreur", "L'extension des ROM doit commencer par un point (ex. '.zip').")
            return
        if not output_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie.")
            return
        
        convert_hyperlist_to_gamelist(hyperlist_file, rom_extension, output_dir)

    # Création de la fenêtre principale
    root = ctk.CTk()
    root.title("HyperList to Gamelist Converter")

    # Variables de contrôle
    hyperlist_file_var = ctk.StringVar()
    rom_extension_var = ctk.StringVar(value=".zip")
    output_dir_var = ctk.StringVar()

    # Interface utilisateur
    ctk.CTkLabel(root, text="Fichier HyperList :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=hyperlist_file_var, width=400).grid(row=0, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_hyperlist_file, width=200).grid(row=0, column=2, padx=10, pady=10)

    ctk.CTkLabel(root, text="Extension des ROM (ex. '.zip') :", font=("Arial", 16)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=rom_extension_var, width=400).grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(root, text="Dossier de sortie :", font=("Arial", 16)).grid(row=2, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=output_dir_var, width=400).grid(row=2, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_output_directory, width=200).grid(row=2, column=2, padx=10, pady=10)

    ctk.CTkButton(root, text="Convertir", command=run_conversion, width=200).grid(row=3, column=1, pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()