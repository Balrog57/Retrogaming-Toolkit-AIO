import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import tempfile

try:
    import utils
except ImportError:
    pass

try:
    import theme
except ImportError:
    theme = None

class BGBackupApp:
    def __init__(self, root):
        self.root = root
        
        if theme:
            theme.apply_theme(root, "BGBackup - Sakura Night")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_CARD = theme.COLOR_CARD_BG
        else:
            ctk.set_appearance_mode("dark")
            root.title("BGBackup")
            root.geometry("450x350")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_CARD = None

        main = ctk.CTkFrame(root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main, text="BGBackup", font=theme.get_font_title(24) if theme else ("Arial", 24)).pack(pady=(0, 20))

        # Buttons
        self.select_button = ctk.CTkButton(main, text="Dossier ROMS (Source)", command=self.select_roms_folder, width=250, fg_color=self.COLOR_ACCENT)
        self.select_button.pack(pady=10)

        self.dest_button = ctk.CTkButton(main, text="Dossier Backup (Destination)", command=self.select_dest_folder, width=250, fg_color=self.COLOR_ACCENT)
        self.dest_button.pack(pady=10)

        self.backup_button = ctk.CTkButton(main, text="CRÉER LE BACKUP", command=self.create_backup, width=250, state="disabled", 
                                           fg_color=theme.COLOR_SUCCESS if theme else "green", font=("Arial", 14, "bold"))
        self.backup_button.pack(pady=20)
        
        # Progress
        self.progress_bar = ctk.CTkProgressBar(main, width=300, progress_color=self.COLOR_ACCENT)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(main, text="", text_color=theme.COLOR_TEXT_MAIN if theme else "white")
        self.status_label.pack(pady=5)

        self.roms_folder = None
        self.dest_folder = None
        
        self.backup_thread = None
        self.backup_error = None
        self.backup_success = None
        self.current_status = ""

    def select_roms_folder(self):
        self.roms_folder = filedialog.askdirectory(title="Dossier ROMS")
        self.check_ready()

    def select_dest_folder(self):
        self.dest_folder = filedialog.askdirectory(title="Dossier Destination")
        self.check_ready()
        
    def check_ready(self):
        if self.roms_folder and self.dest_folder:
            self.backup_button.configure(state="normal")
        else:
            self.backup_button.configure(state="disabled")

    def create_backup(self):
        if not self.roms_folder or not self.dest_folder: return
        
        self.backup_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.dest_button.configure(state="disabled")
        
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        self.status_label.configure(text="Démarrage...")
        
        self.backup_thread = threading.Thread(target=self._run_backup_logic)
        self.backup_thread.start()
        self.root.after(100, self.monitor_backup)

    def monitor_backup(self):
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
            self.check_ready()
            
            if self.backup_error:
                messagebox.showerror("Erreur", f"Erreur: {self.backup_error}")
            elif self.backup_success:
                messagebox.showinfo("Succès", f"Backup OK: {self.backup_success}")

    def _run_backup_logic(self):
        self.backup_error = None
        self.backup_success = None
        self.current_status = "Initialisation..."
        try:
             import utils
        except ImportError:
             self.backup_error = "Utils manquant"
             return

        try:
            manager = utils.DependencyManager()
            if not manager.bootstrap_7za():
                 self.backup_error = "7za error"
                 return

            out_dir = self.dest_folder
            zip_name = os.path.abspath(os.path.join(out_dir, "gamelist_backup.zip"))
            
            self.current_status = "Scanning gamelist.xml..."
            files = []
            count = 0
            for r, d, f in os.walk(self.roms_folder):
                if "gamelist.xml" in f:
                    gp = os.path.join(r, "gamelist.xml")
                    rp = os.path.relpath(gp, self.roms_folder)
                    files.append(rp)
                    count += 1
                    if count % 10 == 0: self.current_status = f"Found: {count}..."
                
                # Depth limit 2
                if os.path.relpath(r, self.roms_folder).count(os.sep) >= 2: d.clear()
            
            if not files: raise Exception("No gamelist.xml found")

            self.current_status = f"Compressing {count} files..."
            fd, list_p = tempfile.mkstemp(text=True)
            try:
                with os.fdopen(fd, 'w') as f:
                    for item in files: f.write(item + "\n")
                
                cmd = [manager.seven_za_path, 'a', '-tzip', zip_name, f'@{list_p}']
                su = subprocess.STARTUPINFO(); su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(cmd, cwd=self.roms_folder, check=True, startupinfo=su, capture_output=True)
                
                self.backup_success = zip_name
                self.current_status = "Terminé !"
            finally:
                if os.path.exists(list_p): os.remove(list_p)

        except Exception as e:
            self.backup_error = str(e)

def main():
    root = ctk.CTk()
    app = BGBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()