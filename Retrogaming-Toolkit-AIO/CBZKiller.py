import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import fitz 
import concurrent.futures
import tempfile
import zipfile
import subprocess
import shutil

# Theme
try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def process_pdf_to_cbz(pdf_path, cbz_path):
    try:
        doc = fitz.open(pdf_path)
        with zipfile.ZipFile(cbz_path, 'w') as cbz:
            for i in range(len(doc)):
                page = doc.load_page(i)
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp: img_p=tmp.name
                page.get_pixmap().save(img_p)
                cbz.write(img_p, arcname=f"p_{i+1:03d}.jpg")
                os.remove(img_p)
        doc.close()
        return True, f"OK: {pdf_path}"
    except Exception as e: return False, f"Err PDF {pdf_path}: {e}"

class PDFCBRtoCBZConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Convertisseur PDF/CBR vers CBZ")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_BG = theme.COLOR_BG
        else:
            self.title("Convertisseur PDF/CBR vers CBZ")
            self.geometry("600x550")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_BG = "#333"

        self.resizable(False, False)

        ctk.CTkLabel(self, text="Convertisseur PDF/CBR vers CBZ", font=theme.get_font_title(20) if theme else ("Arial", 20)).pack(pady=10)

        self.btn_sel = ctk.CTkButton(self, text="Sélectionner Dossier", command=self.select_folder, width=200, fg_color=self.COLOR_ACCENT)
        self.btn_sel.pack(pady=10)

        self.del_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Suppr. originaux après", variable=self.del_var, fg_color=self.COLOR_ACCENT).pack(pady=10)

        self.log_text = ctk.CTkTextbox(self, width=550, height=200, state="disabled", font=("Consolas", 11))
        self.log_text.pack(pady=10)

        self.prog = ctk.CTkProgressBar(self, width=400, progress_color=self.COLOR_ACCENT)
        self.prog.pack(pady=10)
        self.prog.set(0)

        self.btn_go = ctk.CTkButton(self, text="CONVERTIR", command=self.start_conversion, width=200, state="disabled", fg_color=theme.COLOR_SUCCESS if theme else "green")
        self.btn_go.pack(pady=10)

        self.folder_path = None
        self.running = False

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.log(f"Dir: {self.folder_path}")
            self.btn_go.configure(state="normal")
        else:
            self.btn_go.configure(state="disabled")

    def start_conversion(self):
        if self.running: return
        self.running = True
        self.btn_sel.configure(state="disabled")
        self.btn_go.configure(state="disabled")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        try:
            files = []
            for r, _, f_list in os.walk(self.folder_path):
                for f in f_list:
                    if f.lower().endswith(('.pdf', '.cbr')):
                        files.append(os.path.join(r, f))

            if not files:
                self.log("Aucun fichier trouvé.")
                return

            self.update_prog(0)
            total = len(files)
            done = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as exe:
                futures = {}
                for fp in files:
                    cbz = os.path.splitext(fp)[0] + '.cbz'
                    if fp.lower().endswith('.pdf'):
                        ft = exe.submit(process_pdf_to_cbz, fp, cbz)
                        futures[ft] = fp
                    elif fp.lower().endswith('.cbr'):
                        ft = exe.submit(self.convert_cbr, fp, cbz)
                        futures[ft] = fp
                
                for fut in concurrent.futures.as_completed(futures):
                    fp = futures[fut]
                    try:
                        if fp.lower().endswith('.pdf'):
                            ok, msg = fut.result()
                            self.log(msg)
                        else:
                            fut.result()
                            self.log(f"OK CBR: {fp}")

                        if self.del_var.get():
                            try: os.remove(fp); self.log(f"Suppr: {fp}")
                            except: pass
                    except Exception as e:
                         self.log(f"Err {fp}: {e}")
                    
                    done+=1
                    self.update_prog(done/total)

            self.log("Terminé.")

        except Exception as e:
            self.log(f"Fatal Err: {e}")
        finally:
            self.after(0, lambda: self.btn_sel.configure(state="normal"))
            self.after(0, lambda: self.btn_go.configure(state="normal"))
            self.running = False

    def convert_cbr(self, cbr, cbz):
        try:
             import utils
             with tempfile.TemporaryDirectory() as tmp:
                 utils.extract_with_7za(cbr, tmp, root=self)
                 manager = utils.DependencyManager(self)
                 cmd = [manager.seven_za_path, 'a', '-tzip', cbz, os.path.join(tmp, "*")]
                 si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
                 subprocess.run(cmd, check=True, startupinfo=si, capture_output=True)
        except Exception as e: raise e

    def update_prog(self, v):
        self.after(0, self.prog.set, v)

    def log(self, m):
        self.after(0, self._log, m)

    def _log(self, m):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", m + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

def main():
    app = PDFCBRtoCBZConverter()
    app.mainloop()

if __name__ == "__main__":
    main()