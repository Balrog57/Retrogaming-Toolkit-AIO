import os
import customtkinter as ctk
from tkinter import messagebox, filedialog

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

class FolderToTxtApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Créateur de fichiers .txt")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
        else:
            self.title("Créateur de fichiers .txt")
            self.geometry("500x250")
            self.COLOR_ACCENT = "#1f6aa5"

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Row 1
        ctk.CTkLabel(main, text="Dossier:").grid(row=0, column=0, sticky="w", pady=10)
        self.path_var = ctk.StringVar()
        ctk.CTkEntry(main, textvariable=self.path_var, width=250).grid(row=0, column=1, padx=10)
        ctk.CTkButton(main, text="...", width=50, command=self.browse, fg_color=self.COLOR_ACCENT).grid(row=0, column=2)

        # Row 2
        ctk.CTkLabel(main, text="Extension source (ex: mp4):").grid(row=1, column=0, sticky="w", pady=10)
        self.ext_var = ctk.StringVar()
        ctk.CTkEntry(main, textvariable=self.ext_var, width=250).grid(row=1, column=1, padx=10)

        # Btn
        ctk.CTkButton(main, text="CRÉER .TXT", command=self.run, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").grid(row=2, column=1, pady=30)

    def browse(self):
        p = filedialog.askdirectory()
        if p: self.path_var.set(p)

    def run(self):
        fp = self.path_var.get()
        ext = self.ext_var.get().strip()
        
        if not fp or not ext: return messagebox.showerror("Err", "Infos manquantes")
        if not ext.startswith("."): ext = f".{ext}"
        
        try:
            count = 0
            for f in os.listdir(fp):
                if f.endswith(ext):
                    base = os.path.splitext(f)[0]
                    with open(os.path.join(fp, f"{base}.txt"), 'w'): pass
                    count += 1
            messagebox.showinfo("Succès", f"{count} fichiers txt créés.")
        except Exception as e:
            messagebox.showerror("Err", str(e))

def main():
    app = FolderToTxtApp()
    app.mainloop()

if __name__ == "__main__":
    main()