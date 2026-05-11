# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
    import shutil
    import subprocess
    import sys
    import tempfile
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

    def check_and_download_dolphintool(root):
        if os.path.exists(DOLPHIN_TOOL_NAME): return
        if 'utils' not in sys.modules: return messagebox.showerror("Err", "Utils missing")
        try:
            manager = utils.DependencyManager(root)
            res = manager.install_dependency("DolphinTool", "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z", "DolphinTool.exe", "7z")
            if not res: root.destroy()
        except Exception as e:
            messagebox.showerror("Err", str(e)); root.destroy()

    def run_dolphin_convert(args):
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            if details:
                raise RuntimeError(details)
            raise RuntimeError(f"DolphinTool a échoué avec le code {result.returncode}.")

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
                shutil.copyfileobj(source, target)
        return temp_path

    def convert_one_rvz_to_iso(source_path, out):
        o = os.path.join(out, f"{os.path.splitext(os.path.basename(source_path))[0]}.iso")
        if os.path.exists(o): os.remove(o)
        run_dolphin_convert([DOLPHIN_TOOL_NAME, "convert", "--format=iso", f"--input={source_path}", f"--output={o}"])

    def convert_rvz_to_iso(inp, out):
        count = 0
        for f in iter_direct_files(inp, (".rvz",)):
            convert_one_rvz_to_iso(f, out)
            count += 1
        for zip_path, member_name in iter_zip_members(inp, (".rvz",)):
            with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
                temp_path = extract_zip_member_to_temp(zip_path, member_name, temp_dir)
                convert_one_rvz_to_iso(temp_path, out)
                count += 1
        return count

    def convert_one_iso_to_rvz(source_path, out, fmt, lvl, blk):
        o = os.path.join(out, f"{os.path.splitext(os.path.basename(source_path))[0]}.rvz")
        if os.path.exists(o): os.remove(o)
        run_dolphin_convert([DOLPHIN_TOOL_NAME, "convert", "--format=rvz", f"--input={source_path}", f"--output={o}", f"--block_size={blk}", f"--compression={fmt}", f"--compression_level={lvl}"])

    def convert_iso_to_rvz(inp, out, fmt, lvl, blk):
        count = 0
        for f in iter_direct_files(inp, (".iso", ".gcm")):
            convert_one_iso_to_rvz(f, out, fmt, lvl, blk)
            count += 1
        for zip_path, member_name in iter_zip_members(inp, (".iso", ".gcm")):
            with tempfile.TemporaryDirectory(prefix="dolphinconvert_") as temp_dir:
                temp_path = extract_zip_member_to_temp(zip_path, member_name, temp_dir)
                convert_one_iso_to_rvz(temp_path, out, fmt, lvl, blk)
                count += 1
        return count

    def start_conversion():
        inp, out = input_dir_var.get(), output_dir_var.get()
        if not inp or not out: return messagebox.showerror("Err", "Dirs missing")
        if not os.path.isdir(inp): return messagebox.showerror("Err", "Dossier d'entrée invalide")
        if not os.path.isdir(out): return messagebox.showerror("Err", "Dossier de sortie invalide")
        
        op = operation_var.get()
        try:
            if op == "ISO vers RVZ":
                count = convert_iso_to_rvz(inp, out, compression_format_var.get(), compression_level_var.get(), RVZ_BLOCK_SIZE_BY_LABEL[block_size_var.get()])
            elif op == "RVZ vers ISO":
                count = convert_rvz_to_iso(inp, out)
            else: return
        except Exception as e:
            return messagebox.showerror("Erreur", str(e))
        if count == 0:
            return messagebox.showinfo("Info", "Aucun fichier compatible trouvé.")
        messagebox.showinfo("Fini", f"Conversion terminée ({count} fichier(s)).")

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

    ctk.CTkButton(root, text="DÉMARRER", command=start_conversion, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=20)

    check_and_download_dolphintool(root)
    root.mainloop()

if __name__ == '__main__':
    main()
