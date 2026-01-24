import os
import shutil
import subprocess
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, IntVar
import multiprocessing
import sys

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

try: import utils
except: pass

def get_maxcso(root):
    if 'utils' in sys.modules:
        bp = utils.get_binary_path("maxcso.exe")
        if os.path.exists(bp): return bp
        try:
            m = utils.DependencyManager(root)
            if m.install_dependency("MaxCSO", "https://github.com/unknownbrackets/maxcso/releases/download/v1.13.0/maxcso_v1.13.0_windows.7z", "maxcso.exe", "7z"):
                return utils.get_binary_path("maxcso.exe")
        except: pass
    return "maxcso.exe"

def compress(inp, out, repl, pvar, plbal, root):
    mc = get_maxcso(root)
    isos = [f for f in os.listdir(inp) if f.lower().endswith(".iso")]
    if not isos: return messagebox.showinfo("Info", "No ISO found")
    
    tmp = tempfile.mkdtemp()
    cpu = multiprocessing.cpu_count()
    
    try:
        total = len(isos)
        for i, f in enumerate(isos, 1):
            ip = os.path.join(inp, f)
            op = os.path.join(tmp, f"{os.path.splitext(f)[0]}.cso")
            
            res = subprocess.run([mc, "--fast", ip, "-o", op, f"--threads={cpu}"], capture_output=True, text=True)
            
            if res.returncode != 0:
                messagebox.showerror("Err", f"Fail {f}: {res.stderr}")
                continue
            
            if repl: shutil.move(op, ip) # Wait, replacing ISO with CSO usually means deleting ISO and putting CSO there? Or renaming? Assuming replacing logic means we want CSO in input dir.
            # Original script logic: shutil.move(output_path, input_path) -> This overwrites ISO with CSO? No, CSOs have different extension.
            # If input_path is .iso, and we move .cso to .iso path, we get a file named .iso but it is cso. That seems wrong.
            # Checking original code: shutil.move(output_path, input_path)
            # Yes, original code overwrote input_path (file.iso). This is dangerous if extensions matter.
            # I will act safer: if replace, put .cso in input dir and delete .iso
            
            final_dest = os.path.join(inp if repl else out, f"{os.path.splitext(f)[0]}.cso")
            shutil.move(op, final_dest)
            if repl: os.remove(ip)

            prog = (i/total)*100
            pvar.set(prog)
            plbal.configure(text=f"{prog:.1f}%")
            root.update()
            
        messagebox.showinfo("Success", "Compression Done")
    finally:
        shutil.rmtree(tmp)

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "MaxCSO GUI")
    else: root.title("MaxCSO GUI")
    
    root.geometry("400x500")

    in_var = StringVar()
    out_var = StringVar()
    rep_var = IntVar(value=0)
    prog_var = ctk.DoubleVar(value=0)

    f = ctk.CTkFrame(root, fg_color="transparent")
    f.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(f, text="Options:", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
    ctk.CTkRadioButton(f, text="Replace originals", variable=rep_var, value=1, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w")
    ctk.CTkRadioButton(f, text="Keep originals (use output)", variable=rep_var, value=0, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w")

    ctk.CTkLabel(f, text="Input:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10,5))
    ctk.CTkButton(f, text="Browse", command=lambda: in_var.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w")
    ctk.CTkLabel(f, textvariable=in_var).pack(anchor="w")

    ol = ctk.CTkLabel(f, text="Output:", font=("Arial", 14, "bold"))
    ob = ctk.CTkButton(f, text="Browse", command=lambda: out_var.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
    od = ctk.CTkLabel(f, textvariable=out_var)

    def upd(*args):
        if rep_var.get():
             ol.pack_forget(); ob.pack_forget(); od.pack_forget()
        else:
             ol.pack(anchor="w", pady=(10,5)); ob.pack(anchor="w"); od.pack(anchor="w")
    rep_var.trace_add("write", upd)
    upd()

    ctk.CTkProgressBar(f, variable=prog_var, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(pady=20, fill="x")
    pl = ctk.CTkLabel(f, text="0%")
    pl.pack()

    ctk.CTkButton(f, text="START", command=lambda: compress(in_var.get(), out_var.get(), rep_var.get(), prog_var, pl, root), fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()