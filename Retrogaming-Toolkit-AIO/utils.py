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

    def bootstrap_7z_sfx(self):
        """Ensures 7z.sfx (or compatible) is available."""
        # Prefer default name
        sfx_target = os.path.join(self.app_data_dir, "7z.sfx")
        if os.path.exists(sfx_target):
            return sfx_target
        
        # 1. Try Local Installation (C:\Program Files\7-Zip\7z.sfx)
        local_sfx = r"C:\Program Files\7-Zip\7z.sfx"
        if os.path.exists(local_sfx):
            print(f"DEBUG: Found local 7z.sfx at {local_sfx}")
            try:
                shutil.copy2(local_sfx, sfx_target)
                return sfx_target
            except Exception as e:
                print(f"DEBUG: Failed to copy local SFX: {e}")

        # 2. We need 7za to extract .7z archives (chicken and egg handled by bootstrap_7za check below)
        if not self.bootstrap_7za():
            return None

        # Download 7z extra
        url = "https://www.7-zip.org/a/7z2301-extra.7z"
        temp_7z = os.path.join(tempfile.gettempdir(), "7z_extra.7z")
        
        try:
            print(f"DEBUG: Attempting to download {url} to {temp_7z}")
            self.download_with_progress(url, temp_7z, "Téléchargement 7z SFX Modules")
            
            # Extract ALL .sfx files
            print(f"DEBUG: Extracting *.sfx from {temp_7z}")
            # 7za e archive -o{dir} *.sfx -r -y
            cmd = [self.seven_za_path, 'e', temp_7z, f'-o{self.app_data_dir}', '*.sfx', '-r', '-y']
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)
            
            # Check for candidates
            candidates = [f for f in os.listdir(self.app_data_dir) if f.lower().endswith('.sfx')]
            print(f"DEBUG: Found sfx candidates: {candidates}")
            
            if not candidates:
                return None
                
            # Selection priority: 7z.sfx > 7zS.sfx (GUI) > 7zCon.sfx > others
            selected = None
            if "7z.sfx" in candidates: selected = "7z.sfx"
            elif "7zS.sfx" in candidates: selected = "7zS.sfx"
            elif "7zCon.sfx" in candidates: selected = "7zCon.sfx"
            else: selected = candidates[0]
            
            # If selected is not 7z.sfx, copy/rename it to 7z.sfx for consistency or just return it?
            # Let's return the actual path, logic handles variable path.
            # But PackWrapper expects "7z.sfx" hardcoded in on_start check?
            # Wait, PackWrapper logic: sfx_module = os.path.join(dep_manager.app_data_dir, "7z.sfx") in replace_file_content step 230/234
            # I changed PackWrapper to: sfx_module = os.path.join(dep_manager.app_data_dir, "7z.sfx")
            # So I should RENAMME/COPY the best candidate to 7z.sfx to guarantee PackWrapper finds it.
            
            src = os.path.join(self.app_data_dir, selected)
            if selected != "7z.sfx":
                shutil.copy2(src, sfx_target)
                
            return sfx_target
            
        except Exception as e:
            logging.error(f"Failed to bootstrap SFX: {e}")
            print(f"DEBUG ERROR: {e}")
            return None
        finally:
            if os.path.exists(temp_7z):
                try: os.remove(temp_7z)
                except: pass

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

    def install_dependency(self, name, url, target_exe_name, archive_type='7z', extract_file_in_archive=None):
        """
        Main method to install a dependency.
        name: Display name (e.g. "MaxCSO")
        url: Download URL
        target_exe_name: Name of the final exe (e.g. "maxcso.exe")
        archive_type: '7z', 'zip', 'exe_sfx' (like MAME)
        extract_file_in_archive: If specific file needs to be pulled from archive. If None, assumes simple structure or looks for target_exe_name.
        """
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

        temp_download = None
        extract_dir = None
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
             cmd = [self.seven_za_path, 'x' if archive_type != 'exe_sfx' else 'e', f'-o{extract_dir}', '-y', '--', temp_download]
             
             if extract_file_in_archive:
                 cmd.append(extract_file_in_archive)
                 
             startupinfo = None
             if os.name == 'nt':
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
                 
             logging.info(f"{name} installed successfully.")
             return target_path

        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'installation de {name} : {e}")
            return None
        finally:
            # Cleanup
            if extract_dir and os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)
            if temp_download and os.path.exists(temp_download):
                try:
                    os.remove(temp_download)
                except OSError:
                    pass

def extract_with_7za(archive_path, output_dir, file_to_extract=None, root=None):
    """
    Extracts an archive using the bootstrapped 7za.exe.
    Supports 7z, zip, rar, etc.
    """
    manager = DependencyManager(root)
    if not manager.bootstrap_7za():
        raise Exception("Impossible d'installer 7za.exe pour l'extraction.")
    
    cmd = [manager.seven_za_path, 'x', f'-o{output_dir}', '-y', '--', archive_path]
    
    if file_to_extract:
         cmd.append(file_to_extract)
         
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)

