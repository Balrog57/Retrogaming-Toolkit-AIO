import os
# import zipfile
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

class BGBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGBackup")
        self.root.geometry("400x300") # Increased height for progress bar

        # En-tête de la GUI
        self.header_label = ctk.CTkLabel(root, text="BGBackup", font=("Arial", 24))
        self.header_label.pack(pady=20)

        # Bouton pour sélectionner le dossier roms
        self.select_button = ctk.CTkButton(root, text="Sélectionner le dossier roms", command=self.select_roms_folder, width=200)
        self.select_button.pack(pady=10)

        # Bouton pour sélectionner le dossier de destination
        self.dest_button = ctk.CTkButton(root, text="Dossier de destination (Requis)", command=self.select_dest_folder, width=200)
        self.dest_button.pack(pady=10)

        # Bouton pour créer le backup
        self.backup_button = ctk.CTkButton(root, text="Créer le backup", command=self.create_backup, width=200, state="disabled")
        self.backup_button.pack(pady=10)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(root, width=300)
        self.progress_bar.set(0)
        # self.progress_bar.pack(pady=10) # Packed only when running
        
        # Status Label
        self.status_label = ctk.CTkLabel(root, text="")
        self.status_label.pack(pady=5)

        # Variable pour stocker le chemin du dossier roms et destination
        self.roms_folder = None
        self.dest_folder = None
        
        self.backup_thread = None
        self.backup_error = None
        self.backup_success = None
        self.current_status = ""

    def select_roms_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier roms."""
        self.roms_folder = filedialog.askdirectory(title="Sélectionnez le dossier roms")
        self.check_ready()

    def select_dest_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier de destination."""
        self.dest_folder = filedialog.askdirectory(title="Sélectionnez le dossier de destination")
        self.check_ready()
        
    def check_ready(self):
        if self.roms_folder and self.dest_folder:
            self.backup_button.configure(state="normal")
        else:
            self.backup_button.configure(state="disabled")

    def create_backup(self):
        """Lance le backup en tâche de fond."""
        if not self.roms_folder:
            messagebox.showerror("Erreur", "Aucun dossier roms sélectionné.")
            return
        if not self.dest_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination.")
            return

        # Disable UI
        self.backup_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.dest_button.configure(state="disabled")
        
        # Show progress
        self.progress_bar.pack(pady=10)
        self.progress_bar.start() # Indeterminate mode
        self.status_label.configure(text="Démarrage...")
        
        import threading
        self.backup_thread = threading.Thread(target=self._run_backup_logic)
        self.backup_thread.start()
        self.root.after(100, self.monitor_backup)

    def monitor_backup(self):
        # Update Status Label
        if self.current_status:
            self.status_label.configure(text=self.current_status)

        if self.backup_thread.is_alive():
            self.root.after(100, self.monitor_backup)
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.status_label.configure(text="")
            
            self.select_button.configure(state="normal")
            self.dest_button.configure(state="normal")
            self.check_ready() # Re-enable backup button if valid
            
            if self.backup_error:
                messagebox.showerror("Erreur", f"Erreur: {self.backup_error}")
            elif self.backup_success:
                messagebox.showinfo("Succès", f"Backup créé avec succès : {self.backup_success}")

    def _run_backup_logic(self):
        self.backup_error = None
        self.backup_success = None
        self.current_status = "Initialisation..."
        
        import subprocess
        import tempfile
        try:
             import utils
        except ImportError:
             self.backup_error = "Utils manquant"
             return

        try:
            manager = utils.DependencyManager()
            if not manager.bootstrap_7za():
                 self.backup_error = "7za manquant"
                 return

            output_dir = self.dest_folder
            zip_filename = os.path.join(output_dir, "gamelist_backup.zip")
            zip_filename = os.path.abspath(zip_filename)
            
            # Collect files
            self.current_status = "Recherche des fichiers gamelist.xml..."
            files_to_zip = []
            count = 0
            for root_dir, dirs, files in os.walk(self.roms_folder):
                if "gamelist.xml" in files:
                    gamelist_path = os.path.join(root_dir, "gamelist.xml")
                    relative_path = os.path.relpath(gamelist_path, self.roms_folder)
                    files_to_zip.append(relative_path)
                    count += 1
                    if count % 5 == 0:
                        self.current_status = f"Recherche en cours : {count} fichiers trouvés..."

                # Limite la profondeur de recherche à 2 niveaux
                if os.path.relpath(root_dir, self.roms_folder).count(os.sep) >= 2:
                    dirs.clear()
            
            if not files_to_zip:
                 raise Exception("Aucun fichier gamelist.xml trouvé.")

            self.current_status = f"Préparation de l'archive ({count} fichiers)..."

            # Create listfile
            fd, list_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                for item in files_to_zip:
                    f.write(item + "\n")
            
            # Run 7za
            cmd = [manager.seven_za_path, 'a', '-tzip', zip_filename, f'@{list_path}']
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.current_status = f"Compression en cours de {count} fichiers..."
            # Run properly
            subprocess.run(cmd, cwd=self.roms_folder, check=True, startupinfo=startupinfo, capture_output=True)
            
            os.remove(list_path)
            self.backup_success = zip_filename
            self.current_status = "Terminé !"

        except Exception as e:
            self.backup_error = str(e)
            # Clean up listfile if exists? (Ignored for now, temp file)

def main():
    root = ctk.CTk()
    app = BGBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()