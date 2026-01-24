import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

class EmptyFileCreatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Empty File Creator")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
        else:
            self.title("Empty File Creator")
            self.geometry("600x400")
            self.COLOR_ACCENT = "#1f6aa5"

        self.folder_path = None
        self.selected_extension = ctk.StringVar(value="scummvm")
        
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main, text="Empty File Creator", font=theme.get_font_title(20) if theme else ("Arial", 20)).pack(pady=10)
        
        # Ext Frame
        ext_fr = ctk.CTkFrame(main, fg_color=theme.COLOR_CARD_BG if theme else None)
        ext_fr.pack(pady=10, fill="x")
        
        ctk.CTkLabel(ext_fr, text="Extension:", font=theme.get_font_title(14) if theme else None).pack(pady=5)
        
        for ext in ["scummvm", "singe", "cgenius", "autre"]:
             ctk.CTkRadioButton(ext_fr, text=f".{ext}" if ext != "autre" else "Autre", 
                                variable=self.selected_extension, value=ext, fg_color=self.COLOR_ACCENT).pack(pady=5)

        self.custom_entry = ctk.CTkEntry(ext_fr, placeholder_text="Ex: mp4")
        self.selected_extension.trace_add("write", self.on_ext_change)

        ctk.CTkButton(main, text="Choisir Dossier", command=self.choose_folder, fg_color=self.COLOR_ACCENT).pack(pady=10)
        ctk.CTkButton(main, text="CRÉER FICHIERS", command=self.create_files, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

    def on_ext_change(self, *args):
        if self.selected_extension.get() == "autre": self.custom_entry.pack(pady=5)
        else: self.custom_entry.pack_forget()

    def choose_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path: messagebox.showinfo("Info", f"Sel: {self.folder_path}")

    def create_files(self):
        if not self.folder_path: return messagebox.showerror("Err", "Dossier requis")
        
        ext = self.selected_extension.get()
        if ext == "autre":
            ext = self.custom_entry.get().strip()
            if not ext: return messagebox.showerror("Err", "Ext requise")
        
        count = 0
        for name in os.listdir(self.folder_path):
            full = os.path.join(self.folder_path, name)
            if os.path.isdir(full):
                fp = os.path.join(full, f"{name}.{ext}")
                with open(fp, 'w'): pass
                count += 1
        
        messagebox.showinfo("Succès", f"{count} fichiers .{ext} créés.")

def main():
    app = EmptyFileCreatorApp()
    app.mainloop()

if __name__ == "__main__":
    main()