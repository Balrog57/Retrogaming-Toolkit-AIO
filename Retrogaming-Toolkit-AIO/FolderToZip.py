import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import concurrent.futures
import zipfile

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def compress_file(args):
    """
    Helper function to compress a single file using native zipfile.
    args: tuple (filename, source_dir)
    """
    filename, source_dir = args
    fp = os.path.join(source_dir, filename)
    zip_path = os.path.join(source_dir, os.path.splitext(filename)[0] + ".zip")

    try:
        # Optimization: Use native zipfile instead of spawning subprocess
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(fp, arcname=filename)

        os.remove(fp)
        print(f"Compressed & Deleted: {filename}")
        return True
    except Exception as e:
        print(f"Exception compressing {filename}: {e}")
        # Cleanup partial zip if exists
        if os.path.exists(zip_path):
            try: os.remove(zip_path)
            except: pass
        return False

def compress_and_delete_roms(source_dir):
    try:
        if not os.path.exists(source_dir): return messagebox.showerror("Err", "Dossier source invalide")
        
        # Optimization: No need for utils/7za dependency here anymore
        
        # Gather files to process
        files_to_process = []
        for filename in os.listdir(source_dir):
            fp = os.path.join(source_dir, filename)
            if os.path.isfile(fp) and not filename.endswith('.zip'):
                files_to_process.append((filename, source_dir))

        count = 0
        # Parallel execution
        # Using ThreadPoolExecutor allows parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(compress_file, files_to_process)
            for success in results:
                if success:
                    count += 1

        messagebox.showinfo("Succès", f"{count} fichiers compressés.")
    except Exception as e:
        messagebox.showerror("Err", str(e))

def main():
    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Dossier ROM vers ZIP")
        acc = theme.COLOR_ACCENT_PRIMARY
    else:
        root.title("Dossier ROM vers ZIP")
        root.geometry("500x300")
        acc = "#1f6aa5"

    source_dir = ctk.StringVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(fr, text="Compresser fichiers en ZIP (individuel)", font=theme.get_font_title(16) if theme else ("Arial", 16, "bold")).pack(pady=10)
    
    ctk.CTkEntry(fr, textvariable=source_dir, width=350).pack(pady=10)
    ctk.CTkButton(fr, text="Parcourir", command=lambda: source_dir.set(filedialog.askdirectory()), fg_color=acc).pack(pady=5)
    
    ctk.CTkButton(fr, text="COMPRESSER & SUPPRIMER ORIGINAUX", command=lambda: compress_and_delete_roms(source_dir.get()), 
                  width=300, fg_color=theme.COLOR_ERROR if theme else "red").pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
