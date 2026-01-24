import os
import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def detect(roms_dir):
    art_dir = os.path.join(os.path.dirname(roms_dir), "medium_artwork")
    if not os.path.exists(art_dir): return messagebox.showerror("Err", "medium_artwork not found")

    valid = set()
    for f in os.listdir(roms_dir):
        if os.path.isfile(os.path.join(roms_dir, f)):
            valid.add(os.path.splitext(f)[0].lower())

    count = 0
    for sd in os.listdir(art_dir):
        sdp = os.path.join(art_dir, sd)
        if os.path.isdir(sdp):
            orph_dir = os.path.join(sdp, "orphan")
            os.makedirs(orph_dir, exist_ok=True)
            
            for f in os.listdir(sdp):
                if f == "orphan": continue
                bn = os.path.splitext(f)[0].lower()
                if bn == "default": continue
                
                if bn not in valid:
                    try:
                        shutil.move(os.path.join(sdp, f), orph_dir)
                        count += 1
                    except: pass
    
    messagebox.showinfo("Success", f"{count} orphans moved.")

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "Media Orphan Detector")
    else: root.title("Media Orphan Detector")
    
    root.geometry("500x200")

    var = ctk.StringVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)
    
    ctk.CTkLabel(fr, text="ROMS Dir:").grid(row=0, column=0)
    ctk.CTkEntry(fr, textvariable=var, width=300).grid(row=0, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: var.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)
    
    ctk.CTkButton(fr, text="DETECT ORPHANS", command=lambda: detect(var.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=1, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()