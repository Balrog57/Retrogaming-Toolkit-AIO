import os
import subprocess
import requests
import zipfile
from tkinter import filedialog, messagebox
import tkinter as tk
import tempfile
import shutil

def check_and_download_ffmpeg():
    ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        try:
            messagebox.showinfo("Téléchargement", "FFmpeg n'est pas trouvé. Téléchargement en cours...")
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"  # Lien officiel vers FFmpeg
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name

            # Télécharger FFmpeg
            response = requests.get(url, stream=True)
            with open(temp_zip, "wb") as f:
                shutil.copyfileobj(response.raw, f)

            # Extraire le fichier téléchargé
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Rechercher ffmpeg.exe dans le dossier extrait
            for root, dirs, files in os.walk(extract_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_extracted_path = os.path.join(root, "ffmpeg.exe")
                    shutil.move(ffmpeg_extracted_path, ffmpeg_path)
                    break
            else:
                raise FileNotFoundError("Le fichier ffmpeg.exe n'a pas été trouvé après extraction.")

            os.remove(temp_zip)
            messagebox.showinfo("Succès", "FFmpeg a été téléchargé et configuré avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec du téléchargement de FFmpeg : {e}")
            raise SystemExit("Impossible de continuer sans FFmpeg.")

def convert_video(input_file, start_time, end_time, output_file, video_bitrate, audio_bitrate, fps, resolution):
    check_and_download_ffmpeg()  # Vérifiez et téléchargez FFmpeg si nécessaire
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

def browse_files():
    try:
        file_paths = filedialog.askopenfilenames(filetypes=[("Tous les fichiers vidéo", "*.*")])
        if file_paths:
            for file_path in file_paths:
                listbox_files.insert(tk.END, file_path)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la sélection des fichiers : {e}")

def clear_files():
    listbox_files.delete(0, tk.END)

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

        if selected_output_option.get() == "folder":
            output_dir = os.path.join(os.getcwd(), "vidéos_converties")
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = None

        for index in range(listbox_files.size()):
            input_file = listbox_files.get(index)
            if not os.path.isfile(input_file):
                messagebox.showerror("Erreur", f"Fichier non valide : {input_file}")
                continue

            if output_dir:
                file_name = os.path.basename(input_file)
                output_file = os.path.join(output_dir, f"trimmed_{file_name}")
            else:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                convert_video(input_file, start_time, end_time, temp_file, video_bitrate, audio_bitrate, fps, resolution)
                shutil.move(temp_file, input_file)
                continue

            convert_video(input_file, start_time, end_time, output_file, video_bitrate, audio_bitrate, fps, resolution)

        messagebox.showinfo("Succès", "Traitement terminé pour toutes les vidéos.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def handle_drop(event):
    try:
        files = event.data.strip().split()
        for file in files:
            listbox_files.insert(tk.END, file)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du glisser-déposer : {e}")

# Create the main application window
root = tk.Tk()
root.title("Trim et Convertisseur Vidéo par Lot")

# Input file selection
frame_input = tk.Frame(root)
frame_input.pack(padx=10, pady=5, fill="x")

label_input_files = tk.Label(frame_input, text="Fichiers vidéo d'entrée :")
label_input_files.pack(side="left")

button_browse = tk.Button(frame_input, text="Ajouter des fichiers", command=browse_files)
button_browse.pack(side="left")

button_clear = tk.Button(frame_input, text="Effacer la liste", command=clear_files)
button_clear.pack(side="left")

# Listbox to show selected files
listbox_files = tk.Listbox(root, selectmode=tk.MULTIPLE, height=10, width=80)
listbox_files.pack(padx=10, pady=5)

# Start and end time inputs
frame_times = tk.Frame(root)
frame_times.pack(padx=10, pady=5, fill="x")

label_start_time = tk.Label(frame_times, text="Heure de début (HH:MM:SS) :")
label_start_time.pack(side="left")

entry_start_time = tk.Entry(frame_times, width=10)
entry_start_time.insert(0, "00:00:00")
entry_start_time.pack(side="left", padx=5)

label_end_time = tk.Label(frame_times, text="Heure de fin (HH:MM:SS) :")
label_end_time.pack(side="left")

entry_end_time = tk.Entry(frame_times, width=10)
entry_end_time.insert(0, "00:01:30")
entry_end_time.pack(side="left", padx=5)

# Video settings inputs
frame_settings = tk.Frame(root)
frame_settings.pack(padx=10, pady=5, fill="x")

label_video_bitrate = tk.Label(frame_settings, text="Débit vidéo (kbps) :")
label_video_bitrate.pack(side="left")

entry_video_bitrate = tk.Entry(frame_settings, width=10)
entry_video_bitrate.insert(0, "8000k")
entry_video_bitrate.pack(side="left", padx=5)

label_audio_bitrate = tk.Label(frame_settings, text="Débit audio (kbps) :")
label_audio_bitrate.pack(side="left")

entry_audio_bitrate = tk.Entry(frame_settings, width=10)
entry_audio_bitrate.insert(0, "128k")
entry_audio_bitrate.pack(side="left", padx=5)

label_fps = tk.Label(frame_settings, text="FPS :")
label_fps.pack(side="left")

entry_fps = tk.Entry(frame_settings, width=10)
entry_fps.insert(0, "30")
entry_fps.pack(side="left", padx=5)

label_resolution = tk.Label(frame_settings, text="Résolution (LxH) :")
label_resolution.pack(side="left")

entry_resolution = tk.Entry(frame_settings, width=10)
entry_resolution.insert(0, "1920x1080")
entry_resolution.pack(side="left", padx=5)

# Output options
frame_output_options = tk.Frame(root)
frame_output_options.pack(padx=10, pady=5, fill="x")

selected_output_option = tk.StringVar(value="folder")

radio_folder = tk.Radiobutton(frame_output_options, text="Exporter dans un sous-dossier 'vidéos_converties'", variable=selected_output_option, value="folder")
radio_folder.pack(anchor="w")

radio_replace = tk.Radiobutton(frame_output_options, text="Remplacer les fichiers originaux", variable=selected_output_option, value="replace")
radio_replace.pack(anchor="w")

# Convert button
button_convert = tk.Button(root, text="Convertir", command=start_conversion)
button_convert.pack(pady=10)

# Run the application
root.mainloop()
