import os
import subprocess
import requests
import re

import tempfile
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, Checkbutton, BooleanVar
import sys
from tkinterdnd2 import TkinterDnD, DND_FILES

try:
    import utils
except ImportError:
    pass

def validate_inputs(start_time, end_time, video_bitrate, audio_bitrate, fps, resolution):
    # Time format: HH:MM:SS
    time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    if not time_pattern.match(start_time):
        raise ValueError("Start time must be in HH:MM:SS format.")
    if not time_pattern.match(end_time):
        raise ValueError("End time must be in HH:MM:SS format.")

    # Bitrate: digits followed by optional k/K/m/M
    bitrate_pattern = re.compile(r'^\d+[kKmM]?$')
    if not bitrate_pattern.match(video_bitrate):
        raise ValueError("Invalid video bitrate format. Use e.g. '8000k'.")
    if not bitrate_pattern.match(audio_bitrate):
        raise ValueError("Invalid audio bitrate format. Use e.g. '128k'.")

    # FPS: integer or float
    try:
        float(fps)
    except ValueError:
         raise ValueError("FPS must be a number.")

    # Resolution: WxH
    resolution_pattern = re.compile(r'^\d+x\d+$')
    if not resolution_pattern.match(resolution):
         raise ValueError("Resolution must be in WxH format (e.g. 1920x1080).")

    return True

def check_and_download_ffmpeg(root=None):
    target_name = "ffmpeg.exe"
    if 'utils' in sys.modules:
        ffmpeg_path = utils.get_binary_path(target_name)
    else:
        # Fallback if utils not loaded (should not happen in main app)
        ffmpeg_path = os.path.join(os.getcwd(), target_name)

    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Try using DependencyManager
    if 'utils' in sys.modules and root:
        try:
             manager = utils.DependencyManager(root)
             
             # Resolve URL dynamically from GitHub
             ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "essentials")
             if not ffmpeg_url:
                ffmpeg_url = utils.fetch_latest_github_asset("GyanD", "codexffmpeg", "full")
             
             if not ffmpeg_url:
                 ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
             
             result = manager.install_dependency(
                 name="FFmpeg",
                 url=ffmpeg_url,
                 target_exe_name=target_name,
                 archive_type="zip",
                 extract_file_in_archive=None
             )
             return result
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation de FFmpeg: {e}")
            return None
    else:
         # Fallback manual if utils or root missing (CLI/Standlone test?)
         messagebox.showerror("Erreur", "Impossible de télécharger FFmpeg (utils ou root manquant).")
         return None

