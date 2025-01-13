import os
import subprocess
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import VideoUnavailable, RegexMatchError
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, BooleanVar

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

class PyTubeFixGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.title("PyTubeFix GUI")
        self.geometry("600x400")
        self.resizable(False, False)

        # Variables globales
        self.destination_folder = StringVar(value=os.getcwd())
        self.audio_only = BooleanVar(value=False)
        self.subtitles = BooleanVar(value=False)
        self.use_oauth = BooleanVar(value=False)

        # Création des onglets
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Onglet "Vidéo unique"
        self.tab_video = self.tabview.add("Vidéo unique")
        self.setup_video_tab()

        # Onglet "Playlist"
        self.tab_playlist = self.tabview.add("Playlist")
        self.setup_playlist_tab()

        # Onglet "Chaîne"
        self.tab_channel = self.tabview.add("Chaîne")
        self.setup_channel_tab()

        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)

    def setup_video_tab(self):
        """Configure l'onglet pour télécharger une vidéo unique."""
        ctk.CTkLabel(self.tab_video, text="URL de la vidéo :").pack(pady=5)
        self.video_url_entry = ctk.CTkEntry(self.tab_video, width=400)
        self.video_url_entry.pack(pady=5)

        ctk.CTkLabel(self.tab_video, text="Dossier de destination :").pack(pady=5)
        self.destination_entry = ctk.CTkEntry(self.tab_video, textvariable=self.destination_folder, width=400)
        self.destination_entry.pack(pady=5)
        ctk.CTkButton(self.tab_video, text="Parcourir", command=self.browse_destination).pack(pady=5)

        # Cases à cocher alignées verticalement
        ctk.CTkCheckBox(self.tab_video, text="Télécharger uniquement l'audio", variable=self.audio_only).pack(pady=5)
        ctk.CTkCheckBox(self.tab_video, text="Récupérer les sous-titres", variable=self.subtitles).pack(pady=5)
        ctk.CTkCheckBox(self.tab_video, text="Utiliser l'authentification OAuth", variable=self.use_oauth).pack(pady=5)

        ctk.CTkButton(self.tab_video, text="Télécharger", command=self.download_video).pack(pady=10)

    def setup_playlist_tab(self):
        """Configure l'onglet pour télécharger une playlist."""
        ctk.CTkLabel(self.tab_playlist, text="URL de la playlist :").pack(pady=5)
        self.playlist_url_entry = ctk.CTkEntry(self.tab_playlist, width=400)
        self.playlist_url_entry.pack(pady=5)

        ctk.CTkLabel(self.tab_playlist, text="Dossier de destination :").pack(pady=5)
        self.destination_entry_playlist = ctk.CTkEntry(self.tab_playlist, textvariable=self.destination_folder, width=400)
        self.destination_entry_playlist.pack(pady=5)
        ctk.CTkButton(self.tab_playlist, text="Parcourir", command=self.browse_destination).pack(pady=5)

        # Cases à cocher alignées verticalement
        ctk.CTkCheckBox(self.tab_playlist, text="Télécharger uniquement l'audio", variable=self.audio_only).pack(pady=5)
        ctk.CTkCheckBox(self.tab_playlist, text="Récupérer les sous-titres", variable=self.subtitles).pack(pady=5)
        ctk.CTkCheckBox(self.tab_playlist, text="Utiliser l'authentification OAuth", variable=self.use_oauth).pack(pady=5)

        ctk.CTkButton(self.tab_playlist, text="Télécharger", command=self.download_playlist).pack(pady=10)

    def setup_channel_tab(self):
        """Configure l'onglet pour télécharger une chaîne."""
        ctk.CTkLabel(self.tab_channel, text="URL de la chaîne :").pack(pady=5)
        self.channel_url_entry = ctk.CTkEntry(self.tab_channel, width=400)
        self.channel_url_entry.pack(pady=5)

        ctk.CTkLabel(self.tab_channel, text="Dossier de destination :").pack(pady=5)
        self.destination_entry_channel = ctk.CTkEntry(self.tab_channel, textvariable=self.destination_folder, width=400)
        self.destination_entry_channel.pack(pady=5)
        ctk.CTkButton(self.tab_channel, text="Parcourir", command=self.browse_destination).pack(pady=5)

        # Cases à cocher alignées verticalement
        ctk.CTkCheckBox(self.tab_channel, text="Télécharger uniquement l'audio", variable=self.audio_only).pack(pady=5)
        ctk.CTkCheckBox(self.tab_channel, text="Récupérer les sous-titres", variable=self.subtitles).pack(pady=5)
        ctk.CTkCheckBox(self.tab_channel, text="Utiliser l'authentification OAuth", variable=self.use_oauth).pack(pady=5)

        ctk.CTkButton(self.tab_channel, text="Télécharger", command=self.download_channel).pack(pady=10)

    def browse_destination(self):
        """Ouvre une boîte de dialogue pour sélectionner un dossier de destination."""
        folder = filedialog.askdirectory()
        if folder:
            self.destination_folder.set(folder)

    def download_video(self):
        """Télécharge une vidéo unique."""
        self._download_content(self.video_url_entry.get(), is_playlist=False)

    def download_playlist(self):
        """Télécharge une playlist."""
        self._download_content(self.playlist_url_entry.get(), is_playlist=True)

    def download_channel(self):
        """Télécharge toutes les vidéos d'une chaîne."""
        self._download_content(self.channel_url_entry.get(), is_playlist=True)

    def _download_content(self, url, is_playlist):
        """Télécharge une vidéo, une playlist ou une chaîne."""
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
            return

        try:
            self.progress_bar.start()

            if is_playlist:
                content = Playlist(url)
                videos = content.videos
            else:
                content = YouTube(url, use_oauth=self.use_oauth.get(), allow_oauth_cache=True)
                videos = [content]

            for video in videos:
                if self.audio_only.get():
                    # Télécharger uniquement l'audio en .m4a
                    stream = video.streams.filter(only_audio=True, mime_type="audio/mp4").first()
                    filename = f"{video.title}.m4a"
                    stream.download(output_path=self.destination_folder.get(), filename=filename)
                else:
                    # Télécharger la vidéo en haute résolution (1080p ou 4K)
                    video_stream = video.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
                    audio_stream = video.streams.filter(only_audio=True, mime_type="audio/mp4").first()

                    if video_stream and audio_stream:
                        # Télécharger les flux vidéo et audio séparément
                        video_path = video_stream.download(output_path=self.destination_folder.get(), filename="video_temp.mp4")
                        audio_path = audio_stream.download(output_path=self.destination_folder.get(), filename="audio_temp.m4a")

                        # Fusionner les flux vidéo et audio avec ffmpeg
                        final_path = os.path.join(self.destination_folder.get(), f"{video.title}.mp4")
                        self.merge_video_audio(video_path, audio_path, final_path)

                        # Supprimer les fichiers temporaires
                        os.remove(video_path)
                        os.remove(audio_path)
                    else:
                        messagebox.showerror("Erreur", f"Impossible de trouver les flux pour la vidéo : {video.title}")

                if self.subtitles.get():
                    caption = video.captions.get_by_language_code('fr')  # Sous-titres en français
                    if caption:
                        with open(os.path.join(self.destination_folder.get(), f"{video.title}.srt"), "w", encoding="utf-8") as file:
                            file.write(caption.generate_srt_captions())

            messagebox.showinfo("Succès", "Téléchargement terminé !")
        except (VideoUnavailable, RegexMatchError) as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
        except FileNotFoundError as e:
            messagebox.showerror("Erreur", f"ffmpeg.exe introuvable : {e}")
        finally:
            self.progress_bar.stop()

    def merge_video_audio(self, video_path, audio_path, output_path):
        """Fusionne les flux vidéo et audio en utilisant ffmpeg."""
        # Chemin relatif vers ffmpeg.exe (dans le même dossier que le script)
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        
        # Vérifier que ffmpeg.exe existe
        if not os.path.exists(ffmpeg_path):
            raise FileNotFoundError(f"ffmpeg.exe introuvable dans le dossier du script : {ffmpeg_path}")

        # Commande pour fusionner les flux vidéo et audio
        command = [
            ffmpeg_path,
            "-y",  # Force l'écrasement des fichiers existants
            "-i", video_path,  # Fichier vidéo
            "-i", audio_path,  # Fichier audio
            "-c:v", "copy",    # Copier le flux vidéo sans ré-encodage
            "-c:a", "aac",     # Encoder l'audio en AAC
            "-strict", "experimental",
            output_path        # Fichier de sortie
        ]
        
        # Exécuter la commande
        subprocess.run(command, check=True)

# Lancement de l'application
if __name__ == "__main__":
    app = PyTubeFixGUI()
    app.mainloop()