import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # PyInstaller --onedir
        # The data files are located relative to the executable
        # If we use --onefile, they are in sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
             base_path = sys._MEIPASS
        else:
             base_path = os.path.dirname(sys.executable)
    else:
        # Dev mode: assumes running from root
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_binary_path(binary_name):
    """ Get path to external binary """
    possible_paths = []
    
    # 1. Check AppData (User downloaded updates)
    app_data_path = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit', binary_name)
    possible_paths.append(app_data_path)

    if getattr(sys, 'frozen', False):
        # Frozen: Binaries are expected to be next to the executable OR in _internal
        base_path = os.path.dirname(sys.executable)
        possible_paths.append(os.path.join(base_path, binary_name))
        possible_paths.append(os.path.join(base_path, "_internal", binary_name))
    else:
        # Source: Binaries are in the root
        base_path = os.getcwd()
        possible_paths.append(os.path.join(base_path, binary_name))

    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    # Default return (even if not exists, so code can check generic path)
    if getattr(sys, 'frozen', False):
         return os.path.join(os.path.dirname(sys.executable), binary_name)
    return os.path.join(os.getcwd(), binary_name)

def is_frozen():
    return getattr(sys, 'frozen', False)

def fetch_latest_github_asset(owner, repo, match_keyword):
    """
    Fetches the download URL for the latest release asset from a GitHub repository.
    match_keyword: substring to look for in asset name (case insensitive).
    """
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        logging.info(f"Checking GitHub latest release: {api_url}")
        response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        assets = data.get('assets', [])
        
        for asset in assets:
            name = asset.get('name', '').lower()
            if match_keyword.lower() in name and name.endswith('.zip'):
                download_url = asset.get('browser_download_url')
                logging.info(f"Found asset: {name} -> {download_url}")
                return download_url
                
        logging.warning(f"No asset matching '{match_keyword}' found in {owner}/{repo}")
        return None
    except Exception as e:
        logging.error(f"Error fetching GitHub release info: {e}")
        return None
    
# --- Dependency Manager ---
import requests
import subprocess
import shutil
import tempfile
import zipfile
import threading
import customtkinter as ctk
from tkinter import messagebox
import logging

KNOWN_DEPENDENCIES = {
    "FFmpeg": {
        "url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "target_exe_name": "ffmpeg.exe",
        "archive_type": "zip"
    },
    "MaxCSO": {
        "url": "https://github.com/unknownbrackets/maxcso/releases/download/v1.13.0/maxcso_v1.13.0_windows.7z",
        "target_exe_name": "maxcso.exe",
        "archive_type": "7z"
    },
    "CHDman (MAME)": {
        "url": "https://github.com/mamedev/mame/releases/download/mame0284/mame0284b_x64.exe",
        "target_exe_name": "chdman.exe",
        "archive_type": "exe_sfx",
        "extract_file_in_archive": "chdman.exe"
    }
}

