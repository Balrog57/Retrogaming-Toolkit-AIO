import os
import io
import sys
import zipfile
import shutil
import requests

def download_vlc():
    # VLC Version to download
    VLC_VERSION = "3.0.21"
    VLC_URL = f"http://download.videolan.org/pub/videolan/vlc/{VLC_VERSION}/win64/vlc-{VLC_VERSION}-win64.zip"
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "Retrogaming-Toolkit-AIO", "vlc")
    
    if os.path.exists(target_dir):
        print(f"VLC directory already exists at {target_dir}")
        # Validate if it has content? For now assume if it exists it's fine or user cleans it.
        # But to be safe, let's allow overwrite if user wants, or just skip.
        # For this script, we'll just return if it looks populated.
        if os.path.exists(os.path.join(target_dir, "libvlc.dll")):
             print("libvlc.dll found. Skipping download.")
             return

    print(f"Downloading VLC {VLC_VERSION} from {VLC_URL}...")
    try:
        response = requests.get(VLC_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to download VLC: {e}")
        sys.exit(1)
        
    print("Download complete. Extracting...")
    
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # We need to extract only the needed files
            # Structure in zip is vlc-3.0.21/libvlc.dll etc.
            
            # Create target dir
            os.makedirs(target_dir, exist_ok=True)
            
            # Find the root folder name in zip
            root_folder = f"vlc-{VLC_VERSION}/"
            
            # Files to extract
            files_to_extract = [
                "libvlc.dll",
                "libvlccore.dll",
                "plugins/" # We need the plugins folder
            ]
            
            for file_info in z.infolist():
                if not file_info.filename.startswith(root_folder):
                    continue
                
                # Remove root folder from path
                rel_path = file_info.filename[len(root_folder):]
                
                if not rel_path: continue
                
                # Check if this file is interesting
                should_extract = False
                if rel_path in ["libvlc.dll", "libvlccore.dll"]:
                    should_extract = True
                elif rel_path.startswith("plugins/"):
                    should_extract = True
                    
                if should_extract:
                    # Construct output path
                    out_path = os.path.join(target_dir, rel_path)
                    
                    if file_info.is_dir():
                        os.makedirs(out_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(out_path), exist_ok=True)
                        with open(out_path, "wb") as f:
                            f.write(z.read(file_info))
                            
    except Exception as e:
        print(f"Failed to extract VLC: {e}")
        sys.exit(1)

    print(f"VLC binaries extracted to {target_dir}")

if __name__ == "__main__":
    download_vlc()
