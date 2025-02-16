import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

def supprimer_dossiers_vides(chemin, progress_var):
    """
    Supprime récursivement tous les dossiers vides dans un répertoire donné et met à jour le pourcentage de progression.

    Args:
        chemin (str): Le chemin d'accès au répertoire à analyser.
        progress_var (tk.StringVar): Variable pour stocker le pourcentage de progression.
    """
    try:
        total_elements = sum([len(dirs) for _, dirs, _ in os.walk(chemin)])
        elements_traites = 0

        if total_elements == 0:
            print("Le répertoire est vide ou ne contient pas de sous-dossiers.")
            progress_var.set("Progression: 100%")
            return

        for root, dirs, _ in os.walk(chemin, topdown=False):
            for dir in dirs:
                chemin_element = os.path.join(root, dir)
                try:
                    if not os.listdir(chemin_element):
                        os.rmdir(chemin_element)
                        print(f"Dossier vide supprimé: {chemin_element}")
                except OSError as e:
                    print(f"Erreur lors de la suppression de {chemin_element}: {e}")
                finally:
                    elements_traites += 1
                    pourcentage = elements_traites / total_elements * 100
                    progress_var.set(f"Progression: {pourcentage:.1f}%")
                    fenetre.update_idletasks()
    except Exception as e:
        print(f"Erreur lors du traitement du répertoire: {e}")
        progress_var.set(f"Erreur: {e}")

def parcourir_repertoire():
    """
    Ouvre une boîte de dialogue pour sélectionner un répertoire et affiche le chemin dans le champ de saisie.
    """
    repertoire = filedialog.askdirectory()
    if repertoire:
        entry_chemin.delete(0, tk.END)
        entry_chemin.insert(0, repertoire)

def parcourir_et_supprimer():
    """
    Récupère le chemin du répertoire, vérifie s'il est valide, et lance la suppression des dossiers vides.
    """
    chemin_repertoire = entry_chemin.get()
    if not chemin_repertoire:
        print("Veuillez sélectionner un répertoire.")
        return
    progress_var = tk.StringVar(value="Progression: 0%")
    label_progression.pack(padx=20, pady=10)
    supprimer_dossiers_vides(chemin_repertoire, progress_var)
    label_progression.pack_forget()

# GUI avec customtkinter
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

fenetre = ctk.CTk()
fenetre.title("Supprimer Dossiers Vides")

label_chemin = ctk.CTkLabel(fenetre, text="Chemin du répertoire:")
label_chemin.pack(padx=20, pady=20)

entry_chemin = ctk.CTkEntry(fenetre)
entry_chemin.pack(padx=20, pady=10)

bouton_parcourir = ctk.CTkButton(fenetre, text="Parcourir", command=parcourir_repertoire)
bouton_parcourir.pack(padx=20, pady=10)

bouton_supprimer = ctk.CTkButton(fenetre, text="Supprimer", command=parcourir_et_supprimer)
bouton_supprimer.pack(padx=20, pady=10)

label_progression = ctk.CTkLabel(fenetre, textvariable="")

if __name__ == "__main__":
    fenetre.mainloop()