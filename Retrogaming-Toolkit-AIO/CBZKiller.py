import os
# import zipfile # Removed for 7za
# import rarfile # Removed for 7za
# from patoolib import extract_archive # Removed for 7za
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import fitz  # PyMuPDF

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

class PDFCBRtoCBZConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Convertisseur PDF/CBR vers CBZ")
        self.geometry("600x550")  # Ajustement de la taille pour la nouvelle case à cocher
        self.resizable(False, False)

        # Titre de l'application
        self.label_title = ctk.CTkLabel(self, text="Convertisseur PDF/CBR vers CBZ", font=("Arial", 20))
        self.label_title.pack(pady=10)

        # Bouton pour sélectionner le dossier parent
        self.button_select_folder = ctk.CTkButton(self, text="Sélectionner un dossier", command=self.select_folder, width=200)
        self.button_select_folder.pack(pady=10)

        # Case à cocher pour supprimer les fichiers d'origine
        self.delete_originals_var = ctk.BooleanVar(value=False)
        self.checkbox_delete_originals = ctk.CTkCheckBox(self, text="Supprimer les fichiers d'origine après conversion", variable=self.delete_originals_var)
        self.checkbox_delete_originals.pack(pady=10)

        # Zone de texte pour afficher les logs
        self.log_text = scrolledtext.ScrolledText(self, wrap="word", state="disabled", height=15, width=70, bg="#2e2e2e", fg="white")
        self.log_text.pack(pady=10)

        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Bouton pour démarrer la conversion
        self.button_convert = ctk.CTkButton(self, text="Convertir", command=self.start_conversion, width=200, state="disabled")
        self.button_convert.pack(pady=10)

        # Variables
        self.folder_path = None
        self.conversion_in_progress = False

    def select_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner un dossier parent."""
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.log(f"Dossier sélectionné : {self.folder_path}")
            self.button_convert.configure(state="normal")
        else:
            self.log("Aucun dossier sélectionné.")
            self.button_convert.configure(state="disabled")

    def start_conversion(self):
        """Démarre la conversion dans un thread séparé."""
        if self.conversion_in_progress:
            messagebox.showwarning("Conversion en cours", "Une conversion est déjà en cours.")
            return

        if not self.folder_path:
            messagebox.showwarning("Aucun dossier sélectionné", "Veuillez sélectionner un dossier.")
            return

        # Désactiver les boutons pendant la conversion
        self.button_select_folder.configure(state="disabled")
        self.button_convert.configure(state="disabled")
        self.conversion_in_progress = True

        # Lancer la conversion dans un thread séparé
        threading.Thread(target=self.convert_folder_to_cbz, daemon=True).start()

    def convert_folder_to_cbz(self):
        """Convertit tous les fichiers PDF et CBR en CBZ dans le dossier sélectionné."""
        try:
            # Récupérer la liste des fichiers à convertir
            files_to_convert = []
            for root, _, files in os.walk(self.folder_path):
                for file in files:
                    if file.endswith('.pdf') or file.endswith('.cbr'):
                        files_to_convert.append(os.path.join(root, file))

            if not files_to_convert:
                self.log("Aucun fichier PDF ou CBR trouvé.")
                return

            # Initialiser la barre de progression
            self.progress_bar.set(0)
            total_files = len(files_to_convert)

            # Convertir chaque fichier
            for i, file_path in enumerate(files_to_convert):
                try:
                    self.log(f"Conversion de {file_path}...")
                    if file_path.endswith('.pdf'):
                        cbz_path = os.path.splitext(file_path)[0] + '.cbz'
                        self.convert_pdf_to_cbz(file_path, cbz_path)
                    elif file_path.endswith('.cbr'):
                        cbz_path = os.path.splitext(file_path)[0] + '.cbz'
                        self.convert_cbr_to_cbz(file_path, cbz_path)

                    # Supprimer le fichier d'origine si la case est cochée
                    if self.delete_originals_var.get():
                        os.remove(file_path)
                        self.log(f"Fichier d'origine supprimé : {file_path}")

                    # Mettre à jour la barre de progression
                    self.progress_bar.set((i + 1) / total_files)
                    self.update()

                except Exception as e:
                    self.log(f"Erreur lors de la conversion de {file_path} : {type(e).__name__} - {str(e)}")

            self.log("Conversion terminée avec succès.")
        except Exception as e:
            self.log(f"Erreur générale lors de la conversion : {type(e).__name__} - {str(e)}")
        finally:
            # Réactiver les boutons
            self.button_select_folder.configure(state="normal")
            self.button_convert.configure(state="normal")
            self.conversion_in_progress = False

    def convert_pdf_to_cbz(self, pdf_path, cbz_path):
        """Convertit un fichier PDF en CBZ en utilisant PyMuPDF pour une conversion sans perte."""
        try:
            pdf_document = fitz.open(pdf_path)
            with zipfile.ZipFile(cbz_path, 'w') as cbz:
                for i in range(len(pdf_document)):
                    try:
                        page = pdf_document.load_page(i)
                        pix = page.get_pixmap()  # Utilise la résolution d'origine
                        image_path = f"temp_page_{i+1}.jpg"
                        pix.save(image_path)
                        cbz.write(image_path)
                        os.remove(image_path)
                    except Exception as e:
                        self.log(f"Erreur lors de la conversion de la page {i+1} du fichier {pdf_path} : {type(e).__name__} - {str(e)}")
            pdf_document.close()
        except Exception as e:
            self.log(f"Erreur lors de l'ouverture du PDF {pdf_path} : {type(e).__name__} - {str(e)}")
            raise

    def convert_cbr_to_cbz(self, cbr_path, cbz_path):
        """Convertit un fichier CBR en CBZ using 7za."""
        import shutil
        import subprocess
        try:
            # Extraction
            temp_dir = "temp_extract"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # Use utils for 7za extraction
            try:
                import utils
                utils.extract_with_7za(cbr_path, temp_dir, root=self)
            except ImportError:
                 self.log("Module utils manquant, impossible d'utiliser 7za.")
                 return

            # Création du CBZ (ZIP) avec 7za également pour respecter la demande
            # Si utils a le path de 7za, on l'utilise
            manager = utils.DependencyManager(self)
            seven_za = manager.seven_za_path
            
            # cmd: 7za a -tzip "archive.cbz" "./temp_extract/*"
            cmd = [seven_za, 'a', '-tzip', cbz_path, f'.{os.sep}{temp_dir}{os.sep}*']
            
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            else:
                startupinfo = None

            subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)

            shutil.rmtree(temp_dir)
        except Exception as e:
            self.log(f"Erreur lors de la conversion du CBR {cbr_path} : {type(e).__name__} - {str(e)}")
            raise

    def log(self, message):
        """Ajoute un message au log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
        self.update()

def main():
    app = PDFCBRtoCBZConverter()
    app.mainloop()

if __name__ == "__main__":
    main()