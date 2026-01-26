import customtkinter as ctk
import os
import sys
import threading
import shutil
from tkinter import filedialog, messagebox

# Add current directory to path to allow imports if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import theme
except ImportError:
    theme = None

class PatternCopierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Theme Setup ---
        if theme:
            theme.apply_theme(self, "Pattern Copier")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_BG = theme.COLOR_BG
            self.COLOR_CARD_BG = theme.COLOR_CARD_BG
            self.COLOR_TEXT = theme.COLOR_TEXT_MAIN
        else:
            self.title("Pattern Copier")
            ctk.set_appearance_mode("dark")
            self.COLOR_ACCENT = "#ff6699"
            self.COLOR_BG = "#151515"
            self.COLOR_CARD_BG = "#1e1e1e"
            self.COLOR_TEXT = "#ffffff"

        self.geometry("700x550")
        self.resizable(False, False)

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Log area expands

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Extraction par Modèle", 
                                      font=("Roboto", 20, "bold"), text_color=self.COLOR_ACCENT)
        self.title_label.pack(side="left")

        # Input Frame
        self.input_frame = ctk.CTkFrame(self, fg_color=self.COLOR_CARD_BG, corner_radius=10)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # 1. Witness File
        self.create_entry_row(self.input_frame, 0, "Fichier Témoin :", "witness", "Fichier qui servira de modèle (ex: device.png)", is_file=True)
        # 2. Source Root
        self.create_entry_row(self.input_frame, 1, "Dossier Source :", "source", "Racine de la recherche (ex: C:\\RetroFE)", is_file=False)
        # 3. Destination Root
        self.create_entry_row(self.input_frame, 2, "Destination :", "dest", "Dossier d'export (ex: D:\\Export)", is_file=False)

        # Action Buttons
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.start_btn = ctk.CTkButton(self.action_frame, text="Démarrer la Copie", 
                                     fg_color=self.COLOR_ACCENT, hover_color=theme.COLOR_ACCENT_HOVER if theme else "#ff3385",
                                     height=40, font=("Roboto", 14, "bold"),
                                     command=self.start_process_thread)
        self.start_btn.pack(side="right")
        
        
        # Options - Checkbox directly in action_frame
        self.strict_var = ctk.BooleanVar(value=True)
        self.strict_chk = ctk.CTkCheckBox(self.action_frame, text="Même profondeur uniquement", 
                                        variable=self.strict_var, text_color=self.COLOR_TEXT,
                                        checkbox_height=20, checkbox_width=20)
        self.strict_chk.pack(side="left", padx=10)

        # Progress / Log
        self.log_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.progress_bar = ctk.CTkProgressBar(self.log_frame, orientation="horizontal", mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(self.log_frame, fg_color="#000000", text_color="#00ff00", font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True)
        self.log("Prêt. Sélectionnez les chemins pour commencer.")

        # Variables storage
        self.vars = {
            "witness": ctk.StringVar(),
            "source": ctk.StringVar(),
            "dest": ctk.StringVar()
        }
        
    def create_entry_row(self, parent, row, label_text, var_key, placeholder, is_file):
        lbl = ctk.CTkLabel(parent, text=label_text, text_color=self.COLOR_TEXT)
        lbl.grid(row=row, column=0, padx=15, pady=(15 if row==0 else 10, 5), sticky="w")
        
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.grid(row=row, column=1, padx=5, pady=(15 if row==0 else 10, 5), sticky="ew")
        
        btn = ctk.CTkButton(parent, text="...", width=40, 
                          command=lambda: self.browse(entry, is_file))
        btn.grid(row=row, column=2, padx=15, pady=(15 if row==0 else 10, 5))
        
        # We don't store entry widget ref in vars dict, but we could binding if needed. 
        # For now, let's just use the entry widget directly or verify later.
        # Actually easier to store entry refs.
        if not hasattr(self, 'entries'): self.entries = {}
        self.entries[var_key] = entry

    def browse(self, entry_widget, is_file):
        if is_file:
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
            
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)
            # Auto-fill logic similar to batch script?
            # batch script: if witness is C:\RetroFE\collections\MAME\system_artwork\device.png
            # and source is empty, maybe we can guess source?
            # user provided logic: Witness is just a file selection.
            # If user selects witness inside source, we can try to smart guess but let's keep it manual for safety.

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_process_thread(self):
        witness = self.entries["witness"].get().strip().replace('"', '')
        source = self.entries["source"].get().strip().replace('"', '')
        dest = self.entries["dest"].get().strip().replace('"', '')

        if not witness or not source or not dest:
            messagebox.showwarning("Incomplet", "Veuillez remplir tous les champs.")
            return

        if not os.path.isfile(witness):
            messagebox.showerror("Erreur", "Le fichier témoin n'existe pas.")
            return
        if not os.path.isdir(source):
            messagebox.showerror("Erreur", "Le dossier source n'existe pas.")
            return

        self.start_btn.configure(state="disabled")
        self.progress_bar.start()
        
        strict_mode = self.strict_var.get()
        
        thread = threading.Thread(target=self.run_copy_logic, args=(witness, source, dest, strict_mode))
        thread.daemon = True
        thread.start()

    def run_copy_logic(self, witness_path, source_root, dest_root, strict_mode):
        try:
            filename = os.path.basename(witness_path)
            self.log(f"--- Démarrage ---")
            self.log(f"Modèle : {filename}")
            self.log(f"Source : {source_root}")
            self.log(f"Destination : {dest_root}")
            self.log(f"Mode Strict : {'OUI' if strict_mode else 'NON'}")
            
            # Determine Target Depth if possible
            target_depth = -1
            if strict_mode:
                try:
                    # Check if Witness is inside Source
                    common = os.path.commonpath([source_root, witness_path])
                    if common.lower() == source_root.lower() or source_root.lower() in witness_path.lower(): # Basic check
                         # Calculate relative path components
                         try:
                             w_rel_dir = os.path.relpath(os.path.dirname(witness_path), source_root)
                             target_depth = len(w_rel_dir.split(os.sep))
                             if w_rel_dir == ".": target_depth = 0 # Root handling
                             self.log(f"Profondeur Cible (Dossier) : {target_depth} niveaux ({w_rel_dir})")
                         except:
                             self.log("[WARN] Impossible de calculer la profondeur relative du témoin.")
                    else:
                        self.log("[INFO] Le témoin n'est pas dans la source. Désactivation de la vérification de profondeur.")
                except Exception as e:
                    self.log(f"[WARN] Erreur calcul profondeur: {e}")

            self.log("-" * 30)

            count = 0
            errors = 0
            skipped = 0

            # Walk source
            for root, dirs, files in os.walk(source_root):
                if filename in files:
                    full_path = os.path.join(root, filename)
                    
                    # Calculate relative path
                    pass # logic continues below...
                    # rel_path includes the leading separator typically
                    # os.path.relpath returns path relative to start
                    try:
                        rel_path = os.path.relpath(root, source_root)
                    except ValueError:
                         # On Windows, distinct drives can cause issues for relpath
                         self.log(f"[SKIP] Drive différent : {full_path}")
                         continue
                    
                    # Strict Depth & Structure Check
                    if strict_mode:
                        # 1. Depth Check
                        if target_depth >= 0:
                            current_depth = len(rel_path.split(os.sep))
                            if rel_path == ".": current_depth = 0
                            
                            if current_depth != target_depth:
                                # self.log(f"[SKIP-DEPTH] {rel_path}")
                                skipped += 1
                                continue
                        
                        # 2. Root Folder Check (Structure)
                        # If witness is in "collections/...", we expect match to be in "collections/..."
                        # We compare the first component of the relative path
                        if target_depth > 1: # Only if strictly nested
                             w_parts = w_rel_dir.split(os.sep)
                             c_parts = os.path.dirname(rel_path).split(os.sep)
                             
                             if w_parts and c_parts:
                                 if w_parts[0].lower() != c_parts[0].lower():
                                      # self.log(f"[SKIP-STRUCT] {rel_path} (Racine diff: {c_parts[0]} vs {w_parts[0]})")
                                      skipped += 1
                                      continue

                    # Dest folder
                    dest_dir = os.path.join(dest_root, rel_path)
                    dest_file = os.path.join(dest_dir, filename)

                    try:
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.copy2(full_path, dest_file)
                        self.log(f"[OK] {rel_path}\\{filename}")
                        count += 1
                    except Exception as e:
                        self.log(f"[ERREUR] {e}")
                        errors += 1

            self.log("-" * 30)
            self.log(f"Terminé. {count} copiés. {skipped} ignorés (profondeur). {errors} erreurs.")
            messagebox.showinfo("Terminé", f"Opération terminée.\n{count} fichiers copiés.\n{skipped} fichiers ignorés.")

        except Exception as e:
            self.log(f"ERREUR CRITIQUE: {e}")
            messagebox.showerror("Erreur", str(e))
        finally:
            self.start_btn.configure(state="normal")
            self.progress_bar.stop()

def main():
    app = PatternCopierApp()
    app.mainloop()

if __name__ == "__main__":
    main()
