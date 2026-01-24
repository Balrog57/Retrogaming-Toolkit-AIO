import os
import subprocess
import multiprocessing
import urllib.request
import shutil
import zipfile
import tempfile
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, IntVar, BooleanVar
import sys

# Import utils & theme
try:
    import utils
except ImportError:
    pass

try:
    import theme
except ImportError:
    theme = None

CHDMAN_URL = "https://wiki.recalbox.com/tutorials/utilities/rom-conversion/chdman/chdman.zip"
CHDMAN_ZIP = "chdman.zip"

def get_chdman_path():
    if 'utils' in sys.modules:
        bin_path = utils.get_binary_path("chdman.exe")
        if os.path.exists(bin_path): return bin_path
    
    app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', "chdman.exe")
    if os.path.exists(app_data_path): return app_data_path
    return app_data_path

CHDMAN_EXE = get_chdman_path()

class CHDmanGUI:
    def __init__(self, root):
        self.root = root
        
        # Theme
        if theme:
            theme.apply_theme(root, "CHD Converter Tool par Balrog")
        else:
            ctk.set_appearance_mode("dark")
            root.title("CHD_Converter_Tool par Balrog")
            
        root.geometry("800x650")
        root.minsize(600, 500)

        self.max_cores = multiprocessing.cpu_count()
        # Variables
        self.source_folder = StringVar()
        self.destination_folder = StringVar()
        self.num_cores = IntVar(value=self.max_cores)
        self.option = StringVar(value="Info")
        self.overwrite = BooleanVar(value=True)
        
        # Main Layout
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkScrollableFrame(root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # 1. Folders
        top_frame = ctk.CTkFrame(main_frame, fg_color=theme.COLOR_CARD_BG if theme else None)
        top_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        
        ctk.CTkLabel(top_frame, text="Dossiers", font=theme.get_font_title() if theme else None, text_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Source
        ctk.CTkLabel(top_frame, text="Source :").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        ctk.CTkEntry(top_frame, textvariable=self.source_folder, width=400).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(top_frame, text="...", width=40, command=self.parcourir_dossier_source, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=1, column=2, padx=15, pady=5)
        
        # Dest
        ctk.CTkLabel(top_frame, text="Destination :").grid(row=2, column=0, padx=15, pady=5, sticky="e")
        ctk.CTkEntry(top_frame, textvariable=self.destination_folder, width=400).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(top_frame, text="...", width=40, command=self.parcourir_dossier_destination, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=2, column=2, padx=15, pady=5)

        ctk.CTkButton(top_frame, text="⇅ Inverser", command=self.inverser_dossiers, fg_color="transparent", border_width=1, border_color=theme.COLOR_ACCENT_PRIMARY if theme else "gray").grid(row=3, column=1, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        # 2. Options
        mid_frame = ctk.CTkFrame(main_frame, fg_color=theme.COLOR_CARD_BG if theme else None)
        mid_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        
        ctk.CTkLabel(mid_frame, text="Mode & Options", font=theme.get_font_title() if theme else None, text_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", padx=15, pady=10)
        
        opts_container = ctk.CTkFrame(mid_frame, fg_color="transparent")
        opts_container.pack(fill="x", padx=15, pady=5)
        
        modes = [("Info", "Info"), ("Vérifier", "Verify"), ("Convertir", "Convert"), ("Extraire", "Extract")]
        for text, val in modes:
            ctk.CTkRadioButton(opts_container, text=text, variable=self.option, value=val, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(side="left", padx=10)
            
        ctk.CTkCheckBox(mid_frame, text="Écraser les fichiers existants (Overwrite)", variable=self.overwrite, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", padx=25, pady=10)
        
        # CPU
        cpu_frame = ctk.CTkFrame(mid_frame, fg_color="transparent")
        cpu_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(cpu_frame, text=f"CPU Threads (Max {self.max_cores}):").pack(side="left")
        
        slider = ctk.CTkSlider(cpu_frame, from_=1, to=self.max_cores, number_of_steps=self.max_cores-1, variable=self.num_cores, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkLabel(cpu_frame, textvariable=self.num_cores, width=30, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue", corner_radius=5).pack(side="left")

        # 3. Actions & Status
        bot_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bot_frame.grid(row=2, column=0, sticky="nsew")
        
        # Progress
        self.progress_bar = ctk.CTkProgressBar(bot_frame, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        
        status_row = ctk.CTkFrame(bot_frame, fg_color="transparent")
        status_row.pack(fill="x")
        self.status_label = ctk.CTkLabel(status_row, text="Prêt.")
        self.status_label.pack(side="left")
        self.percent_label = ctk.CTkLabel(status_row, text="0%")
        self.percent_label.pack(side="right")
        
        # Controls
        ctrl_frame = ctk.CTkFrame(bot_frame, fg_color="transparent")
        ctrl_frame.pack(pady=15)
        
        self.btn_start = ctk.CTkButton(ctrl_frame, text="▶ Démarrer", command=self.start_conversion, width=150, height=40, font=("Arial", 14, "bold"),
                                       fg_color=theme.COLOR_SUCCESS if theme else "green", hover_color="#27ae60")
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_pause = ctk.CTkButton(ctrl_frame, text="⏸ Pause", command=self.pause_conversion, width=100, height=40, state="disabled",
                                       fg_color=theme.COLOR_WARNING if theme else "orange", hover_color="#d35400")
        self.btn_pause.pack(side="left", padx=5)
        
        self.btn_stop = ctk.CTkButton(ctrl_frame, text="⏹ Arrêter", command=self.stop_conversion, width=100, height=40, state="disabled",
                                      fg_color=theme.COLOR_ERROR if theme else "red", hover_color="#c0392b")
        self.btn_stop.pack(side="left", padx=5)
        
        self.is_running = False
        self.is_paused = False
        self.current_process = None
        
        self.verifier_chdman()

    # --- Methods (Logic Preserved) ---
    def parcourir_dossier_source(self):
        f = filedialog.askdirectory()
        if f: self.source_folder.set(f)

    def parcourir_dossier_destination(self):
        f = filedialog.askdirectory()
        if f: self.destination_folder.set(f)

    def inverser_dossiers(self):
        s, d = self.source_folder.get(), self.destination_folder.get()
        self.source_folder.set(d); self.destination_folder.set(s)

    def verifier_chdman(self):
        if not os.path.exists(CHDMAN_EXE):
            self.telecharger_chdman()

    def telecharger_chdman(self):
        if 'utils' not in sys.modules: return messagebox.showerror("Err", "Utils missing")
        try:
            manager = utils.DependencyManager(self.root)
            MAME_URL = "https://github.com/mamedev/mame/releases/download/mame0284/mame0284b_x64.exe"
            res = manager.install_dependency("CHDman", MAME_URL, "chdman.exe", 'exe_sfx', 'chdman.exe')
            if res:
                global CHDMAN_EXE
                CHDMAN_EXE = res
            else:
                self.root.destroy()
        except:
            self.root.destroy()

    def update_progress(self, val):
        self.progress_bar.set(val)
        self.percent_label.configure(text=f"{int(val*100)}%")

    def start_conversion(self):
        if self.is_running: return
        self.is_running = True; self.is_paused = False
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_pause.configure(state="normal")
        threading.Thread(target=self.run_logic, daemon=True).start()

    def stop_conversion(self):
        if not self.is_running: return
        self.is_running = False
        if self.current_process:
            try: self.current_process.terminate()
            except: pass
        
        # Cleanup logic (same as original simplified)
        self.status_label.configure(text="Arrêté.")
        self.reset_buttons()

    def pause_conversion(self):
        if not self.is_running: return
        self.is_paused = not self.is_paused
        self.btn_pause.configure(text="▶ Reprendre" if self.is_paused else "⏸ Pause")

    def reset_buttons(self):
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_pause.configure(state="disabled", text="⏸ Pause")
        self.is_running = False

    def run_logic(self):
        src, dst = self.source_folder.get(), self.destination_folder.get()
        if not src or not dst:
            self.reset_buttons()
            return messagebox.showerror("Err", "Dossiers requis")

        # Extract archives
        self.status_label.configure(text="Extraction des archives...")
        for f in os.listdir(src):
            fp = os.path.join(src, f)
            if f.lower().endswith((".zip", ".rar", ".7z")):
                try: utils.extract_with_7za(fp, src, root=self.root)
                except: pass
        
        # Identify files
        exts = (".chd", ".cue", ".gdi", ".iso")
        files = [os.path.join(src, f) for f in os.listdir(src) if f.lower().endswith(exts)]
        total = len(files)
        
        log_path = os.path.join(dst, "chdman_log.txt")
        self.status_label.configure(text="Traitement en cours...")
        
        with open(log_path, "w") as log:
            for i, f in enumerate(files):
                if not self.is_running: break
                while self.is_paused: time.sleep(0.1)
                
                self.update_progress((i)/total)
                self.status_label.configure(text=f"Traitement: {os.path.basename(f)}")
                
                try:
                    mode = self.option.get()
                    cmd = [CHDMAN_EXE]
                    
                    if mode == "Info":
                        cmd.extend(["info", "-i", f])
                    elif mode == "Verify":
                        cmd.extend(["verify", "-i", f])
                    elif mode == "Convert":
                        out = os.path.join(dst, os.path.splitext(os.path.basename(f))[0] + ".chd")
                        if self.overwrite.get() or not os.path.exists(out):
                            cmd.extend(["createcd", "--numprocessors", str(self.num_cores.get()), "-i", f, "-o", out])
                    elif mode == "Extract":
                        out = os.path.join(dst, os.path.splitext(os.path.basename(f))[0] + ".cue")
                        if self.overwrite.get() or not os.path.exists(out):
                            cmd.extend(["extractcd", "-i", f, "-o", out])

                    # Run
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.current_process = p
                    out, err = p.communicate()
                    log.write(f"--- {os.path.basename(f)} ---\n{out}\n{err}\n\n")
                    
                except Exception as e:
                    log.write(f"Error {f}: {e}\n")

                self.update_progress((i+1)/total)

        self.reset_buttons()
        self.status_label.configure(text="Terminé.")
        messagebox.showinfo("Fini", "Opération terminée.")

def main():
    root = ctk.CTk()
    app = CHDmanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()