import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import concurrent.futures

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def compress_file(args):
    """
    Helper function to compress a single file.
    args: tuple (filename, source_dir, seven_za_path)
    """
    filename, source_dir, seven_za_path = args
    fp = os.path.join(source_dir, filename)
    zip_path = os.path.join(source_dir, os.path.splitext(filename)[0] + ".zip")

    cmd = [seven_za_path, 'a', '-tzip', zip_path, fp]

    # Cross-platform STARTUPINFO
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        res = subprocess.run(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            os.remove(fp)
            print(f"Compressed & Deleted: {filename}")
            return True
        else:
            print(f"Err {filename}: {res.stderr}")
            return False
    except Exception as e:
        print(f"Exception compressing {filename}: {e}")
        return False

def compress_and_delete_roms(source_dir):
    try:
        if not os.path.exists(source_dir): return messagebox.showerror("Err", "Dossier source invalide")
        
        try: import utils
        except ImportError: return messagebox.showerror("Err", "Utils manquant")
        
        manager = utils.DependencyManager()
        if not manager.bootstrap_7za(): return messagebox.showerror("Err", "7za manquant")

        # Gather files to process
        files_to_process = []
        for filename in os.listdir(source_dir):
            fp = os.path.join(source_dir, filename)
            if os.path.isfile(fp) and not filename.endswith('.zip'):
                files_to_process.append((filename, source_dir, manager.seven_za_path))

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
