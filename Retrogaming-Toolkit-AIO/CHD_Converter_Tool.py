import os
import subprocess
import multiprocessing
import urllib.request
import shutil
import zipfile
import tempfile
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, IntVar, BooleanVar
import patoolib
import sys

# Import utils
try:
    import utils
except ImportError:
    pass

CHDMAN_URL = "https://wiki.recalbox.com/tutorials/utilities/rom-conversion/chdman/chdman.zip"
CHDMAN_ZIP = "chdman.zip"

def get_chdman_path():
    # 1. Check bundled/utils path
    if 'utils' in sys.modules:
        bin_path = utils.get_binary_path("chdman.exe")
        if os.path.exists(bin_path):
            return bin_path
    
    # 2. Check AppData
    app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', "chdman.exe")
    if os.path.exists(app_data_path):
        return app_data_path
        
    return app_data_path # Default to AppData for download target

CHDMAN_EXE = get_chdman_path()

class CHDmanGUI:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Détecter et configurer les cœurs CPU
        self.max_cores = multiprocessing.cpu_count()
        print(f"Nombre de cœurs CPU détectés : {self.max_cores}")
        print(f"Vous pouvez utiliser jusqu'à {self.max_cores} cœurs pour la conversion")
        
        self.root.title("CHD_Converter_Tool par Balrog")
        self.root.geometry("800x600")

        # Variables pour les dossiers source et destination
        self.source_folder = StringVar()
        self.destination_folder = StringVar()
        self.num_cores = IntVar(value=self.max_cores)
        self.option = StringVar(value="Info")
        self.overwrite = BooleanVar(value=True)  # Overwrite par défaut activé
        self.available_cores = [str(i) for i in range(1, self.max_cores + 1)]
        
        # Main container avec grille
        main_frame = ctk.CTkScrollableFrame(root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Créer des cadres avec grille
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        middle_frame = ctk.CTkFrame(main_frame)
        middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Cadre supérieur : Dossiers source et destination
        ctk.CTkLabel(top_frame, text="Dossier Source :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(top_frame, textvariable=self.source_folder, width=300).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="...", width=30, command=self.parcourir_dossier_source).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(top_frame, text="Dossier Destination :", font=("Arial", 16)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(top_frame, textvariable=self.destination_folder, width=300).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(top_frame, text="...", width=30, command=self.parcourir_dossier_destination).grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(top_frame, text="Inverser", command=self.inverser_dossiers).grid(row=2, column=1, pady=10)

        # Cadre du milieu : Options et sélection des cœurs
        ctk.CTkLabel(middle_frame, text="Options :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(middle_frame, text="Info", variable=self.option, value="Info").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(middle_frame, text="Vérifier", variable=self.option, value="Verify").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(middle_frame, text="Convertir", variable=self.option, value="Convert").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkRadioButton(middle_frame, text="Extraire", variable=self.option, value="Extract").grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Option Overwrite
        ctk.CTkCheckBox(middle_frame, text="Overwrite", variable=self.overwrite).grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Sélection du nombre de cœurs
        cores_frame = ctk.CTkFrame(middle_frame, fg_color="#1a1a1a", corner_radius=10)
        cores_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=5, pady=15)
        
        cores_container = ctk.CTkFrame(cores_frame, fg_color="transparent")
        cores_container.pack(fill="x", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            cores_container,
            text=f"Optimisation CPU (1-{self.max_cores} cœurs) :",
            font=("Arial", 16, "bold"),
            text_color="#ffffff",
            fg_color="transparent"
        ).pack(side="left", padx=(0, 15))
        
        self.cores_slider = ctk.CTkSlider(
            cores_container,
            from_=1,
            to=self.max_cores,
            number_of_steps=self.max_cores-1,
            variable=self.num_cores,
            width=350,
            height=25,
            progress_color="#1f6aa5",
            button_color="#144870",
            button_hover_color="#0d3550",
            border_width=2,
            border_color="#0d3550"
        )
        self.cores_slider.pack(side="left", expand=True, fill="x", padx=10)
        self.cores_slider.set(self.max_cores)
        
        self.cores_value_label = ctk.CTkLabel(
            cores_container,
            textvariable=self.num_cores,
            font=("Arial", 18, "bold"),
            width=50,
            text_color="#ffffff",
            fg_color="#1f6aa5",
            corner_radius=8,
            bg_color="#1a1a1a"
        )
        self.cores_value_label.pack(side="left", padx=(10, 0))

        # Progress Bar
        progress_frame = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
        progress_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        progress_container = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Titre de la progression
        progress_title = ctk.CTkLabel(
            progress_container,
            text="📊 Progression :",
            font=("Arial", 16, "bold"),
            text_color="#1f6aa5"
        )
        progress_title.pack(side="top", anchor="w", pady=(0, 10))

        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            orientation="horizontal",
            height=20,
            mode="determinate",
            progress_color="#1f6aa5",
            fg_color="#0d3550",
            corner_radius=10
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)

        # Conteneur pour le label et le pourcentage
        progress_info_frame = ctk.CTkFrame(progress_container, fg_color="transparent")
        progress_info_frame.pack(fill="x", pady=(5, 0))

        # Label de progression
        self.progress_label = ctk.CTkLabel(
            progress_info_frame,
            text="Progression :",
            font=("Arial", 14),
            text_color="#ffffff"
        )
        self.progress_label.pack(side="left", padx=(0, 5))

        # Pourcentage de progression
        self.progress_percent = ctk.CTkLabel(
            progress_info_frame,
            text="0%",
            font=("Arial", 14, "bold"),
            text_color="#1f6aa5"
        )
        self.progress_percent.pack(side="left")

        # Ajout d'une fonction de mise à jour de la progression
        self.update_progress(0)

        # Bouton Exécuter
        exec_frame = ctk.CTkFrame(bottom_frame)
        exec_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        bottom_frame.grid_rowconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        exec_button = ctk.CTkButton(exec_frame, 
                     text="Exécuter", 
                     command=self.executer_operation, 
                     width=250,
                     height=40,
                     fg_color="#1f6aa5",
                     hover_color="#144870",
                     font=("Arial", 16, "bold"))
        exec_button.grid(row=0, column=0, pady=10)
        
        exec_button_tooltip = ctk.CTkLabel(exec_frame, 
                     text="Lance l'opération sélectionnée sur les fichiers du dossier source",
                     font=("Arial", 12),
                     text_color="#808080")
        exec_button_tooltip.grid(row=1, column=0, pady=5)

        # Boutons de contrôle
        control_frame = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
        control_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        buttons_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Bouton Démarrer
        self.start_button = ctk.CTkButton(
            buttons_container,
            text="▶️ Démarrer",
            command=self.start_conversion,
            state="normal",  # Activé par défaut
            fg_color="#1f6aa5",
            hover_color="#144870",
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=10,
            border_width=2,
            border_color="#0d3550"
        )
        self.start_button.pack(side="left", padx=10, pady=10)

        # Bouton Arrêter
        self.stop_button = ctk.CTkButton(
            buttons_container,
            text="⏹️ Arrêter",
            command=self.stop_conversion,
            state="disabled",  # Désactivé par défaut
            fg_color="#dc3545",
            hover_color="#a71d2a",
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=10,
            border_width=2,
            border_color="#5c1d23"
        )
        self.stop_button.pack(side="left", padx=10, pady=10)

        # Bouton Pause
        self.pause_button = ctk.CTkButton(
            buttons_container,
            text="⏸️ Pause",
            command=self.pause_conversion,
            state="disabled",  # Désactivé par défaut
            fg_color="#ffc107",
            hover_color="#cc9a06",
            width=120,
            height=40,
            font=("Arial", 14, "bold"),
            corner_radius=10,
            border_width=2,
            border_color="#8a6d0b"
        )
        self.pause_button.pack(side="left", padx=10, pady=10)

        # Ajout des variables de contrôle
        self.is_running = False
        self.is_paused = False
        self.current_process = None  # Pour stocker le processus en cours

        tooltip = ctk.CTkLabel(
            control_frame,
            text="Contrôlez le processus de conversion avec ces boutons",
            font=("Arial", 12),
            text_color="#808080",
            fg_color="transparent"
        )
        tooltip.pack(pady=(0, 5))

        self.verifier_chdman()

    def parcourir_dossier_source(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)

    def parcourir_dossier_destination(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier destination")
        if folder:
            self.destination_folder.set(folder)

    def inverser_dossiers(self):
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        self.source_folder.set(destination)
        self.destination_folder.set(source)

    def verifier_chdman(self):
        """Vérifie si chdman.exe est disponible ; télécharge-le si nécessaire."""
        if not os.path.exists(CHDMAN_EXE):
            answer = messagebox.askyesno("CHDman manquant", f"CHDman est introuvable. Voulez-vous le télécharger ?\n{CHDMAN_URL}")
            if answer:
                self.telecharger_chdman()
            else:
                messagebox.showerror("Erreur", "CHDman est requis pour utiliser cet outil.")
                self.root.destroy()
                return

    def telecharger_chdman(self):
        """Télécharge chdman.exe depuis la release officielle MAME (via 7za)."""
        import requests
        import subprocess
        import sys 
        
        try:
            # Ensure AppData dir exists
            app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit')
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)

            target_exe = os.path.join(app_data_dir, "chdman.exe")
            seven_za_path = os.path.join(app_data_dir, "7za.exe")

            # URL MAME 0.284 Official (GitHub mirror)
            # The file is a self-extracting 7z archive (exe)
            MAME_URL = "https://github.com/mamedev/mame/releases/download/mame0284/mame0284b_x64.exe"

            mame_exe_path = os.path.join(tempfile.gettempdir(), "mame_setup.exe")

            # 1. Start Download MAME (Progress UI would be nice but simple logic for now)
            # Use requests
            headers = {'User-Agent': 'Mozilla/5.0'}
            # Note: This is a large file (~90MB), might take a while.
            messagebox.showinfo("Téléchargement en cours", "Téléchargement de MAME (env. 90Mo) pour extraire CHDman.\nVeuillez patienter...")
            
            with requests.get(MAME_URL, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(mame_exe_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # 2. Bootstrap 7za if needed
            if not os.path.exists(seven_za_path):
                url_7za = "https://www.7-zip.org/a/7za920.zip"
                zip_7za_path = os.path.join(tempfile.gettempdir(), "7za920.zip")
                
                r_7za = requests.get(url_7za, headers=headers, stream=True)
                r_7za.raise_for_status()
                with open(zip_7za_path, 'wb') as f:
                    for chunk in r_7za.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                import zipfile
                with zipfile.ZipFile(zip_7za_path, 'r') as z:
                    for file in z.namelist():
                        if file == "7za.exe":
                            z.extract(file, app_data_dir)
                            break
                if os.path.exists(zip_7za_path):
                    os.remove(zip_7za_path)
            
            if not os.path.exists(seven_za_path):
                raise Exception("Impossible d'installer 7za.exe")

            # 3. Extract ONLY chdman.exe from mame exe using 7za
            # Command: 7za.exe e mame.exe -o{app_data_dir} chdman.exe -y
            cmd = [seven_za_path, 'e', mame_exe_path, f'-o{app_data_dir}', 'chdman.exe', '-y']
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)

            # 4. Cleanup
            if os.path.exists(mame_exe_path):
                os.remove(mame_exe_path)

            if os.path.exists(target_exe):
                global CHDMAN_EXE
                CHDMAN_EXE = target_exe
                messagebox.showinfo("Succès", f"CHDman extrait avec succès depuis la release officielle MAME.")
            else:
                raise Exception("chdman.exe non trouvé après extraction de MAME.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation MAME/CHDman : {e}")
            self.root.destroy()
            sys.exit()

    def extraire_archives(self, dossier):
        """Extrait les archives ZIP, RAR et 7z dans le dossier."""
        for file in os.listdir(dossier):
            file_path = os.path.join(dossier, file)
            if file.lower().endswith((".zip", ".rar", ".7z")):
                try:
                    # Utilisation de patool pour extraire les archives
                    patoolib.extract_archive(file_path, outdir=dossier)
                    print(f"Archive extraite : {file_path}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction de {file_path}: {e}")

    def executer_chdman(self, commande, fichier_entree=None, fichier_sortie=None):
        """Exécute une commande CHDman avec gestion de l'interruption."""
        if not os.path.exists(CHDMAN_EXE):
            self.verifier_chdman()

        cmd = [CHDMAN_EXE] + commande
        if fichier_entree:
            cmd += ["-i", fichier_entree]
        if fichier_sortie:
            cmd += ["-o", fichier_sortie]

        try:
            # Lancer le processus avec subprocess.Popen
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.current_process = process  # Stocker le processus en cours

            # Attendre la fin du processus ou l'interruption
            while process.poll() is None:  # Tant que le processus est en cours
                if not self.is_running:  # Si l'utilisateur a cliqué sur Arrêter
                    process.terminate()  # Interrompre le processus
                    return "Processus interrompu par l'utilisateur."
                if self.is_paused:  # Si l'utilisateur a cliqué sur Mettre en pause
                    time.sleep(0.1)  # Mettre en pause temporairement

            # Récupérer la sortie du processus
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
            return stdout
        except subprocess.CalledProcessError as e:
            error_message = f"Erreur lors de l'exécution de la commande : {e.stderr}"
            response = messagebox.askretrycancel("Erreur", f"{error_message}\nVoulez-vous réessayer ou annuler ?")
            if response:
                return self.executer_chdman(commande, fichier_entree, fichier_sortie)  # Réessayer
            else:
                return error_message  # Annuler et retourner l'erreur

    def executer_operation(self):
        """Exécute l'opération sélectionnée."""
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        if not source or not destination:
            messagebox.showerror("Erreur", "Les dossiers source et destination doivent être sélectionnés.")
            return

        self.extraire_archives(source)

        log_file = os.path.join(destination, "chdman_log.txt")
        files_to_process = list(self.obtenir_fichiers(source, (".chd", ".cue", ".gdi", ".iso")))
        total_files = len(files_to_process)

        with open(log_file, "w") as log:
            for index, file in enumerate(files_to_process):
                if not self.is_running:
                    break  # Arrêter si l'utilisateur a cliqué sur Arrêter

                if self.is_paused:
                    while self.is_paused:
                        time.sleep(0.1)  # Mettre en pause

                # Mettre à jour la barre de progression
                progress = (index + 1) / total_files
                self.update_progress(progress)

                # Traitement du fichier
                if self.option.get() == "Info":
                    result = self.executer_chdman(["info"], fichier_entree=file)
                    log.write(f"Info pour {file}:\n{result}\n\n")
                elif self.option.get() == "Verify":
                    result = self.executer_chdman(["verify"], fichier_entree=file)
                    log.write(f"Vérification pour {file}:\n{result}\n\n")
                elif self.option.get() == "Convert":
                    fichier_sortie = os.path.join(destination, os.path.splitext(os.path.basename(file))[0] + ".chd")
                    if self.overwrite.get() or not os.path.exists(fichier_sortie):
                        result = self.executer_chdman(["createcd", "--numprocessors", str(self.num_cores.get())], fichier_entree=file, fichier_sortie=fichier_sortie)
                        log.write(f"Conversion de {file}:\n{result}\n\n")
                elif self.option.get() == "Extract":
                    fichier_sortie = os.path.join(destination, os.path.splitext(os.path.basename(file))[0] + ".cue")
                    if self.overwrite.get() or not os.path.exists(fichier_sortie):
                        result = self.executer_chdman(["extractcd"], fichier_entree=file, fichier_sortie=fichier_sortie)
                        log.write(f"Extraction de {file}:\n{result}\n\n")

        # Mettre à jour les états des boutons à la fin du processus
        self.is_running = False
        self.is_paused = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.pause_button.configure(state="disabled")

        messagebox.showinfo("Succès", f"Opération terminée. Le rapport est disponible dans {log_file}")

    def update_progress(self, value):
        """Met à jour la barre de progression et le pourcentage"""
        self.progress_bar.set(value)
        self.progress_percent.configure(text=f"{int(value*100)}%")
        
    def start_conversion(self):
        """Démarre le processus de conversion."""
        if self.is_running:
            return  # Ne rien faire si le processus est déjà en cours

        self.is_running = True
        self.is_paused = False

        # Mettre à jour les états des boutons
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.pause_button.configure(state="normal")

        # Exécuter l'opération dans un thread séparé
        self.process_thread = threading.Thread(target=self.executer_operation)
        self.process_thread.start()

    def stop_conversion(self):
        """Arrête le processus de conversion."""
        if not self.is_running:
            return  # Ne rien faire si le processus n'est pas en cours

        self.is_running = False
        self.is_paused = False

        # Interrompre le processus en cours
        if self.current_process:
            self.current_process.terminate()  # Interrompre le processus
            self.current_process = None

        # Supprimer les fichiers partiellement traités
        if self.option.get() == "Convert":
            for file in self.obtenir_fichiers(self.source_folder.get(), (".chd", ".cue", ".gdi", ".iso")):
                fichier_sortie = os.path.join(self.destination_folder.get(), os.path.splitext(os.path.basename(file))[0] + ".chd")
                if os.path.exists(fichier_sortie):
                    os.remove(fichier_sortie)  # Supprimer le fichier partiellement converti
        elif self.option.get() == "Extract":
            for file in self.obtenir_fichiers(self.source_folder.get(), (".chd", ".cue", ".gdi", ".iso")):
                fichier_sortie = os.path.join(self.destination_folder.get(), os.path.splitext(os.path.basename(file))[0] + ".cue")
                if os.path.exists(fichier_sortie):
                    os.remove(fichier_sortie)  # Supprimer le fichier partiellement extrait

        # Mettre à jour les états des boutons
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.pause_button.configure(state="disabled")

        messagebox.showinfo("Conversion", "Conversion arrêtée.")

    def pause_conversion(self):
        """Met en pause ou reprend le processus de conversion."""
        if not self.is_running:
            return  # Ne rien faire si le processus n'est pas en cours

        if self.is_paused:
            # Reprendre le processus
            self.is_paused = False
            self.pause_button.configure(text="⏸️ Pause")
            messagebox.showinfo("Conversion", "Conversion reprise.")
        else:
            # Mettre en pause le processus
            self.is_paused = True
            self.pause_button.configure(text="▶️ Reprendre")
            messagebox.showinfo("Conversion", "Conversion en pause.")

    def obtenir_fichiers(self, dossier, extensions):
        """Récupère les fichiers avec des extensions spécifiées."""
        for file in os.listdir(dossier):
            if file.lower().endswith(extensions):
                yield os.path.join(dossier, file)

def main():
    """Point d'entrée principal de l'application"""
    root = ctk.CTk()
    app = CHDmanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()