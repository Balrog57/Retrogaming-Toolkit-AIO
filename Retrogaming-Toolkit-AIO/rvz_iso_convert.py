# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
    import subprocess
    import urllib.request
    import tarfile
    import sys
    import customtkinter as ctk
    from tkinter import filedialog, messagebox

    # Configuration du thème
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Import utils
    try:
        import utils
    except ImportError:
        pass

    # Nom du fichier DolphinTool
    # Nom du fichier DolphinTool
    def get_dolphin_tool_path():
        if 'utils' in sys.modules:
            bin_path = utils.get_binary_path("DolphinTool.exe")
            if os.path.exists(bin_path):
                return bin_path
        
        # AppData fallback
        app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', "DolphinTool.exe")
        if os.path.exists(app_data_path):
            return app_data_path
            
        return app_data_path

    DOLPHIN_TOOL_NAME = get_dolphin_tool_path()
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
            # Ensure AppData dir exists (since get_dolphin_tool_path defaults to it)
            app_data_dir = os.path.dirname(DOLPHIN_TOOL_NAME)
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)

            # Use requests for better reliability
            import requests
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(DOLPHIN_DOWNLOAD_URL, headers=headers, stream=True, verify=False)
            response.raise_for_status()
            
            archive_path = os.path.join(app_data_dir, "dolphin.7z")
            with open(archive_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            extract_dolphintool(archive_path)
            if os.path.exists(archive_path):
                os.remove(archive_path)
            messagebox.showinfo("Téléchargement Réussi", f"DolphinTool a été téléchargé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur de Téléchargement", f"Le téléchargement a échoué : {e}")
            sys.exit() # Changed from exit() to sys.exit()

    def extract_dolphintool(archive_path):
        """Extrait DolphinTool.exe d'une archive .7z en utilisant 7za.exe (bootstrapped)."""
        app_data_dir = os.path.dirname(DOLPHIN_TOOL_NAME)
        seven_za_path = os.path.join(app_data_dir, "7za.exe")

        try:
            # Step 1: Bootstrap 7za.exe if needed
            if not os.path.exists(seven_za_path):
                import requests
                import tempfile
                import zipfile
                
                url_7za = "https://www.7-zip.org/a/7za920.zip"
                zip_7za_path = os.path.join(tempfile.gettempdir(), "7za920.zip")
                
                headers = {'User-Agent': 'Mozilla/5.0'}
                r_7za = requests.get(url_7za, headers=headers, stream=True)
                r_7za.raise_for_status()
                with open(zip_7za_path, 'wb') as f:
                    for chunk in r_7za.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                with zipfile.ZipFile(zip_7za_path, 'r') as z:
                    for file in z.namelist():
                        if file == "7za.exe":
                            z.extract(file, app_data_dir)
                            break
                if os.path.exists(zip_7za_path):
                    os.remove(zip_7za_path)

            if not os.path.exists(seven_za_path):
                messagebox.showerror("Erreur", "Impossible d'installer le moteur 7-Zip (7za.exe).")
                sys.exit()

            # Step 2: Extract using 7za.exe
            import subprocess
            import tempfile
            temp_extract_dir = tempfile.mkdtemp()
            
            # Command: 7za.exe x archive.7z -o{output_dir} -y
            cmd = [seven_za_path, 'x', archive_path, f'-o{temp_extract_dir}', '-y']
            
            # Hide console
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)

            # Find DolphinTool.exe
            extracted_tool = None
            for root, dirs, files in os.walk(temp_extract_dir):
                if "DolphinTool.exe" in files:
                    extracted_tool = os.path.join(root, "DolphinTool.exe")
                    break
            
            if extracted_tool:
                import shutil
                shutil.move(extracted_tool, DOLPHIN_TOOL_NAME)
            else:
                raise FileNotFoundError("DolphinTool.exe non trouvé dans l'archive.")

            # Cleanup
            import shutil
            shutil.rmtree(temp_extract_dir, ignore_errors=True)

        except Exception as e:
            messagebox.showerror("Erreur d'extraction", f"Erreur lors de l'extraction de DolphinTool via 7za : {e}")
            sys.exit()

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