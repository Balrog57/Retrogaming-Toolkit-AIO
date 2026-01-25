import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import shutil
import zipfile
import zlib
import datetime
import time
import tempfile
import subprocess

# Attempt to import utils/theme
try:
    from utils import resource_path
except ImportError:
    def resource_path(path): return path

try:
    import theme
except ImportError:
    # Fallback theme if missing
    class theme:
        COLOR_BG = "#2b2b2b"
        COLOR_ACCENT_PRIMARY = "#1f6aa5"
        COLOR_TEXT_MAIN = "white"
        COLOR_CARD_BG = "#333333"

class Reporter:
    """Handles logic for stats and manifest generation."""
    def __init__(self):
        self.stats = {
            "source_size": 0,
            "export_size": 0,
            "file_count": 0,
            "files": []
        }

    def add_file(self, rel_path, size):
        self.stats["export_size"] += size
        self.stats["file_count"] += 1
        self.stats["files"].append(rel_path)

    def set_source_size(self, size):
        self.stats["source_size"] = size

    def generate_manifest_content(self, description, final_size=0):
        """Generates the string content of the manifest."""
        initial_size = self.stats["export_size"]
        if initial_size > 0 and final_size > 0:
            compression_rate = 100 - (final_size / initial_size * 100)
        else:
            compression_rate = 0

        lines = []
        lines.append(f"Pack Description: {description}")
        lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("-" * 40)
        lines.append(f"Total Source Size (Scanned): {self.format_bytes(self.stats['source_size'])}")
        lines.append(f"Total Exported Content Size: {self.format_bytes(initial_size)}")
        if final_size > 0:
            lines.append(f"Final Package Size: {self.format_bytes(final_size)}")
            lines.append(f"Compression Rate: {compression_rate:.2f}%")
        lines.append("-" * 40)
        lines.append("Files Included:")
        for f in self.stats["files"]:
            lines.append(f" - {f}")
            
        return "\n".join(lines)

    def generate_manifest(self, description, destination_path, zip_size):
        content = self.generate_manifest_content(description, zip_size)
        manifest_path = os.path.join(destination_path, "manifest.txt")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)
        return manifest_path

    @staticmethod
    def format_bytes(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    @staticmethod
    def calculate_crc32(filepath):
        prev = 0
        try:
            with open(filepath, "rb") as f:
                for line in f:
                    prev = zlib.crc32(line, prev)
            return "%X" % (prev & 0xFFFFFFFF)
        except Exception:
            return "ERROR"

class ComparisonEngine:
    """Handles the scanning and comparison logic."""
    def __init__(self, log_callback):
        self.log = log_callback
        self.stop_event = threading.Event()

    def get_directory_size(self, path):
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def scan(self, source_dir, base_dir, mode, submode):
        """
        Compares source against base.
        Returns (file_groups, source_size)
        file_groups = { "snes": [(abs, rel, cat)], "ps2": [...], "default": [...] }
        """
        file_groups = {} # Key: group_name (e.g. 'snes' or 'default'), Value: list of tuples
        
        self.log("Calculating source size...", 0)
        source_size = self.get_directory_size(source_dir)
        
        self.log("Starting comparison scan...", 5)
        
        file_list = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_list.append(os.path.join(root, file))

        total_files = len(file_list)
        processed = 0

        for source_path in file_list:
            if self.stop_event.is_set():
                return None, 0

            rel_path = os.path.relpath(source_path, source_dir)
            base_path = os.path.join(base_dir, rel_path)

            include = False
            
            if not os.path.exists(base_path):
                include = True
            else:
                s_size = os.path.getsize(source_path)
                b_size = os.path.getsize(base_path)
                if s_size != b_size:
                    include = True

            if include:
                # Logic per mode
                is_retrobat = mode == "Retrobat"
                is_retrofe = mode == "RetroFE"
                
                parts = rel_path.lower().split(os.sep)
                
                group = "default"
                is_content_file = False
                
                if is_retrobat:
                    # RetroBat Logic: roms/* or saves/* is content
                    console_name = None
                    if "roms" in parts:
                        try:
                            idx = parts.index("roms")
                            if idx + 1 < len(parts):
                                console_name = parts[idx+1]
                                is_content_file = True
                        except: pass
                    elif "saves" in parts:
                        try:
                            idx = parts.index("saves")
                            if idx + 1 < len(parts):
                                console_name = parts[idx+1]
                                is_content_file = True
                        except: pass
                    
                    if is_content_file and console_name:
                        group = console_name

                elif is_retrofe:
                    # RetroFE Logic: 
                    # 1. Outside "collections" -> BASE
                    # 2. Inside "collections":
                    #    - If /collections/<System> HAS a "roms" folder -> CONTENT (Group = <System>)
                    #    - Else -> BASE
                    
                    if parts[0] == "collections":
                        try:
                            # It is strictly in the main collections folder
                            idx = 0 # collections is at 0
                            if idx + 1 < len(parts):
                                system_name = parts[idx+1] # Folder after collections
                                
                                # Check for roms presence in this system folder
                                # path to system is just collections/System
                                
                                # Reconstruct check path: source_dir/collections/System/roms
                                # We use parts (lower) for logic but need real casing for path? 
                                # Windows is insensitive, but let's try to be clean.
                                # actually sys_real needs to be fetched from parts_real
                                
                                parts_real = rel_path.split(os.sep)
                                sys_real = parts_real[1] # idx+1 where idx=0
                                
                                check_path = os.path.join(source_dir, "collections", sys_real, "roms")
                                
                                if os.path.exists(check_path):
                                    is_content_file = True
                                    group = sys_real
                        except Exception: 
                            pass # Fallback to Base
                    
                    # If parts[0] != "collections", it is Base (layouts, meta, etc.)
                    
                    # If not in collections, remains is_content_file=False (Base)

                # Shared Filtering Logic based on SubMode
                should_add = False
                if is_retrobat or is_retrofe:
                    if submode == "Base":
                        if not is_content_file: 
                            should_add = True
                    elif submode == "Content":
                        if is_content_file: 
                             should_add = True
                else:
                    should_add = True # Standard

                if should_add:
                    if group not in file_groups:
                        file_groups[group] = []
                    
                    file_groups[group].append((source_path, rel_path, "FLAT"))

            processed += 1
            if processed % 100 == 0:
                progress = 5 + (processed / total_files * 40)
                self.log(f"Scanning... {processed}/{total_files}", progress)

        total_found = sum(len(v) for v in file_groups.values())
        self.log(f"Scan complete. Found {total_found} files across {len(file_groups)} groups.", 45)
        return file_groups, source_size

class ArchiveCreator:
    """Handles creation of the output package."""
    def __init__(self, log_callback):
        self.log = log_callback

    def create_archives(self, file_groups, destination, name_prefix, description, output_format, source_size):
        """
        Creates one or more archives based on file_groups.
        file_groups: { "snes": [...], "default": [...] }
        name_prefix: The user-provided pack name (or default 'diff_pack')
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results = []
        
        # We need to distribute source_size roughly or just report total?
        # Reporter logic assumes one stats object. We might need a master reporter or individual ones.
        
        # Calculate total items for progress
        total_items_all = sum(len(v) for v in file_groups.values())
        current_item_global = 0
        
        # Retrieve 7z info if exe requested
        from utils import DependencyManager
        dep_manager = DependencyManager()
        seven_za = None
        sfx_module = None
        
        if output_format == "exe":
            seven_za = dep_manager.seven_za_path
            sfx_module = os.path.join(dep_manager.app_data_dir, "7z.sfx")
            
            if not os.path.exists(seven_za) or not os.path.exists(sfx_module):
                self.log("Erreur: Composants SFX manquants (check skip?). Fallback ZIP.", 10)
                output_format = "zip"
        
        for group_name, diff_files in file_groups.items():
            if not diff_files: continue
            
            # Name logic
            suffix = ""
            if group_name != "default":
                suffix = f"_{group_name.upper()}"
            
            base_name = f"{name_prefix}{suffix}_{timestamp}"
            
            reporter = Reporter()
            reporter.set_source_size(0) 

            ext = ".exe" if output_format == "exe" else ".zip"
            out_path = os.path.join(destination, base_name + ext)
            
            self.log(f"Création archive ({group_name}) [{output_format.upper()}]: {out_path}", 50)
            
            try:
                if output_format == "exe" and seven_za and sfx_module:
                    # SFX Mode: Create via Temp Directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 1. Copy files
                        for abs_path, rel_path, category in diff_files:
                            target_path = os.path.join(temp_dir, rel_path)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            shutil.copy2(abs_path, target_path)
                            
                            reporter.add_file(rel_path.replace("\\", "/"), os.path.getsize(abs_path))
                            
                            current_item_global += 1
                            if current_item_global % 10 == 0:
                                prog = 50 + (current_item_global / total_items_all * 40)
                                self.log(f"Préparation SFX ({group_name}): {rel_path}...", prog)
                        
                        # 2. Invoke 7za
                        self.log(f"Compression SFX (7-Zip) en cours... Veuillez patienter.", 90)
                        
                        cmd = [seven_za, 'a', f'-sfx{sfx_module}', out_path, '.']
                        startupinfo = None
                        if os.name == 'nt':
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        subprocess.run(cmd, cwd=temp_dir, check=True, startupinfo=startupinfo, capture_output=True)
                        
                        if os.path.exists(out_path):
                             results.append(out_path)
                        else:
                             raise Exception("SFX File creation failed (not found)")

                else:
                    # ZIP Mode (Standard)
                    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for abs_path, rel_path, category in diff_files:
                            internal_path = rel_path.replace("\\", "/")
                            zipf.write(abs_path, internal_path)
                            reporter.add_file(internal_path, os.path.getsize(abs_path))
                            
                            current_item_global += 1
                            if current_item_global % 10 == 0:
                                prog = 50 + (current_item_global / total_items_all * 40)
                                self.log(f"Archivage ({group_name}): {rel_path}...", prog)
    
                    results.append(out_path)

                # --- EXTERNAL MANIFEST GENERATION (After stats populated) ---
                final_size = os.path.getsize(out_path)
                
                # Check compression ratio/stats
                reporter.set_source_size(reporter.stats["export_size"]) # Set source size to what we found
                
                manifest_txt = reporter.generate_manifest_content(f"{description}", final_size=final_size)
                
                manifest_filename = f"{base_name}.txt"
                manifest_path_acc = os.path.join(destination, manifest_filename)
                with open(manifest_path_acc, "w", encoding="utf-8") as f:
                    f.write(manifest_txt)

                crc = reporter.calculate_crc32(out_path)
                self.log(f"Terminé ({group_name}) - CRC32: {crc}", 100)
            
            except Exception as e:
                self.log(f"Erreur archive ({group_name}): {e}", 100)
                raise e
                
        return results, "Voir dossier de destination"



class PackWrapperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.engine = ComparisonEngine(self.log_message)
        self.archiver = ArchiveCreator(self.log_message)
        
        # Apply theme manually or via function if available
        self.title("PackWrapper - Diff & Deploy System")
        self.geometry("850x700") # Slightly larger
        self.configure(fg_color=theme.COLOR_BG)
        
        try:
            # Try to see if theme has apply_theme
            if hasattr(theme, 'apply_theme'):
                theme.apply_theme(self, "PackWrapper - Diff & Deploy System")
        except:
            pass

        self._init_ui()

    def _init_ui(self):
        # Using frames with transparent effect or card color
        
        # --- Frame: Paths ---
        files_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_CARD_BG)
        files_frame.pack(pady=15, padx=20, fill="x")

        self.wdg_source = self._create_path_entry(files_frame, "Dossier Source (Modifié):", 0)
        self.wdg_base = self._create_path_entry(files_frame, "Dossier Type (Original):", 1)
        self.wdg_dest = self._create_path_entry(files_frame, "Dossier Destination:", 2)

        # --- Frame: Configuration ---
        # Grouping Mode, Type, and Output Format
        config_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_CARD_BG)
        config_frame.pack(pady=10, padx=20, fill="x")
        
        # Configure grid for better spacing
        config_frame.grid_columnconfigure(0, weight=1)
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(2, weight=1)

        # 1. Mode
        lbl_mode = ctk.CTkLabel(config_frame, text="Mode de fonctionnement", font=("Roboto", 12, "bold"), text_color=theme.COLOR_TEXT_MAIN)
        lbl_mode.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.mode_var = ctk.StringVar(value="Standard")
        self.seg_mode = ctk.CTkSegmentedButton(config_frame, values=["Standard", "Retrobat", "RetroFE"], 
                                             variable=self.mode_var, command=self._update_ui_state,
                                             selected_color=theme.COLOR_ACCENT_PRIMARY,
                                             selected_hover_color=theme.COLOR_ACCENT_HOVER)
        self.seg_mode.grid(row=1, column=0, padx=10, pady=(5, 15), sticky="ew")

        # 2. Type (Base / Content)
        lbl_type = ctk.CTkLabel(config_frame, text="Type de contenu", font=("Roboto", 12, "bold"), text_color=theme.COLOR_TEXT_MAIN)
        lbl_type.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.submode_var = ctk.StringVar(value="Base")
        self.seg_submode = ctk.CTkSegmentedButton(config_frame, values=["Base", "Content"], variable=self.submode_var,
                                                  selected_color=theme.COLOR_ACCENT_PRIMARY,
                                                  selected_hover_color=theme.COLOR_ACCENT_HOVER)
        self.seg_submode.grid(row=1, column=1, padx=10, pady=(5, 15), sticky="ew")

        # 3. Output Format (ZIP / SFX) - Changed to SegmentedButton for consistency
        lbl_fmt = ctk.CTkLabel(config_frame, text="Format Sortie", font=("Roboto", 12, "bold"), text_color=theme.COLOR_TEXT_MAIN)
        lbl_fmt.grid(row=0, column=2, padx=10, pady=(10, 0))
        self.out_var = ctk.StringVar(value="zip")
        self.seg_out = ctk.CTkSegmentedButton(config_frame, values=["ZIP", "EXE (SFX)"], variable=self.out_var,
                                              selected_color=theme.COLOR_ACCENT_PRIMARY,
                                              selected_hover_color=theme.COLOR_ACCENT_HOVER)
         # Using mapping for values? No, just map logic later: "EXE (SFX)" -> "exe"
        self.seg_out.grid(row=1, column=2, padx=10, pady=(5, 15), sticky="ew")
        self.seg_out.set("ZIP") # Force default selection visual


        # --- Frame: Pack Details (Name & Desc) ---
        details_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_CARD_BG)
        details_frame.pack(pady=10, padx=20, fill="x")
        
        details_frame.grid_columnconfigure(1, weight=1)

        # Pack Name
        ctk.CTkLabel(details_frame, text="Nom du Pack:", font=("Roboto", 12, "bold"), text_color=theme.COLOR_TEXT_MAIN).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.pack_name_var = ctk.StringVar(value="MyPack")
        self.ent_pack_name = ctk.CTkEntry(details_frame, textvariable=self.pack_name_var, height=35)
        self.ent_pack_name.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        # Description
        ctk.CTkLabel(details_frame, text="Description:", font=("Roboto", 12, "bold"), text_color=theme.COLOR_TEXT_MAIN).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nw")
        self.txt_desc = ctk.CTkTextbox(details_frame, height=80, border_width=2, border_color=theme.COLOR_CARD_BORDER)
        self.txt_desc.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        # --- Button ---
        self.btn_start = ctk.CTkButton(self, text="Lancer la Création du Pack", height=45, font=("Roboto", 16, "bold"), 
                                       command=self.on_start, fg_color=theme.COLOR_ACCENT_PRIMARY, hover_color=theme.COLOR_ACCENT_HOVER)
        self.btn_start.pack(pady=15, padx=20, fill="x")

        # --- Console ---
        self.console_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_CARD_BG)
        self.console_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.txt_console = ctk.CTkTextbox(self.console_frame, state="disabled", font=("Consolas", 12), text_color=theme.COLOR_TEXT_SUB)
        self.txt_console.pack(fill="both", expand=True, padx=5, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.console_frame, progress_color=theme.COLOR_ACCENT_PRIMARY)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)

        # Trigger initial UI state
        self._update_ui_state()

    def _create_path_entry(self, parent, label_text, row):
        ctk.CTkLabel(parent, text=label_text, text_color=theme.COLOR_TEXT_MAIN).grid(row=row, column=0, padx=10, pady=5, sticky="e")
        var = ctk.StringVar()
        ent = ctk.CTkEntry(parent, textvariable=var, width=450)
        ent.grid(row=row, column=1, padx=5, pady=5)
        
        def browse():
            d = filedialog.askdirectory()
            if d: var.set(d)
            
        ctk.CTkButton(parent, text="Parcourir", width=80, command=browse, fg_color=theme.COLOR_ACCENT_PRIMARY, hover_color=theme.COLOR_ACCENT_HOVER).grid(row=row, column=2, padx=5, pady=5)
        return var

    def _browse_logo(self):
        pass # Removed feature
    
    def _update_ui_state(self, event=None):
        mode = self.mode_var.get()
        if mode == "Standard":
            self.seg_submode.configure(state="disabled")
        else:
            self.seg_submode.configure(state="normal")

    def log_message(self, msg, progress=None):
        def _update():
            self.txt_console.configure(state="normal")
            self.txt_console.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
            self.txt_console.see("end")
            self.txt_console.configure(state="disabled")
            if progress is not None:
                self.progress_bar.set(progress / 100)
        self.after(0, _update)

    def on_start(self):
        source = self.wdg_source.get()
        base = self.wdg_base.get()
        dest = self.wdg_dest.get()
        mode = self.mode_var.get()
        submode = self.submode_var.get()
        
        # Map UI value to internal value
        raw_fmt = self.out_var.get()
        if raw_fmt == "EXE (SFX)":
            out_fmt = "exe"
        else:
            out_fmt = "zip"
            
        desc = self.txt_desc.get("1.0", "end-1c")
        # logo = self.logo_path_var.get() # Removed
        pack_name = self.pack_name_var.get().strip() or "FullPack"

        if not all([source, base, dest]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs de dossiers.")
            return
        
        if not os.path.isdir(source) or not os.path.isdir(base) or not os.path.isdir(dest):
             messagebox.showerror("Erreur", "Les chemins spécifiés doivent être des dossiers valides.")
             return

        if not os.access(dest, os.W_OK):
             messagebox.showerror("Erreur", "Pas de droits d'écriture dans le dossier de destination.")
             return

        # Check dependencies for SFX on MAIN THREAD
        exe_sfx_ready = False
        if out_fmt == "exe":
            try:
                from utils import DependencyManager
                # Pass self as root for the progress window
                dep = DependencyManager(self) 
                
                self.log_message("Vérification des dépendances 7-Zip (SFX)...")
                # Force update to show log
                self.update()
                
                if dep.bootstrap_7za():
                    if dep.bootstrap_7z_sfx():
                         exe_sfx_ready = True
                    else:
                         msg = "Impossible de récupérer '7z.sfx' (module SFX).\nAnnulation de l'opération."
                         self.log_message(msg)
                         messagebox.showerror("Erreur SFX", msg)
                         self.btn_start.configure(state="normal")
                         return
                else:
                    msg = "Impossible de récupérer '7za.exe' (7-Zip CLI).\nAnnulation de l'opération."
                    self.log_message(msg)
                    messagebox.showerror("Erreur SFX", msg)
                    self.btn_start.configure(state="normal")
                    return
                    
            except Exception as e:
                msg = f"Erreur lors de l'initialisation SFX : {e}\nAnnulation."
                self.log_message(msg)
                messagebox.showerror("Erreur SFX", msg)
                self.btn_start.configure(state="normal")
                return

        self.btn_start.configure(state="disabled")
        self.log_message(f"Initialisation: Mode={mode}, Type={submode}...")

        t = threading.Thread(target=self._run_process, args=(source, base, dest, mode, submode, out_fmt, desc, pack_name))
        t.start()
    
    def _run_process(self, source, base, dest, mode, submode, out_fmt, desc, pack_name):
        try:
            # 1. Scan
            files_to_pack, source_size = self.engine.scan(source, base, mode, submode)
            
            if not files_to_pack:
                self.log_message("Aucune différence trouvée ou opération annulée.")
                return

            # 2. Archive
            out_paths, manifest_msg = self.archiver.create_archives(
                files_to_pack, dest, pack_name, desc, out_fmt, source_size
            )
            
            archives_str = "\n".join([os.path.basename(p) for p in out_paths])
            self.log_message(f"Terminé avec succès !\nArchives générées :\n{archives_str}\n{manifest_msg}", 100)
            messagebox.showinfo("Succès", f"{len(out_paths)} Pack(s) généré(s) avec succès !")

        except Exception as e:
            self.log_message(f"Erreur fatale : {e}")
            messagebox.showerror("Erreur", str(e))
        finally:
            self.btn_start.configure(state="normal")

def main():
    app = PackWrapperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
