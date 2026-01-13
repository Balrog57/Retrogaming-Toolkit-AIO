import os
# import zipfile
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration de l'apparence et du thème
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

def compress_and_delete_roms(source_dir):
    """
    Compresse tous les fichiers d'un dossier individuellement en ZIP et supprime les originaux.
    
    :param source_dir: Dossier contenant les fichiers à compresser.
    """
    try:
        # Vérifie si le dossier source existe
        if not os.path.exists(source_dir):
            messagebox.showerror("Erreur", f"Le dossier source '{source_dir}' n'existe pas.")
            return

        # Parcourt tous les fichiers dans le dossier source
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)

            # Ignore les dossiers (ne traite que les fichiers)
            if os.path.isfile(file_path):
                # Crée le chemin de l'archive ZIP
                zip_filename = os.path.splitext(filename)[0] + ".zip"
                zip_path = os.path.join(source_dir, zip_filename)

                # Compresse le fichier avec 7za
                try:
                    import utils
                    import subprocess
                    
                    manager = utils.DependencyManager()
                    if not manager.bootstrap_7za():
                         print("7za non trouvé")
                         continue

                    cmd = [manager.seven_za_path, 'a', '-tzip', zip_path, file_path]
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)
                    print(f"Fichier compressé : {zip_filename}")
    
                    # Supprime le fichier d'origine
                    os.remove(file_path)
                    print(f"Fichier supprimé : {filename}")
                except Exception as e:
                     print(f"Erreur compression {filename}: {e}")

        messagebox.showinfo("Succès", "Compression et suppression terminées.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def select_source_dir():
    """Ouvre une boîte de dialogue pour sélectionner le dossier source."""
    folder = filedialog.askdirectory()
    if folder:
        source_dir.set(folder)

def start_compression():
    """Lance la compression des fichiers."""
    if not source_dir.get():
        messagebox.showwarning("Attention", "Veuillez sélectionner un dossier source.")
        return
    compress_and_delete_roms(source_dir.get())

def main():
    global source_dir, root
    # Crée une instance de CTk (fenêtre principale)
    root = ctk.CTk()
    root.title("Dossier rom vers ZIP")  # Titre modifié
    root.geometry("500x300")  # Taille de la fenêtre

    # Variable pour le dossier source
    source_dir = ctk.StringVar()

    # Titre
    title_label = ctk.CTkLabel(root, text="Dossier rom vers ZIP", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    # Sélection du dossier source
    source_label = ctk.CTkLabel(root, text="Dossier source (Fichiers nes/bin/cue/gdi/iso/chd...) :", font=("Arial", 12))
    source_label.pack(pady=5)

    # Champ de saisie customtkinter pour afficher le chemin
    entry = ctk.CTkEntry(root, textvariable=source_dir, width=400)
    entry.pack(pady=5)

    # Bouton pour parcourir les dossiers
    browse_button = ctk.CTkButton(root, text="Parcourir...", command=select_source_dir, width=200)
    browse_button.pack(pady=10)

    # Bouton pour lancer la compression
    compress_button = ctk.CTkButton(root, text="ZIP", command=start_compression, width=200)
    compress_button.pack(pady=20)

    # Lancement de l'interface
    root.mainloop()

if __name__ == "__main__":
    main()