def main():
    import os
    import unicodedata
    import customtkinter as ctk
    from tkinter import messagebox
    from tkinter import filedialog

    # Configuration de l'apparence de l'interface
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème de couleur bleu

    def normalize_french_text_in_files(directory, include_subdirs):
        """
        Parcourt tous les fichiers .txt dans le dossier spécifié (et éventuellement ses sous-dossiers),
        remplace les caractères français non-ASCII par leurs équivalents ASCII, remplace '&' par '&amp;',
        et écrase les fichiers originaux avec le texte normalisé.
        """
        # Vérifie que le dossier existe
        if not os.path.isdir(directory):
            messagebox.showerror("Erreur", f"Le dossier '{directory}' n'existe pas.")
            return

        # Initialisation du compteur de fichiers traités
        files_processed = 0

        # Fonction pour parcourir les fichiers
        def process_files(folder):
            nonlocal files_processed
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isdir(file_path) and include_subdirs:
                    process_files(file_path)  # Traiter les sous-dossiers récursivement
                elif file_name.endswith('.txt'):  # S'assurer de traiter uniquement les fichiers .txt
                    try:
                        # Lire le contenu du fichier
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()

                        # Normaliser le texte
                        normalized_content = normalize_french_text(content)

                        # Écraser le fichier avec le contenu normalisé
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(normalized_content)

                        print(f"Fichier traité : {file_path}")
                        files_processed += 1
                    except Exception as e:
                        print(f"Erreur lors du traitement du fichier '{file_path}': {e}")

        # Commencer le traitement
        process_files(directory)

        messagebox.showinfo("Succès", f"Traitement terminé : {files_processed} fichier(s) traité(s).")

    def normalize_french_text(text):
        """
        Remplace les caractères français non-ASCII dans un texte par leurs équivalents ASCII
        et remplace '&' par '&amp;'.
        """
        # Supprimer les accents en utilisant unicodedata
        normalized_text = unicodedata.normalize('NFD', text)
        ascii_text = normalized_text.encode('ascii', 'ignore').decode('utf-8')

        # Remplacer les caractères spécifiques manuellement
        replacements = {
            'œ': 'oe',
            'Œ': 'OE',
            'æ': 'ae',
            'Æ': 'AE',
            'ç': 'c',
            'Ç': 'C',
            '&': '&amp;'  # Remplacement de & par &amp;
        }

        for char, replacement in replacements.items():
            ascii_text = ascii_text.replace(char, replacement)

        return ascii_text

    def select_directory():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            directory_var.set(folder_selected)

    def run_script():
        directory = directory_var.get()

        if not directory:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier.")
            return

        include_subdirs = include_subdirs_var.get()
        normalize_french_text_in_files(directory, include_subdirs)

    # Création de la fenêtre principale
    root = ctk.CTk()
    root.title("Story Format Cleaner")

    # Variables de contrôle
    directory_var = ctk.StringVar()
    include_subdirs_var = ctk.BooleanVar(value=False)  # Case à cocher pour inclure les sous-dossiers

    # Interface utilisateur
    ctk.CTkLabel(root, text="Dossier à traiter :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=directory_var, width=300).grid(row=0, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_directory, width=100).grid(row=0, column=2, padx=10, pady=10)

    ctk.CTkCheckBox(root, text="Inclure les sous-dossiers", variable=include_subdirs_var).grid(row=1, column=1, pady=10)

    ctk.CTkButton(root, text="Normaliser le texte", command=run_script, width=200).grid(row=2, column=1, pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()