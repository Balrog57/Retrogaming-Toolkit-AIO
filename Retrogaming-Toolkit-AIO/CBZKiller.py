import os
# import zipfile # Removed for 7za
# import rarfile # Removed for 7za
# from patoolib import extract_archive # Removed for 7za
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import fitz  # PyMuPDF
import concurrent.futures
import tempfile
import subprocess
import shutil

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

def process_pdf_to_cbz(pdf_path, cbz_path):
    """
    Worker function for PDF to CBZ conversion.
    Returns (success, message)
    """
    try:
        pdf_document = fitz.open(pdf_path)
        with zipfile.ZipFile(cbz_path, 'w') as cbz:
            for i in range(len(pdf_document)):
                try:
                    page = pdf_document.load_page(i)
                    pix = page.get_pixmap()
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_img:
                        image_path = tmp_img.name
                    pix.save(image_path)
                    cbz.write(image_path, arcname=f"page_{i+1:03d}.jpg")
                    os.remove(image_path)
                except Exception as e:
                    return False, f"Erreur page {i+1} de {pdf_path}: {e}"
        pdf_document.close()
        return True, f"Succès: {pdf_path}"
    except Exception as e:
        return False, f"Erreur PDF {pdf_path}: {e}"

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
            
            # Utilisation de ThreadPoolExecutor pour la parallélisation
            completed_count = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                future_to_file = {}
                for file_path in files_to_convert:
                    cbz_path = os.path.splitext(file_path)[0] + '.cbz'
                    if file_path.endswith('.pdf'):
                        future = executor.submit(process_pdf_to_cbz, file_path, cbz_path)
                        future_to_file[future] = file_path
                    elif file_path.endswith('.cbr'):
                        # CBR conversion kept in main class method for now as it might use self.log or utils
                        # actually we can wrap it or call it inside a lambda, 
                        # but threading tkinter methods directly is risky if they touch GUI.
                        # convert_cbr_to_cbz uses utils and subprocess, safe for threads if logging is safe.
                        future = executor.submit(self.convert_cbr_to_cbz, file_path, cbz_path)
                        future_to_file[future] = file_path

                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        # Handle return from process_pdf_to_cbz or convert_cbr_to_cbz
                        # convert_cbr_to_cbz raises exception on error, returns nothing on success
                        # process_pdf_to_cbz returns (success, msg)
                        
                        if file_path.endswith('.pdf'):
                            success, msg = future.result()
                            if not success:
                                self.log(msg)
                            else:
                                self.log(f"Converti: {file_path}")
                        else:
                            future.result() # Will raise if exception occurred
                            self.log(f"Converti: {file_path}")

                        # Supprimer le fichier d'origine si la case est cochée
                        if self.delete_originals_var.get():
                            try:
                                os.remove(file_path)
                                self.log(f"Originaux supprimés: {file_path}")
                            except OSError as e:
                                self.log(f"Impossible de supprimer {file_path}: {e}")

                    except Exception as e:
                        self.log(f"Erreur avec {file_path}: {e}")
                    
                    completed_count += 1
                    self.update_progress(completed_count / total_files)

            self.log("Conversion terminée avec succès.")
            
        except Exception as e:
            self.log(f"Erreur générale lors de la conversion : {type(e).__name__} - {str(e)}")
        finally:
            # Réactiver les boutons (sur le thread principal via after si besoin, mais ici on est dans le thread worker)
            # Tkinter est parfois capricieux appelant configure depuis un thread
            self.after(0, lambda: self.button_select_folder.configure(state="normal"))
            self.after(0, lambda: self.button_convert.configure(state="normal"))
            self.conversion_in_progress = False

    def update_progress(self, val):
        self.after(0, self.progress_bar.set, val)

    # convert_pdf_to_cbz method removed as it is replaced by process_pdf_to_cbz global function for pickling/threading support

    def convert_cbr_to_cbz(self, cbr_path, cbz_path):
        """Convertit un fichier CBR en CBZ using 7za."""
        import subprocess
        try:
            # Extraction
            # Use tempfile to avoid race conditions
            with tempfile.TemporaryDirectory() as temp_dir:
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

                # Ensure output path is absolute because we change cwd
                cbz_path_abs = os.path.abspath(cbz_path)

                # cmd: 7za a -tzip "archive.cbz" "*" (run from inside temp_dir)
                cmd = [seven_za, 'a', '-tzip', cbz_path_abs, '*']

                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                subprocess.run(cmd, check=True, cwd=temp_dir, startupinfo=startupinfo, capture_output=True)

        except Exception as e:
            self.log(f"Erreur lors de la conversion du CBR {cbr_path} : {type(e).__name__} - {str(e)}")
            raise

    def log(self, message):
        """Ajoute un message au log (Thread-safe)."""
        self.after(0, self._log_impl, message)

    def _log_impl(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

def main():
    app = PDFCBRtoCBZConverter()
    app.mainloop()

if __name__ == "__main__":
    main()