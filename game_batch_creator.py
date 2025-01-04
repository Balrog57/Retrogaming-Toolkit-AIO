import os
import customtkinter as ctk
from tkinter import messagebox, filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_normal_batch(game_name, game_path, batch_name):
    batch_content = f"""@echo off
set "GAMENAME={game_name}"
set "GAMEPATH={game_path}"
set HOME="%~dp0"
set "GAMEROOT=%~dp0%GAMEPATH%"
cd %GAMEROOT%
start "" /WAIT "%GAMEROOT%%GAMENAME%" -fullscreen
exit
"""
    with open(batch_name, "w") as file:
        file.write(batch_content)
    messagebox.showinfo("Succès", f"Batch pour jeu normal créé : {batch_name}")

def create_steam_batch(steam_id, game_exe, batch_name):
    batch_content = f"""@echo off
START "" "C:\\Program Files (x86)\\Steam\\steam.exe" -silent "steam://rungameid/{steam_id}"
TIMEOUT /T 60
set EXE={game_exe}
:LOOPSTART
TIMEOUT /T 1
FOR /F %%x IN ('tasklist /NH /FI "IMAGENAME eq %EXE%"') DO IF %%x == %EXE% goto FOUND
goto FIN
:FOUND
TIMEOUT /T 1
goto LOOPSTART
:FIN
taskkill /f /im steam.exe
Exit
"""
    with open(batch_name, "w") as file:
        file.write(batch_content)
    messagebox.showinfo("Succès", f"Batch pour jeu Steam créé : {batch_name}")

def create_epic_batch(game_exe, url_file, batch_name):
    batch_content = f"""@echo off
set game={game_exe}

start /wait "" "{url_file}"

timeout /t 15

:WAITLOOP

tasklist /FI "IMAGENAME eq %game%" 2>NUL | find /I /N "%game%">NUL
if "%ERRORLEVEL%"=="0" goto found
goto notfound

:found
timeout /t 5
goto WAITLOOP

:notfound
exit
"""
    with open(batch_name, "w") as file:
        file.write(batch_content)
    messagebox.showinfo("Succès", f"Batch pour jeu Epic créé : {batch_name}")

def main_gui():
    def on_create_normal():
        game_name = entry_game_name.get()
        game_path = entry_game_path.get()
        batch_name = entry_normal_batch_name.get() + ".bat"
        create_normal_batch(game_name, game_path, batch_name)

    def on_create_steam():
        steam_id = entry_steam_id.get()
        game_exe = entry_steam_exe.get()
        batch_name = entry_steam_batch_name.get() + ".bat"
        create_steam_batch(steam_id, game_exe, batch_name)

    def on_create_epic():
        game_exe = entry_epic_exe.get()
        url_file = filedialog.askopenfilename(title="Sélectionnez le fichier .url", filetypes=[("URL Files", "*.url")])
        batch_name = entry_epic_batch_name.get() + ".bat"
        if url_file:
            create_epic_batch(game_exe, url_file, batch_name)

    root = ctk.CTk()
    root.title("Créateur de Batch GUI")

    # Définir une structure principale scrollable
    main_frame = ctk.CTkScrollableFrame(root, width=800, height=900)
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Créer un Batch pour un Jeu Normal", font=("Arial", 16)).pack(pady=10)
    ctk.CTkLabel(main_frame, text="Nom du fichier batch").pack(pady=5)
    entry_normal_batch_name = ctk.CTkEntry(main_frame, placeholder_text="Ex: MonJeuNormal", width=400)
    entry_normal_batch_name.pack(pady=5)
    ctk.CTkLabel(main_frame, text="Nom de l'exécutable (Normal)").pack(pady=5)
    entry_game_name = ctk.CTkEntry(main_frame, placeholder_text="Ex: LEGOJurassicWorld.exe", width=400)
    entry_game_name.pack(pady=5)
    ctk.CTkLabel(main_frame, text="Chemin du jeu (Normal)").pack(pady=5)
    entry_game_path = ctk.CTkEntry(main_frame, placeholder_text="Ex: \\LEGO Jurassic World\\", width=400)
    entry_game_path.pack(pady=5)
    ctk.CTkButton(main_frame, text="Créer Batch Normal", command=on_create_normal, width=200).pack(pady=20)

    ctk.CTkLabel(main_frame, text="Créer un Batch pour un Jeu Steam", font=("Arial", 16)).pack(pady=10)
    ctk.CTkLabel(main_frame, text="Nom du fichier batch").pack(pady=5)
    entry_steam_batch_name = ctk.CTkEntry(main_frame, placeholder_text="Ex: MonJeuSteam", width=400)
    entry_steam_batch_name.pack(pady=5)
    ctk.CTkLabel(main_frame, text="ID Steam").pack(pady=5)
    entry_steam_id = ctk.CTkEntry(main_frame, placeholder_text="Ex: 271590", width=400)
    entry_steam_id.pack(pady=5)
    ctk.CTkLabel(main_frame, text="Nom de l'exécutable (Steam)").pack(pady=5)
    entry_steam_exe = ctk.CTkEntry(main_frame, placeholder_text="Ex: GTA5.exe", width=400)
    entry_steam_exe.pack(pady=5)
    ctk.CTkButton(main_frame, text="Créer Batch Steam", command=on_create_steam, width=200).pack(pady=20)

    ctk.CTkLabel(main_frame, text="Créer un Batch pour un Jeu Epic", font=("Arial", 16)).pack(pady=10)
    ctk.CTkLabel(main_frame, text="Nom du fichier batch").pack(pady=5)
    entry_epic_batch_name = ctk.CTkEntry(main_frame, placeholder_text="Ex: MonJeuEpic", width=400)
    entry_epic_batch_name.pack(pady=5)
    ctk.CTkLabel(main_frame, text="Nom de l'exécutable (Epic)").pack(pady=5)
    entry_epic_exe = ctk.CTkEntry(main_frame, placeholder_text="Ex: shapezio.exe", width=400)
    entry_epic_exe.pack(pady=5)
    ctk.CTkButton(main_frame, text="Créer Batch Epic", command=on_create_epic, width=200).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
