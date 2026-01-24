import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def run(d):
    try:
        entries = os.listdir(d)
        out = os.path.join(d, "Liste.txt")
        with open(out, "w", encoding="utf-8") as f:
            for e in entries: f.write(f"{e}\n")
        messagebox.showinfo("Succès", f"Liste créée: {out}")
    except Exception as e: messagebox.showerror("Err", str(e))

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "Liste Fichiers/Dossiers")
    else: root.title("Liste Fichiers/Dossiers")
    
    root.geometry("500x200")
    
    folder = ctk.StringVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)
    
    ctk.CTkLabel(fr, text="Dossier:").grid(row=0, column=0)
    ctk.CTkEntry(fr, textvariable=folder, width=300).grid(row=0, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: folder.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)
    
    ctk.CTkButton(fr, text="GÉNÉRER", command=lambda: run(folder.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=1, column=1, pady=20)
    
    root.mainloop()

if __name__ == '__main__':
    main()