def convert_video(input_file, start_time, end_time, output_file, video_bitrate, audio_bitrate, fps, resolution, root=None, ffmpeg_path=None):
    if not ffmpeg_path:
        check_and_download_ffmpeg(root)  # Vérifiez et téléchargez FFmpeg si nécessaire
        if 'utils' in sys.modules:
            ffmpeg_path = utils.get_binary_path("ffmpeg.exe")
        else:
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    try:
        command = [
            ffmpeg_path,
            "-i", input_file,
            "-ss", start_time,
            "-to", end_time,
            "-c:v", "libx264",
            "-preset", "fast",
            f"-b:v", video_bitrate,
            f"-r", fps,
            f"-vf", f"scale={resolution}",
            "-c:a", "aac",
            f"-b:a", audio_bitrate,
            "-y",  # Overwrite output file if it exists
            output_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'exportation de la vidéo.\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur inattendue s'est produite : {e}")

def capture_first_frame(input_file, output_file, rotate=False, root=None, ffmpeg_path=None):
    if not ffmpeg_path:
        check_and_download_ffmpeg(root)  # Vérifiez et téléchargez FFmpeg si nécessaire
        if 'utils' in sys.modules:
            ffmpeg_path = utils.get_binary_path("ffmpeg.exe")
        else:
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    try:
        command = [
            ffmpeg_path,
            "-i", input_file,
            "-ss", "00:00:01",  # Capture à la première seconde
            "-vframes", "1",    # Capture une seule frame
        ]
        if rotate:
            command.extend(["-vf", "transpose=1"])  # Rotation à droite
        command.append(output_file)
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de la capture de l'image.\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur inattendue s'est produite : {e}")

def browse_files():
    try:
        file_paths = filedialog.askopenfilenames(filetypes=[("Tous les fichiers vidéo", "*.*")])
        if file_paths:
            for file_path in file_paths:
                listbox_files.insert("end", file_path)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la sélection des fichiers : {e}")

def clear_files():
    listbox_files.delete(0, "end")

def delete_selected_files(event):
    """Supprime les éléments sélectionnés de la liste lors de l'appui sur Suppr."""
    selection = listbox_files.curselection()
    for index in reversed(selection):
        listbox_files.delete(index)

def start_conversion():
    try:
        start_time = entry_start_time.get()
        end_time = entry_end_time.get()
        video_bitrate = entry_video_bitrate.get()
        audio_bitrate = entry_audio_bitrate.get()
        fps = entry_fps.get()
        resolution = entry_resolution.get()

        if not start_time or not end_time:
            messagebox.showerror("Erreur", "Veuillez entrer les heures de début et de fin.")
            return

        validate_inputs(start_time, end_time, video_bitrate, audio_bitrate, fps, resolution)

        # Prepare FFmpeg once
        check_and_download_ffmpeg(root)
        if 'utils' in sys.modules:
            ffmpeg_path = utils.get_binary_path("ffmpeg.exe")
        else:
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
            
        if not os.path.exists(ffmpeg_path):
             messagebox.showerror("Erreur", "FFmpeg introuvable.")
             return

        for index in range(listbox_files.size()):
            input_file = listbox_files.get(index)
            if not os.path.isfile(input_file):
                messagebox.showerror("Erreur", f"Fichier non valide : {input_file}")
                continue
            
            # Determine output extension
            format_choice = selected_format.get()
            if format_choice == "MP4":
                ext = ".mp4"
            elif format_choice == "MKV":
                ext = ".mkv"
            else: # Source
                 ext = os.path.splitext(input_file)[1]

            if selected_output_option.get() == "folder":
                # Create output dir relative to input file
                input_dir = os.path.dirname(input_file)
                output_dir = os.path.join(input_dir, "vidéos_converties")
                os.makedirs(output_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(output_dir, base_name + ext)
            else:
                # Replace mode
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext).name
                convert_video(input_file, start_time, end_time, temp_file, video_bitrate, audio_bitrate, fps, resolution, root, ffmpeg_path=ffmpeg_path)
                
                # If extension changed, we must rename the target file
                if ext != os.path.splitext(input_file)[1]:
                     new_input_path = os.path.splitext(input_file)[0] + ext
                     shutil.move(temp_file, new_input_path)
                     try:
                        os.remove(input_file) # Remove the old extension file
                     except:
                        pass
                else:
                    shutil.move(temp_file, input_file)
                continue

            convert_video(input_file, start_time, end_time, output_file, video_bitrate, audio_bitrate, fps, resolution, root, ffmpeg_path=ffmpeg_path)

            # Capture d'image si les options sont cochées
            if capture_without_rotation_var.get() or capture_with_rotation_var.get():
                capture_dir = os.path.join(os.getcwd(), "captures")
                os.makedirs(capture_dir, exist_ok=True)
                file_name = os.path.basename(input_file)
                output_image = os.path.join(capture_dir, f"screenshot-{os.path.splitext(file_name)[0]}.png")

                if capture_without_rotation_var.get():
                    capture_first_frame(input_file, output_image, rotate=False, root=root, ffmpeg_path=ffmpeg_path)
                if capture_with_rotation_var.get():
                    capture_first_frame(input_file, output_image, rotate=True, root=root, ffmpeg_path=ffmpeg_path)

        messagebox.showinfo("Succès", "Traitement terminé pour toutes les vidéos.")
    except ValueError as ve:
        messagebox.showerror("Erreur de saisie", str(ve))
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def handle_drop(event):
    try:
        files = root.tk.splitlist(event.data)
        for file in files:
            listbox_files.insert("end", file)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du glisser-déposer : {e}")

# Wrapper pour supporter Drag & Drop avec CustomTkinter
class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

def main():
    global root, listbox_files, entry_start_time, entry_end_time, entry_video_bitrate, entry_audio_bitrate, entry_fps, entry_resolution, selected_output_option, capture_without_rotation_var, capture_with_rotation_var, selected_format

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Initialisation avec support DnD
    root = Tk()
    root.title("Trim et Convertisseur Vidéo par Lot")
    root.geometry("800x600")

    # Input file selection
    frame_input = ctk.CTkFrame(root)
    frame_input.pack(padx=10, pady=5, fill="x")

    label_input_files = ctk.CTkLabel(frame_input, text="Fichiers vidéo d'entrée (Glisser-Déposer accepté) :", font=("Arial", 16))
    label_input_files.pack(side="left")

    button_browse = ctk.CTkButton(frame_input, text="Ajouter des fichiers", command=browse_files, width=150)
    button_browse.pack(side="left", padx=5)

    button_clear = ctk.CTkButton(frame_input, text="Effacer la liste", command=clear_files, width=150)
    button_clear.pack(side="left", padx=5)

    # Listbox to show selected files
    listbox_files = Listbox(root, selectmode="multiple", height=8, width=80)
    listbox_files.pack(padx=10, pady=5, fill="both", expand=True)

    # Enable Drag & Drop
    listbox_files.drop_target_register(DND_FILES)
    listbox_files.dnd_bind('<<Drop>>', handle_drop)
    
    # Enable Delete key
    listbox_files.bind("<Delete>", delete_selected_files)

    # Start/End time & Format (Compact Row)
    frame_times = ctk.CTkFrame(root)
    frame_times.pack(padx=10, pady=5, fill="x")

    label_start_time = ctk.CTkLabel(frame_times, text="Début (HH:MM:SS) :", font=("Arial", 13))
    label_start_time.pack(side="left", padx=5)

    entry_start_time = ctk.CTkEntry(frame_times, width=80)
    entry_start_time.insert(0, "00:00:00")
    entry_start_time.pack(side="left", padx=5)

    label_end_time = ctk.CTkLabel(frame_times, text="Fin (HH:MM:SS) :", font=("Arial", 13))
    label_end_time.pack(side="left", padx=5)

    entry_end_time = ctk.CTkEntry(frame_times, width=80)
    entry_end_time.insert(0, "00:01:30")
    entry_end_time.pack(side="left", padx=5)

    # Output Format Selection (Moved here)
    label_format = ctk.CTkLabel(frame_times, text="Format :", font=("Arial", 13))
    label_format.pack(side="left", padx=(15, 5))
    
    selected_format = ctk.StringVar(value="Source")
    combo_format = ctk.CTkComboBox(frame_times, variable=selected_format, values=["Source", "MP4", "MKV"], width=80, state="readonly")
    combo_format.pack(side="left", padx=5)

    # Video settings inputs (Compact Row)
    frame_settings = ctk.CTkFrame(root)
    frame_settings.pack(padx=10, pady=5, fill="x")

    label_video_bitrate = ctk.CTkLabel(frame_settings, text="Vidéo (kbps) :", font=("Arial", 13))
    label_video_bitrate.pack(side="left", padx=5)

    entry_video_bitrate = ctk.CTkEntry(frame_settings, width=80)
    entry_video_bitrate.insert(0, "8000k")
    entry_video_bitrate.pack(side="left", padx=5)

    label_audio_bitrate = ctk.CTkLabel(frame_settings, text="Audio (kbps) :", font=("Arial", 13))
    label_audio_bitrate.pack(side="left", padx=5)

    entry_audio_bitrate = ctk.CTkEntry(frame_settings, width=80)
    entry_audio_bitrate.insert(0, "128k")
    entry_audio_bitrate.pack(side="left", padx=5)

    label_fps = ctk.CTkLabel(frame_settings, text="FPS :", font=("Arial", 13))
    label_fps.pack(side="left", padx=5)

    entry_fps = ctk.CTkEntry(frame_settings, width=60)
    entry_fps.insert(0, "30")
    entry_fps.pack(side="left", padx=5)

    label_resolution = ctk.CTkLabel(frame_settings, text="Résolution :", font=("Arial", 13))
    label_resolution.pack(side="left", padx=5)

    entry_resolution = ctk.CTkEntry(frame_settings, width=100)
    entry_resolution.insert(0, "1920x1080")
    entry_resolution.pack(side="left", padx=5)

    # Output options
    frame_output_options = ctk.CTkFrame(root)
    frame_output_options.pack(padx=10, pady=5, fill="x")

    selected_output_option = ctk.StringVar(value="folder")

    radio_folder = ctk.CTkRadioButton(frame_output_options, text="Exporter dans un sous-dossier 'vidéos_converties'", variable=selected_output_option, value="folder")
    radio_folder.pack(anchor="w", padx=10, pady=2)

    radio_replace = ctk.CTkRadioButton(frame_output_options, text="Remplacer les fichiers originaux", variable=selected_output_option, value="replace")
    radio_replace.pack(anchor="w", padx=10, pady=2)

    # Capture options
    frame_capture_options = ctk.CTkFrame(root)
    frame_capture_options.pack(padx=10, pady=5, fill="x")

    capture_without_rotation_var = BooleanVar()
    capture_with_rotation_var = BooleanVar()

    check_capture_without_rotation = ctk.CTkCheckBox(frame_capture_options, text="Capture d'une cover sans rotation", variable=capture_without_rotation_var)
    check_capture_without_rotation.pack(side="left", padx=10, pady=5)

    check_capture_with_rotation = ctk.CTkCheckBox(frame_capture_options, text="Capture d'une cover avec rotation", variable=capture_with_rotation_var)
    check_capture_with_rotation.pack(side="left", padx=10, pady=5)

    # Convert button
    button_convert = ctk.CTkButton(root, text="Convertir", command=start_conversion, width=200, height=40, font=("Arial", 14, "bold"))
    button_convert.pack(pady=10)

    # Check dependencies at startup
    check_and_download_ffmpeg(root)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()