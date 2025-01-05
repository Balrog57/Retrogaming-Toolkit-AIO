# Module généré automatiquement à partir de story_format_cleaner.py

def main():
    import os
    import unicodedata
    import customtkinter as ctk
    from tkinter import messagebox
    from tkinter import filedialog

    # Configuration de l'apparence de l'interface
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème de couleur bleu

    def normalize_french_text_in_files(directory):
        """
        Parcourt tous les fichiers .txt dans le dossier spécifié, remplace les caractères français non-ASCII
        par leurs équivalents ASCII, remplace '&' par '&amp;', et écrase les fichiers originaux avec le texte normalisé.
        """
        # Vérifie que le dossier existe
        if not os.path.isdir(directory):
            messagebox.showerror("Erreur", f"Le dossier '{directory}' n'existe pas.")
            return

        # Initialisation du compteur de fichiers traités
        files_processed = 0

        # Parcourt tous les fichiers du dossier
        for file_name in os.listdir(directory):
            if file_name.endswith('.txt'):  # S'assurer de traiter uniquement les fichiers .txt
                file_path = os.path.join(directory, file_name)

                try:
                    # Lire le contenu du fichier
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # Normaliser le texte
                    normalized_content = normalize_french_text(content)

                    # Écraser le fichier avec le contenu normalisé
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(normalized_content)

                    print(f"Fichier traité : {file_name}")
                    files_processed += 1
                except Exception as e:
                    print(f"Erreur lors du traitement du fichier '{file_name}': {e}")

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

        normalize_french_text_in_files(directory)

    # Création de la fenêtre principale
    root = ctk.CTk()
    root.title("Story Format Cleaner")

    # Variables de contrôle
    directory_var = ctk.StringVar()

    # Interface utilisateur
    ctk.CTkLabel(root, text="Dossier à traiter :", font=("Arial", 16)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ctk.CTkEntry(root, textvariable=directory_var, width=300).grid(row=0, column=1, padx=10, pady=10)
    ctk.CTkButton(root, text="Parcourir", command=select_directory, width=100).grid(row=0, column=2, padx=10, pady=10)

    ctk.CTkButton(root, text="Normaliser le texte", command=run_script, width=200).grid(row=1, column=1, pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == '__main__':
    main()