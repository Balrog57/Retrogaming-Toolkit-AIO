# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
    import re
    import subprocess
    import sys
    import tempfile
    import threading
    import time
    import zipfile
    import customtkinter as ctk
    from tkinter import filedialog, messagebox

    try: import theme
    except: theme=None

    ctk.set_appearance_mode("dark")

    try: import utils
    except ImportError: pass

    def get_dolphin_tool_path():
        if 'utils' in sys.modules:
            p = utils.get_binary_path("DolphinTool.exe")
            if os.path.exists(p): return p
        p = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', "DolphinTool.exe")
        return p

    DOLPHIN_TOOL_NAME = get_dolphin_tool_path()
    RVZ_BLOCK_SIZES = [
        ("32 Kio", "32768"),
        ("64 Kio", "65536"),
        ("128 Kio", "131072"),
        ("256 Kio", "262144"),
        ("512 Kio", "524288"),
        ("1 Mio", "1048576"),
        ("2 Mio", "2097152"),
    ]
    RVZ_BLOCK_SIZE_LABELS = [label for label, _ in RVZ_BLOCK_SIZES]
    RVZ_BLOCK_SIZE_BY_LABEL = dict(RVZ_BLOCK_SIZES)
    OPERATIONS = [
        "ISO vers RVZ",
        "RVZ vers ISO",
        "Vérifier RVZ",
        "Vérifier ISO/GCM",
        "Comparer RVZ -> ISO",
        "Comparer ISO -> RVZ",
    ]
    ISO_EXTS = (".iso", ".gcm")
    RVZ_EXTS = (".rvz",)

    class ConversionStopped(Exception):
        pass

    def check_and_download_dolphintool(root):
        if os.path.exists(DOLPHIN_TOOL_NAME): return
        if 'utils' not in sys.modules: return messagebox.showerror("Err", "Utils missing")
        try:
            manager = utils.DependencyManager(root)
            res = manager.install_dependency("DolphinTool", "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z", "DolphinTool.exe", "7z")
            if not res: root.destroy()
        except Exception as e:
            messagebox.showerror("Err", str(e)); root.destroy()

    def create_startupinfo():
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return startupinfo

    def run_dolphin(args, output_path=None):
        if stop_event.is_set():
            raise ConversionStopped()

        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=create_startupinfo()
        )
        worker_state["process"] = process
        try:
            while process.poll() is None:
                if stop_event.is_set():
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    if output_path and os.path.exists(output_path):
                        try: os.remove(output_path)
                        except OSError: pass
                    raise ConversionStopped()
                time.sleep(0.2)

            stdout, stderr = process.communicate()
            if stop_event.is_set():
                if output_path and os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError: pass
                raise ConversionStopped()
            if process.returncode != 0:
                if output_path and os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError: pass
                details = (stderr or stdout or "").strip()
                if details:
                    raise RuntimeError(details)
                raise RuntimeError(f"DolphinTool a échoué avec le code {process.returncode}.")
            return stdout or "", stderr or ""
        finally:
            worker_state["process"] = None

    def base_name(name):
        return os.path.splitext(os.path.basename(name.replace("\\", "/")))[0]

    def output_path_for(source_name, out_dir, extension):
        return os.path.join(out_dir, f"{base_name(source_name)}{extension}")

    def iter_direct_tasks(folder, extensions):
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and name.lower().endswith(extensions):
                yield {
                    "kind": "direct",
                    "display": name,
                    "base": base_name(name),
                    "path": path,
                }

    def iter_zip_tasks(folder, extensions):
        for zip_name in sorted(os.listdir(folder)):
            zip_path = os.path.join(folder, zip_name)
            if not os.path.isfile(zip_path) or not zip_name.lower().endswith(".zip"):
                continue
            try:
                with zipfile.ZipFile(zip_path) as archive:
                    for member in archive.infolist():
                        if member.is_dir() or not member.filename.lower().endswith(extensions):
                            continue
                        member_name = member.filename
                        yield {
                            "kind": "zip",
                            "display": os.path.basename(member_name.replace("\\", "/")),
                            "base": base_name(member_name),
                            "zip_path": zip_path,
                            "member": member_name,
                        }
            except zipfile.BadZipFile:
                raise RuntimeError(f"Archive ZIP invalide: {zip_name}")

    def list_source_tasks(folder, extensions):
        return list(iter_direct_tasks(folder, extensions)) + list(iter_zip_tasks(folder, extensions))

    def attach_outputs(tasks, out_dir, extension):
        for task in tasks:
            task["output"] = output_path_for(task["display"], out_dir, extension)
        return tasks

    def extract_task_to_temp(task, temp_dir):
        if task["kind"] == "direct":
            return task["path"]

        temp_path = os.path.join(temp_dir, task["display"])
        with zipfile.ZipFile(task["zip_path"]) as archive:
            with archive.open(task["member"]) as source, open(temp_path, "wb") as target:
                while True:
                    if stop_event.is_set():
                        raise ConversionStopped()
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
        return temp_path

    def convert_task(task, output_format, fmt=None, lvl=None, blk=None):
        if os.path.exists(task["output"]):
            return "skipped"

        with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
            source_path = extract_task_to_temp(task, temp_dir)
            cmd = [DOLPHIN_TOOL_NAME, "convert", f"--format={output_format}", f"--input={source_path}", f"--output={task['output']}"]
            if output_format == "rvz":
                cmd.extend([f"--block_size={blk}", f"--compression={fmt}", f"--compression_level={lvl}"])
            run_dolphin(cmd, task["output"])
        return "converted"

    def verify_task(task):
        with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
            source_path = extract_task_to_temp(task, temp_dir)
            run_dolphin([DOLPHIN_TOOL_NAME, "verify", f"--input={source_path}"])

    def digest_task(task):
        with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
            source_path = extract_task_to_temp(task, temp_dir)
            stdout, stderr = run_dolphin([DOLPHIN_TOOL_NAME, "verify", "--algorithm=sha1", f"--input={source_path}"])
        text = f"{stdout}\n{stderr}"
        matches = re.findall(r"\b[a-fA-F0-9]{40}\b", text)
        if not matches:
            raise RuntimeError("SHA1 introuvable dans la sortie DolphinTool.")
        return matches[-1].lower()

    def output_direct_tasks(out_dir, extensions):
        tasks = list(iter_direct_tasks(out_dir, extensions))
        for task in tasks:
            task["display"] = os.path.basename(task["path"])
        return tasks

    def compare_targets(inp, out, primary_exts):
        targets = output_direct_tasks(out, primary_exts)
        if not targets and os.path.abspath(inp) != os.path.abspath(out):
            targets = list_source_tasks(inp, primary_exts)
        return targets

    def iso_compare_targets(inp, out):
        targets = list_source_tasks(inp, ISO_EXTS)
        if not targets and os.path.abspath(inp) != os.path.abspath(out):
            targets = output_direct_tasks(out, ISO_EXTS)
        return targets

    def index_sources(inp, extensions):
        sources = {}
        for task in list_source_tasks(inp, extensions):
            sources.setdefault(task["base"].lower(), task)
        return sources

    def run_conversion(tasks, output_format, fmt, lvl, blk, progress_cb):
        stats = {"converted": 0, "skipped": 0, "verified": 0, "failed": 0, "missing": 0}
        for index, task in enumerate(tasks):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb(index, task["display"])
            result = convert_task(task, output_format, fmt, lvl, blk)
            stats[result] += 1
        return stats

    def run_verify_rvz(tasks, progress_cb):
        stats = {"converted": 0, "skipped": 0, "verified": 0, "failed": 0, "missing": 0}
        errors = []
        for index, task in enumerate(tasks):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb(index, task["display"])
            try:
                verify_task(task)
                stats["verified"] += 1
            except Exception as e:
                stats["failed"] += 1
                errors.append(f"{task['display']}: {e}")
        return stats, errors

    def run_compare(primary_tasks, counterpart_sources, missing_label, progress_cb):
        stats = {"converted": 0, "skipped": 0, "verified": 0, "failed": 0, "missing": 0}
        errors = []
        for index, primary_task in enumerate(primary_tasks):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb(index, primary_task["display"])
            counterpart_task = counterpart_sources.get(primary_task["base"].lower())
            if not counterpart_task:
                stats["missing"] += 1
                errors.append(f"{primary_task['display']}: {missing_label} introuvable.")
                continue
            try:
                primary_sha1 = digest_task(primary_task)
                counterpart_sha1 = digest_task(counterpart_task)
                if primary_sha1 == counterpart_sha1:
                    stats["verified"] += 1
                else:
                    stats["failed"] += 1
                    errors.append(f"{primary_task['display']}: SHA1 différent ({primary_sha1} != {counterpart_sha1}).")
            except Exception as e:
                stats["failed"] += 1
                errors.append(f"{primary_task['display']}: {e}")
        return stats, errors

    def summary_message(stats, errors=None):
        parts = [
            f"Convertis: {stats['converted']}",
            f"Ignorés: {stats['skipped']}",
            f"Vérifiés OK: {stats['verified']}",
            f"Échecs: {stats['failed']}",
            f"Sources manquantes: {stats['missing']}",
        ]
        message = "\n".join(parts)
        if errors:
            shown = errors[:10]
            message += "\n\nDétails:\n" + "\n".join(shown)
            if len(errors) > len(shown):
                message += f"\n... {len(errors) - len(shown)} erreur(s) supplémentaire(s)."
        return message

    def write_report(out_dir, op, stats, errors):
        safe_op = re.sub(r"[^A-Za-z0-9_-]+", "_", op).strip("_")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(out_dir, f"dolphinconvert_{safe_op}_{timestamp}.txt")
        lines = [
            f"Operation: {op}",
            f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            summary_message(stats, errors),
        ]
        with open(report_path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines))
            report.write("\n")
        return report_path

    def ui_set_running(running):
        worker_state["running"] = running
        start_button.configure(state="disabled" if running else "normal", text="DÉMARRER" if running else "REPRENDRE / DÉMARRER")
        stop_button.configure(state="normal" if running else "disabled")

    def ui_set_progress(done, total, current=""):
        if total:
            progress_bar.set(done / total)
            status_var.set(f"{done}/{total} - {current}" if current else f"{done}/{total}")
        else:
            progress_bar.set(0)
            status_var.set(current or "Prêt.")

    def finish_conversion(title, message):
        ui_set_running(False)
        messagebox.showinfo(title, message)

    def fail_conversion(message):
        ui_set_running(False)
        messagebox.showerror("Erreur", message)

    def stopped_conversion(stats):
        ui_set_running(False)
        status_var.set("Arrêté. Reprise possible.")
        messagebox.showinfo("Arrêté", "Traitement arrêté. Relancez DÉMARRER pour reprendre les fichiers manquants.\n\n" + summary_message(stats))

    def after_ui(callback):
        try:
            if root.winfo_exists():
                root.after(0, callback)
        except Exception:
            pass

    def run_conversion_worker(inp, out, op, fmt, lvl, blk, verify_after):
        stats = {"converted": 0, "skipped": 0, "verified": 0, "failed": 0, "missing": 0}
        errors = []
        try:
            if op == "ISO vers RVZ":
                tasks = attach_outputs(list_source_tasks(inp, ISO_EXTS), out, ".rvz")
                total = len(tasks) + (len(tasks) if verify_after else 0)
            elif op == "RVZ vers ISO":
                tasks = attach_outputs(list_source_tasks(inp, RVZ_EXTS), out, ".iso")
                total = len(tasks)
            elif op == "Vérifier RVZ":
                tasks = list_source_tasks(inp, RVZ_EXTS)
                total = len(tasks)
            elif op == "Vérifier ISO/GCM":
                tasks = list_source_tasks(inp, ISO_EXTS)
                total = len(tasks)
            elif op == "Comparer RVZ -> ISO":
                tasks = compare_targets(inp, out, RVZ_EXTS)
                counterpart_sources = index_sources(inp, ISO_EXTS)
                missing_label = "ISO/GCM source"
                total = len(tasks)
            elif op == "Comparer ISO -> RVZ":
                tasks = iso_compare_targets(inp, out)
                counterpart_sources = index_sources(out, RVZ_EXTS)
                if not counterpart_sources and os.path.abspath(inp) != os.path.abspath(out):
                    counterpart_sources = index_sources(inp, RVZ_EXTS)
                missing_label = "RVZ source"
                total = len(tasks)
            else:
                return

            if total == 0:
                after_ui(lambda: finish_conversion("Info", "Aucun fichier compatible trouvé."))
                return

            def progress_cb(done, name):
                after_ui(lambda d=done, n=name: ui_set_progress(d, total, n))

            if op == "ISO vers RVZ":
                stats.update(run_conversion(tasks, "rvz", fmt, lvl, blk, progress_cb))
                if verify_after:
                    rvz_tasks = [{"kind": "direct", "display": os.path.basename(task["output"]), "base": task["base"], "path": task["output"]} for task in tasks if os.path.exists(task["output"])]
                    verify_stats, verify_errors = run_verify_rvz(rvz_tasks, lambda done, name: progress_cb(len(tasks) + done, name))
                    stats["verified"] += verify_stats["verified"]
                    stats["failed"] += verify_stats["failed"]
                    errors.extend(verify_errors)
            elif op == "RVZ vers ISO":
                stats.update(run_conversion(tasks, "iso", fmt, lvl, blk, progress_cb))
            elif op == "Vérifier RVZ":
                stats, errors = run_verify_rvz(tasks, progress_cb)
            elif op == "Vérifier ISO/GCM":
                stats, errors = run_verify_rvz(tasks, progress_cb)
            elif op in ("Comparer RVZ -> ISO", "Comparer ISO -> RVZ"):
                stats, errors = run_compare(tasks, counterpart_sources, missing_label, progress_cb)
        except ConversionStopped:
            after_ui(lambda s=stats: stopped_conversion(s))
            return
        except Exception as e:
            after_ui(lambda err=str(e): fail_conversion(err))
            return

        report_path = None
        if op in ("Vérifier RVZ", "Vérifier ISO/GCM"):
            try:
                report_path = write_report(out, op, stats, errors)
            except Exception as e:
                errors.append(f"Rapport: impossible d'écrire le rapport ({e}).")
                stats["failed"] += 1
        title = "Terminé" if stats["failed"] == 0 and stats["missing"] == 0 else "Terminé avec erreurs"
        message = summary_message(stats, errors)
        if report_path:
            message += f"\n\nRapport: {report_path}"
        after_ui(lambda s=stats, err=errors, t=title: (
            ui_set_progress(1, 1, "Terminé."),
            finish_conversion(t, message)
        ))

    def start_conversion():
        if worker_state["running"]:
            return
        inp, out = input_dir_var.get(), output_dir_var.get()
        op = operation_var.get()
        verify_only = op in ("Vérifier RVZ", "Vérifier ISO/GCM")
        if not inp: return messagebox.showerror("Err", "Dossier d'entrée manquant")
        if not out and verify_only:
            out = inp
        if not out: return messagebox.showerror("Err", "Dossier de sortie manquant")
        if not os.path.isdir(inp): return messagebox.showerror("Err", "Dossier d'entrée invalide")
        if not os.path.isdir(out): return messagebox.showerror("Err", "Dossier de sortie invalide")

        blk = RVZ_BLOCK_SIZE_BY_LABEL[block_size_var.get()]
        stop_event.clear()
        ui_set_running(True)
        ui_set_progress(0, 0, "Préparation...")
        threading.Thread(
            target=run_conversion_worker,
            args=(inp, out, op, compression_format_var.get(), compression_level_var.get(), blk, verify_after_var.get()),
            daemon=True
        ).start()

    def stop_conversion():
        if not worker_state["running"]:
            return
        stop_event.set()
        process = worker_state.get("process")
        if process and process.poll() is None:
            try: process.terminate()
            except OSError: pass
        status_var.set("Arrêt demandé...")
        stop_button.configure(state="disabled")

    def on_close():
        stop_event.set()
        process = worker_state.get("process")
        if process and process.poll() is None:
            try: process.terminate()
            except OSError: pass
        root.destroy()

    def update_operation_options(*_):
        enabled = operation_var.get() == "ISO vers RVZ"
        verify_after_check.configure(state="normal" if enabled else "disabled")
        if not enabled:
            verify_after_var.set(False)

    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Convertisseur RVZ/ISO")
        acc = theme.COLOR_ACCENT_PRIMARY
    else:
        root.title("Convertisseur RVZ/ISO")
        root.geometry("620x500")
        acc = "#1f6aa5"

    input_dir_var = ctk.StringVar()
    output_dir_var = ctk.StringVar()
    operation_var = ctk.StringVar(value="ISO vers RVZ")
    compression_format_var = ctk.StringVar(value="zstd")
    compression_level_var = ctk.StringVar(value="19")
    block_size_var = ctk.StringVar(value="128 Kio")
    verify_after_var = ctk.BooleanVar(value=False)
    status_var = ctk.StringVar(value="Prêt.")
    stop_event = threading.Event()
    worker_state = {"running": False, "process": None}

    main_fr = ctk.CTkFrame(root, fg_color="transparent")
    main_fr.pack(padx=20, pady=20)

    def mk_row(r, txt, var=None, vals=None, cmd=None):
        ctk.CTkLabel(main_fr, text=txt, anchor="e").grid(row=r, column=0, padx=5, pady=5, sticky="e")
        if vals: ctk.CTkOptionMenu(main_fr, variable=var, values=vals, fg_color=acc).grid(row=r, column=1, padx=5, pady=5, sticky="ew")
        else:
            ctk.CTkEntry(main_fr, textvariable=var, width=330).grid(row=r, column=1, padx=5, pady=5)
            if cmd: ctk.CTkButton(main_fr, text="...", width=50, command=cmd, fg_color=acc).grid(row=r, column=2, padx=5, pady=5)

    mk_row(0, "Entrée:", input_dir_var, cmd=lambda: input_dir_var.set(filedialog.askdirectory()))
    mk_row(1, "Sortie / rapport:", output_dir_var, cmd=lambda: output_dir_var.set(filedialog.askdirectory()))
    mk_row(2, "Opération:", operation_var, vals=OPERATIONS)
    mk_row(3, "Format:", compression_format_var, vals=["zstd", "lzma2", "lzma", "bzip2", "none"])
    mk_row(4, "Niveau:", compression_level_var, vals=[str(i) for i in range(1, 23)])
    mk_row(5, "Taille des blocs:", block_size_var, vals=RVZ_BLOCK_SIZE_LABELS)

    verify_after_check = ctk.CTkCheckBox(main_fr, text="Vérifier après conversion", variable=verify_after_var, fg_color=acc)
    verify_after_check.grid(row=6, column=1, padx=5, pady=8, sticky="w")
    operation_var.trace_add("write", update_operation_options)

    progress_bar = ctk.CTkProgressBar(root, width=480, progress_color=acc)
    progress_bar.set(0)
    progress_bar.pack(pady=(10, 5))
    ctk.CTkLabel(root, textvariable=status_var).pack(pady=(0, 10))

    btn_fr = ctk.CTkFrame(root, fg_color="transparent")
    btn_fr.pack(pady=10)
    start_button = ctk.CTkButton(btn_fr, text="REPRENDRE / DÉMARRER", command=start_conversion, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green")
    start_button.pack(side="left", padx=5)
    stop_button = ctk.CTkButton(btn_fr, text="ARRÊTER", command=stop_conversion, width=120, state="disabled", fg_color=theme.COLOR_ERROR if theme else "red")
    stop_button.pack(side="left", padx=5)

    check_and_download_dolphintool(root)
    update_operation_options()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
