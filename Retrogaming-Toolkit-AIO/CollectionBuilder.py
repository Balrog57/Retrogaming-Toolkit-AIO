# -*- coding: utf-8 -*-
import os
import re
import logging
import xml.etree.ElementTree as ET
import customtkinter as ctk
from tkinter import filedialog
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='collection_builder.log'
)
logger = logging.getLogger(__name__)

# Constantes
CDATA_PATTERN = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
TEXT_PATTERN = re.compile(r'>(.*?)<', re.DOTALL)
AMPERSAND_PATTERN = re.compile(r'&(?!amp;|lt;|gt;|apos;|quot;)')

BASE_DIR_TEMPLATE = "CTP - {collection_name}"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_directories(collection_name: str):
    """Crée les répertoires nécessaires pour la collection."""
    base_dir = BASE_DIR_TEMPLATE.format(collection_name=collection_name)
    dirs = [
        f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/COLLECTIONS/menu",
        f"{base_dir}/collections/COLLECTIONS/medium_artwork/logo",
        f"{base_dir}/readme",
        f"{base_dir}/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/{collection_name}/medium_artwork/fanart"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def create_placeholder_files(collection_name: str):
    """Crée les fichiers placeholder pour la collection."""
    base_dir = BASE_DIR_TEMPLATE.format(collection_name=collection_name)
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
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def match_keywords(description: str, keywords_list: List[str]) -> bool:
    """Vérifie si les mots-clés sont présents dans la description."""
    description = description.lower()
    return any(all(keyword.lower() in description for keyword in keywords.split()) for keywords in keywords_list)

def read_xml_file(file_path: str) -> str:
    """Lit un fichier XML et gère les problèmes d'encodage."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    # Détecter l'encodage depuis la déclaration XML
    xml_decl = raw_data[:30].decode('utf-8', 'ignore')  # On suppose que la déclaration est dans les 30 premiers octets
    encoding_match = re.search(r'encoding\s*=\s*["\'](.*?)["\']', xml_decl)
    if encoding_match:
        encoding = encoding_match.group(1)
    else:
        encoding = 'utf-8'
    try:
        xml_content = raw_data.decode(encoding)
    except UnicodeDecodeError:
        try:
            xml_content = raw_data.decode('latin-1')
        except UnicodeDecodeError:
            logger.error(f"Impossible de décoder {file_path} avec UTF-8 ou latin-1")
            xml_content = raw_data.decode('utf-8', errors='replace')
    return xml_content

def fix_xml_ampersands(xml_content: str) -> str:
    """Corrige les '&' non échappés dans le contenu XML."""
    # Remplacer '&' par '&amp;' dans les sections de texte hors CDATA et balises
    # Remplacer '&' par '&amp;' dans les sections de texte hors CDATA et balises
    cdata_sections = []
    def replace_cdata(match):
        placeholder = f'CDATA_PLACEHOLDER_{len(cdata_sections)}'
        cdata_sections.append((placeholder, match.group(0)))
        return placeholder
    temp_xml = CDATA_PATTERN.sub(replace_cdata, xml_content)
    
    # Remplacer '&' par '&amp;' dans les sections de texte
    def replace_ampersands(match):
        text = match.group(1)
        text = AMPERSAND_PATTERN.sub('&amp;', text)
        return f'>{text}<'
    corrected_xml = TEXT_PATTERN.sub(replace_ampersands, temp_xml)
    
    # Remplacer les placeholders CDATA par leur contenu original
    for placeholder, original in cdata_sections:
        corrected_xml = corrected_xml.replace(placeholder, original)
    return corrected_xml

def generate_collection(collection_name: str, keywords_list: List[str], hyperlist_dir: str):
    """Génère la collection en fonction des mots-clés et du dossier hyperlist."""
    create_directories(collection_name)
    create_placeholder_files(collection_name)
    
    base_dir = BASE_DIR_TEMPLATE.format(collection_name=collection_name)
    games_list_path = os.path.join(base_dir, "readme", f"{collection_name} Games List.txt")
    
    # Réinitialiser le fichier de liste des jeux
    with open(games_list_path, 'w', encoding='utf-8') as games_list:
        pass
    
    for filename in os.listdir(hyperlist_dir):
        if filename.endswith(".xml"):
            system_name = os.path.splitext(filename)[0]
            xml_path = os.path.join(hyperlist_dir, filename)
            
            # Lire et corriger le contenu XML
            xml_content = read_xml_file(xml_path)
            corrected_xml = fix_xml_ampersands(xml_content)
            
            # Parser le XML corrigé
            try:
                root = ET.fromstring(corrected_xml)
                matching_games = []
                
                for game in root.findall(".//game"):
                    description_elem = game.find("description")
                    game_name = game.get("name")
                    
                    if description_elem is not None and game_name:
                        clean_description = description_elem.text.replace('&', '&') if description_elem.text else ""
                        if match_keywords(clean_description, keywords_list):
                            matching_games.append(game_name)
                
                if matching_games:
                    sub_file_path = os.path.join(base_dir, "collections", collection_name, f"{system_name}.sub")
                    with open(sub_file_path, 'w', encoding='utf-8') as sub_file:
                        sub_file.write("\n".join(matching_games))
                    
                    with open(games_list_path, 'a', encoding='utf-8') as games_list:
                        for game in matching_games:
                            games_list.write(f"{system_name} | {game}\n")
                
            except ET.ParseError as e:
                logger.error(f"Erreur XML dans {filename}: {e}")
                continue

def main():
    root = ctk.CTk()
    root.title("Créateur de Collection Personnalisée")
    root.geometry("600x400")
    
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    main_frame = ctk.CTkFrame(root, border_width=2, border_color="#1f6aa5", width=550, corner_radius=20)
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)
    
    title_label = ctk.CTkLabel(main_frame, text="Créateur de Collection", font=("Arial", 20, "bold"))
    title_label.grid(row=0, column=0, pady=(10, 20))
    
    collection_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    collection_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
    
    collection_label = ctk.CTkLabel(collection_frame, text="Nom de la collection:", font=("Arial", 16))
    collection_label.pack(side="left", padx=(0, 10))
    
    collection_entry = ctk.CTkEntry(collection_frame, width=250)
    collection_entry.pack(side="left", expand=True, fill="x")
    
    core_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    core_frame.grid(row=2, column=0, pady=(0, 10), sticky="ew")
    
    core_label = ctk.CTkLabel(core_frame, text="Dossier core:", font=("Arial", 16))
    core_label.pack(side="left", padx=(0, 10))
    
    core_entry = ctk.CTkEntry(core_frame, width=250)
    core_entry.pack(side="left", expand=True, fill="x")
    
    def select_core_dir():
        directory = filedialog.askdirectory()
        if directory:
            core_entry.delete(0, "end")
            core_entry.insert(0, directory)
    
    core_btn = ctk.CTkButton(core_frame, text="Parcourir", command=select_core_dir, width=80)
    core_btn.pack(side="left", padx=(10, 0))
    
    keywords_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    keywords_frame.grid(row=3, column=0, pady=(0, 20), sticky="ew")
    
    keywords_label = ctk.CTkLabel(keywords_frame, text="Mots-clés (séparés par ;):", font=("Arial", 16))
    keywords_label.pack(side="left", padx=(0, 10))
    
    keywords_entry = ctk.CTkEntry(keywords_frame, width=250)
    keywords_entry.pack(side="left", expand=True, fill="x")
    
    def on_submit():
        collection_name = collection_entry.get()
        keywords_input = keywords_entry.get()
        
        if collection_name:
            collection_name += " Collection"
            keywords_list = [kw.strip() for kw in keywords_input.split(';')]
            
            hyperlist_dir = os.path.join(core_entry.get(), "meta", "hyperlist")
            if not os.path.exists(hyperlist_dir):
                result_label.configure(text="Dossier hyperlist introuvable", text_color="#e74c3c")
                return
            
            generate_collection(collection_name, keywords_list, hyperlist_dir)
            
            result_label.configure(text=f"Collection \"{collection_name}\" créée avec succès!", text_color="#2ecc71")
        else:
            result_label.configure(text="Veuillez entrer un nom de collection", text_color="#e74c3c")
    
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=4, column=0, pady=(0, 20))
    
    submit_btn = ctk.CTkButton(button_frame, text="Créer la collection", command=on_submit, width=200, fg_color="#1f6aa5", hover_color="#144870")
    submit_btn.pack()
    
    result_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    result_frame.grid(row=5, column=0, pady=(0, 10))
    
    result_label = ctk.CTkLabel(result_frame, text="", font=("Arial", 14), wraplength=500, corner_radius=10)
    result_label.pack()
    
    def on_closing():
        root.destroy()
        os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()