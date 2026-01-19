import os
import zipfile
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
            # Use a temporary directory for extracting images to avoid collisions
            with tempfile.TemporaryDirectory() as temp_dir:
                for i in range(len(pdf_document)):
                    try:
                        page = pdf_document.load_page(i)
                        pix = page.get_pixmap()
                        image_path = os.path.join(temp_dir, f"page_{i+1}.jpg")
                        pix.save(image_path)
                        cbz.write(image_path, arcname=f"page_{i+1}.jpg")
                    except Exception as e:
                        # Return partial failure or log?
                        # We will just raise to capture in the caller
                        raise Exception(f"Page {i+1} failed: {e}")
        pdf_document.close()
        return True, f"PDF converti : {os.path.basename(pdf_path)}"
    except Exception as e:
        return False, f"Erreur PDF {os.path.basename(pdf_path)}: {str(e)}"

def process_cbr_to_cbz(cbr_path, cbz_path, seven_za_path):
    """
    Worker function for CBR to CBZ conversion.
    Returns (success, message)
    """
    try:
        # Unique temp dir handled by context manager for auto-cleanup
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extraction
            cmd_extract = [seven_za_path, 'x', cbr_path, f'-o{temp_dir}', '-y']

            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(cmd_extract, check=True, startupinfo=startupinfo, capture_output=True)

            # Zip (Create CBZ)
            # Use wildcard to add all files from temp_dir
            cmd_zip = [seven_za_path, 'a', '-tzip', cbz_path, f'{temp_dir}{os.sep}*']
            subprocess.run(cmd_zip, check=True, startupinfo=startupinfo, capture_output=True)

        return True, f"CBR converti : {os.path.basename(cbr_path)}"
    except Exception as e:
        return False, f"Erreur CBR {os.path.basename(cbr_path)}: {str(e)}"

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

            # Bootstrap 7za once
            seven_za_path = None
            try:
                import utils
                manager = utils.DependencyManager(self)
                if manager.bootstrap_7za():
                     seven_za_path = manager.seven_za_path
            except ImportError:
                 self.log("Module utils manquant, impossible d'utiliser 7za.")
            except Exception as e:
                 self.log(f"Erreur lors de l'initialisation de 7za: {e}")

            if not seven_za_path:
                 self.log("Attention: 7za non trouvé. La conversion CBR échouera.")


            # Initialiser la barre de progression
            self.progress_bar.set(0)
            total_files = len(files_to_convert)

            # Use CPU count for workers, default to 4
            max_workers = os.cpu_count() or 4
            self.log(f"Démarrage de la conversion avec {max_workers} threads...")

            processed_count = 0

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for file_path in files_to_convert:
                    cbz_path = os.path.splitext(file_path)[0] + '.cbz'

                    if file_path.endswith('.pdf'):
                        future = executor.submit(process_pdf_to_cbz, file_path, cbz_path)
                        futures[future] = file_path
                    elif file_path.endswith('.cbr'):
                        if seven_za_path:
                            future = executor.submit(process_cbr_to_cbz, file_path, cbz_path, seven_za_path)
                            futures[future] = file_path
                        else:
                            self.log(f"Ignoré (7za manquant): {file_path}")
                            processed_count += 1 # Count as processed (skipped)
                            continue

                for future in concurrent.futures.as_completed(futures):
                    file_path = futures[future]
                    try:
                        success, message = future.result()
                        if success:
                            self.log(message)
                            if self.delete_originals_var.get():
                                try:
                                    os.remove(file_path)
                                    self.log(f"Supprimé: {os.path.basename(file_path)}")
                                except Exception as del_err:
                                    self.log(f"Erreur suppression {os.path.basename(file_path)}: {del_err}")
                        else:
                            self.log(f"ECHEC: {message}")
                    except Exception as e:
                        self.log(f"Exception critique sur {os.path.basename(file_path)}: {e}")

                    processed_count += 1
                    self.after(0, self.update_progress, processed_count / total_files)

            self.log("Conversion terminée avec succès.")
        except Exception as e:
            self.log(f"Erreur générale lors de la conversion : {type(e).__name__} - {str(e)}")
        finally:
            # Réactiver les boutons via after pour être thread-safe
            self.after(0, self.toggle_controls, "normal")
            self.conversion_in_progress = False

    def toggle_controls(self, state):
        self.button_select_folder.configure(state=state)
        self.button_convert.configure(state=state)

    def update_progress(self, value):
        self.progress_bar.set(value)

    def log(self, message):
        """Ajoute un message au log."""
        # Using after to schedule GUI update on main thread
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
