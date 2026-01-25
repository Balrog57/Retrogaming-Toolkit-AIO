import os
import subprocess
import re
import requests
import tempfile
import shutil
import customtkinter as ctk
import tkinter as tk # For some internals if needed
from tkinter import filedialog, messagebox, BooleanVar
import sys
from tkinterdnd2 import TkinterDnD, DND_FILES

# --- Import Theme ---
try:
    import theme
except ImportError:
    theme = None

# --- Helpers ---
try:
    import utils
except ImportError:
    pass

class FileListFrame(ctk.CTkScrollableFrame):
    """
    Manages a list of files with a modern look.
    Each file has a remove button.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        if theme:
             self.configure(fg_color=theme.COLOR_CARD_BG)
        
        self.files = [] # List of full paths
        
    def add_file(self, file_path):
        if file_path in self.files: return # Avoid duplicates
        self.files.append(file_path)
        self._render_row(file_path)
        
    def add_files(self, file_paths):
        for p in file_paths:
            self.add_file(p)

    def get_files(self):
        return self.files

    def clear(self):
        self.files = []
        for widget in self.winfo_children():
            widget.destroy()

    def _remove_file(self, file_path, row_frame):
        if file_path in self.files:
            self.files.remove(file_path)
        row_frame.destroy()

    def _render_row(self, file_path):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        # Filename label
        name = os.path.basename(file_path)
        lbl = ctk.CTkLabel(row, text=name, anchor="w", font=theme.get_font_main() if theme else None)
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        
        # Remove button (small X)
        btn_del = ctk.CTkButton(
            row, 
            text="✕", 
            width=24, 
            height=24,
            fg_color="transparent",
            text_color=theme.COLOR_ERROR if theme else "red",
            hover_color=theme.COLOR_GHOST_HOVER if theme else "#333",
            command=lambda: self._remove_file(file_path, row)
        )
        btn_del.pack(side="right", padx=5)
        
        # Tooltip or path on hover? Simpler: Title on list?
        # CTk doesn't have native tooltips. We'll stick to basename.

# --- Logic copy-pasted/adapted ---

def check_and_download_ffmpeg(root=None):
    target_name = "ffmpeg.exe"
    if 'utils' in sys.modules:
        ffmpeg_path = utils.get_binary_path(target_name)
    else:
        ffmpeg_path = os.path.join(os.getcwd(), target_name)

    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Try using DependencyManager
    if 'utils' in sys.modules and root:
        try:
             manager = utils.DependencyManager(root)
             ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "essentials")
             if not ffmpeg_url:
                ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "full")
             if not ffmpeg_url:
                 ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
             
             result = manager.install_dependency("FFmpeg", ffmpeg_url, target_name, "zip")
             return result
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation de FFmpeg: {e}")
            return None
    else:
         return None

def convert_video(input_file, start_time, end_time, output_file, video_bitrate, audio_bitrate, fps, resolution, root=None, ffmpeg_path=None):
    if not ffmpeg_path:
        check_and_download_ffmpeg(root)
        if 'utils' in sys.modules: ffmpeg_path = utils.get_binary_path("ffmpeg.exe")
        else: ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
            
    try:
        command = [
            ffmpeg_path, "-i", input_file, "-ss", start_time, "-to", end_time,
            "-c:v", "libx264", "-preset", "fast",
            f"-b:v", video_bitrate, f"-r", fps, f"-vf", f"scale={resolution}",
            "-c:a", "aac", f"-b:a", audio_bitrate, "-y", output_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur export vidéo.\n{e.stderr}")
        return False
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")
        return False

def capture_first_frame(input_file, output_file, rotate=False, root=None, ffmpeg_path=None):
    if not ffmpeg_path:
        check_and_download_ffmpeg(root)
        if 'utils' in sys.modules: ffmpeg_path = utils.get_binary_path("ffmpeg.exe")
        else: ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    try:
        command = [ffmpeg_path, "-i", input_file, "-ss", "00:00:01", "-vframes", "1"]
        if rotate: command.extend(["-vf", "transpose=1"])
        command.append(output_file)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode != 0: raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur capture.\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

# --- Apps Class ---

class VideoConvertApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Theme
        if theme:
            theme.apply_theme(self, "Trim et Convertisseur Vidéo par Lot")
        else:
            ctk.set_appearance_mode("dark")
            self.title("Trim et Convertisseur Vidéo par Lot")
            
        self.geometry("800x650")
            
        self._setup_ui()
        
        # DnD
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Check Dependency
        self.after(100, lambda: check_and_download_ffmpeg(self))

    def _setup_ui(self):
        # 1. Inputs
        frame_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_input.pack(padx=20, pady=(20, 10), fill="x")
        
        ctk.CTkLabel(frame_input, text="Vidéo d'entrée", font=theme.get_font_title() if theme else None).pack(anchor="w")
        ctk.CTkLabel(frame_input, text="(Glisser-déposer disponible)", text_color=theme.COLOR_TEXT_SUB if theme else "gray").pack(anchor="w")

        btn_row = ctk.CTkFrame(frame_input, fg_color="transparent")
        btn_row.pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_row, text="Ajouter des fichiers", command=self.browse_files, width=150,
                      fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None, hover_color=theme.COLOR_ACCENT_HOVER if theme else None).pack(side="left", padx=(0, 10))
                      
        ctk.CTkButton(btn_row, text="Tout effacer", command=lambda: self.file_list.clear(), width=100,
                      fg_color="transparent", border_width=1, border_color=theme.COLOR_ACCENT_PRIMARY if theme else "gray").pack(side="left")

        # List
        self.file_list = FileListFrame(self, height=150)
        self.file_list.pack(padx=20, pady=0, fill="x")
        
        # 2. Settings
        settings_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_CARD_BG if theme else None, corner_radius=10)
        settings_frame.pack(padx=20, pady=20, fill="x")
        
        # Times
        row_time = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row_time.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(row_time, text="Début:", width=60).pack(side="left")
        self.entry_start = ctk.CTkEntry(row_time, width=80); self.entry_start.insert(0, "00:00:00"); self.entry_start.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_time, text="Fin:", width=50).pack(side="left")
        self.entry_end = ctk.CTkEntry(row_time, width=80); self.entry_end.insert(0, "00:01:30"); self.entry_end.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_time, text="Format:", width=60).pack(side="left", padx=(10,0))
        self.combo_format = ctk.CTkComboBox(row_time, values=["Source", "MP4", "MKV"], width=80)
        self.combo_format.pack(side="left", padx=5)
        
        # Quality
        row_qual = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row_qual.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(row_qual, text="Vidéo (kbps):").pack(side="left")
        self.entry_v_bitrate = ctk.CTkEntry(row_qual, width=80); self.entry_v_bitrate.insert(0, "8000k"); self.entry_v_bitrate.pack(side="left", padx=5)

        ctk.CTkLabel(row_qual, text="Audio (kbps):").pack(side="left", padx=(10,0))
        self.entry_a_bitrate = ctk.CTkEntry(row_qual, width=80); self.entry_a_bitrate.insert(0, "128k"); self.entry_a_bitrate.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_qual, text="FPS:").pack(side="left", padx=(10,0))
        self.entry_fps = ctk.CTkEntry(row_qual, width=60); self.entry_fps.insert(0, "30"); self.entry_fps.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_qual, text="Res:").pack(side="left", padx=(10,0))
        self.entry_res = ctk.CTkEntry(row_qual, width=100); self.entry_res.insert(0, "1920x1080"); self.entry_res.pack(side="left", padx=5)
        
        # 3. Output Options
        opt_frame = ctk.CTkFrame(self, fg_color="transparent")
        opt_frame.pack(padx=20, fill="x")
        
        self.out_opt = ctk.StringVar(value="folder")
        ctk.CTkRadioButton(opt_frame, text="Exporter dans 'vidéos_converties'", variable=self.out_opt, value="folder", 
                           fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(opt_frame, text="Remplacer originaux", variable=self.out_opt, value="replace",
                           fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=2)
                           
        # Capture covers
        self.cap_no_rot = BooleanVar()
        self.cap_rot = BooleanVar()
        ctk.CTkCheckBox(opt_frame, text="Capture cover (sans rotation)", variable=self.cap_no_rot, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(opt_frame, text="Capture cover (avec rotation)", variable=self.cap_rot, fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(anchor="w", pady=2)

        # 4. Action
        ctk.CTkButton(self, text="CONVERTIR", command=self.start_conversion, height=50, width=250,
                      font=theme.get_font_title() if theme else ("Arial", 16, "bold"),
                      fg_color=theme.COLOR_SUCCESS if theme else "green", 
                      hover_color="#27ae60").pack(pady=20)

    def browse_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Vidéo", "*.*")])
        if paths: self.file_list.add_files(paths)
        
    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.file_list.add_files(files)

    def start_conversion(self):
        files = self.file_list.get_files()
        if not files: return
        
        # Validation checks (same as before)
        start = self.entry_start.get()
        end = self.entry_end.get()
        v_bit = self.entry_v_bitrate.get()
        a_bit = self.entry_a_bitrate.get()
        fps = self.entry_fps.get()
        res = self.entry_res.get()
        
        # Regex (Simplified from original)
        if not re.match(r"^\d{2}:\d{2}:\d{2}$", start) or not re.match(r"^\d{2}:\d{2}:\d{2}$", end): return messagebox.showerror("Err", "Format Heure invalide")
        
        # Validation Inputs
        if not re.match(r"^\d+[kK]?$", v_bit):
             return messagebox.showerror("Erreur", "Bitrate Vidéo invalide (ex: 8000k ou 8000)")
        if not re.match(r"^\d+[kK]?$", a_bit):
             return messagebox.showerror("Erreur", "Bitrate Audio invalide (ex: 128k ou 128)")
        if not re.match(r"^\d+(\.\d+)?$", fps):
             return messagebox.showerror("Erreur", "FPS invalide (ex: 30 ou 29.97)")
        if not re.match(r"^\d+x\d+$", res):
             return messagebox.showerror("Erreur", "Résolution invalide (ex: 1920x1080)")

        # Get FFmpeg
        ff_path = check_and_download_ffmpeg(self)
        if not ff_path: return
        
        # Loop
        for f in files:
            if not os.path.isfile(f): continue
            
            fmt_choice = self.combo_format.get()
            ext = ".mp4" if fmt_choice == "MP4" else ".mkv" if fmt_choice == "MKV" else os.path.splitext(f)[1]
            
            if self.out_opt.get() == "folder":
                out_dir = os.path.join(os.path.dirname(f), "vidéos_converties")
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0] + ext)
                convert_video(f, start, end, out_path, v_bit, a_bit, fps, res, self, ff_path)
            else:
                # Replace logic
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext).name
                if convert_video(f, start, end, tmp, v_bit, a_bit, fps, res, self, ff_path):
                     if ext != os.path.splitext(f)[1]:
                         try: os.remove(f) 
                         except: pass
                         shutil.move(tmp, os.path.splitext(f)[0] + ext)
                     else:
                         shutil.move(tmp, f)
            
            # Captures
            cap_dir = os.path.join(os.getcwd(), "captures")
            if self.cap_no_rot.get():
                os.makedirs(cap_dir, exist_ok=True)
                capture_first_frame(f, os.path.join(cap_dir, "screen-"+os.path.basename(f)+".png"), False, self, ff_path)
            if self.cap_rot.get():
                os.makedirs(cap_dir, exist_ok=True)
                capture_first_frame(f, os.path.join(cap_dir, "screen-rot-"+os.path.basename(f)+".png"), True, self, ff_path)

        messagebox.showinfo("Fini", "Conversion Terminée")

def main():
    app = VideoConvertApp()
    app.mainloop()

if __name__ == "__main__":
    main()