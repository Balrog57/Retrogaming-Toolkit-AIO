import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import os
import subprocess
import requests
import tempfile
import shutil
# import zipfile
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Import utils
try:
    import utils
except ImportError:
    utils = None

# Fonction pour vérifier et télécharger FFmpeg
# Fonction pour vérifier et télécharger FFmpeg
def check_and_download_ffmpeg(root=None):
    target_name = "ffmpeg.exe"
    
    # Check bundled/existing via utils first if possible
    if utils:
        ffmpeg_path = utils.get_binary_path(target_name)
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
    
    # AppData fallback path check
    app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit')
    ffmpeg_dest_path = os.path.join(app_data_dir, target_name)
    if os.path.exists(ffmpeg_dest_path):
        return ffmpeg_dest_path

    # If we are here, we need to download
    if utils and root:
        try:
            manager = utils.DependencyManager(root)
            
            # Resolve URL dynamically from GitHub
            ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "essentials")
            if not ffmpeg_url:
                # Fallback to full if essentials missing
                ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "full")
            
            if not ffmpeg_url:
                 # Last resort fallback if API fails
                 ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                 logging.warning("GitHub API failed, falling back to gyan.dev")

            result = manager.install_dependency(
                name="FFmpeg",
                url=ffmpeg_url,
                target_exe_name=target_name,
                archive_type="zip",
                extract_file_in_archive=None # Logic acts recursively if not found or I can specify
                # The zip structure is ffmpeg-release-essentials/bin/ffmpeg.exe usually.
                # install_dependency searches recursively if file not found in root of extract.
            )
            return result
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec du téléchargement de FFmpeg : {e}")
            return None
    else:
        # Fallback if utils missing (should not happen)
        messagebox.showerror("Erreur", "Impossible de télécharger FFmpeg (utils manquant).")
        return None

# Fonction pour convertir les images
# Fonction pour convertir les images
def convert_images(root, input_dir, output_dir, input_format, output_format, delete_originals):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Création du dossier de sortie : {output_dir}")

        # Gestion des extensions multiples pour certains formats
        input_extensions = [input_format.lower()]
        if input_format.lower() == "jpeg":
            input_extensions = ["jpeg", "jpg"]
        elif input_format.lower() == "tiff":
            input_extensions = ["tiff", "tif"]

        # Optimize: Check FFmpeg once before processing files
        # Fix: Pass root to ensure download dialog has a parent window
        ffmpeg_exe = check_and_download_ffmpeg(root)
        if not ffmpeg_exe:
            return

        for filename in os.listdir(input_dir):
            if any(filename.lower().endswith(f".{ext}") for ext in input_extensions):
                input_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + f".{output_format.lower()}"
                output_path = os.path.join(output_dir, output_filename)

                logging.info(f"Conversion de : {input_path} vers {output_path}")

                # Utilisation de FFmpeg pour la conversion
                # Use resolved ffmpeg path

                
                ffmpeg_cmd = [
                    ffmpeg_exe,
                    "-i", input_path,
                    "-frames:v", "1",  # Ajout de l'argument -frames:v 1
                    "-update", "1",     # Ajout de l'argument -update 1
                    output_path
                ]
                subprocess.run(ffmpeg_cmd, check=True)

                if delete_originals:
                    os.remove(input_path)
                    logging.info(f"Fichier original supprimé : {input_path}")

        messagebox.showinfo("Succès", "Conversion terminée.")
        logging.info("Conversion terminée avec succès.")
    except Exception as e:
        logging.error(f"Une erreur s'est produite lors de la conversion : {e}")
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la conversion : {e}")

