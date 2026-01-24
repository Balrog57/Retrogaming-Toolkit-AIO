import os
import subprocess
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tempfile
import shutil

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def extract_first_image(file_path, output_dir):
    try:
        try: import utils
        except ImportError: return messagebox.showerror("Err", "Utils missing")

        temp_dir = tempfile.mkdtemp()
        manager = utils.DependencyManager()
        if not manager.bootstrap_7za(): raise Exception("7za missing")
             
        cmd = [manager.seven_za_path, 'e', file_path, f'-o{temp_dir}', '*.jpg', '*.jpeg', '*.png', '-r', '-y']
        su = subprocess.STARTUPINFO(); su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=su, capture_output=True)
        
        found_img = None
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    found_img = os.path.join(root, f)
                    break
            if found_img: break
            
        if found_img:
            dest = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.png")
            Image.open(found_img).save(dest)
            
        shutil.rmtree(temp_dir)
    except Exception as e: print(f"Err {file_path}: {e}")

def process_directory(input_dir):
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(('.cbz', '.cbr', '.pdf', '.zip', '.rar')):
                extract_first_image(os.path.join(root, f), input_dir)
    messagebox.showinfo("Fini", "Extraction terminée !")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Extracteur de Cover")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_BG = theme.COLOR_BG
        else:
            self.title("Extracteur de Cover")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_BG = None
            
        self.geometry("500x350")
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(main_frame, text="Extracteur de Cover", font=theme.get_font_title(24) if theme else ("Arial", 24, "bold")).pack(pady=(10, 25))
        
        self.lbl = ctk.CTkLabel(main_frame, text="Choisissez un répertoire :", font=theme.get_font_main(14) if theme else ("Arial", 14))
        self.lbl.pack(pady=10)

        ctk.CTkButton(main_frame, text="Parcourir", command=self.browse, width=220, height=40, fg_color=self.COLOR_ACCENT).pack(pady=15)
        ctk.CTkButton(main_frame, text="EXECUTER", command=self.validate, width=220, height=40, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

        self.sel_dir = ""

    def browse(self):
        self.sel_dir = filedialog.askdirectory()
        if self.sel_dir: self.lbl.configure(text=f"Dir: {self.sel_dir}")

    def validate(self):
        if not self.sel_dir: return messagebox.showwarning("Warn", "Sélectionnez un dossier.")
        process_directory(self.sel_dir)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()