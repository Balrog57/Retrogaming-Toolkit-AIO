import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def is_64bit():
    """Detect if the system is 64-bit."""
    return platform.architecture()[0] == "64bit"

def run_installer(file, args=""):
    """Run an installer file with optional arguments."""
    try:
        print(f"Running {file}...")
        subprocess.run(f"{file} {args}", check=True, shell=True)
        print(f"{file} installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {file}: {e}")
        return False

def install_dependencies():
    # Chemin relatif vers le sous-dossier "install_dependencies"
    install_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_dependencies")

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

    # Demander confirmation avant de lancer les installations
    confirm = messagebox.askyesno("Confirmation", "Voulez-vous lancer l'installation des dépendances ?")
    if not confirm:
        print("Installation annulée par l'utilisateur.")
        return

    # Install all runtimes
    success = True
    for file, args in installers.items():
        file_path = os.path.join(install_dir, file)
        if os.path.exists(file_path):
            if not run_installer(file_path, args):
                success = False
        else:
            print(f"{file} not found in {install_dir}. Skipping...")
            success = False

    if success:
        messagebox.showinfo("Succès", "Toutes les installations ont été terminées avec succès.")
    else:
        messagebox.showwarning("Avertissement", "Certaines installations ont échoué ou des fichiers sont manquants.")

def main():
    # Création de la fenêtre principale
    root = tk.Tk()
    root.title("Installation des dépendances")

    # Interface utilisateur
    tk.Label(root, text="Cliquez sur le bouton pour installer les dépendances :").pack(pady=10)
    tk.Button(root, text="Installer les dépendances", command=install_dependencies).pack(pady=20)

    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()

if __name__ == "__main__":
    main()