class DependencyManager:
    def __init__(self, root=None):
        self.app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'RetrogamingToolkit')
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
        self.seven_za_path = os.path.join(self.app_data_dir, "7za.exe")
        self.root = root

    def get_headers(self):
        return {'User-Agent': 'Mozilla/5.0'}

    def bootstrap_7za(self):
        """Ensures 7za.exe is available for extracting other archives."""
        if os.path.exists(self.seven_za_path):
            return True
        
        # Download 7za
        url = "https://www.7-zip.org/a/7za920.zip"
        zip_path = os.path.join(tempfile.gettempdir(), "7za920.zip")
        
        try:
            r = requests.get(url, headers=self.get_headers(), stream=True)
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                f.write(r.content)
            
            with zipfile.ZipFile(zip_path, 'r') as z:
                for file in z.namelist():
                    if file == "7za.exe":
                        z.extract(file, self.app_data_dir)
                        break
            
            return os.path.exists(self.seven_za_path)
        except Exception as e:
            print(f"Failed to bootstrap 7za: {e}")
            return False
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

    def download_with_progress(self, url, dest_path, description="Téléchargement"):
        """Downloads a file with a progress bar UI."""
        # Setup UI
        progress_win = ctk.CTkToplevel(self.root)
        progress_win.title("Téléchargement Requis")
        progress_win.geometry("400x150")
        progress_win.transient(self.root) 
        progress_win.grab_set()
        
        # Center window logic could be added here
        
        ctk.CTkLabel(progress_win, text=f"{description}...", font=("Arial", 14)).pack(pady=10)
        
        progress_bar = ctk.CTkProgressBar(progress_win, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        status_label = ctk.CTkLabel(progress_win, text="0%")
        status_label.pack(pady=5)
        
        result_container = {"success": False, "error": None}
        
        import queue
        progress_queue = queue.Queue()
        stop_event = threading.Event()
        
        def on_close():
            stop_event.set()
            progress_win.destroy()
            
        progress_win.protocol("WM_DELETE_WINDOW", on_close)
        
        def _download_thread():
            try:
                logging.info(f"Starting download: {url}")
                response = requests.get(url, headers=self.get_headers(), stream=True, timeout=60)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                logging.info(f"Content-Length: {total_size}")
                
                with open(dest_path, 'wb') as f:
                    chunk_count = 0
                    last_reported_bytes = 0
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if stop_event.is_set():
                            logging.warning("Download cancelled by user.")
                            raise Exception("Download cancelled")
                        f.write(chunk)
                        downloaded += len(chunk)
                        chunk_count += 1
                        
                        # Update GUI every 200KB or so to prevent freeze, logic simplified via mod
                        # 8KB * 25 = 200KB
                        if chunk_count % 25 == 0 or downloaded == total_size:
                            if total_size > 0:
                                progress = downloaded / total_size
                                progress_queue.put(("progress", progress))
                                progress_queue.put(("status", f"{int(progress*100)}%"))
                            else:
                                # Unknown size, just show downloaded MB
                                mb = downloaded / (1024*1024)
                                progress_queue.put(("status", f"{mb:.1f} MB"))
                                
                        if chunk_count % 500 == 0: # Log every ~4MB
                            logging.debug(f"Downloaded {downloaded} bytes")
                
                logging.info("Download finished.")
                if not stop_event.is_set():
                    result_container["success"] = True
                    progress_queue.put(("done", None))
            except Exception as e:
                logging.error(f"Download error: {e}")
                result_container["error"] = str(e)
                progress_queue.put(("done", None))

        t = threading.Thread(target=_download_thread)
        t.start()
        
        def process_queue():
             try:
                 while True:
                     msg_type, data = progress_queue.get_nowait()
                     if msg_type == "progress":
                         if progress_win.winfo_exists():
                            progress_bar.set(data)
                     elif msg_type == "status":
                         if progress_win.winfo_exists():
                            status_label.configure(text=data)
                     elif msg_type == "done":
                         if progress_win.winfo_exists():
                            progress_win.destroy()
                         return # Stop polling
             except queue.Empty:
                 pass
             
             if not stop_event.is_set() and progress_win.winfo_exists():
                progress_win.after(100, process_queue)
             else:
                stop_event.set() # Ensure thread stops if window died unexpectedly

        process_queue()



        
        # Keep main loop responsive
        if self.root:
            self.root.wait_window(progress_win)
        else:
            t.join()
            
        if not result_container["success"]:
            raise Exception(result_container["error"] if result_container["error"] else "Unknown error")

    def install_dependency(self, name, url=None, target_exe_name=None, archive_type=None, extract_file_in_archive=None):
        """
        Main method to install a dependency.
        name: Display name (e.g. "MaxCSO")
        url: Download URL (optional if name is in KNOWN_DEPENDENCIES)
        target_exe_name: Name of the final exe (optional if name is in KNOWN_DEPENDENCIES)
        archive_type: '7z', 'zip', 'exe_sfx' (optional if name is in KNOWN_DEPENDENCIES)
        extract_file_in_archive: If specific file needs to be pulled from archive.
        """
        # Apply defaults from KNOWN_DEPENDENCIES if available
        if name in KNOWN_DEPENDENCIES:
            config = KNOWN_DEPENDENCIES[name]
            url = url or config.get("url")
            target_exe_name = target_exe_name or config.get("target_exe_name")
            archive_type = archive_type or config.get("archive_type", "7z")
            extract_file_in_archive = extract_file_in_archive or config.get("extract_file_in_archive")

        # Set default archive_type if still None
        if archive_type is None:
            archive_type = '7z'

        if not url or not target_exe_name:
             raise ValueError(f"Missing configuration for dependency '{name}' and no defaults found.")

        target_path = os.path.join(self.app_data_dir, target_exe_name)
        
        # Check existing
        if os.path.exists(target_path):
            return target_path
            
        bundled = get_binary_path(target_exe_name)
        if os.path.exists(bundled) and bundled != target_path: # Avoid circular if bundled is appdata
             return bundled

        # If missing, automatically download (User requested no prompt)
        logging.info(f"Dependency {name} missing, starting auto-download.")
        # if not messagebox.askyesno("Outil Manquant", f"{name} est manquant. Voulez-vous le télécharger et l'installer ?"):
        #      return None

        try:
             # Ensure 7za
             if not self.bootstrap_7za():
                 raise Exception("Could not install 7-Zip engine.")

             # Download
             temp_download = os.path.join(tempfile.gettempdir(), f"temp_dep_{target_exe_name}.{archive_type}")
             self.download_with_progress(url, temp_download, f"Téléchargement de {name}")
             
             # Extract
             extract_dir = tempfile.mkdtemp()
             
             # Command construction
             # 7za x archive -o{dir} -y
             cmd = [self.seven_za_path, 'x' if archive_type != 'exe_sfx' else 'e', temp_download, f'-o{extract_dir}', '-y']
             
             if extract_file_in_archive:
                 cmd.append(extract_file_in_archive)
                 
             startupinfo = subprocess.STARTUPINFO()
             startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
             
             subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)
             
             # Find file
             found_file = None
             for root, dirs, files in os.walk(extract_dir):
                 if target_exe_name in files:
                     found_file = os.path.join(root, target_exe_name)
                     break
             
             if found_file:
                 shutil.move(found_file, target_path)
             else:
                 raise Exception(f"{target_exe_name} not found in archive.")
                 
             # Cleanup
             shutil.rmtree(extract_dir, ignore_errors=True)
             if os.path.exists(temp_download):
                 os.remove(temp_download)
                 
             # messagebox.showinfo("Succès", f"{name} installé avec succès.") # Implicit success, no popup needed if auto
             # Maybe just log it? User wants "ouvre le script demande".
             logging.info(f"{name} installed successfully.")
             return target_path

        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation de {name} : {e}")
            return None

def extract_with_7za(archive_path, output_dir, file_to_extract=None, root=None):
    """
    Extracts an archive using the bootstrapped 7za.exe.
    Supports 7z, zip, rar, etc.
    """
    manager = DependencyManager(root)
    if not manager.bootstrap_7za():
        raise Exception("Impossible d'installer 7za.exe pour l'extraction.")
    
    cmd = [manager.seven_za_path, 'x', archive_path, f'-o{output_dir}', '-y']
    
    if file_to_extract:
         cmd.append(file_to_extract)
         
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)

