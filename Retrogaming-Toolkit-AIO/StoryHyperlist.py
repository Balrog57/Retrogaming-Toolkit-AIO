# Module généré automatiquement à partir de merge_story_hyperlist.py

def main():
    import os
    import time
    import xml.etree.ElementTree as ET
    from tqdm import tqdm
    import customtkinter as ctk
    from tkinter import messagebox
    from tkinter import filedialog

    # Configuration de l'apparence et du thème
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème de couleur bleu

    # Fonction pour lire un fichier avec gestion d'erreurs d'encodage
    def read_file_with_fallback(file_path):
        """Tente de lire un fichier avec plusieurs encodages possibles."""
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read().strip()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Impossible de lire le fichier : {file_path} avec les encodages {encodings}")

    def merge_story_hyperlist(xml_file, story_folder):
        try:
            # Charger le fichier XML
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse du fichier XML : {e}")
            return

        # Vérifier l'existence du dossier story
        if not os.path.exists(story_folder):
            messagebox.showerror("Erreur", "Le dossier 'story' n'existe pas. Veuillez le créer et ajouter les fichiers TXT.")
            return

        # Début du traitement
        start_time = time.time()
        updated_count = 0

        # Prétraiter les fichiers TXT pour optimiser la recherche
        story_files = {os.path.splitext(f)[0]: os.path.join(story_folder, f) for f in os.listdir(story_folder) if f.endswith(".txt")}

        # Parcourir les jeux dans le fichier XML
        for game in tqdm(root.findall(".//game"), desc="Traitement des jeux dans le fichier XML"):
            game_name = game.get("name")
            if game_name in story_files:
                try:
                    # Lire le contenu du fichier TXT correspondant avec fallback d'encodage
                    story_content = read_file_with_fallback(story_files[game_name])

                    # Remplacer ou ajouter la balise story
                    story_element = game.find("story")
                    if story_element is None:
                        story_element = ET.SubElement(game, "story")
                    story_element.text = story_content
                    updated_count += 1
                except Exception as e:
                    print(f"Erreur lors du traitement de {game_name}: {e}")

        # Sauvegarder les modifications dans un nouveau fichier XML
        output_file = f"Updated_{os.path.basename(xml_file)}"
        try:
            tree.write(output_file, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde du fichier XML : {e}")
            return

        # Fin du traitement
        end_time = time.time()
        duration = end_time - start_time

        # Résumé
        messagebox.showinfo("Succès", f"Traitement terminé!\n\n"
                                      f"Nombre total de jeux dans le fichier XML : {len(root.findall('.//game'))}\n"
                                      f"Nombre d'éléments mis à jour : {updated_count}\n"
                                      f"Nombre de fichiers TXT sans correspondance : {len(story_files) - updated_count}\n"
                                      f"Temps de traitement : {duration:.2f} secondes\n"
                                      f"Fichier mis à jour sauvegardé sous : {output_file}")

    def select_xml_file():
        file_selected = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_selected:
            xml_file_var.set(file_selected)

    def select_story_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            story_folder_var.set(folder_selected)

    def run_script():
        xml_file = xml_file_var.get()
        story_folder = story_folder_var.get()

        if not xml_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier XML.")
            return
        if not story_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner le dossier 'story'.")
            return

        merge_story_hyperlist(xml_file, story_folder)

    # Création de la fenêtre principale avec customtkinter
    root = ctk.CTk()
    root.title("CTP - Story Integrator")

    # Variables de contrôle
    xml_file_var = ctk.StringVar()
    story_folder_var = ctk.StringVar()

    # Interface utilisateur avec customtkinter
    ctk.CTkLabel(root, text="Fichier XML :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=xml_file_var, width=300).grid(row=0, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_xml_file, width=200).grid(row=0, column=2, padx=10, pady=10)

    ctk.CTkLabel(root, text="Dossier 'story' :", font=("Arial", 16)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=story_folder_var, width=300).grid(row=1, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_story_folder, width=200).grid(row=1, column=2, padx=10, pady=10)

    ctk.CTkButton(root, text="Fusionner les fichiers", command=run_script, width=200).grid(row=2, column=1, pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()