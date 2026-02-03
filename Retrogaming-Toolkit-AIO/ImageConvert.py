import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import os
import concurrent.futures
import sys
from PIL import Image

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def process_single_image(input_path, output_path, delete_originals, output_fmt):
    try:
        with Image.open(input_path) as img:
             if output_fmt.lower() in ['jpeg', 'jpg'] and img.mode in ('RGBA', 'LA'):
                 img = img.convert('RGB')
             img.save(output_path)
        if delete_originals: os.remove(input_path)
        return True, input_path, None
    except Exception as e: return False, input_path, str(e)

def convert_images(root, input_dir, output_dir, input_fmt, output_fmt, delete_originals):
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    input_exts = [input_fmt.lower()]
    if input_fmt.lower() == "jpeg": input_exts = ["jpeg", "jpg"]
    elif input_fmt.lower() == "tiff": input_exts = ["tiff", "tif"]

    files_to_process = []
    for f in os.listdir(input_dir):
        if any(f.lower().endswith(f".{ext}") for ext in input_exts):
            ip = os.path.join(input_dir, f)
            op = os.path.join(output_dir, os.path.splitext(f)[0] + f".{output_fmt.lower()}")
            files_to_process.append((ip, op, delete_originals, output_fmt))

    if not files_to_process: return messagebox.showinfo("Info", "Aucune image trouvée.")

    max_workers = os.cpu_count() or 4
    failed = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exe:
        future_map = {exe.submit(process_single_image, *args): args[1] for args in files_to_process}
        for future in concurrent.futures.as_completed(future_map):
            ip = future_map[future]
            try:
                succ, _, err = future.result()
                if not succ: failed.append((ip, err))
            except Exception as e: failed.append((ip, str(e)))

    if failed:
        msg = "\n".join([f"{os.path.basename(f[0])}: {f[1]}" for f in failed[:5]])
        messagebox.showwarning("Erreurs", f"{len(failed)} erreurs:\n{msg}")
    else:
        messagebox.showinfo("Succès", "Conversion terminée.")

def main():
    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Convertisseur d'Images")
        acc = theme.COLOR_ACCENT_PRIMARY
    else:
        root.title("Convertisseur d'Images")
        acc = "#1f6aa5"

    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)

    # Input
    ctk.CTkLabel(fr, text="Dossier d'entrée:").grid(row=0, column=0, sticky="w")
    entry_in = ctk.CTkEntry(fr, width=300)
    entry_in.grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: entry_in.insert(0, filedialog.askdirectory()), fg_color=acc).grid(row=0, column=2)

    # Output
    ctk.CTkLabel(fr, text="Dossier de sortie:").grid(row=1, column=0, sticky="w")
    entry_out = ctk.CTkEntry(fr, width=300)
    entry_out.grid(row=1, column=1, padx=5, pady=5)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: entry_out.insert(0, filedialog.askdirectory()), fg_color=acc).grid(row=1, column=2)

    # Formats
    ctk.CTkLabel(fr, text="Format Entrée:").grid(row=2, column=0, sticky="w")
    fmt_in = ctk.CTkOptionMenu(fr, values=["webp", "jpeg", "png", "tiff", "bmp", "gif", "ppm", "pgm", "pbm", "pnm"], fg_color=acc)
    fmt_in.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    ctk.CTkLabel(fr, text="Format Sortie:").grid(row=3, column=0, sticky="w")
    fmt_out = ctk.CTkOptionMenu(fr, values=["jpeg", "png", "tiff", "bmp", "gif", "ppm", "pgm", "pbm", "pnm", "webp"], fg_color=acc)
    fmt_out.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    fmt_out.set("png")

    del_var = ctk.BooleanVar()
    ctk.CTkCheckBox(fr, text="Supprimer originaux", variable=del_var, fg_color=acc).grid(row=4, column=0, columnspan=3, pady=10)

    ctk.CTkButton(root, text="CONVERTIR", command=lambda: convert_images(root, entry_in.get(), entry_out.get(), fmt_in.get(), fmt_out.get(), del_var.get()), width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()