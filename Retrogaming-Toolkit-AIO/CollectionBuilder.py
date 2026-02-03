# -*- coding: utf-8 -*-
import os
import re
import logging
from lxml import etree as ET
import customtkinter as ctk
from tkinter import filedialog
from typing import List

try:
    import theme
except ImportError:
    theme = None

# Constantes
CDATA_PATTERN = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
TEXT_PATTERN = re.compile(r'>(.*?)<', re.DOTALL)
AMPERSAND_PATTERN = re.compile(r'&(?!amp;|lt;|gt;|apos;|quot;)')
BASE_DIR_TEMPLATE = "CTP - {collection_name}"

# --- Logic Preserved ---
def create_directories(collection_name: str):
    base_dir = BASE_DIR_TEMPLATE.format(collection_name=collection_name)
    dirs = [
        f"{base_dir}/layouts/TITAN/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/COLLECTIONS/menu",
        f"{base_dir}/collections/COLLECTIONS/medium_artwork/logo",
        f"{base_dir}/readme",
        f"{base_dir}/collections/{collection_name}/system_artwork",
        f"{base_dir}/collections/{collection_name}/medium_artwork/fanart"
    ]
    for dir_path in dirs: os.makedirs(dir_path, exist_ok=True)

def create_placeholder_files(collection_name: str):
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
        with open(file_path, 'w', encoding='utf-8') as f: f.write(content)

def match_keywords(description: str, keywords_list: List[str]) -> bool:
    description = description.lower()
    return any(all(keyword.lower() in description for keyword in keywords.split()) for keywords in keywords_list)

def read_xml_file(file_path: str) -> str:
    with open(file_path, 'rb') as f: raw_data = f.read()
    xml_decl = raw_data[:30].decode('utf-8', 'ignore')
    match = re.search(r'encoding\s*=\s*["\'](.*?)["\']', xml_decl)
    encoding = match.group(1) if match else 'utf-8'
    try: return raw_data.decode(encoding)
    except: return raw_data.decode('utf-8', errors='replace')

def fix_xml_ampersands(xml_content: str) -> str:
    cdata_sections = []
    def replace_cdata(match):
        placeholder = f'CDATA_PLACEHOLDER_{len(cdata_sections)}'
        cdata_sections.append((placeholder, match.group(0)))
        return placeholder
    temp_xml = CDATA_PATTERN.sub(replace_cdata, xml_content)
    
    def replace_ampersands(match):
        text = match.group(1)
        text = AMPERSAND_PATTERN.sub('&amp;', text)
        return f'>{text}<'
    corrected_xml = TEXT_PATTERN.sub(replace_ampersands, temp_xml)
    
    for placeholder, original in cdata_sections:
        corrected_xml = corrected_xml.replace(placeholder, original)
    return corrected_xml

def generate_collection(collection_name: str, keywords_list: List[str], hyperlist_dir: str):
    create_directories(collection_name)
    create_placeholder_files(collection_name)
    
    base_dir = BASE_DIR_TEMPLATE.format(collection_name=collection_name)
    games_list_path = os.path.join(base_dir, "readme", f"{collection_name} Games List.txt")
    with open(games_list_path, 'w', encoding='utf-8') as _: pass
    
    for filename in os.listdir(hyperlist_dir):
        if filename.endswith(".xml"):
            sys_name = os.path.splitext(filename)[0]
            xml_path = os.path.join(hyperlist_dir, filename)
            try:
                parser = ET.XMLParser(resolve_entities=False, no_network=True, recover=True)
                root = ET.fromstring(fix_xml_ampersands(read_xml_file(xml_path)), parser=parser)
                matched = []
                for game in root.findall(".//game"):
                    desc = game.find("description")
                    name = game.get("name")
                    if desc is not None and name:
                        if match_keywords(desc.text.replace('&', '&') if desc.text else "", keywords_list):
                            matched.append(name)
                
                if matched:
                    with open(os.path.join(base_dir, "collections", collection_name, f"{sys_name}.sub"), 'w', encoding='utf-8') as f: f.write("\n".join(matched))
                    with open(games_list_path, 'a', encoding='utf-8') as f:
                        for g in matched: f.write(f"{sys_name} | {g}\n")
            except Exception: continue

def main():
    root = ctk.CTk()
    if theme: 
        theme.apply_theme(root, "Créateur de Collection Personnalisée")
        acc = theme.COLOR_ACCENT_PRIMARY
    else: 
        ctk.set_appearance_mode("dark")
        root.title("Créateur de Collection")
        acc = "#1f6aa5"
    
    root.geometry("600x450")
    root.grid_columnconfigure(0, weight=1)
    
    main_frame = ctk.CTkFrame(root, border_width=2, border_color=acc, corner_radius=20, fg_color=theme.COLOR_BG if theme else "#2b2b2b")
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)
    
    ctk.CTkLabel(main_frame, text="Créateur de Collection", font=theme.get_font_title(20) if theme else ("Arial", 20, "bold")).grid(row=0, column=0, pady=(10, 20), padx=20)
    
    def mk_row(r, txt, btn_cmd=None):
        fr = ctk.CTkFrame(main_frame, fg_color="transparent")
        fr.grid(row=r, column=0, pady=5, sticky="ew", padx=20)
        ctk.CTkLabel(fr, text=txt, width=150, anchor="w").pack(side="left", padx=10)
        e = ctk.CTkEntry(fr)
        e.pack(side="left", expand=True, fill="x", padx=5)
        if btn_cmd: ctk.CTkButton(fr, text="...", width=40, command=btn_cmd, fg_color=acc).pack(side="left", padx=10)
        return e

    coll_entry = mk_row(1, "Nom Collection:")
    
    core_entry = mk_row(2, "Dossier Core:", lambda: (core_entry.delete(0, "end") or core_entry.insert(0, filedialog.askdirectory())))
    
    kw_entry = mk_row(3, "Mots-clés (sep ;):")

    res_lbl = ctk.CTkLabel(main_frame, text="")
    
    def on_submit():
        cn = coll_entry.get()
        kw = kw_entry.get()
        if cn:
            cn += " Collection"
            kwl = [k.strip() for k in kw.split(';')]
            hld = os.path.join(core_entry.get(), "meta", "hyperlist")
            if not os.path.exists(hld):
                res_lbl.configure(text="Dossier HyperList Introuvable", text_color=theme.COLOR_ERROR if theme else "red")
                return
            generate_collection(cn, kwl, hld)
            res_lbl.configure(text=f"Succès: {cn}", text_color=theme.COLOR_SUCCESS if theme else "green")
        else:
            res_lbl.configure(text="Nom manquant", text_color=theme.COLOR_ERROR if theme else "red")

    ctk.CTkButton(main_frame, text="CRÉER", command=on_submit, width=200, fg_color=acc).grid(row=4, column=0, pady=20, padx=20)
    res_lbl.grid(row=5, column=0, padx=20)

    root.mainloop()

if __name__ == "__main__":
    main()