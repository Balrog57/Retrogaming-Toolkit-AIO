# Module généré automatiquement à partir de MaxCSO_Compression_Script.py

def main():
    import os
    import shutil
    import subprocess
    import tempfile
    import customtkinter as ctk
    from tkinter import filedialog, messagebox, StringVar, IntVar
    import webbrowser
    import requests
    import multiprocessing

    # Configuration du thème
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème bleu

    # Import utils
    try:
        import utils
    except ImportError:
        pass

    def find_7z():
        """Vérifie l'emplacement de 7z.exe et retourne son chemin complet."""
        possible_paths = [
            shutil.which("7z"),
            "C:\\Program Files\\7-Zip\\7z.exe",
            "C:\\Program Files (x86)\\7-Zip\\7z.exe"
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        return None

    def download_and_extract_maxcso():
        """Télécharge et extrait maxcso.exe si nécessaire en utilisant 7z."""
        url = "https://github.com/unknownbrackets/maxcso/releases/download/v1.13.0/maxcso_v1.13.0_windows.7z"
        archive_path = "maxcso.7z"

        if not os.path.exists("maxcso.exe"):
            if messagebox.askyesno("Télécharger MaxCSO", "maxcso.exe est introuvable. Voulez-vous le télécharger maintenant ?"):
                try:
                    response = requests.get(url, stream=True)
                    with open(archive_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Vérification et utilisation de 7z
                    seven_zip_path = find_7z()
                    if not seven_zip_path:
                        messagebox.showerror("Erreur", "L'outil 7z (SevenZip) est requis pour extraire l'archive. Veuillez l'installer et réessayer.")
                        return False

                    # Extraction avec 7z
                    extract_dir = tempfile.mkdtemp()
                    subprocess.run([seven_zip_path, "x", archive_path, f"-o{extract_dir}"], check=True)

                    extracted_file = [f for f in os.listdir(extract_dir) if f.lower() == "maxcso.exe"]
                    if extracted_file:
                        shutil.move(os.path.join(extract_dir, extracted_file[0]), os.getcwd())
                    else:
                        messagebox.showerror("Erreur", "maxcso.exe n'a pas été trouvé dans l'archive téléchargée.")
                        return False
                except Exception as e:
                    messagebox.showerror("Erreur", f"Une erreur s'est produite lors du téléchargement ou de l'extraction : {e}")
                    return False
                finally:
                    if os.path.exists(archive_path):
                        os.remove(archive_path)
                    if os.path.exists(extract_dir):
                        shutil.rmtree(extract_dir)

        return os.path.exists("maxcso.exe")

    def get_cpu_count():
        """Retourne le nombre de cœurs CPU disponibles."""
        return multiprocessing.cpu_count()

    def compress_iso(input_dir, output_dir, replace_original, progress_var, progress_label):
        """Compresse les fichiers ISO à l'aide de MaxCSO."""
        # Use bundled binary if available, otherwise check/download
        if 'utils' in sys.modules and os.path.exists(utils.get_binary_path("maxcso.exe")):
            maxcso_path = utils.get_binary_path("maxcso.exe")
        else:
            if not download_and_extract_maxcso():
                return
            maxcso_path = "maxcso.exe"

        iso_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".iso")]
        if not iso_files:
            messagebox.showinfo("Info", "Aucun fichier ISO trouvé dans le dossier sélectionné.")
            return

        temp_dir = tempfile.mkdtemp()
        total_files = len(iso_files)
        cpu_count = get_cpu_count()

        try:
            for idx, iso_file in enumerate(iso_files, start=1):
                input_path = os.path.join(input_dir, iso_file)
                output_path = os.path.join(temp_dir, f"{os.path.splitext(iso_file)[0]}.cso")

                command = [maxcso_path, "--fast", input_path, "-o", output_path, f"--threads={cpu_count}"]
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode != 0:
                    messagebox.showerror("Erreur", f"Erreur lors de la compression de {iso_file} :\n{result.stderr}")
                    continue

                if replace_original:
                    shutil.move(output_path, input_path)
                else:
                    shutil.move(output_path, os.path.join(output_dir, f"{os.path.splitext(iso_file)[0]}.cso"))

                progress = (idx / total_files) * 100
                progress_var.set(progress)
                progress_label.configure(text=f"Progression : {progress:.2f}%")

            messagebox.showinfo("Succès", f"Compression terminée avec succès en utilisant {cpu_count} cœurs CPU !")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def browse_input():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            input_var.set(folder_selected)

    def browse_output():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            output_var.set(folder_selected)

    def toggle_input_output(*args):
        if replace_var.get() == 1:
            output_var.set("")
            output_label.pack_forget()
            output_button.pack_forget()
            output_display.pack_forget()
        else:
            output_label.pack(anchor="w", padx=20, pady=5)
            output_button.pack(pady=5)
            output_display.pack(pady=5)

    def start_compression():
        input_dir = input_var.get()
        output_dir = output_var.get()
        replace_original = replace_var.get()

        if not input_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier contenant les fichiers à traiter.")
            return

        if not replace_original and not output_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie.")
            return

        progress_var.set(0)
        progress_label.configure(text="Progression : 0%")
        compress_iso(input_dir, output_dir, replace_original, progress_var, progress_label)

    # Création de l'interface CTk
    root = ctk.CTk()
    root.title("MaxCSO GUI")
    root.geometry("400x600")
    root.configure(bg="#1f1f1f")

    if not download_and_extract_maxcso():
        root.destroy()
        return

    input_var = StringVar()
    output_var = StringVar()
    replace_var = IntVar(value=0)
    progress_var = ctk.DoubleVar(value=0)
    replace_var.trace("w", toggle_input_output)

    # Header
    header = ctk.CTkFrame(root, fg_color="#292b2f", height=50)
    header.pack(fill="x")
    ctk.CTkLabel(header, text="MaxCSO Compressor", fg_color="#292b2f", text_color="white", font=("Arial", 16)).pack(pady=10)

    # Content
    content = ctk.CTkFrame(root, fg_color="#1f1f1f")
    content.pack(expand=True, fill="both")

    ctk.CTkLabel(content, text="Options :", text_color="white").pack(anchor="w", padx=20, pady=5)
    ctk.CTkRadioButton(content, text="Remplacer les fichiers originaux", variable=replace_var, value=1, fg_color="#4caf50", text_color="white").pack(anchor="w", padx=20)
    ctk.CTkRadioButton(content, text="Garder les fichiers originaux", variable=replace_var, value=0, fg_color="#4caf50", text_color="white").pack(anchor="w", padx=20)

    ctk.CTkLabel(content, text="Dossier de traitement :", text_color="white").pack(anchor="w", padx=20, pady=5)
    ctk.CTkButton(content, text="Parcourir", command=browse_input, fg_color="#4caf50", text_color="white", width=200).pack(pady=5)
    ctk.CTkLabel(content, textvariable=input_var, text_color="white", wraplength=350).pack(pady=5)

    output_label = ctk.CTkLabel(content, text="Dossier de sortie :", text_color="white")
    output_button = ctk.CTkButton(content, text="Parcourir", command=browse_output, fg_color="#4caf50", text_color="white", width=200)
    output_display = ctk.CTkLabel(content, textvariable=output_var, text_color="white", wraplength=350)

    if replace_var.get() == 0:
        output_label.pack(anchor="w", padx=20, pady=5)
        output_button.pack(pady=5)
        output_display.pack(pady=5)

    # Progress bar
    ctk.CTkLabel(content, text="Progression :", text_color="white").pack(anchor="w", padx=20, pady=5)
    progress_bar = ctk.CTkProgressBar(content, orientation="horizontal", width=300, variable=progress_var)
    progress_bar.pack(pady=10)
    progress_label = ctk.CTkLabel(content, text="Progression : 0%", text_color="white")
    progress_label.pack(pady=5)

    # Action button
    ctk.CTkButton(content, text="Lancer la compression", command=start_compression, fg_color="#2196f3", text_color="white", width=200).pack(pady=20)

    # Footer
    footer = ctk.CTkFrame(root, fg_color="#292b2f", height=50)
    footer.pack(fill="x")
    ctk.CTkLabel(footer, text="© 2025 - MaxCSO GUI", text_color="white").pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()