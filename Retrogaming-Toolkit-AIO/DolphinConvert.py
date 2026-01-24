# Module généré automatiquement à partir de rvz_iso_convert.py

def main():
    import os
    import subprocess
    import sys
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

    def check_and_download_dolphintool(root):
        if os.path.exists(DOLPHIN_TOOL_NAME): return
        if 'utils' not in sys.modules: return messagebox.showerror("Err", "Utils missing")
        try:
            manager = utils.DependencyManager(root)
            res = manager.install_dependency("DolphinTool", "https://dl.dolphin-emu.org/releases/2412/dolphin-2412-x64.7z", "DolphinTool.exe", "7z")
            if not res: root.destroy()
        except Exception as e:
            messagebox.showerror("Err", str(e)); root.destroy()

    def convert_rvz_to_iso(inp, out):
        files = [os.path.join(inp, f) for f in os.listdir(inp) if f.endswith(".rvz")]
        for f in files:
            o = os.path.join(out, f"{os.path.splitext(os.path.basename(f))[0]}.iso")
            if os.path.exists(o): os.remove(o)
            subprocess.run([DOLPHIN_TOOL_NAME, "convert", "--format=iso", f"--input={f}", f"--output={o}"])

    def convert_iso_to_rvz(inp, out, fmt, lvl, blk):
        files = [os.path.join(inp, f) for f in os.listdir(inp) if f.endswith(".iso")]
        for f in files:
            o = os.path.join(out, f"{os.path.splitext(os.path.basename(f))[0]}.rvz")
            if os.path.exists(o): os.remove(o)
            subprocess.run([DOLPHIN_TOOL_NAME, "convert", "--format=rvz", f"--input={f}", f"--output={o}", f"--block_size={blk}", f"--compression={fmt}", f"--compression_level={lvl}"])

    def start_conversion():
        inp, out = input_dir_var.get(), output_dir_var.get()
        if not inp or not out: return messagebox.showerror("Err", "Dirs missing")
        
        op = operation_var.get()
        if op == "ISO vers RVZ":
            convert_iso_to_rvz(inp, out, compression_format_var.get(), compression_level_var.get(), block_size_var.get())
        elif op == "RVZ vers ISO":
            convert_rvz_to_iso(inp, out)
        else: return
        messagebox.showinfo("Fini", "Conversion terminée.")

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
    compression_level_var = ctk.IntVar(value=5)
    block_size_var = ctk.StringVar(value="131072")

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
    mk_row(3, "Format:", compression_format_var, vals=["zstd", "lzma2", "lzma", "bzip", "none"])
    mk_row(4, "Niveau:", compression_level_var, vals=[str(i) for i in range(1, 23)])
    mk_row(5, "Block Size:", block_size_var, vals=["32768", "65536", "131072", "262144", "524288", "1048576", "2097152", "8388608", "16777216", "33554432"])

    ctk.CTkButton(root, text="DÉMARRER", command=start_conversion, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=20)

    check_and_download_dolphintool(root)
    root.mainloop()

if __name__ == '__main__':
    main()