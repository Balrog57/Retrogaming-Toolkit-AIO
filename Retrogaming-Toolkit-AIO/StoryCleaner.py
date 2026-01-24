import os
import unicodedata
import customtkinter as ctk
from tkinter import messagebox, filedialog

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def clean_text(text):
    norm = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    repl = {'œ':'oe', 'Œ':'OE', 'æ':'ae', 'Æ':'AE', 'ç':'c', 'Ç':'C', '&':'&amp;'}
    for k,v in repl.items(): norm = norm.replace(k,v)
    return norm

def process_dir(d, sub):
    if not os.path.exists(d): return messagebox.showerror("Err", "Dossier introuvable")
    
    count = 0
    for root, _, files in os.walk(d):
        if not sub and root != d: continue
        for f in files:
            if f.endswith('.txt'):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8') as file: content = file.read()
                    new_content = clean_text(content)
                    with open(fp, 'w', encoding='utf-8') as file: file.write(new_content)
                    count += 1
                except Exception as e: print(f"Err {f}: {e}")
    
    messagebox.showinfo("Succès", f"{count} fichiers traités.")

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "Story Format Cleaner")
    else: root.title("Story Format Cleaner")
    
    root.geometry("500x250")
    
    d_var = ctk.StringVar()
    sub_var = ctk.BooleanVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)
    
    ctk.CTkLabel(fr, text="Dossier:").grid(row=0, column=0)
    ctk.CTkEntry(fr, textvariable=d_var, width=300).grid(row=0, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: d_var.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)
    
    ctk.CTkCheckBox(fr, text="Sous-dossiers", variable=sub_var).grid(row=1, column=1, pady=10)
    
    ctk.CTkButton(fr, text="NORMALISER", command=lambda: process_dir(d_var.get(), sub_var.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=2, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()