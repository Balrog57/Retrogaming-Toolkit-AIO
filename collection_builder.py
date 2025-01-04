# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import simpledialog

def create_directories(collection_name):
    base_dir = f"CTP - {collection_name}"
    dirs = [
        f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/COLLECTIONS/menu",
        f"{base_dir}/collections/COLLECTIONS/medium_artwork/logo",
        f"{base_dir}/readme",
        f"{base_dir}/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/{collection_name}/medium_artwork/fanart"
    ]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)

def create_placeholder_files(collection_name):
    base_dir = f"CTP - {collection_name}"
    placeholders = [
        (f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork/Character.png.txt", "720x810 \"Character.png\""),
        (f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork/menuextra1.png.txt", "600x600 \"menuextra1.png\""),
        (f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork/menuextra2.png.txt", "1920x1080 \"menuextra2.png\""),
        (f"{base_dir}/collections/COLLECTIONS/menu/{collection_name}.txt", ""),
        (f"{base_dir}/collections/{collection_name}/system_artwork/device.png.txt", "800x800 \"device.png\""),
        (f"{base_dir}/collections/{collection_name}/system_artwork/fanart.jpg.txt", "1920x1080 \"fanart.jpg\""),
        (f"{base_dir}/collections/{collection_name}/system_artwork/logo.png.txt", "Custom Collection \"logo.png\""),
        (f"{base_dir}/collections/{collection_name}/system_artwork/story.txt.txt", "Custom Collection \"story.txt\""),
        (f"{base_dir}/collections/{collection_name}/system_artwork/video.mp4.txt", "Custom Collection \"video.mp4\"")
    ]
    for file_path, content in placeholders:
        with open(file_path, 'w') as f:
            f.write(content)

def match_keywords(description, keywords_list):
    description = description.lower()
    return any(all(keyword.lower() in description for keyword in keywords.split()) for keywords in keywords_list)

def generate_collection(collection_name, keywords_list):
    create_directories(collection_name)
    create_placeholder_files(collection_name)
    
    base_dir = f"CTP - {collection_name}"
    hyperlist_dir = ".\\meta\\hyperlist"
    
    for filename in os.listdir(hyperlist_dir):
        if filename.endswith(".xml"):
            system_name = os.path.splitext(filename)[0]
            xml_path = os.path.join(hyperlist_dir, filename)
            
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                matching_games = []
                
                for game in root.findall(".//game"):
                    description = game.find("description")
                    game_name = game.get("name")  # Récupérer le nom du jeu
                    if description is not None and description.text:
                        if match_keywords(description.text, keywords_list):
                            matching_games.append(game_name)  # Ajouter le nom du jeu au lieu de la description
                
                if matching_games:
                    sub_file_path = os.path.join(base_dir, "collections", collection_name, f"{system_name}.sub")
                    with open(sub_file_path, 'w', encoding='utf-8') as sub_file:
                        for game in matching_games:
                            sub_file.write(f"{game}\n")
                    
                    games_list_path = os.path.join(base_dir, "readme", f"{collection_name} Games List.txt")
                    with open(games_list_path, 'a', encoding='utf-8') as games_list:
                        for game in matching_games:
                            games_list.write(f"{system_name} | {game}\n")
            
            except ET.ParseError:
                print(f"Erreur lors de l'analyse du fichier XML : {filename}")

def main():
    root = tk.Tk()
    root.withdraw()
    
    collection_name = simpledialog.askstring("Créateur de Collection Personnalisée", "Veuillez entrer un nom pour votre collection personnalisée :")
    if collection_name:
        collection_name += " Collection"
        keywords_input = simpledialog.askstring("Créateur de Collection Personnalisée", 
                                                "Veuillez entrer les mots-clés à rechercher pour ajouter des jeux à votre collection :\n"
                                                "(Utilisez ; pour séparer plusieurs groupes de mots-clés)")
        
        keywords_list = [kw.strip() for kw in keywords_input.split(';')]
        
        generate_collection(collection_name, keywords_list)
        
        print(f"\nVous venez de créer \"{collection_name}\" !")
        print(f"Les résultats de la recherche pour {', '.join(keywords_list)} ont été enregistrés dans les fichiers .sub dans votre nouvelle collection \"{collection_name}\".")
        print("\nVeuillez vérifier chaque fichier .sub généré et confirmer que vous êtes satisfait des jeux ajoutés. Supprimez les correspondances incorrectes si nécessaire.")
        print("\nAjoutez les éléments graphiques nécessaires pour compléter la collection. Les répertoires ont déjà été créés pour vous.")
        input("\nAppuyez sur Entrée pour fermer la fenêtre...")

if __name__ == "__main__":
    main()
