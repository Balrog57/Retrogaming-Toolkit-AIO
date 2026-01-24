import os
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def create_normal_batch(gn, gp, bn):
    content = f"""@echo off
set "GAMENAME={gn}"
set "GAMEPATH={gp}"
set "GAMEROOT=%~dp0%GAMEPATH%\"
cd /d "%GAMEROOT%"
start "" /WAIT "%GAMEROOT%%GAMENAME%" -fullscreen
exit
"""
    with open(bn, "w") as f: f.write(content)
    messagebox.showinfo("OK", f"Batch créé: {bn}")

def create_steam_batch(sid, exe, bn):
    content = f"""@echo off
START "" "C:\\Program Files (x86)\\Steam\\steam.exe" -silent "steam://rungameid/{sid}"
TIMEOUT /T 5
set EXE={exe}
:LOOP
TIMEOUT /T 2
tasklist /FI "IMAGENAME eq %EXE%" 2>NUL | find /I /N "%EXE%">NUL
if "%ERRORLEVEL%"=="0" goto FOUND
goto LOOP
:FOUND
:WAIT
TIMEOUT /T 2
tasklist /FI "IMAGENAME eq %EXE%" 2>NUL | find /I /N "%EXE%">NUL
if "%ERRORLEVEL%"=="0" goto WAIT
taskkill /f /im steam.exe
exit
"""
    with open(bn, "w") as f: f.write(content)
    messagebox.showinfo("OK", f"Steam Batch créé: {bn}")

def create_epic_batch(exe, url, bn):
    content = f"""@echo off
start /wait "" "{url}"
timeout /t 10
set game={exe}
:WAIT
timeout /t 2
tasklist /FI "IMAGENAME eq %game%" 2>NUL | find /I /N "%game%">NUL
if "%ERRORLEVEL%"=="0" goto WAIT
exit
"""
    with open(bn, "w") as f: f.write(content)
    messagebox.showinfo("OK", f"Epic Batch créé: {bn}")

def main():
    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Créateur de Batch GUI")
        acc = theme.COLOR_ACCENT_PRIMARY
    else:
        root.title("Créateur de Batch GUI")
        acc = "#1f6aa5"
        
    root.geometry("1000x800")

    dest_var = ctk.StringVar()

    def get_path(vn):
        d = dest_var.get() or os.getcwd()
        n = vn.get().strip()
        if not n: return None
        if not n.endswith('.bat'): n += '.bat'
        return os.path.join(d, n)

    sf = ctk.CTkScrollableFrame(root)
    sf.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Dest
    ctk.CTkLabel(sf, text="Dossier Destination (Opt)", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=10)
    ctk.CTkButton(sf, text="Choisir Dossier", command=lambda: dest_var.set(filedialog.askdirectory()), width=200, fg_color=acc).pack(pady=5)
    ctk.CTkLabel(sf, text="-"*50).pack(pady=10)

    # Normal
    ctk.CTkLabel(sf, text="Jeu Normal (EXE)", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=10)
    nbn = ctk.CTkEntry(sf, placeholder_text="Nom Batch", width=300); nbn.pack(pady=2)
    ngn = ctk.CTkEntry(sf, placeholder_text="Nom EXE (ex: game.exe)", width=300); ngn.pack(pady=2)
    ngp = ctk.CTkEntry(sf, placeholder_text="Chemin Relatif (ex: \\GameFolder\\)", width=300); ngp.pack(pady=2)
    
    def do_norm():
        bp = get_path(nbn)
        if bp and ngn.get() and ngp.get(): create_normal_batch(ngn.get(), ngp.get(), bp)
        else: messagebox.showerror("Err", "Champs manquants")
    
    ctk.CTkButton(sf, text="Créer Batch Normal", command=do_norm, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)
    ctk.CTkLabel(sf, text="-"*50).pack(pady=10)

    # Steam
    ctk.CTkLabel(sf, text="Jeu Steam", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=10)
    sbn = ctk.CTkEntry(sf, placeholder_text="Nom Batch", width=300); sbn.pack(pady=2)
    sid = ctk.CTkEntry(sf, placeholder_text="Steam ID", width=300); sid.pack(pady=2)
    sexe = ctk.CTkEntry(sf, placeholder_text="Nom EXE à surveiller", width=300); sexe.pack(pady=2)

    def do_steam():
        bp = get_path(sbn)
        if bp and sid.get() and sexe.get(): create_steam_batch(sid.get(), sexe.get(), bp)
        else: messagebox.showerror("Err", "Champs manquants")
        
    ctk.CTkButton(sf, text="Créer Batch Steam", command=do_steam, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)
    ctk.CTkLabel(sf, text="-"*50).pack(pady=10)

    # Epic
    ctk.CTkLabel(sf, text="Jeu Epic", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=10)
    ebn = ctk.CTkEntry(sf, placeholder_text="Nom Batch", width=300); ebn.pack(pady=2)
    eexe = ctk.CTkEntry(sf, placeholder_text="Nom EXE à surveiller", width=300); eexe.pack(pady=2)
    
    def do_epic():
        bp = get_path(ebn)
        if bp and eexe.get():
            u = filedialog.askopenfilename(filetypes=[("URL", "*.url")])
            if u: create_epic_batch(eexe.get(), u, bp)
        else: messagebox.showerror("Err", "Champs manquants")

    ctk.CTkButton(sf, text="Créer Batch Epic", command=do_epic, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()