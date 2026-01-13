import os
import subprocess
# import zipfile
# import rarfile
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Fonction pour extraire la première image d'un fichier
def extract_first_image(file_path, output_dir):
    try:
        import shutil
        import tempfile
        try:
             import utils
        except ImportError:
             messagebox.showerror("Erreur", "Module utils manquant.")
             return

        # Temp dir for extraction
        temp_dir = tempfile.mkdtemp()
        
        # Extensions to look for inside archive
        # 7za wildcards
        # We try to extract only images
        # 7za e archive -o{dir} *.jpg *.png *.jpeg -r -y
        
        # Note: extract_with_7za helper accepts file_to_extract but here we wont multiple.
        # Let's call 7za directly via manager or modify helper?
        # Helper is simple. Let's do it manually using manager path for flexibility or just use helper if we don't pass file (extract all? risky if huge).
        # Better to modify helper? No, let's just use the manager instance here.
        
        manager = utils.DependencyManager()
        if not manager.bootstrap_7za():
             raise Exception("7za manquant")
             
        cmd = [manager.seven_za_path, 'e', file_path, f'-o{temp_dir}', '*.jpg', '*.jpeg', '*.png', '-r', '-y']
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)
        
        # Find first image in temp_dir
        found_img = None
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    found_img = os.path.join(root, f)
                    break
            if found_img: break
            
        if found_img:
            # Save as png in output_dir
            dest_name = f"{os.path.splitext(os.path.basename(file_path))[0]}.png"
            dest_path = os.path.join(output_dir, dest_name)
            
            # Convert to PNG using Pillow just in case
            img = Image.open(found_img)
            img.save(dest_path)
            # shutil.move(found_img, dest_path) # or just move if we don't care about format conversion, but original code converted to PNG.
            
        shutil.rmtree(temp_dir)

    except Exception as e:
        # messagebox.showerror("Erreur", f"Erreur lors de l'extraction de l'image : {e}")
        print(f"Erreur extraction {file_path}: {e}") # Non-blocking log


# Fonction pour parcourir les fichiers du répertoire
def process_directory(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.cbz', '.cbr', '.pdf', '.zip', '.rar')):
                extract_first_image(os.path.join(root, file), input_dir)
    messagebox.showinfo("Succès", "Extraction des images terminée !")

# Interface graphique
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Extracteur d'images")
        self.geometry("400x200")

        self.label = ctk.CTkLabel(self, text="Choisissez un répertoire :", font=("Arial", 16))
        self.label.pack(pady=10)

        self.button_browse = ctk.CTkButton(self, text="Parcourir", command=self.browse_directory, width=200)
        self.button_browse.pack(pady=10)

        self.button_validate = ctk.CTkButton(self, text="Valider", command=self.validate, width=200)
        self.button_validate.pack(pady=10)

        self.selected_directory = ""

    def browse_directory(self):
        self.selected_directory = filedialog.askdirectory()
        if self.selected_directory:
            self.label.configure(text=f"Répertoire sélectionné : {self.selected_directory}")

    def validate(self):
        if not self.selected_directory:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un répertoire.")
            return

        process_directory(self.selected_directory)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()