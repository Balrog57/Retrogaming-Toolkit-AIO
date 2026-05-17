import os
import subprocess
import multiprocessing
import concurrent.futures
import shutil
import zipfile
import tempfile
import threading
import time
import re
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

DISC_EXTS = (".gdi", ".cue", ".iso")
CHD_EXTS = (".chd",)
ALL_INPUT_EXTS = CHD_EXTS + DISC_EXTS
OPERATIONS = [
    "Info CHD",
    "Vérifier CHD",
    "Vérifier Source",
    "Convertir vers CHD",
    "Extraire CHD vers CUE/BIN",
    "Comparer CHD -> Source",
    "Comparer Source -> CHD",
]
REPORT_STAT_KEYS = ("converted", "extracted", "skipped", "info", "verified", "matched", "failed", "missing")

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
        self.option = StringVar(value="Convertir vers CHD")
        self.overwrite = BooleanVar(value=True)
        self.verify_after = BooleanVar(value=False)
        
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
        
        ctk.CTkLabel(opts_container, text="Opération :").pack(side="left", padx=(0, 10))
        self.operation_menu = ctk.CTkOptionMenu(
            opts_container,
            variable=self.option,
            values=OPERATIONS,
            command=lambda _: self.update_operation_options(),
            fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None
        )
        self.operation_menu.pack(side="left", fill="x", expand=True)

        self.overwrite_check = ctk.CTkCheckBox(mid_frame, text="Écraser les fichiers existants (Overwrite)", variable=self.overwrite, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
        self.overwrite_check.pack(anchor="w", padx=25, pady=(10, 3))

        self.verify_after_check = ctk.CTkCheckBox(mid_frame, text="Vérifier après conversion", variable=self.verify_after, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
        self.verify_after_check.pack(anchor="w", padx=25, pady=(3, 10))
        
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
        self.current_processes = set()
        self.processes_lock = threading.Lock()
        
        self.verifier_chdman()
        self.update_operation_options()

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
        val = max(0, min(1, val))
        self.root.after(0, lambda: (
            self.progress_bar.set(val),
            self.percent_label.configure(text=f"{int(val*100)}%")
        ))

    def update_status(self, text):
        self.root.after(0, lambda: self.status_label.configure(text=text))

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
        with self.processes_lock:
            processes = list(self.current_processes)
        for process in processes:
            try: process.terminate()
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

    def update_operation_options(self):
        mode = self.option.get()
        conversion_mode = mode == "Convertir vers CHD"
        output_mode = mode in ("Convertir vers CHD", "Extraire CHD vers CUE/BIN")
        self.verify_after_check.configure(state="normal" if conversion_mode else "disabled")
        if not conversion_mode:
            self.verify_after.set(False)
        self.overwrite_check.configure(state="normal" if output_mode else "disabled")

    def create_startupinfo(self):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return startupinfo

    def wait_if_paused(self):
        while self.is_running and self.is_paused:
            time.sleep(0.1)

    def run_tracked_process(self, cmd):
        if not self.is_running:
            return "", "Arrêt demandé avant lancement.", -1

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=self.create_startupinfo()
        )
        with self.processes_lock:
            self.current_process = process
            self.current_processes.add(process)
        try:
            out, err = process.communicate()
            return out, err, process.returncode
        finally:
            with self.processes_lock:
                self.current_processes.discard(process)
                if self.current_process is process:
                    self.current_process = None

    def empty_result(self):
        return {"stats": {key: 0 for key in REPORT_STAT_KEYS}, "logs": []}

    def merge_result(self, target, source):
        for key, value in source["stats"].items():
            target["stats"][key] += value
        target["logs"].extend(source["logs"])

    def summary_message(self, stats):
        return "\n".join([
            f"Convertis: {stats['converted']}",
            f"Extraits: {stats['extracted']}",
            f"Ignorés: {stats['skipped']}",
            f"Infos générées: {stats['info']}",
            f"Vérifiés OK: {stats['verified']}",
            f"Comparaisons OK: {stats['matched']}",
            f"Échecs: {stats['failed']}",
            f"Sources manquantes: {stats['missing']}",
        ])

    def write_report(self, dst, mode, result):
        safe_mode = re.sub(r"[^A-Za-z0-9_-]+", "_", mode).strip("_")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(dst, f"chdmanager_{safe_mode}_{timestamp}.txt")
        lines = [
            f"Operation: {mode}",
            f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Source: {self.source_folder.get()}",
            f"Destination / rapport: {dst}",
            "",
            self.summary_message(result["stats"]),
            "",
            "Détails:",
            "",
        ]
        lines.extend(result["logs"])
        with open(report_path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines))
            report.write("\n")
        return report_path

    def input_exts_for_mode(self, mode):
        if mode in ("Convertir vers CHD", "Vérifier Source", "Comparer Source -> CHD"):
            return DISC_EXTS
        if mode in ("Info CHD", "Vérifier CHD", "Extraire CHD vers CUE/BIN", "Comparer CHD -> Source"):
            return CHD_EXTS
        return ALL_INPUT_EXTS

    def find_disc_inputs(self, folder, mode):
        exts = self.input_exts_for_mode(mode)

        files = []
        for root_dir, _, names in os.walk(folder):
            for name in names:
                if name.lower().endswith(exts):
                    files.append(os.path.join(root_dir, name))

        priority = {".gdi": 0, ".cue": 1, ".iso": 2, ".chd": 3}
        files.sort(key=lambda p: (priority.get(os.path.splitext(p)[1].lower(), 99), p.lower()))
        return files

    def is_archive_start(self, filename):
        lower = filename.lower()
        part_match = re.search(r"\.part0*(\d+)\.rar$", lower)
        if part_match:
            return int(part_match.group(1)) == 1

        split_match = re.search(r"\.(7z|zip)\.0*(\d+)$", lower)
        if split_match:
            return int(split_match.group(2)) == 1

        return lower.endswith((".zip", ".rar", ".7z"))

    def build_chdman_cmd(self, mode, input_file, dst, overwrite, chd_threads):
        cmd = [CHDMAN_EXE]
        name = os.path.splitext(os.path.basename(input_file))[0]
        out_file = None

        if mode == "Info CHD":
            cmd.extend(["info", "-i", input_file])
        elif mode == "Vérifier CHD":
            cmd.extend(["verify", "-i", input_file])
        elif mode == "Convertir vers CHD":
            out_file = os.path.join(dst, name + ".chd")
            if not overwrite and os.path.exists(out_file):
                return None, f"Déjà existant, ignoré: {out_file}\n", out_file
            cmd.extend(["createcd", "--numprocessors", str(chd_threads), "-i", input_file, "-o", out_file])
        elif mode == "Extraire CHD vers CUE/BIN":
            out_file = os.path.join(dst, name + ".cue")
            if not overwrite and os.path.exists(out_file):
                return None, f"Déjà existant, ignoré: {out_file}\n", out_file
            cmd.extend(["extractcd", "-i", input_file, "-o", out_file])

        return cmd, None, out_file

    def command_log(self, title, cmd, out, err, returncode):
        return f"--- {title} ---\nCMD: {' '.join(cmd)}\nReturn code: {returncode}\n{out}\n{err}\n\n"

    def run_required(self, cmd, cleanup_path=None):
        out, err, returncode = self.run_tracked_process(cmd)
        if returncode != 0:
            if cleanup_path and os.path.exists(cleanup_path):
                try:
                    os.remove(cleanup_path)
                except OSError:
                    pass
            details = (err or out or "").strip()
            raise RuntimeError(details or f"chdman a échoué avec le code {returncode}.")
        return out, err, returncode

    def parse_data_sha1(self, text):
        data_matches = re.findall(r"Data SHA1\s*:\s*([a-fA-F0-9]{40})", text, flags=re.IGNORECASE)
        if data_matches:
            return data_matches[-1].lower()
        matches = re.findall(r"\b[a-fA-F0-9]{40}\b", text)
        if matches:
            return matches[-1].lower()
        raise RuntimeError("SHA1 CHD introuvable dans la sortie chdman info.")

    def chd_data_sha1(self, chd_file):
        cmd = [CHDMAN_EXE, "info", "-i", chd_file]
        out, err, _ = self.run_required(cmd)
        return self.parse_data_sha1(f"{out}\n{err}"), self.command_log(f"Info {os.path.basename(chd_file)}", cmd, out, err, 0)

    def create_temp_chd_from_source(self, source_file, temp_dir, chd_threads):
        temp_chd = os.path.join(temp_dir, os.path.splitext(os.path.basename(source_file))[0] + ".chd")
        cmd = [CHDMAN_EXE, "createcd", "--numprocessors", str(chd_threads), "-i", source_file, "-o", temp_chd]
        out, err, returncode = self.run_required(cmd, cleanup_path=temp_chd)
        return temp_chd, self.command_log(f"CHD temporaire {os.path.basename(source_file)}", cmd, out, err, returncode)

    def source_data_sha1(self, source_file, chd_threads):
        with tempfile.TemporaryDirectory(prefix="chdmanager_compare_") as temp_dir:
            temp_chd, create_log = self.create_temp_chd_from_source(source_file, temp_dir, chd_threads)
            sha1, info_log = self.chd_data_sha1(temp_chd)
        return sha1, create_log + info_log

    def verify_chd_file(self, chd_file):
        cmd = [CHDMAN_EXE, "verify", "-i", chd_file]
        out, err, returncode = self.run_required(cmd)
        return self.command_log(f"Verify {os.path.basename(chd_file)}", cmd, out, err, returncode)

    def verify_source_file(self, source_file, chd_threads):
        with tempfile.TemporaryDirectory(prefix="chdmanager_verify_") as temp_dir:
            temp_chd, create_log = self.create_temp_chd_from_source(source_file, temp_dir, chd_threads)
            verify_log = self.verify_chd_file(temp_chd)
        return create_log + verify_log

    def find_counterpart(self, base_name, folder, extensions):
        if not folder or not os.path.isdir(folder):
            return None

        candidates = []
        for root_dir, _, names in os.walk(folder):
            for name in names:
                stem, ext = os.path.splitext(name)
                if stem.lower() == base_name.lower() and ext.lower() in extensions:
                    candidates.append(os.path.join(root_dir, name))

        priority = {".gdi": 0, ".cue": 1, ".iso": 2, ".chd": 3}
        candidates.sort(key=lambda p: (priority.get(os.path.splitext(p)[1].lower(), 99), p.lower()))
        return candidates[0] if candidates else None

    def compare_input_file(self, input_file, dst, mode, chd_threads):
        result = self.empty_result()
        name = os.path.basename(input_file)
        base = os.path.splitext(name)[0]
        src = self.source_folder.get()
        try:
            if mode == "Comparer CHD -> Source":
                counterpart = self.find_counterpart(base, dst, DISC_EXTS) or self.find_counterpart(base, src, DISC_EXTS)
                missing_label = "source ISO/CUE/GDI"
                if not counterpart:
                    result["stats"]["missing"] += 1
                    result["logs"].append(f"--- {name} ---\n{missing_label} introuvable.\n\n")
                    return result
                primary_sha1, primary_log = self.chd_data_sha1(input_file)
                counterpart_sha1, counterpart_log = self.source_data_sha1(counterpart, chd_threads)
            else:
                counterpart = self.find_counterpart(base, dst, CHD_EXTS) or self.find_counterpart(base, src, CHD_EXTS)
                missing_label = "CHD"
                if not counterpart:
                    result["stats"]["missing"] += 1
                    result["logs"].append(f"--- {name} ---\n{missing_label} introuvable.\n\n")
                    return result
                primary_sha1, primary_log = self.source_data_sha1(input_file, chd_threads)
                counterpart_sha1, counterpart_log = self.chd_data_sha1(counterpart)

            log = [
                f"--- Comparaison {name} ---",
                f"Primaire: {input_file}",
                f"Contrepartie: {counterpart}",
                f"SHA1 primaire: {primary_sha1}",
                f"SHA1 contrepartie: {counterpart_sha1}",
                "",
                primary_log,
                counterpart_log,
            ]
            if primary_sha1 == counterpart_sha1:
                result["stats"]["matched"] += 1
                log.insert(5, "Résultat: OK")
            else:
                result["stats"]["failed"] += 1
                log.insert(5, "Résultat: ÉCHEC")
            result["logs"].append("\n".join(log) + "\n")
        except Exception as e:
            result["stats"]["failed"] += 1
            result["logs"].append(f"--- Comparaison {name} ---\nErreur: {e}\n\n")
        return result

    def process_input_file(self, input_file, dst, mode, overwrite, chd_threads, verify_after):
        result = self.empty_result()
        self.wait_if_paused()
        if not self.is_running:
            result["logs"].append(f"--- {os.path.basename(input_file)} ---\nArrêté.\n\n")
            return result

        if mode in ("Comparer CHD -> Source", "Comparer Source -> CHD"):
            self.update_status(f"Comparaison: {os.path.basename(input_file)}")
            return self.compare_input_file(input_file, dst, mode, chd_threads)

        if mode == "Vérifier Source":
            self.update_status(f"Vérification source: {os.path.basename(input_file)}")
            try:
                result["logs"].append(self.verify_source_file(input_file, chd_threads))
                result["stats"]["verified"] += 1
            except Exception as e:
                result["stats"]["failed"] += 1
                result["logs"].append(f"--- {os.path.basename(input_file)} ---\nErreur: {e}\n\n")
            return result

        self.update_status(f"Conversion: {os.path.basename(input_file)}" if mode == "Convertir vers CHD" else f"Traitement: {os.path.basename(input_file)}")
        cmd, skipped, output_file = self.build_chdman_cmd(mode, input_file, dst, overwrite, chd_threads)
        if skipped:
            result["stats"]["skipped"] += 1
            result["logs"].append(f"--- {os.path.basename(input_file)} ---\n{skipped}\n")
            if mode == "Convertir vers CHD" and verify_after and output_file and os.path.exists(output_file):
                try:
                    result["logs"].append(self.verify_chd_file(output_file))
                    result["stats"]["verified"] += 1
                except Exception as e:
                    result["stats"]["failed"] += 1
                    result["logs"].append(f"--- Vérification {os.path.basename(output_file)} ---\nErreur: {e}\n\n")
            return result
        if not cmd or len(cmd) == 1:
            result["stats"]["failed"] += 1
            result["logs"].append(f"--- {os.path.basename(input_file)} ---\nMode inconnu: {mode}\n\n")
            return result

        if output_file and overwrite and os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError as e:
                result["stats"]["failed"] += 1
                result["logs"].append(f"--- {os.path.basename(input_file)} ---\nImpossible de remplacer {output_file}: {e}\n\n")
                return result

        out, err, returncode = self.run_tracked_process(cmd)
        result["logs"].append(self.command_log(os.path.basename(input_file), cmd, out, err, returncode))
        if returncode == 0:
            if mode == "Info CHD":
                result["stats"]["info"] += 1
            elif mode == "Vérifier CHD":
                result["stats"]["verified"] += 1
            elif mode == "Convertir vers CHD":
                result["stats"]["converted"] += 1
                if verify_after and output_file and os.path.exists(output_file):
                    try:
                        result["logs"].append(self.verify_chd_file(output_file))
                        result["stats"]["verified"] += 1
                    except Exception as e:
                        result["stats"]["failed"] += 1
                        result["logs"].append(f"--- Vérification {os.path.basename(output_file)} ---\nErreur: {e}\n\n")
            elif mode == "Extraire CHD vers CUE/BIN":
                result["stats"]["extracted"] += 1
        else:
            result["stats"]["failed"] += 1
            if output_file and os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except OSError:
                    pass
        return result

    def process_task(self, task, dst, mode, overwrite, chd_threads, seven_za_path, verify_after):
        path = task["path"]
        result = self.empty_result()
        temp_dir = None
        try:
            if task["type"] == "archive":
                self.wait_if_paused()
                if not self.is_running:
                    result["logs"].append(f"--- {os.path.basename(path)} ---\nArrêté avant extraction.\n\n")
                    return result

                self.update_status(f"Extraction: {os.path.basename(path)}")
                temp_dir = tempfile.mkdtemp(prefix="chdmanager_")
                out, err, returncode = self.run_tracked_process([seven_za_path, "x", path, f"-o{temp_dir}", "-y"])
                result["logs"].append(f"--- Extraction {os.path.basename(path)} ---\nReturn code: {returncode}\n{out}\n{err}\n\n")
                if returncode != 0:
                    result["stats"]["failed"] += 1
                    return result

                input_files = self.find_disc_inputs(temp_dir, mode)
                if mode == "Convertir vers CHD" and input_files:
                    input_files = input_files[:1]
                if not input_files:
                    result["logs"].append(f"Aucun fichier compatible trouvé dans {path}\n\n")
                    result["stats"]["missing"] += 1
                    return result
            else:
                input_files = [path]

            for input_file in input_files:
                self.merge_result(result, self.process_input_file(input_file, dst, mode, overwrite, chd_threads, verify_after))
                if not self.is_running:
                    break
            return result
        except Exception as e:
            result["stats"]["failed"] += 1
            result["logs"].append(f"--- {os.path.basename(path)} ---\nError: {e}\n\n")
            return result
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def run_logic(self):
        src, dst = self.source_folder.get(), self.destination_folder.get()
        if not src or not dst:
            self.root.after(0, self.reset_buttons)
            return self.root.after(0, lambda: messagebox.showerror("Err", "Dossiers requis"))

        mode = self.option.get()
        overwrite = self.overwrite.get()
        verify_after = self.verify_after.get()
        workers = max(1, min(self.num_cores.get(), self.max_cores))
        aggregate = self.empty_result()
        report_path = None

        try:
            os.makedirs(dst, exist_ok=True)

            seven_za_path = None
            if 'utils' in sys.modules:
                manager = utils.DependencyManager(self.root)
                if manager.bootstrap_7za():
                    seven_za_path = manager.seven_za_path

            input_exts = self.input_exts_for_mode(mode)
            tasks = []
            for name in os.listdir(src):
                path = os.path.join(src, name)
                if not os.path.isfile(path):
                    continue
                lower = name.lower()
                if self.is_archive_start(name):
                    if seven_za_path:
                        tasks.append({"type": "archive", "path": path})
                elif lower.endswith(input_exts):
                    tasks.append({"type": "file", "path": path})

            total = len(tasks)
            if total == 0:
                aggregate["logs"].append("Aucun fichier compatible trouvé.\n")
                report_path = self.write_report(dst, mode, aggregate)
                self.update_status("Aucun fichier compatible trouvé.")
                self.root.after(0, lambda: messagebox.showinfo("Info", f"Aucun fichier compatible trouvé.\n\nRapport: {report_path}"))
                self.root.after(0, self.reset_buttons)
                return

            active_workers = min(workers, total)
            chd_threads = max(1, workers // active_workers)
            self.update_progress(0)
            self.update_status(f"Traitement de {total} élément(s) avec {active_workers} worker(s)...")

            done = 0
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=active_workers)
            futures = []
            try:
                for task in tasks:
                    futures.append(executor.submit(
                        self.process_task,
                        task,
                        dst,
                        mode,
                        overwrite,
                        chd_threads,
                        seven_za_path,
                        verify_after
                    ))

                for future in concurrent.futures.as_completed(futures):
                    done += 1
                    try:
                        self.merge_result(aggregate, future.result())
                    except Exception as e:
                        aggregate["stats"]["failed"] += 1
                        aggregate["logs"].append(f"Erreur worker: {e}\n\n")
                    self.update_progress(done / total)
                    if not self.is_running:
                        break
            finally:
                for future in futures:
                    future.cancel()
                executor.shutdown(wait=True, cancel_futures=True)

            report_path = self.write_report(dst, mode, aggregate)
            message = self.summary_message(aggregate["stats"]) + f"\n\nRapport: {report_path}"
            if self.is_running:
                self.update_status("Terminé.")
                title = "Fini" if aggregate["stats"]["failed"] == 0 and aggregate["stats"]["missing"] == 0 else "Fini avec erreurs"
                self.root.after(0, lambda t=title, m=message: messagebox.showinfo(t, m))
            else:
                self.update_status("Arrêté.")
                self.root.after(0, lambda m=message: messagebox.showinfo("Arrêté", m))
        finally:
            self.root.after(0, self.reset_buttons)

def main():
    root = ctk.CTk()
    app = CHDmanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
