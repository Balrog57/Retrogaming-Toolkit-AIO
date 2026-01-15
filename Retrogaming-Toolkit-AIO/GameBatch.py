import os
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Fonction pour créer un fichier batch pour un jeu normal
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

# Fonction pour créer un fichier batch pour un jeu Steam
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

# Fonction pour créer un fichier batch pour un jeu Epic
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
    try:
        with open(batch_name, "w") as file:
            file.write(batch_content)
        messagebox.showinfo("Succès", f"Batch pour jeu Epic créé : {batch_name}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de créer le fichier batch : {e}")

# Fonction principale pour l'interface graphique
def main_gui():
    try:
        # Création de la fenêtre principale (Doit être fait en premier pour les StringVars)
        root = ctk.CTk()
        root.title("Créateur de Batch GUI")
        root.geometry("800x600")

        # Variable globale pour le dossier de destination
        dest_folder_var = ctk.StringVar(value="")

        def select_dest_folder():
            folder = filedialog.askdirectory(title="Choisir le dossier de destination")
            if folder:
                dest_folder_var.set(folder)
                btn_dest.configure(text=f"Dossier: {os.path.basename(folder)}")

        def get_full_batch_path(batch_name):
            folder = dest_folder_var.get()
            if not folder:
                folder = os.getcwd() # Default to current dir if not selected
            
            if not batch_name.endswith('.bat'):
                batch_name += '.bat'
            
            return os.path.join(folder, batch_name)

        def on_create_normal():
            batch_name = entry_normal_batch_name.get().strip()
            game_name = entry_game_name.get().strip()
            game_path = entry_game_path.get().strip()
            
            if not all([batch_name, game_name, game_path]):
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
                return
                
            full_path = get_full_batch_path(batch_name)
            create_normal_batch(game_name, game_path, full_path)

        def on_create_steam():
            batch_name = entry_steam_batch_name.get().strip()
            steam_id = entry_steam_id.get().strip()
            steam_exe = entry_steam_exe.get().strip()
            
            if not all([batch_name, steam_id, steam_exe]):
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
                return
                
            full_path = get_full_batch_path(batch_name)
            create_steam_batch(steam_id, steam_exe, full_path)

        def on_create_epic():
            batch_name = entry_epic_batch_name.get().strip()
            epic_exe = entry_epic_exe.get().strip()
            
            if not all([batch_name, epic_exe]):
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
                return
            
            url_file = filedialog.askopenfilename(
                title="Sélectionner le fichier URL Epic",
                filetypes=[("Fichiers URL", "*.url")]
            )
            if not url_file:
                return
                
            full_path = get_full_batch_path(batch_name)
            create_epic_batch(epic_exe, url_file, full_path)

        def on_closing():
            try:
                root.quit()
                root.destroy()
                sys.exit(0)
            except Exception as e:
                print(f"Erreur lors de la fermeture: {str(e)}")
                sys.exit(1)

        root.protocol("WM_DELETE_WINDOW", on_closing)  # Gestionnaire de fermeture

        # Cadre principal scrollable
        main_frame = ctk.CTkScrollableFrame(root, width=800, height=900)
        main_frame.pack(fill="both", expand=True)

        # Destination Folder Selection
        ctk.CTkLabel(main_frame, text="Dossier de Destination (Optionnel)", font=("Arial", 16)).pack(pady=10)
        btn_dest = ctk.CTkButton(main_frame, text="Choisir le dossier de destination", command=select_dest_folder, width=300)
        btn_dest.pack(pady=5)
        # Separator (simulated with empty label)
        ctk.CTkLabel(main_frame, text="------------------------------------------------", text_color="gray").pack(pady=5)

        # Section pour les jeux normaux
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

        # Section pour les jeux Steam
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

        # Section pour les jeux Epic
        ctk.CTkLabel(main_frame, text="Créer un Batch pour un Jeu Epic", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(main_frame, text="Nom du fichier batch").pack(pady=5)
        entry_epic_batch_name = ctk.CTkEntry(main_frame, placeholder_text="Ex: MonJeuEpic", width=400)
        entry_epic_batch_name.pack(pady=5)
        ctk.CTkLabel(main_frame, text="Nom de l'exécutable (Epic)").pack(pady=5)
        entry_epic_exe = ctk.CTkEntry(main_frame, placeholder_text="Ex: shapezio.exe", width=400)
        entry_epic_exe.pack(pady=5)
        ctk.CTkButton(main_frame, text="Créer Batch Epic", command=on_create_epic, width=200).pack(pady=20)

        # Lancement de la boucle principale de l'interface graphique
        root.mainloop()

    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")
        sys.exit(1)

def main():
    try:
        # Configuration de l'apparence de l'interface graphique
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        main_gui()
    except Exception as e:
        print(f"Erreur dans main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()