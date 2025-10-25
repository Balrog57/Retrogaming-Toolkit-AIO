#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface graphique (GUI) pour yt-dlp.

Ce script vérifie et installe les dépendances requises :
- customtkinter (pour l'interface)
- yt-dlp (pour le téléchargement)
- imageio-ffmpeg (pour ffmpeg)
"""

# --- VÉRIFICATION ET INSTALLATION DES DÉPENDANCES ---
import sys
import os
import subprocess
import importlib
import traceback
import threading
import json
import re # <-- AJOUT : Importation du module Regex
from tkinter import filedialog, messagebox, StringVar, BooleanVar

def install_package(package):
    """Installe un package pip."""
    print(f"Tentative d'installation de {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"Installation de {package} réussie.")
    except subprocess.CalledProcessError as e:
        print(f"ERREUR: La commande pip a échoué pour {package}. {e}", file=sys.stderr)
        print(f"Veuillez l'installer manuellement : pip install {package}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
         print(f"ERREUR: Commande 'pip' non trouvée. Assurez-vous que Python et pip sont installés et dans le PATH.", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"ERREUR INATTENDUE lors de l'installation de {package}:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

def check_and_import(package_name, import_name=None):
    """
    Vérifie si un package est installé, sinon l'installe, puis l'importe
    et retourne le module.
    """
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    print(f"Vérification de '{package_name}' (import as '{import_name}')...")
    
    try:
        module = importlib.import_module(import_name)
        print(f"'{package_name}' est déjà installé.")
        return module
    except ImportError:
        print(f"Dépendance '{package_name}' non trouvée.")
        install_package(package_name)
        try:
            importlib.invalidate_caches()
            module = importlib.import_module(import_name)
            print(f"Importation de '{package_name}' réussie après installation.")
            return module
        except ImportError:
            print(f"ERREUR: Impossible d'importer {package_name} même après l'installation.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERREUR INATTENDUE lors de l'importation de {package_name} après installation:", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print(f"ERREUR INATTENDUE lors de la vérification de {package_name}:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

# --- Bootstrap : Vérifie et importe les dépendances avant tout ---
print("--- Début du script : Vérification des dépendances ---")

try:
    print("\n[Étape 1/3] Vérification de customtkinter...")
    ctk = check_and_import("customtkinter")
    
    print("\n[Étape 2/3] Vérification de yt-dlp...")
    yt_dlp = check_and_import("yt-dlp", "yt_dlp")
    
    print("\n[Étape 3/3] Vérification de imageio-ffmpeg...")
    imageio_ffmpeg = check_and_import("imageio-ffmpeg", "imageio_ffmpeg")
    
    print("\n--- Dépendances vérifiées avec succès ---")

except Exception as e:
    print("\n--- ERREUR FATALE LORS DU BOOTSTRAP ---", file=sys.stderr)
    print(f"Le script n'a pas pu initialiser les dépendances.", file=sys.stderr)
    traceback.print_exc()
    # Affiche une boîte de dialogue d'erreur si tkinter est au moins disponible
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erreur de dépendance", f"Le script n'a pas pu démarrer:\n{e}\n\nConsultez le terminal pour plus de détails.")
    except:
        pass # Ne peut rien faire si tkinter échoue aussi
    sys.exit(1)

# --- Fin de la section dépendances ---

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YtdlpLogger:
    """
    Logger pour capturer les messages de yt-dlp et les
    afficher dans la console (ou un widget de log futur).
    """
    def __init__(self, gui_instance):
        self.gui = gui_instance

    def debug(self, msg):
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        # Affiche les messages qui ne sont pas des indicateurs de progression
        if not msg.startswith('[download]'):
            print(f"[INFO] {msg}")

    def warning(self, msg):
        print(f"[ATTENTION] {msg}", file=sys.stderr)

    def error(self, msg):
        print(f"[ERREUR] {msg}", file=sys.stderr)

class YtDlpGui(ctk.CTk):
    def __init__(self, yt_dlp_module, ffmpeg_module):
        super().__init__()
        
        # Stocker les modules importés
        self.yt_dlp = yt_dlp_module
        self.ffmpeg_path = ffmpeg_module.get_ffmpeg_exe()

        # Configuration de la fenêtre principale
        self.title("YT Downloader Pro (yt-dlp)")
        # SUPPRESSION de la géométrie fixe pour laisser la fenêtre s'adapter au contenu
        # self.geometry("600x550") 
        self.resizable(False, False)

        # Variables globales
        self.destination_folder = StringVar(value=os.getcwd())
        self.audio_only = BooleanVar(value=False)
        # NOUVELLES options
        self.no_playlist = BooleanVar(value=False)
        self.quality = StringVar(value='Source (Best)') # Qualité par défaut
        self.codec = StringVar(value='Copier la vidéo (Rapide)') # <-- NOUVEAU : Codec par défaut

        # --- SUPPRESSION DES ONGLETS ---
        # Les widgets d'URL et de Destination sont ajoutés directement à la fenêtre principale
        
        ctk.CTkLabel(self, text="URL (Vidéo, Playlist ou Chaîne) :", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w", padx=10)
        self.url_entry = ctk.CTkEntry(self, width=580) # Largeur ajustée
        self.url_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self, text="Dossier de destination :", font=ctk.CTkFont(weight="bold")).pack(pady=5, anchor="w", padx=10)
        dest_frame = ctk.CTkFrame(self)
        dest_frame.pack(fill="x", padx=10)
        
        self.destination_entry = ctk.CTkEntry(dest_frame, textvariable=self.destination_folder, width=400)
        self.destination_entry.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10))
        ctk.CTkButton(dest_frame, text="Parcourir", command=self.browse_destination, width=100).pack(side="right", pady=5)


        # Frame pour les options communes
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=10, pady=10)
        self.setup_options_frame()

        # Barre de progression
        self.progress_label = ctk.CTkLabel(self, text="Prêt.", font=ctk.CTkFont(size=13))
        self.progress_label.pack(fill="x", padx=10, pady=(0, 0))
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=(5, 10))
        self.progress_bar.set(0)
        
        # Bouton Télécharger
        self.download_button = ctk.CTkButton(self, text="Télécharger", command=self.start_download_thread, fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(size=14, weight="bold"))
        self.download_button.pack(pady=(5, 15), padx=10, fill="x", ipady=5) # Changement de pady pour l'assurer en bas
        
        # Prêt
        print(f"Interface initialisée. ffmpeg trouvé à: {self.ffmpeg_path}")

    # --- setup_download_tab SUPPRIMÉ ---

    def setup_options_frame(self):
        """Configure la frame des options communes."""
        
        self.options_frame.grid_columnconfigure((0, 1), weight=1)

        # --- Frame gauche (Options) ---
        left_frame = ctk.CTkFrame(self.options_frame)
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Renommé de "Type" à "Options"
        ctk.CTkLabel(left_frame, text="Options :", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkCheckBox(left_frame, text="Audio seulement (MP3)", variable=self.audio_only, command=self.toggle_quality_menu).pack(anchor="w", pady=10, padx=10)
        
        # Checkbox "vidéo seule" déplacée ici
        ctk.CTkCheckBox(left_frame, text="Télécharger la vidéo seule (si c'est une playlist)", variable=self.no_playlist).pack(anchor="w", pady=10, padx=10)
        
        # --- Frame droite (Qualité) ---
        right_frame = ctk.CTkFrame(self.options_frame)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Qualité Vidéo :", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.quality_menu = ctk.CTkOptionMenu(right_frame, variable=self.quality, values=['Source (Best)', '1080p', '720p', '480p'])
        self.quality_menu.pack(anchor="w", pady=(0, 10), fill="x", padx=10)

        # --- Menu Codec ---
        ctk.CTkLabel(right_frame, text="Codec Vidéo :", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        # Suppression de 'AV1' car le ffmpeg inclus ne le supporte pas (cause "Encoder not found")
        # Ajout du mode "Copier" (vcodec copy) pour des performances maximales
        self.codec_menu = ctk.CTkOptionMenu(right_frame, variable=self.codec, values=['Copier la vidéo (Rapide)', 'h264 (Lent)', 'h265 (Très lent)'])
        self.codec_menu.pack(anchor="w", pady=(0, 10), fill="x", padx=10)


        # --- Frame bas (Options Playlist) SUPPRIMÉE ---

    def toggle_quality_menu(self):
        """Active/Désactive le menu qualité si "audio only" est coché."""
        if self.audio_only.get():
            self.quality_menu.configure(state="disabled")
            self.codec_menu.configure(state="disabled") # <-- AJOUT
        else:
            self.quality_menu.configure(state="normal")
            self.codec_menu.configure(state="normal") # <-- AJOUT

    def browse_destination(self):
        """Ouvre une boîte de dialogue pour sélectionner un dossier de destination."""
        folder = filedialog.askdirectory()
        if folder:
            self.destination_folder.set(folder)

    def build_ytdlp_options(self):
        """Construit le dictionnaire d'options pour yt-dlp basé sur la GUI."""
        
        out_path = self.destination_folder.get()
        os.makedirs(out_path, exist_ok=True)
        
        # --- CORRECTION DU BUG ---
        # Au lieu d'un template yt-dlp conditionnel complexe qui cause des KeyErrors,
        # nous utilisons la logique Python pour choisir le bon template.
        
        if self.no_playlist.get():
            # Si l'utilisateur coche "vidéo seule", on n'inclut jamais l'index de playlist.
            template_name = '%(title)s.%(ext)s'
        else:
            # Si c'est une playlist, yt-dlp mettra le numéro (ex: "01 - Titre.mp4").
            # Si c'est une vidéo seule, yt-dlp mettra "NA" (ex: "NA - Titre.mp4").
            # C'est un peu moins joli pour les vidéos seules, mais c'est 100% robuste
            # et évite le crash.
            template_name = '%(playlist_index)s - %(title)s.%(ext)s'
        
        out_template = os.path.join(out_path, template_name)
        # --- FIN DE LA CORRECTION ---

        common_options = {
            'logger': YtdlpLogger(self),
            'progress_hooks': [self.hook_progress],
            'postprocessor_hooks': [self.hook_postprocessing], # <-- AJOUT : Hook pour l'encodage
            'outtmpl': out_template,
            'noplaylist': self.no_playlist.get(),
            'encoding': 'utf-8',
            'ffmpeg_location': self.ffmpeg_path,
            'no_color': True, # <-- CORRECTION 1: Désactiver les codes de couleur
        }
        
        if self.audio_only.get():
            audio_options = {
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {'key': 'FFmpegMetadata', 'add_metadata': True},
                ],
                'writethumbnail': True,
                'embedthumbnail': True,
                'add_metadata': True,
            }
            return {**common_options, **audio_options}
            
        else: # Mode vidéo
            quality_str = self.quality.get()
            quality_map = {
                'Source (Best)': 'bestvideo+bestaudio/best', # <-- MODIFIÉ
                '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            }
            
            # --- NOUVEAU : Logique pour le codec ---
            selected_codec = self.codec.get()
            codec_map = {
                'Copier la vidéo (Rapide)': 'copy',
                'h264 (Lent)': 'libx264',
                'h265 (Très lent)': 'libx265',
            }
            # Par défaut 'copy' si sélection invalide
            ffmpeg_vcodec = codec_map.get(selected_codec, 'copy') 
            
            video_options = {
                'format': quality_map.get(quality_str, 'bestvideo+bestaudio/best'),
                'merge_output_format': 'mp4',
                
                # --- CORRECTION DE L'ERREUR TypeError ---
                # Au lieu de 'FFmpegVideoConvertor', nous passons les arguments
                # de codec directement au 'merger' (FFmpegMerger).
                'postprocessor_args': {
                    'merger': [
                        '-vcodec', ffmpeg_vcodec, # Force le codec vidéo choisi
                        '-acodec', 'aac',         # Force le codec audio en AAC
                    ]
                },
                
                # Nous gardons 'FFmpegMetadata' pour écrire les métadonnées
                'postprocessors': [
                    {'key': 'FFmpegMetadata', 'add_metadata': True},
                ],
                # --- FIN DE LA CORRECTION ---
            }
            return {**common_options, **video_options}

    def hook_progress(self, d):
        """Hook (rappel) appelé par yt-dlp pour la progression."""
        # Note : ce hook est appelé depuis un thread différent.
        # Nous devons utiliser 'self.after' pour mettre à jour la GUI
        # en toute sécurité depuis le thread principal.
        
        if d['status'] == 'downloading':
            try:
                # --- CORRECTION 3: Nettoyage robuste de la string de progression ---
                percent_str = d['_percent_str'].replace('%', '').strip()
                # Supprimer les codes ANSI juste au cas où 'no_color' ne suffirait pas
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                percent_str = ansi_escape.sub('', percent_str)
                
                percent = float(percent_str) / 100.0
                # --- Fin de la correction 3 ---

                eta = d.get('_eta_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                status_msg = f"Téléchargement... {percent*100:.1f}% ({speed} | ETA: {eta})"
                
                # Mettre à jour la GUI via 'after'
                self.after(0, self.update_progress, percent, status_msg)
            except ValueError as e:
                # Gérer spécifiquement l'erreur de conversion
                print(f"Erreur hook_progress (ValueError): {e}. String reçue: {d['_percent_str']!r}")
                # Ne pas planter, juste afficher le message de base
                self.after(0, self.update_progress, 0, "Téléchargement...")

        elif d['status'] == 'finished':
            # NE PAS mettre "Terminé", car l'encodage commence.
            # Le hook_postprocessing prendra le relais.
            self.after(0, self.update_progress, 1.0, "Téléchargement terminé, préparation de l'encodage...")
        
        elif d['status'] == 'error':
            self.after(0, self.update_progress, 0, "Erreur de téléchargement.")

    def hook_postprocessing(self, d):
        """Hook (rappel) appelé par yt-dlp pour l'encodage/fusion (post-processing)."""
        # print(f"[POST-HOOK] Status: {d.get('status')}, Info: {d.get('info_dict')}") # Debug
        
        if d.get('status') == 'started' or d.get('status') == 'processing':
            self.after(0, self.update_postprocessing_status, "Encodage / Fusion en cours... (Patientez)")
        elif d.get('status') == 'finished':
            # Ce hook est appelé *avant* on_download_complete
            self.after(0, self.update_postprocessing_status, "Encodage terminé.")

    def update_postprocessing_status(self, text):
        """Met à jour le label et met la barre en mode indéterminé pour l'encodage."""
        self.progress_label.configure(text=text)
        self.download_button.configure(text="Encodage en cours...") # <-- CORRECTION UI
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

    def update_progress(self, value, text):
        """Met à jour la barre de progression et le label (thread-safe)."""
        self.progress_bar.set(value)
        self.progress_label.configure(text=text)

    def start_download_thread(self):
        """Lance le téléchargement dans un thread séparé pour ne pas geler la GUI."""
        
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
            return

        # Démarrer le téléchargement dans un nouveau thread
        # 'daemon=True' permet à l'application de se fermer même si le thread tourne encore
        download_thread = threading.Thread(target=self._download_content, args=(url,), daemon=True)
        download_thread.start()
        
        # Désactiver le bouton pour éviter les clics multiples
        self.download_button.configure(state="disabled", text="Téléchargement en cours...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Initialisation...")

    def _download_content(self, url):
        """La fonction de téléchargement réelle exécutée dans le thread."""
        try:
            options = self.build_ytdlp_options()
            
            # Encapsule YoutubeDL dans un 'with' pour un nettoyage correct
            with self.yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            # Signaler le succès à la GUI (via 'after')
            self.after(0, self.on_download_complete, "Téléchargement terminé !")
            
        except yt_dlp.utils.DownloadError as e:
            print(f"\n[ERREUR FATALE] {e}", file=sys.stderr)
            self.after(0, self.on_download_error, f"Erreur: {e}")
        except Exception as e:
            print(f"\n[ERREUR INATTENDUE] {e}", file=sys.stderr)
            traceback.print_exc()
            self.after(0, self.on_download_error, f"Erreur inattendue: {e}")

    def on_download_complete(self, message):
        """Appelé dans le thread principal à la fin d'un téléchargement réussi."""
        messagebox.showinfo("Succès", message)
        self.progress_bar.stop() # Arrêter le mode indéterminé
        self.progress_bar.configure(mode="determinate")
        self.download_button.configure(state="normal", text="Télécharger")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Prêt.")

    def on_download_error(self, error_message):
        """Appelé dans le thread principal en cas d'erreur."""
        messagebox.showerror("Erreur", f"Le téléchargement a échoué:\n{error_message}")
        self.progress_bar.stop() # Arrêter le mode indéterminé
        self.progress_bar.configure(mode="determinate")
        self.download_button.configure(state="normal", text="Télécharger")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Prêt (erreur précédente).")


# Lancement de l'application
if __name__ == "__main__":
    print("Lancement de l'application GUI...")
    try:
        app = YtDlpGui(yt_dlp_module=yt_dlp, ffmpeg_module=imageio_ffmpeg)
        app.mainloop()
    except Exception as e:
        print(f"ERREUR FATALE au lancement de la GUI: {e}", file=sys.stderr)
        traceback.print_exc()
        try:
            # Ultime tentative d'afficher une erreur
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erreur GUI", f"L'application n'a pas pu démarrer:\n{e}\n\nConsultez le terminal.")
        except:
            pass



