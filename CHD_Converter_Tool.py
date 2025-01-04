import os
import subprocess
import multiprocessing
import urllib.request
import shutil
import zipfile
import rarfile
import py7zr
from tkinter import Tk, filedialog, Button, Label, Entry, StringVar, IntVar, messagebox, Frame, Radiobutton
from tkinter.ttk import Combobox

CHDMAN_URL = "https://wiki.recalbox.com/tutorials/utilities/rom-conversion/chdman/chdman.zip"
CHDMAN_ZIP = "chdman.zip"
CHDMAN_EXE = "chdman.exe"

class CHDmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CHD_Converter_Tool par Balrog")
        self.root.geometry("600x300")

        # Variables pour les dossiers source et destination
        self.source_folder = StringVar()
        self.destination_folder = StringVar()
        self.num_cores = IntVar(value=1)  # Par défaut, 1 cœur
        self.option = StringVar(value="Info")  # Par défaut : "Info"

        # Détecter le nombre de cœurs disponibles sur le système
        self.available_cores = list(range(1, multiprocessing.cpu_count() + 1))

        # Créer des cadres
        top_frame = Frame(root)
        top_frame.pack(pady=5)

        middle_frame = Frame(root)
        middle_frame.pack(pady=5)

        bottom_frame = Frame(root)
        bottom_frame.pack(pady=10)

        # Cadre supérieur : Dossiers source et destination
        Label(top_frame, text="Dossier Source :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        Entry(top_frame, textvariable=self.source_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        Button(top_frame, text="...", command=self.parcourir_dossier_source).grid(row=0, column=2, padx=5, pady=5)

        Label(top_frame, text="Dossier Destination :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        Entry(top_frame, textvariable=self.destination_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        Button(top_frame, text="...", command=self.parcourir_dossier_destination).grid(row=1, column=2, padx=5, pady=5)

        Button(top_frame, text="Inverser", command=self.inverser_dossiers).grid(row=2, column=1, pady=10)

        # Cadre du milieu : Options et sélection des cœurs
        Label(middle_frame, text="Options :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Radiobutton(middle_frame, text="Info", variable=self.option, value="Info").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Radiobutton(middle_frame, text="Vérifier", variable=self.option, value="Verify").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        Radiobutton(middle_frame, text="Convertir", variable=self.option, value="Convert").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        Radiobutton(middle_frame, text="Extraire", variable=self.option, value="Extract").grid(row=0, column=4, padx=5, pady=5, sticky="w")

        Label(middle_frame, text="Cœurs :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        Combobox(middle_frame, textvariable=self.num_cores, values=self.available_cores, state="readonly", width=5).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Cadre inférieur : Bouton Exécuter
        Button(bottom_frame, text="Exécuter", command=self.executer_operation, width=20).pack(pady=10)

        self.verifier_chdman()

    def parcourir_dossier_source(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)

    def parcourir_dossier_destination(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier destination")
        if folder:
            self.destination_folder.set(folder)

    def inverser_dossiers(self):
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        self.source_folder.set(destination)
        self.destination_folder.set(source)

    def verifier_chdman(self):
        """Vérifie si chdman.exe est disponible ; télécharge-le si nécessaire."""
        if not os.path.exists(CHDMAN_EXE):
            answer = messagebox.askyesno("CHDman manquant", f"CHDman est introuvable. Voulez-vous le télécharger ?\n{CHDMAN_URL}")
            if answer:
                self.telecharger_chdman()
            else:
                messagebox.showerror("Erreur", "CHDman est requis pour utiliser cet outil.")
                self.root.quit()

    def telecharger_chdman(self):
        """Télécharge et extrait CHDman."""
        try:
            urllib.request.urlretrieve(CHDMAN_URL, CHDMAN_ZIP)
            subprocess.run(["unzip", CHDMAN_ZIP], check=True)
            os.remove(CHDMAN_ZIP)
            messagebox.showinfo("Téléchargement terminé", "CHDman a été téléchargé et extrait avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec du téléchargement de CHDman : {e}")
            self.root.quit()

    def extraire_archives(self, dossier):
        """Extrait les archives ZIP, RAR et 7z dans le dossier."""
        for file in os.listdir(dossier):
            file_path = os.path.join(dossier, file)
            if file.lower().endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(dossier)
            elif file.lower().endswith(".rar"):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(dossier)
            elif file.lower().endswith(".7z"):
                with py7zr.SevenZipFile(file_path, 'r') as sevenz_ref:
                    sevenz_ref.extractall(dossier)

    def executer_chdman(self, commande, fichier_entree=None, fichier_sortie=None):
        """Exécute une commande CHDman."""
        if not os.path.exists(CHDMAN_EXE):
            self.verifier_chdman()

        cmd = [CHDMAN_EXE] + commande
        if fichier_entree:
            cmd += ["-i", fichier_entree]
        if fichier_sortie:
            cmd += ["-o", fichier_sortie]

        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Succès", f"Commande exécutée avec succès :\n{' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erreur", f"Échec de l'exécution de la commande :\n{e}")

    def executer_operation(self):
        """Exécute l'opération sélectionnée."""
        source = self.source_folder.get()
        destination = self.destination_folder.get()
        if not source or not destination:
            messagebox.showerror("Erreur", "Les dossiers source et destination doivent être sélectionnés.")
            return

        # Extraire les archives avant de continuer
        self.extraire_archives(source)

        if self.option.get() == "Info":
            for file in self.obtenir_fichiers(source, (".chd",)):
                self.executer_chdman(["info"], fichier_entree=file)
        elif self.option.get() == "Verify":
            for file in self.obtenir_fichiers(source, (".chd",)):
                self.executer_chdman(["verify"], fichier_entree=file)
        elif self.option.get() == "Convert":
            for file in self.obtenir_fichiers(source, (".cue", ".gdi", ".iso")):
                fichier_sortie = os.path.join(destination, os.path.splitext(os.path.basename(file))[0] + ".chd")
                self.executer_chdman(["createcd", "--numprocessors", str(self.num_cores.get())], fichier_entree=file, fichier_sortie=fichier_sortie)
        elif self.option.get() == "Extract":
            for file in self.obtenir_fichiers(source, (".chd",)):
                fichier_sortie = os.path.join(destination, os.path.splitext(os.path.basename(file))[0] + ".cue")
                self.executer_chdman(["extractcd"], fichier_entree=file, fichier_sortie=fichier_sortie)

    def obtenir_fichiers(self, dossier, extensions):
        """Récupère les fichiers avec des extensions spécifiées."""
        for file in os.listdir(dossier):
            if file.lower().endswith(extensions):
                yield os.path.join(dossier, file)

# Exécuter l'interface utilisateur
if __name__ == "__main__":
    root = Tk()
    app = CHDmanGUI(root)
    root.mainloop()
