import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

def supprimer_dossiers_vides(chemin, progress_var):
    """
    Supprime récursivement tous les dossiers vides dans un répertoire donné.
    Affiche une progression indéterminée (nombre de dossiers traités) pour éviter un double parcours coûteux.

    Args:
        chemin (str): Le chemin d'accès au répertoire à analyser.
        progress_var (tk.StringVar): Variable pour stocker le statut de progression.
    """
    try:
        elements_traites = 0

        # On supprime le calcul préalable de total_elements (os.walk initial) qui doublait le temps d'exécution.
        # On parcourt directement en mode bottom-up (topdown=False) pour supprimer les dossiers devenus vides.
        
        for root, dirs, _ in os.walk(chemin, topdown=False):
            for dir in dirs:
                chemin_element = os.path.join(root, dir)
                try:
                    # check if dir is empty
                    if not os.listdir(chemin_element):
                        os.rmdir(chemin_element)
                        print(f"Dossier vide supprimé: {chemin_element}")
                except OSError as e:
                    print(f"Erreur lors de la suppression de {chemin_element}: {e}")
                finally:
                    elements_traites += 1
                    # Optimisation: Mise à jour de l'interface graphique tous les 10 éléments seulement
                    if elements_traites % 10 == 0:
                        progress_var.set(f"Dossiers traités: {elements_traites}")
                        fenetre.update_idletasks()
        
        # Mise à jour finale
        progress_var.set(f"Terminé. {elements_traites} dossiers analysés.")
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

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    global fenetre, entry_chemin, label_progression
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

    fenetre.mainloop()

if __name__ == "__main__":
    main()