import os
import subprocess
import requests
# import zipfile
import tempfile
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, Checkbutton, BooleanVar
import sys

# Import utils
try:
    import utils
except ImportError:
    pass

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
                 # utils.DependencyManager logic might need enhancement if we want to extract from subfolder
                 # The current generic extract logic in utils might fail if ffmpeg.exe is in a subfolder 
                 # BUT, I already updated convert_images which uses the same install_dependency call 
                 # and I didn't see an explicit "scan subfolders" update in utils.
                 # Wait, looking at utils.py code earlier...
                 # It does:
                 # for root, dirs, files in os.walk(extract_dir):
                 #    if target_exe_name in files:
                 #        found_file = os.path.join(root, target_exe_name)
                 # So yes, it finds it recursively!
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

        if not start_time or not end_time:
            messagebox.showerror("Erreur", "Veuillez entrer les heures de début et de fin.")
            return

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

            if selected_output_option.get() == "folder":
                # Create output dir relative to input file
                input_dir = os.path.dirname(input_file)
                output_dir = os.path.join(input_dir, "vidéos_converties")
                os.makedirs(output_dir, exist_ok=True)
                
                file_name = os.path.basename(input_file)
                output_file = os.path.join(output_dir, file_name)
            else:
                # Replace mode
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                convert_video(input_file, start_time, end_time, temp_file, video_bitrate, audio_bitrate, fps, resolution, root, ffmpeg_path=ffmpeg_path)
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
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def handle_drop(event):
    try:
        files = event.data.strip().split()
        for file in files:
            listbox_files.insert("end", file)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du glisser-déposer : {e}")

# Configuration de l'apparence de l'interface
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème de couleur bleu

# Création de la fenêtre principale
root = ctk.CTk()
root.title("Trim et Convertisseur Vidéo par Lot")

def main():
    global root, listbox_files, entry_start_time, entry_end_time, entry_video_bitrate, entry_audio_bitrate, entry_fps, entry_resolution, selected_output_option, capture_without_rotation_var, capture_with_rotation_var

    # Configuration de l'apparence de l'interface
    ctk.set_appearance_mode("dark")  # Mode sombre
    ctk.set_default_color_theme("blue")  # Thème de couleur bleu

    # Création de la fenêtre principale
    root = ctk.CTk()
    root.title("Trim et Convertisseur Vidéo par Lot")

    # Input file selection
    frame_input = ctk.CTkFrame(root)
    frame_input.pack(padx=10, pady=5, fill="x")

    label_input_files = ctk.CTkLabel(frame_input, text="Fichiers vidéo d'entrée :", font=("Arial", 16))
    label_input_files.pack(side="left")

    button_browse = ctk.CTkButton(frame_input, text="Ajouter des fichiers", command=browse_files, width=200)
    button_browse.pack(side="left", padx=5)

    button_clear = ctk.CTkButton(frame_input, text="Effacer la liste", command=clear_files, width=200)
    button_clear.pack(side="left", padx=5)

    # Listbox to show selected files
    listbox_files = Listbox(root, selectmode="multiple", height=10, width=80)
    listbox_files.pack(padx=10, pady=5)

    # Start and end time inputs
    frame_times = ctk.CTkFrame(root)
    frame_times.pack(padx=10, pady=5, fill="x")

    label_start_time = ctk.CTkLabel(frame_times, text="Heure de début (HH:MM:SS) :", font=("Arial", 14))
    label_start_time.pack(side="left")

    entry_start_time = ctk.CTkEntry(frame_times, width=100)
    entry_start_time.insert(0, "00:00:00")
    entry_start_time.pack(side="left", padx=5)

    label_end_time = ctk.CTkLabel(frame_times, text="Heure de fin (HH:MM:SS) :", font=("Arial", 14))
    label_end_time.pack(side="left")

    entry_end_time = ctk.CTkEntry(frame_times, width=100)
    entry_end_time.insert(0, "00:01:30")
    entry_end_time.pack(side="left", padx=5)

    # Video settings inputs
    frame_settings = ctk.CTkFrame(root)
    frame_settings.pack(padx=10, pady=5, fill="x")

    label_video_bitrate = ctk.CTkLabel(frame_settings, text="Débit vidéo (kbps) :", font=("Arial", 14))
    label_video_bitrate.pack(side="left")

    entry_video_bitrate = ctk.CTkEntry(frame_settings, width=100)
    entry_video_bitrate.insert(0, "8000k")
    entry_video_bitrate.pack(side="left", padx=5)

    label_audio_bitrate = ctk.CTkLabel(frame_settings, text="Débit audio (kbps) :", font=("Arial", 14))
    label_audio_bitrate.pack(side="left")

    entry_audio_bitrate = ctk.CTkEntry(frame_settings, width=100)
    entry_audio_bitrate.insert(0, "128k")
    entry_audio_bitrate.pack(side="left", padx=5)

    label_fps = ctk.CTkLabel(frame_settings, text="FPS :", font=("Arial", 14))
    label_fps.pack(side="left")

    entry_fps = ctk.CTkEntry(frame_settings, width=100)
    entry_fps.insert(0, "30")
    entry_fps.pack(side="left", padx=5)

    label_resolution = ctk.CTkLabel(frame_settings, text="Résolution (LxH) :", font=("Arial", 14))
    label_resolution.pack(side="left")

    entry_resolution = ctk.CTkEntry(frame_settings, width=100)
    entry_resolution.insert(0, "1920x1080")
    entry_resolution.pack(side="left", padx=5)

    # Output options
    frame_output_options = ctk.CTkFrame(root)
    frame_output_options.pack(padx=10, pady=5, fill="x")

    selected_output_option = ctk.StringVar(value="folder")

    radio_folder = ctk.CTkRadioButton(frame_output_options, text="Exporter dans un sous-dossier 'vidéos_converties'", variable=selected_output_option, value="folder")
    radio_folder.pack(anchor="w")

    radio_replace = ctk.CTkRadioButton(frame_output_options, text="Remplacer les fichiers originaux", variable=selected_output_option, value="replace")
    radio_replace.pack(anchor="w")

    # Capture options
    frame_capture_options = ctk.CTkFrame(root)
    frame_capture_options.pack(padx=10, pady=5, fill="x")

    capture_without_rotation_var = BooleanVar()
    capture_with_rotation_var = BooleanVar()

    check_capture_without_rotation = ctk.CTkCheckBox(frame_capture_options, text="Capture d'une cover sans rotation", variable=capture_without_rotation_var)
    check_capture_without_rotation.pack(anchor="w")

    check_capture_with_rotation = ctk.CTkCheckBox(frame_capture_options, text="Capture d'une cover avec rotation", variable=capture_with_rotation_var)
    check_capture_with_rotation.pack(anchor="w")

    # Convert button
    button_convert = ctk.CTkButton(root, text="Convertir", command=start_conversion, width=200)
    button_convert.pack(pady=10)

    # Check dependencies at startup
    check_and_download_ffmpeg(root)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()