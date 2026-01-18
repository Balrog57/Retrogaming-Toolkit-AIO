import os
import shutil
import subprocess
import requests

import re
import glob
import tempfile
import customtkinter as ctk
from tkinter import messagebox
from threading import Thread

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def log(message):
    print(message)

def get_tpu_download_link(url):
    """
    Scrapes the direct download link from a TechPowerUp download page.
    """
    try:
        log(f"Fetching {url}...")
        s = requests.Session()
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        r = s.get(url, timeout=15)
        if r.status_code != 200:
            log(f"Failed to load page: {r.status_code}")
            return None
        
        # Find file ID
        id_match = re.search(r'input[^>]*name=["\']id["\'][^>]*value=["\'](\d+)["\']', r.text, re.IGNORECASE)
        if not id_match:
            id_match = re.search(r'value=["\'](\d+)["\'][^>]*name=["\']id["\']', r.text, re.IGNORECASE)
            
        if not id_match:
            log("Could not find file ID on TechPowerUp page.")
            return None
            
        file_id = id_match.group(1)
        
        # Find server ID
        # Try to find any button/input with name="server_id" and capture its value
        # Pattern 1: name="server_id" ... value="X"
        server_match = re.search(r'name=["\']server_id["\'][^>]*value=["\'](\d+)["\']', r.text, re.IGNORECASE)
        # Pattern 2: value="X" ... name="server_id"
        if not server_match:
            server_match = re.search(r'value=["\'](\d+)["\'][^>]*name=["\']server_id["\']', r.text, re.IGNORECASE)
            
        server_id = server_match.group(1) if server_match else "12"
        log(f"Found Server ID: {server_id}")
        
        # Submit the form to get the link
        data = {'id': file_id, 'server_id': server_id}
        log(f"Requesting download link (ID: {file_id}, Server: {server_id})...")
        
        r_post = s.post(url, data=data, allow_redirects=False)
        
        if r_post.status_code in [301, 302, 303, 307]:
            return r_post.headers.get('Location')
        elif r_post.status_code == 200:
            # Check for meta refresh
            meta_match = re.search(r'http-equiv=["\']refresh["\'][^>]*content=["\']\d+;\s*url=([^"\']+)["\']', r_post.text, re.IGNORECASE)
            if meta_match:
                return meta_match.group(1)
            # Check for 'click here' link
            link_match = re.search(r'href=["\']([^"\']+)["\'][^>]*>click here<', r_post.text, re.IGNORECASE)
            if link_match:
                return link_match.group(1)
                
        log("No download link found in response.")
        return None
    except Exception as e:
        log(f"Error scraping TechPowerUp: {e}")
        return None

def download_file(url, target_path):
    """
    Downloads a file from a URL to a target path.
    """
    try:
        log(f"Downloading {url} to {target_path}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(target_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return True
    except Exception as e:
        log(f"Error downloading {url}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """
    Extracts a zip file using 7za via utils.
    """
    try:
        log(f"Extracting {zip_path} to {extract_to}...")
        try:
            import utils
        except ImportError:
            log("Error: utils module not found. cannot use 7za.")
            return False

        utils.extract_with_7za(zip_path, extract_to)
        return True
    except Exception as e:
        log(f"Error extracting {zip_path}: {e}")
        return False

def run_command(command, args, cwd=None):
    """
    Runs a command with arguments.
    """
    try:
        full_command = f'"{command}" {args}'
        log(f"Executing: {full_command}")
        process = subprocess.Popen(full_command, shell=True, cwd=cwd)
        process.wait()
        return process.returncode == 0
    except Exception as e:
        log(f"Error running command: {e}")
        return False

def install_logic(status_label, progress_bar):
    temp_dir = tempfile.mkdtemp()
    log(f"Created temporary directory: {temp_dir}")
    
    status_label.configure(text="Initialisation...")
    progress_bar.set(0)
    
    try:
        # --- 1. OpenAL ---
        status_label.configure(text="Installation d'OpenAL...")
        openal_url = "https://www.openal.org/downloads/oalinst.zip"
        openal_zip = os.path.join(temp_dir, "oalinst.zip")
        openal_dir = os.path.join(temp_dir, "openal")
        
        if download_file(openal_url, openal_zip):
            if extract_zip(openal_zip, openal_dir):
                oal_exe = os.path.join(openal_dir, "oalinst.exe")
                if os.path.exists(oal_exe):
                    run_command(oal_exe, "/silent")
                else:
                    log("oalinst.exe not found")
        progress_bar.set(0.33)

        # --- 2. DirectX ---
        status_label.configure(text="Installation de DirectX...")
        dx_page = "https://www.techpowerup.com/download/directx-redistributable-runtime/"
        dx_url = get_tpu_download_link(dx_page)
        
        if dx_url:
            dx_zip = os.path.join(temp_dir, "dx.zip")
            dx_dir = os.path.join(temp_dir, "directx")
            
            if download_file(dx_url, dx_zip):
                if extract_zip(dx_zip, dx_dir):
                    dx_setup = os.path.join(dx_dir, "DXSETUP.exe")
                    if os.path.exists(dx_setup):
                        run_command(dx_setup, "/silent")
                    else:
                        log("DXSETUP.exe not found")
        else:
            log("Failed to get DirectX download link")
        progress_bar.set(0.66)

        # --- 3. Visual C++ AIO ---
        status_label.configure(text="Installation de Visual C++ AIO...")
        vc_page = "https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/"
        vc_url = get_tpu_download_link(vc_page)
        
        if vc_url:
            vc_zip = os.path.join(temp_dir, "vc.zip")
            vc_dir = os.path.join(temp_dir, "vc_aio")
            
            if download_file(vc_url, vc_zip):
                if extract_zip(vc_zip, vc_dir):
                    # Look for install_all.bat
                    bat_files = glob.glob(os.path.join(vc_dir, "install_all.bat"))
                    if bat_files:
                        # Assuming Abbodi repack, usually just running it works, but verifying if flags needed.
                        # Usually it prompts unless /y is passed? Common repacks use /y for silent.
                        run_command(bat_files[0], "/y", cwd=vc_dir)
                    else:
                        log("install_all.bat not found in VC pack")
        else:
            log("Failed to get VC++ AIO download link")
            
        progress_bar.set(1.0)
        status_label.configure(text="Terminé !")
        messagebox.showinfo("Succès", "Toutes les installations sont terminées.")
        
    except Exception as e:
        log(f"Global error: {e}")
        messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")
    finally:
        log("Cleaning up...")
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            log(f"Failed to cleanup temp dir: {e}")

def start_installation(status_label, progress_bar, button):
    button.configure(state="disabled")
    thread = Thread(target=install_logic, args=(status_label, progress_bar))
    thread.start()

def main():
    root = ctk.CTk()
    root.title("Installation des dépendances (Téléchargement)")
    root.geometry("400x250")

    label = ctk.CTkLabel(root, text="Installation automatique des dépendances\n(OpenAL, DirectX, Visual C++)", font=("Arial", 14))
    label.pack(pady=20)
    
    status_label = ctk.CTkLabel(root, text="Prêt", font=("Arial", 12))
    status_label.pack(pady=5)
    
    progress = ctk.CTkProgressBar(root)
    progress.set(0)
    progress.pack(pady=10)

    install_button = ctk.CTkButton(root, text="Télécharger et Installer", 
                                 command=lambda: start_installation(status_label, progress, install_button))
    install_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
