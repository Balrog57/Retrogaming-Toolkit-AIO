import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES

def compress_and_delete_roms(source_dir):
    """
    Compresse tous les fichiers d'un dossier individuellement en ZIP et supprime les originaux.
    
    :param source_dir: Dossier contenant les fichiers à compresser.
    """
    try:
        # Vérifie si le dossier source existe
        if not os.path.exists(source_dir):
            messagebox.showerror("Erreur", f"Le dossier source '{source_dir}' n'existe pas.")
            return

        # Parcourt tous les fichiers dans le dossier source
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)

            # Ignore les dossiers (ne traite que les fichiers)
            if os.path.isfile(file_path):
                # Crée le chemin de l'archive ZIP
                zip_filename = os.path.splitext(filename)[0] + ".zip"
                zip_path = os.path.join(source_dir, zip_filename)

                # Compresse le fichier
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, arcname=filename)
                print(f"Fichier compressé : {zip_filename}")

                # Supprime le fichier d'origine
                os.remove(file_path)
                print(f"Fichier supprimé : {filename}")

        messagebox.showinfo("Succès", "Compression et suppression terminées.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def select_source_dir():
    """Ouvre une boîte de dialogue pour sélectionner le dossier source."""
    folder = filedialog.askdirectory()
    if folder:
        source_dir.set(folder)

def handle_drop(event):
    """Gère le glisser-déposer de fichiers."""
    # Nettoie le chemin en supprimant les accolades
    file_path = event.data.strip().strip("{}")
    if file_path:
        # Récupère le dossier parent du fichier déposé
        source_dir.set(os.path.dirname(file_path))

def start_compression():
    """Lance la compression des fichiers."""
    if not source_dir.get():
        messagebox.showwarning("Attention", "Veuillez sélectionner un dossier source.")
        return
    compress_and_delete_roms(source_dir.get())

# Interface graphique
root = TkinterDnD.Tk()
root.title("Batch Games Converter")
root.geometry("500x300")
root.configure(bg="#0078D7")

# Style pour les boutons et labels
style = ttk.Style()
style.configure("TButton", background="#FFA500", foreground="black", font=("Arial", 10), borderwidth=0)
style.map("TButton", background=[("active", "#FF8C00")])
style.configure("TLabel", background="#0078D7", foreground="white", font=("Arial", 10))

# Variable pour le dossier source
source_dir = tk.StringVar()

# Titre
ttk.Label(root, text="Batch Games Converter", style="TLabel", font=("Arial", 14, "bold")).pack(pady=20)

# Sélection du dossier source
ttk.Label(root, text="Dossier source (Fichiers nes/bin/cue/gdi/iso/chd...) :", style="TLabel").pack(pady=5)
entry = ttk.Entry(root, textvariable=source_dir, width=50)
entry.pack(pady=5)
entry.drop_target_register(DND_FILES)
entry.dnd_bind('<<Drop>>', handle_drop)

ttk.Button(root, text="Parcourir...", command=select_source_dir, style="TButton").pack(pady=10)

# Bouton pour lancer la compression
ttk.Button(root, text="ZIP", command=start_compression, style="TButton").pack(pady=20)

# Lancement de l'interface
root.mainloop()