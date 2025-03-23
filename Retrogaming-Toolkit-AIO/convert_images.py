import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import os
import subprocess
import requests
import tempfile
import shutil
import zipfile
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction pour vérifier et télécharger FFmpeg
def check_and_download_ffmpeg():
    ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        try:
            logging.info("FFmpeg n'est pas trouvé. Téléchargement en cours...")
            messagebox.showinfo("Téléchargement", "FFmpeg n'est pas trouvé. Téléchargement en cours...")
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"  # Lien officiel vers FFmpeg
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name

            # Télécharger FFmpeg
            response = requests.get(url, stream=True)
            with open(temp_zip, "wb") as f:
                shutil.copyfileobj(response.raw, f)

            # Extraire le fichier téléchargé
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Rechercher ffmpeg.exe dans le dossier extrait
            for root, dirs, files in os.walk(extract_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_extracted_path = os.path.join(root, "ffmpeg.exe")
                    shutil.move(ffmpeg_extracted_path, ffmpeg_path)
                    break
            else:
                raise FileNotFoundError("Le fichier ffmpeg.exe n'a pas été trouvé après extraction.")

            os.remove(temp_zip)
            messagebox.showinfo("Succès", "FFmpeg a été téléchargé et configuré avec succès.")
            logging.info("FFmpeg a été téléchargé et configuré avec succès.")
        except Exception as e:
            logging.error(f"Échec du téléchargement de FFmpeg : {e}")
            messagebox.showerror("Erreur", f"Échec du téléchargement de FFmpeg : {e}")
            # Laisser l'utilisateur gérer la fermeture de la fenêtre
            return  # Ne pas détruire la fenêtre ici

# Fonction pour convertir les images
def convert_images(input_dir, output_dir, input_format, output_format, delete_originals):
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

        for filename in os.listdir(input_dir):
            if any(filename.lower().endswith(f".{ext}") for ext in input_extensions):
                input_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + f".{output_format.lower()}"
                output_path = os.path.join(output_dir, output_filename)

                logging.info(f"Conversion de : {input_path} vers {output_path}")

                # Utilisation de FFmpeg pour la conversion
                ffmpeg_cmd = [
                    "ffmpeg",
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
    button_convert = ctk.CTkButton(root, text="Convertir", command=lambda: convert_images(entry_input_dir.get(), entry_output_dir.get(), input_format_var.get(), output_format_var.get(), delete_originals_var.get()), width=200)
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
    check_and_download_ffmpeg()
    if root := create_gui(): # Assignation possible depuis Python 3.8
        root.mainloop()

if __name__ == "__main__":
    main()