# Création de l'interface graphique
def create_gui():
    root = ctk.CTk()
    root.title("Convertisseur d'Images")

    # Configuration du thème sombre et bleu
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Police Arial pour les titres
    font_titre = ("Arial", 16)

    # Cadre pour la sélection des dossiers et des formats
    frame_options = ctk.CTkFrame(root)
    frame_options.pack(pady=20, padx=20, fill="x")

    # Sélection du dossier d'entrée
    label_input_dir = ctk.CTkLabel(frame_options, text="Dossier d'entrée:", font=font_titre)
    label_input_dir.grid(row=0, column=0, sticky="w", pady=5)
    entry_input_dir = ctk.CTkEntry(frame_options, width=300)
    entry_input_dir.grid(row=0, column=1, padx=5, pady=5)
    button_input_dir = ctk.CTkButton(frame_options, text="Parcourir", command=lambda: entry_input_dir.insert(0, filedialog.askdirectory()), width=100)
    button_input_dir.grid(row=0, column=2, padx=5, pady=5)

    # Sélection du dossier de sortie
    label_output_dir = ctk.CTkLabel(frame_options, text="Dossier de sortie:", font=font_titre)
    label_output_dir.grid(row=1, column=0, sticky="w", pady=5)
    entry_output_dir = ctk.CTkEntry(frame_options, width=300)
    entry_output_dir.grid(row=1, column=1, padx=5, pady=5)
    button_output_dir = ctk.CTkButton(frame_options, text="Parcourir", command=lambda: entry_output_dir.insert(0, filedialog.askdirectory()), width=100)
    button_output_dir.grid(row=1, column=2, padx=5, pady=5)

    # Sélection du format d'entrée
    label_input_format = ctk.CTkLabel(frame_options, text="Format d'entrée:", font=font_titre)
    label_input_format.grid(row=2, column=0, sticky="w", pady=5)
    input_format_choices = ["webp", "jpeg", "png", "tiff", "bmp", "gif", "ppm", "pgm", "pbm", "pnm"]
    input_format_var = tk.StringVar(value="webp")  # Valeur par défaut
    input_format_menu = ttk.Combobox(frame_options, textvariable=input_format_var, values=input_format_choices, state="readonly", width=10, postcommand=lambda: check_format_choices())
    input_format_menu.grid(row=2, column=1, padx=5, pady=5)

    # Sélection du format de sortie
    label_output_format = ctk.CTkLabel(frame_options, text="Format de sortie:", font=font_titre)
    label_output_format.grid(row=3, column=0, sticky="w", pady=5)
    output_format_choices = ["jpeg", "png", "tiff", "bmp", "gif", "ppm", "pgm", "pbm", "pnm", "webp"]
    output_format_var = tk.StringVar(value="png")  # Valeur par défaut
    output_format_menu = ttk.Combobox(frame_options, textvariable=output_format_var, values=output_format_choices, state="readonly", width=10, postcommand=lambda: check_format_choices())
    output_format_menu.grid(row=3, column=1, padx=5, pady=5)

    # Case à cocher pour supprimer les originaux
    delete_originals_var = tk.BooleanVar()
    check_delete_originals = ctk.CTkCheckBox(frame_options, text="Supprimer les fichiers originaux", variable=delete_originals_var)
    check_delete_originals.grid(row=4, column=0, columnspan=3, pady=5)

    # Bouton de conversion
    # Update call to include root
    button_convert = ctk.CTkButton(root, text="Convertir", command=lambda: convert_images(root, entry_input_dir.get(), entry_output_dir.get(), input_format_var.get(), output_format_var.get(), delete_originals_var.get()), width=200)
    button_convert.pack(pady=10)

    # Fonction de validation des choix de format
    def check_format_choices():
        input_format = input_format_var.get()
        output_format = output_format_var.get()

        if input_format == output_format:
            messagebox.showwarning("Attention", "Le format d'entrée et le format de sortie doivent être différents.")
            button_convert.configure(state="disabled")  # Désactiver le bouton
        else:
            button_convert.configure(state="normal")    # Activer le bouton

    return root  # Retourne l'objet root

def main():
    # Vérifier FFmpeg et lancer l'interface graphique
    # Create root first to allow progress window
    root = create_gui()
    if root:
        if check_and_download_ffmpeg(root):
            root.mainloop()
        else:
            root.destroy()

if __name__ == "__main__":
    main()