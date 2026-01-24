import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def compress_and_delete_roms(source_dir):
    try:
        if not os.path.exists(source_dir): return messagebox.showerror("Err", "Dossier source invalide")
        
        try: import utils
        except ImportError: return messagebox.showerror("Err", "Utils manquant")
        
        manager = utils.DependencyManager()
        if not manager.bootstrap_7za(): return messagebox.showerror("Err", "7za manquant")

        count = 0
        for filename in os.listdir(source_dir):
            fp = os.path.join(source_dir, filename)
            if os.path.isfile(fp) and not filename.endswith('.zip'):
                zip_path = os.path.join(source_dir, os.path.splitext(filename)[0] + ".zip")
                
                cmd = [manager.seven_za_path, 'a', '-tzip', zip_path, fp]
                si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                res = subprocess.run(cmd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0:
                    os.remove(fp)
                    print(f"Compressed & Deleted: {filename}")
                    count += 1
                else:
                    print(f"Err {filename}: {res.stderr}")

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