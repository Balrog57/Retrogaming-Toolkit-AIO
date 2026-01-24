import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

class FolderCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Supprimer Dossiers Vides")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
        else:
            self.title("Supprimer Dossiers Vides")
            self.geometry("500x300")
            self.COLOR_ACCENT = "#1f6aa5"

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main, text="Nettoyeur de Dossiers Vides", font=theme.get_font_title(20) if theme else ("Arial", 20)).pack(pady=10)
        
        self.path_entry = ctk.CTkEntry(main, width=350)
        self.path_entry.pack(pady=10)
        
        ctk.CTkButton(main, text="Parcourir", command=self.browse, fg_color=self.COLOR_ACCENT).pack(pady=5)
        ctk.CTkButton(main, text="NETTOYER", command=self.clean, fg_color=theme.COLOR_ERROR if theme else "red").pack(pady=20)
        
        self.status = ctk.StringVar(value="")
        ctk.CTkLabel(main, textvariable=self.status, text_color=theme.COLOR_TEXT_SUB if theme else "gray").pack(pady=10)

    def browse(self):
        p = filedialog.askdirectory()
        if p:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, p)

    def clean(self):
        p = self.path_entry.get()
        if not p: return
        
        self.status.set("Analyse...")
        self.update()
        
        count = 0
        removed = 0
        for root, dirs, _ in os.walk(p, topdown=False):
            for d in dirs:
                fp = os.path.join(root, d)
                try:
                    if not os.listdir(fp):
                        os.rmdir(fp)
                        removed += 1
                except: pass
                count += 1
                if count % 10 == 0:
                    self.status.set(f"Analysés: {count} | Supprimés: {removed}")
                    self.update()
        
        self.status.set(f"Terminé! {removed} dossiers vides supprimés.")

def main():
    app = FolderCleanerApp()
    app.mainloop()

if __name__ == "__main__":
    main()