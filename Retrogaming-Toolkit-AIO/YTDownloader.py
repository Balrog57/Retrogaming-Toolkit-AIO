#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized YT Downloader Pro (yt-dlp)
"""

import sys
import os
import subprocess
import importlib
import traceback
import threading
import json
import re
from tkinter import filedialog, messagebox, StringVar, BooleanVar

# Import Utils & Theme
try:
    import utils
except ImportError:
    pass

try:
    import theme
except ImportError:
    theme = None

# --- Dependency Logic (Preserved but condensed) ---
def check_and_import(package_name, import_name=None):
    if not import_name: import_name = package_name.replace('-', '_')
    try:
        return importlib.import_module(import_name)
    except ImportError:
        if getattr(sys, 'frozen', False):
            # In frozen mode, we cannot pip install. 
            # We must assume dependencies are bundled or we fail gracefully.
            # Using sys.executable in frozen mode launches the app itself, causing a loop.
            messagebox.showerror("Erreur Dépendance", f"La dépendance '{package_name}' est manquante et ne peut pas être installée automatiquement dans la version portable.")
            return None
        else:
            try:
                 subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--quiet"])
                 importlib.invalidate_caches()
                 return importlib.import_module(import_name)
            except Exception as e:
                 print(f"Failed to install/import {package_name}: {e}")
                 sys.exit(1)

# Bootstrap dependencies
ctk = check_and_import("customtkinter")
yt_dlp = check_and_import("yt-dlp", "yt_dlp")
try:
    imageio_ffmpeg = check_and_import("imageio-ffmpeg", "imageio_ffmpeg")
except:
    imageio_ffmpeg = None

ANSI_ESCAPE_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class YtdlpLogger:
    def __init__(self, gui): self.gui = gui
    def debug(self, msg): pass
    def info(self, msg): 
        if not msg.startswith('[download]'): print(f"[INFO] {msg}")
    def warning(self, msg): print(f"[WARN] {msg}")
    def error(self, msg): print(f"[ERR] {msg}")

class YtDlpGui(ctk.CTk):
    def __init__(self, yt_dlp_module, ffmpeg_module):
        super().__init__()
        self.yt_dlp = yt_dlp_module
        
        # Shared Theme Init
        if theme:
             theme.apply_theme(self, "YT Downloader Pro (Sakura Night)")
             self.COLOR_SUCCESS = theme.COLOR_SUCCESS
             self.COLOR_TEXT_SUB = theme.COLOR_TEXT_SUB
             self.COLOR_CARD_BG = theme.COLOR_CARD_BG
        else:
             ctk.set_appearance_mode("dark")
             self.title("YT Downloader Pro")
             self.geometry("800x600")
             self.COLOR_SUCCESS = "green"
             self.COLOR_TEXT_SUB = "gray"
             self.COLOR_CARD_BG = None

        # Resolve FFmpeg
        self.ffmpeg_path = self._resolve_ffmpeg(ffmpeg_module)
        
        # Variables
        self.destination_folder = StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.audio_only = BooleanVar(value=False)
        self.no_playlist = BooleanVar(value=False)
        self.quality = StringVar(value='Source (Best)')
        self.codec = StringVar(value='Copier la vidéo (Rapide)')
        
        self._setup_ui()

    def _resolve_ffmpeg(self, ffmpeg_module):
        target = "ffmpeg.exe"
        # 1. Utils
        if 'utils' in sys.modules:
            p = utils.get_binary_path(target)
            if os.path.exists(p): return p
        # 2. AppData
        ad = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', target)
        if os.path.exists(ad): return ad
        # 3. Download
        if 'utils' in sys.modules:
            try:
                m = utils.DependencyManager(self)
                url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "essentials")
                if not url: url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                return m.install_dependency("FFmpeg", url, target, "zip")
            except Exception as e:
                print(f"[WARN] Failed to install FFmpeg via Utils: {e}")
        # 4. ImageIO
        if ffmpeg_module:
            try: return ffmpeg_module.get_ffmpeg_exe()
            except: pass
        return "ffmpeg" # PATH fallback

    def _setup_ui(self):
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Filler

        # 1. Inputs
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(top_frame, text="URL (Vidéo/Playlist):", font=theme.get_font_title(14) if theme else None).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(top_frame)
        self.url_entry.pack(fill="x", pady=(5, 10))
        
        ctk.CTkLabel(top_frame, text="Destination:", font=theme.get_font_title(14) if theme else None).pack(anchor="w")
        dest_row = ctk.CTkFrame(top_frame, fg_color="transparent")
        dest_row.pack(fill="x", pady=5)
        
        self.destination_entry = ctk.CTkEntry(dest_row, textvariable=self.destination_folder)
        self.destination_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(dest_row, text="Parcourir", width=100, command=self.browse_dest, 
                      fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(side="right")

        # 2. Options Grid
        opts_frame = ctk.CTkFrame(self, fg_color=self.COLOR_CARD_BG, corner_radius=10)
        opts_frame.pack(fill="x", padx=20, pady=10)
        opts_frame.grid_columnconfigure(1, weight=1)
        
        # Left: Switches
        left_col = ctk.CTkFrame(opts_frame, fg_color="transparent")
        left_col.pack(side="left", fill="y", padx=20, pady=20)
        
        ctk.CTkCheckBox(left_col, text="Audio seulement (MP3)", variable=self.audio_only, command=self.toggle_quality, 
                        fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(left_col, text="Ignorer Playlist (Vidéo seule)", variable=self.no_playlist, 
                        fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=10)
        
        # Right: Dropdowns
        right_col = ctk.CTkFrame(opts_frame, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(right_col, text="Qualité:").pack(anchor="w")
        self.quality_menu = ctk.CTkOptionMenu(right_col, variable=self.quality, values=['Source (Best)', '1080p', '720p', '480p'],
                                              fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue",
                                              button_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue",
                                              button_hover_color=theme.COLOR_ACCENT_HOVER if theme else "darkblue")
        self.quality_menu.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(right_col, text="Codec:").pack(anchor="w")
        self.codec_menu = ctk.CTkOptionMenu(right_col, variable=self.codec, values=['Copier la vidéo (Rapide)', 'h264 (Lent)', 'h265 (Très lent)'],
                                            fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue",
                                            button_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue",
                                            button_hover_color=theme.COLOR_ACCENT_HOVER if theme else "darkblue")
        self.codec_menu.pack(fill="x", pady=(0, 10))

        # 3. Progress & Action
        bot_frame = ctk.CTkFrame(self, fg_color="transparent")
        bot_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.progress_label = ctk.CTkLabel(bot_frame, text="Prêt.", text_color=self.COLOR_TEXT_SUB)
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(bot_frame, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.download_button = ctk.CTkButton(bot_frame, text="TÉLÉCHARGER", command=self.start_download, height=50,
                                             font=theme.get_font_title(16) if theme else None,
                                             fg_color=self.COLOR_SUCCESS, hover_color="#218838")
        self.download_button.pack(fill="x", pady=10)

    def browse_dest(self):
        f = filedialog.askdirectory()
        if f: self.destination_folder.set(f)

    def toggle_quality(self):
        state = "disabled" if self.audio_only.get() else "normal"
        self.quality_menu.configure(state=state)
        self.codec_menu.configure(state=state)

    def start_download(self):
        url = self.url_entry.get()
        if not url: return messagebox.showerror("Err", "URL requise")
        
        self.download_button.configure(state="disabled", text="En cours...")
        self.progress_bar.set(0)
        threading.Thread(target=self._run_download, args=(url,), daemon=True).start()

    def _run_download(self, url):
        try:
            opts = self._build_opts()
            with self.yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_finish, "Succès !")
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _build_opts(self):
        dest = self.destination_folder.get()
        os.makedirs(dest, exist_ok=True)
        tmpl = '%(title)s.%(ext)s' if self.no_playlist.get() else '%(playlist_index)s - %(title)s.%(ext)s'
        
        opts = {
            'logger': YtdlpLogger(self),
            'progress_hooks': [self._hook_prog],
            'outtmpl': os.path.join(dest, tmpl),
            'noplaylist': self.no_playlist.get(),
            'ffmpeg_location': self.ffmpeg_path,
        }
        
        if self.audio_only.get():
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}, {'key': 'FFmpegMetadata'}],
            })
        else:
            q_map = {'Source (Best)': 'bestvideo+bestaudio/best', '1080p': 'bestvideo[height<=1080]+bestaudio/best'}
            c_map = {'Copier la vidéo (Rapide)': 'copy', 'h264 (Lent)': 'libx264', 'h265 (Très lent)': 'libx265'}
            
            opts.update({
                'format': q_map.get(self.quality.get(), 'bestvideo+bestaudio/best'),
                'merge_output_format': 'mp4',
                'postprocessor_args': {'merger': ['-vcodec', c_map.get(self.codec.get(), 'copy'), '-acodec', 'aac']},
            })
        return opts

    def _hook_prog(self, d):
        if d['status'] == 'downloading':
            try:
                p = float(ANSI_ESCAPE_REGEX.sub('', d.get('_percent_str', '0%')).strip('%')) / 100
                msg = f"DL: {p*100:.0f}% - {d.get('_eta_str', '?')}"
                self.after(0, self._update_ui, p, msg)
            except: pass
        elif d['status'] == 'finished':
            self.after(0, self._update_ui, 1, "Encodage...")

    def _update_ui(self, val, txt):
        self.progress_bar.set(val)
        self.progress_label.configure(text=txt)

    def _on_finish(self, msg):
        self.download_button.configure(state="normal", text="TÉLÉCHARGER")
        self.progress_label.configure(text="Prêt.")
        messagebox.showinfo("Fini", msg)

    def _on_error(self, err):
        self.download_button.configure(state="normal", text="TÉLÉCHARGER")
        self.progress_label.configure(text="Erreur.")
        messagebox.showerror("Erreur", err)

def main():
    app = YtDlpGui(yt_dlp, imageio_ffmpeg)
    app.mainloop()

if __name__ == "__main__":
    main()
