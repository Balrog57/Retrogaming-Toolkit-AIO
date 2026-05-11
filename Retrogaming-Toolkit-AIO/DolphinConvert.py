# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
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

    def run_dolphin_convert(args, output_path):
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
                    if os.path.exists(output_path):
                        try: os.remove(output_path)
                        except OSError: pass
                    raise ConversionStopped()
                time.sleep(0.2)

            stdout, stderr = process.communicate()
            if stop_event.is_set():
                if os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError: pass
                raise ConversionStopped()
            if process.returncode != 0:
                if os.path.exists(output_path):
                    try: os.remove(output_path)
                    except OSError: pass
                details = (stderr or stdout or "").strip()
                if details:
                    raise RuntimeError(details)
                raise RuntimeError(f"DolphinTool a échoué avec le code {process.returncode}.")
        finally:
            worker_state["process"] = None

    def iter_direct_files(inp, extensions):
        for name in sorted(os.listdir(inp)):
            path = os.path.join(inp, name)
            if os.path.isfile(path) and name.lower().endswith(extensions):
                yield path

    def iter_zip_members(inp, extensions):
        for zip_name in sorted(os.listdir(inp)):
            zip_path = os.path.join(inp, zip_name)
            if not os.path.isfile(zip_path) or not zip_name.lower().endswith(".zip"):
                continue
            try:
                with zipfile.ZipFile(zip_path) as archive:
                    for member in archive.infolist():
                        if member.is_dir() or not member.filename.lower().endswith(extensions):
                            continue
                        yield zip_path, member.filename
            except zipfile.BadZipFile:
                raise RuntimeError(f"Archive ZIP invalide: {zip_name}")

    def extract_zip_member_to_temp(zip_path, member_name, temp_dir):
        base_name = os.path.basename(member_name.replace("\\", "/"))
        if not base_name:
            raise RuntimeError(f"Fichier invalide dans l'archive: {member_name}")
        temp_path = os.path.join(temp_dir, base_name)
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open(member_name) as source, open(temp_path, "wb") as target:
                while True:
                    if stop_event.is_set():
                        raise ConversionStopped()
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
        return temp_path

    def get_output_path(source_name, out, extension):
        return os.path.join(out, f"{os.path.splitext(os.path.basename(source_name))[0]}{extension}")

    def convert_one_rvz_to_iso(source_path, out, source_name=None):
        source_name = source_name or source_path
        o = get_output_path(source_name, out, ".iso")
        if os.path.exists(o):
            return "skipped"
        run_dolphin_convert([DOLPHIN_TOOL_NAME, "convert", "--format=iso", f"--input={source_path}", f"--output={o}"], o)
        return "converted"

    def count_rvz_to_iso(inp):
        return sum(1 for _ in iter_direct_files(inp, (".rvz",))) + sum(1 for _ in iter_zip_members(inp, (".rvz",)))

    def convert_rvz_to_iso(inp, out, progress_cb=None):
        converted = skipped = done = 0
        for f in iter_direct_files(inp, (".rvz",)):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb and progress_cb(done, os.path.basename(f))
            result = convert_one_rvz_to_iso(f, out)
            converted += result == "converted"
            skipped += result == "skipped"
            done += 1
        for zip_path, member_name in iter_zip_members(inp, (".rvz",)):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb and progress_cb(done, os.path.basename(member_name))
            with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
                temp_path = extract_zip_member_to_temp(zip_path, member_name, temp_dir)
                result = convert_one_rvz_to_iso(temp_path, out, member_name)
                converted += result == "converted"
                skipped += result == "skipped"
                done += 1
        return converted, skipped

    def convert_one_iso_to_rvz(source_path, out, fmt, lvl, blk, source_name=None):
        source_name = source_name or source_path
        o = get_output_path(source_name, out, ".rvz")
        if os.path.exists(o):
            return "skipped"
        run_dolphin_convert([DOLPHIN_TOOL_NAME, "convert", "--format=rvz", f"--input={source_path}", f"--output={o}", f"--block_size={blk}", f"--compression={fmt}", f"--compression_level={lvl}"], o)
        return "converted"

    def count_iso_to_rvz(inp):
        return sum(1 for _ in iter_direct_files(inp, (".iso", ".gcm"))) + sum(1 for _ in iter_zip_members(inp, (".iso", ".gcm")))

    def convert_iso_to_rvz(inp, out, fmt, lvl, blk, progress_cb=None):
        converted = skipped = done = 0
        for f in iter_direct_files(inp, (".iso", ".gcm")):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb and progress_cb(done, os.path.basename(f))
            result = convert_one_iso_to_rvz(f, out, fmt, lvl, blk)
            converted += result == "converted"
            skipped += result == "skipped"
            done += 1
        for zip_path, member_name in iter_zip_members(inp, (".iso", ".gcm")):
            if stop_event.is_set(): raise ConversionStopped()
            progress_cb and progress_cb(done, os.path.basename(member_name))
            with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
                temp_path = extract_zip_member_to_temp(zip_path, member_name, temp_dir)
                result = convert_one_iso_to_rvz(temp_path, out, fmt, lvl, blk, member_name)
                converted += result == "converted"
                skipped += result == "skipped"
                done += 1
        return converted, skipped

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

    def stopped_conversion(converted, skipped):
        ui_set_running(False)
        status_var.set(f"Arrêté. Reprise possible ({converted} converti(s), {skipped} ignoré(s)).")
        messagebox.showinfo("Arrêté", "Conversion arrêtée. Relancez DÉMARRER pour reprendre les fichiers manquants.")

    def after_ui(callback):
        try:
            if root.winfo_exists():
                root.after(0, callback)
        except Exception:
            pass

    def run_conversion_worker(inp, out, op, fmt, lvl, blk):
        converted = skipped = total = 0
        try:
            total = count_iso_to_rvz(inp) if op == "ISO vers RVZ" else count_rvz_to_iso(inp)
            if total == 0:
                after_ui(lambda: finish_conversion("Info", "Aucun fichier compatible trouvé."))
                return

            def progress_cb(done, name):
                after_ui(lambda d=done, n=name: ui_set_progress(d, total, n))

            if op == "ISO vers RVZ":
                converted, skipped = convert_iso_to_rvz(inp, out, fmt, lvl, blk, progress_cb)
            elif op == "RVZ vers ISO":
                converted, skipped = convert_rvz_to_iso(inp, out, progress_cb)
            else:
                return
        except ConversionStopped:
            after_ui(lambda c=converted, s=skipped: stopped_conversion(c, s))
            return
        except Exception as e:
            after_ui(lambda err=str(e): fail_conversion(err))
            return
        after_ui(lambda: (
            ui_set_progress(total, total, "Terminé."),
            finish_conversion("Fini", f"Conversion terminée ({converted} converti(s), {skipped} déjà présent(s)).")
        ))

    def start_conversion():
        if worker_state["running"]:
            return
        inp, out = input_dir_var.get(), output_dir_var.get()
        if not inp or not out: return messagebox.showerror("Err", "Dirs missing")
        if not os.path.isdir(inp): return messagebox.showerror("Err", "Dossier d'entrée invalide")
        if not os.path.isdir(out): return messagebox.showerror("Err", "Dossier de sortie invalide")
        
        op = operation_var.get()
        blk = RVZ_BLOCK_SIZE_BY_LABEL[block_size_var.get()]
        stop_event.clear()
        ui_set_running(True)
        ui_set_progress(0, 0, "Préparation...")
        threading.Thread(
            target=run_conversion_worker,
            args=(inp, out, op, compression_format_var.get(), compression_level_var.get(), blk),
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

    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Convertisseur RVZ/ISO")
        acc = theme.COLOR_ACCENT_PRIMARY
    else:
        root.title("Convertisseur RVZ/ISO")
        root.geometry("600x450")
        acc = "#1f6aa5"

    input_dir_var = ctk.StringVar()
    output_dir_var = ctk.StringVar()
    operation_var = ctk.StringVar(value="ISO vers RVZ")
    compression_format_var = ctk.StringVar(value="zstd")
    compression_level_var = ctk.StringVar(value="19")
    block_size_var = ctk.StringVar(value="128 Kio")
    status_var = ctk.StringVar(value="Prêt.")
    stop_event = threading.Event()
    worker_state = {"running": False, "process": None}

    main_fr = ctk.CTkFrame(root, fg_color="transparent")
    main_fr.pack(padx=20, pady=20)

    def mk_row(r, txt, var=None, vals=None, cmd=None):
        ctk.CTkLabel(main_fr, text=txt, anchor="e").grid(row=r, column=0, padx=5, pady=5, sticky="e")
        if vals: ctk.CTkOptionMenu(main_fr, variable=var, values=vals, fg_color=acc).grid(row=r, column=1, padx=5, pady=5, sticky="ew")
        else: 
            ctk.CTkEntry(main_fr, textvariable=var, width=300).grid(row=r, column=1, padx=5, pady=5)
            if cmd: ctk.CTkButton(main_fr, text="...", width=50, command=cmd, fg_color=acc).grid(row=r, column=2, padx=5, pady=5)

    mk_row(0, "Entrée:", input_dir_var, cmd=lambda: input_dir_var.set(filedialog.askdirectory()))
    mk_row(1, "Sortie:", output_dir_var, cmd=lambda: output_dir_var.set(filedialog.askdirectory()))
    mk_row(2, "Opération:", operation_var, vals=["ISO vers RVZ", "RVZ vers ISO"])
    mk_row(3, "Format:", compression_format_var, vals=["zstd", "lzma2", "lzma", "bzip2", "none"])
    mk_row(4, "Niveau:", compression_level_var, vals=[str(i) for i in range(1, 23)])
    mk_row(5, "Taille des blocs:", block_size_var, vals=RVZ_BLOCK_SIZE_LABELS)

    progress_bar = ctk.CTkProgressBar(root, width=460, progress_color=acc)
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
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
