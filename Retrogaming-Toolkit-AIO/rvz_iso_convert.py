# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
    import subprocess
    import urllib.request
    import tarfile
    import customtkinter as ctk
    from tkinter import filedialog, messagebox

    # Configuration du thème
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Nom du fichier DolphinTool
    DOLPHIN_TOOL_NAME = "DolphinTool.exe"
    # URL de téléchargement de Dolphin Emulator
    DOLPHIN_DOWNLOAD_URL = "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z"

    def check_and_download_dolphintool():
        """Vérifie la présence de DolphinTool.exe et le télécharge si nécessaire."""
        if not os.path.isfile(DOLPHIN_TOOL_NAME):
            response = messagebox.askyesno(
                "DolphinTool Manquant",
                f"{DOLPHIN_TOOL_NAME} est introuvable. Voulez-vous le télécharger maintenant ?"
            )
            if response:
                download_dolphintool()
            else:
                messagebox.showerror("Erreur", "DolphinTool est requis pour continuer.")
                root.destroy()
                return

    def download_dolphintool():
        """Télécharge DolphinTool.exe depuis le site officiel."""
        try:
            archive_path, _ = urllib.request.urlretrieve(DOLPHIN_DOWNLOAD_URL, "dolphin.7z")
            extract_dolphintool(archive_path)
            os.remove(archive_path)
            messagebox.showinfo("Téléchargement Réussi", f"{DOLPHIN_TOOL_NAME} a été téléchargé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur de Téléchargement", f"Le téléchargement a échoué : {e}")
            exit()

    def extract_dolphintool(archive_path):
        """Extrait DolphinTool.exe d'une archive .7z."""
        try:
            import py7zr
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall()
            extracted_path = os.path.join("Dolphin-x64", DOLPHIN_TOOL_NAME)
            if os.path.exists(extracted_path):
                os.rename(extracted_path, DOLPHIN_TOOL_NAME)
                # Supprimer le dossier Dolphin-x64 après avoir déplacé l'exécutable
                if os.path.exists(DOLPHIN_TOOL_NAME):
                    import shutil
                    shutil.rmtree("Dolphin-x64", ignore_errors=True)
        except ImportError:
            messagebox.showerror("Erreur", "Le module py7zr est requis pour extraire l'archive .7z. Installez-le avec 'pip install py7zr'.")
            exit()

    def select_directory(title):
        """Ouvre une boîte de dialogue pour sélectionner un répertoire."""
        return filedialog.askdirectory(title=title)

    def convert_rvz_to_iso(input_dir, output_dir):
        """Convertit les fichiers RVZ en ISO en utilisant DolphinTool."""
        rvz_files = [
            os.path.join(input_dir, file)
            for file in os.listdir(input_dir)
            if file.endswith(".rvz")
        ]

        for rvz_file in rvz_files:
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(rvz_file))[0]}.iso")
            if os.path.exists(output_file):
                os.remove(output_file)
            subprocess.run([
                DOLPHIN_TOOL_NAME, "convert", "--format=iso",
                f"--input={rvz_file}", f"--output={output_file}"
            ])

    def convert_iso_to_rvz(input_dir, output_dir, compression_format, compression_level, block_size):
        """Convertit les fichiers ISO en RVZ en utilisant DolphinTool avec des options de compression."""
        iso_files = [
            os.path.join(input_dir, file)
            for file in os.listdir(input_dir)
            if file.endswith(".iso")
        ]

        for iso_file in iso_files:
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(iso_file))[0]}.rvz")
            if os.path.exists(output_file):
                os.remove(output_file)
            subprocess.run([
                DOLPHIN_TOOL_NAME, "convert", "--format=rvz",
                f"--input={iso_file}", f"--output={output_file}",
                f"--block_size={block_size}", f"--compression={compression_format}",
                f"--compression_level={compression_level}"
            ])

    def start_conversion():
        """Démarre le processus de conversion en fonction des paramètres sélectionnés."""
        input_dir = input_dir_var.get()
        output_dir = output_dir_var.get()
        operation = operation_var.get()
        compression_format = compression_format_var.get()
        compression_level = compression_level_var.get()
        block_size = block_size_var.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner les répertoires d'entrée et de sortie.")
            return

        if operation == "ISO vers RVZ":
            convert_iso_to_rvz(input_dir, output_dir, compression_format, compression_level, block_size)
        elif operation == "RVZ vers ISO":
            convert_rvz_to_iso(input_dir, output_dir)
        else:
            messagebox.showerror("Erreur", "Opération inconnue sélectionnée.")

        messagebox.showinfo("Terminé", "La conversion est terminée.")

    # Interface graphique
    root = ctk.CTk()
    root.title("Convertisseur RVZ/ISO")

    # Variables CTk
    input_dir_var = ctk.StringVar()
    output_dir_var = ctk.StringVar()
    operation_var = ctk.StringVar(value="ISO vers RVZ")
    compression_format_var = ctk.StringVar(value="zstd")
    compression_level_var = ctk.IntVar(value=5)
    block_size_var = ctk.StringVar(value="131072")

    # Fonctions de sélection de répertoire
    def browse_input_dir():
        input_dir = select_directory("Sélectionnez le répertoire d'entrée")
        input_dir_var.set(input_dir)

    def browse_output_dir():
        output_dir = select_directory("Sélectionnez le répertoire de sortie")
        output_dir_var.set(output_dir)

    # Layout de l'interface
    ctk.CTkLabel(root, text="Répertoire d'entrée :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    ctk.CTkEntry(root, textvariable=input_dir_var, width=300).grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkButton(root, text="Parcourir...", command=browse_input_dir, width=200).grid(row=0, column=2, padx=5, pady=5)

    ctk.CTkLabel(root, text="Répertoire de sortie :", font=("Arial", 16)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    ctk.CTkEntry(root, textvariable=output_dir_var, width=300).grid(row=1, column=1, padx=5, pady=5)
    ctk.CTkButton(root, text="Parcourir...", command=browse_output_dir, width=200).grid(row=1, column=2, padx=5, pady=5)

    ctk.CTkLabel(root, text="Opération :", font=("Arial", 16)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    operation_menu = ctk.CTkOptionMenu(root, variable=operation_var, values=["ISO vers RVZ", "RVZ vers ISO"])
    operation_menu.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(root, text="Compression Format :", font=("Arial", 16)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
    compression_format_menu = ctk.CTkOptionMenu(root, variable=compression_format_var, values=["zstd", "lzma2", "lzma", "bzip", "none"])
    compression_format_menu.grid(row=3, column=1, padx=5, pady=5)

    ctk.CTkLabel(root, text="Compression Level :", font=("Arial", 16)).grid(row=4, column=0, padx=5, pady=5, sticky="e")
    compression_level_menu = ctk.CTkOptionMenu(root, variable=compression_level_var, values=[str(i) for i in range(1, 23)])
    compression_level_menu.grid(row=4, column=1, padx=5, pady=5)

    ctk.CTkLabel(root, text="Block Size (Bytes) :", font=("Arial", 16)).grid(row=5, column=0, padx=5, pady=5, sticky="e")
    block_size_menu = ctk.CTkOptionMenu(root, variable=block_size_var, values=["32768", "65536", "131072", "262144", "524288", "1048576", "2097152", "8388608", "16777216", "33554432"])
    block_size_menu.grid(row=5, column=1, padx=5, pady=5)

    ctk.CTkButton(root, text="Démarrer la conversion", command=start_conversion, width=200).grid(row=6, column=1, padx=5, pady=10)

    # Vérification et lancement
    check_and_download_dolphintool()
    root.mainloop()

if __name__ == '__main__':
    main()