import os
import zipfile
import rarfile
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
        if file_path.endswith('.cbz') or file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        with zip_ref.open(file) as img_file:
                            img = Image.open(img_file)
                            img.save(os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.png"))
                            break
        elif file_path.endswith('.cbr') or file_path.endswith('.rar'):
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                for file in rar_ref.namelist():
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        with rar_ref.open(file) as img_file:
                            img = Image.open(img_file)
                            img.save(os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.png"))
                            break
        elif file_path.endswith('.pdf'):
            # Utilisation de PyMuPDF pour extraire la première image du PDF
            pdf_document = fitz.open(file_path)
            first_page = pdf_document.load_page(0)  # Charger la première page
            pix = first_page.get_pixmap()  # Convertir la page en image
            output_image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.png")
            pix.save(output_image_path)  # Sauvegarder l'image
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'extraction de l'image : {e}")

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