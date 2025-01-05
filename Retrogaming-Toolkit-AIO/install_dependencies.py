import os
import platform
import subprocess
import customtkinter as ctk
from tkinter import messagebox

# Configuration de l'apparence et du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def is_64bit():
    """Detect if the system is 64-bit."""
    return platform.architecture()[0] == "64bit"

def run_installer(file, args=""):
    """Run an installer file with optional arguments in a separate process."""
    try:
        print(f"Running {file}...")
        command = f'"{file}" {args}'
        process = subprocess.Popen(command, shell=True)
        process.wait()
        if process.returncode == 0:
            print(f"{file} installed successfully.")
            return True
        else:
            print(f"Failed to install {file}.")
            return False
    except Exception as e:
        print(f"Error running {file}: {e}")
        return False

def install_dependencies():
    """Install all dependencies."""
    # Chemin vers le dossier des dépendances
    deps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_dependencies")
    
    if not os.path.exists(deps_dir):
        messagebox.showerror("Erreur", f"Le dossier des dépendances n'existe pas: {deps_dir}")
        return

    # Define the installers
    installers = {
        "vcredist2005_x86.exe": "/q",
        "vcredist2008_x86.exe": "/qb",
        "vcredist2010_x86.exe": "/passive /norestart",
        "vcredist2012_x86.exe": "/passive /norestart",
        "vcredist2013_x86.exe": "/passive /norestart",
        "vcredist2015_2017_2019_2022_x86.exe": "/passive /norestart",
        "dxsetup.exe": "/silent",
        "oalinst.exe": "/silent",
    }

    if is_64bit():
        installers.update({
            "vcredist2005_x64.exe": "/q",
            "vcredist2008_x64.exe": "/qb",
            "vcredist2010_x64.exe": "/passive /norestart",
            "vcredist2012_x64.exe": "/passive /norestart",
            "vcredist2013_x64.exe": "/passive /norestart",
            "vcredist2015_2017_2019_2022_x64.exe": "/passive /norestart",
        })

    # Demander confirmation
    confirm = messagebox.askyesno("Confirmation", "Voulez-vous lancer l'installation des dépendances ?")
    if not confirm:
        print("Installation annulée par l'utilisateur.")
        return

    # Install all runtimes
    success = True
    for file, args in installers.items():
        file_path = os.path.join(deps_dir, file)
        if os.path.exists(file_path):
            if not run_installer(file_path, args):
                success = False
        else:
            print(f"{file} not found in {deps_dir}. Skipping...")
            success = False

    if success:
        messagebox.showinfo("Succès", "Toutes les installations ont été terminées avec succès.")
    else:
        messagebox.showwarning("Avertissement", "Certaines installations ont échoué ou des fichiers sont manquants.")

def main():
    # Création de la fenêtre principale avec customtkinter
    root = ctk.CTk()
    root.title("Installation des dépendances")

    # Interface utilisateur
    label = ctk.CTkLabel(root, text="Cliquez sur le bouton pour installer les dépendances :", font=("Arial", 16))
    label.pack(pady=10)

    install_button = ctk.CTkButton(root, text="Installer les dépendances", command=install_dependencies, width=200)
    install_button.pack(pady=10)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == "__main__":
    main()
