import os
import requests
import subprocess
import shutil
import tempfile
import zipfile

def test_download():
    app_data_dir = r"C:\Users\Marc\AppData\Local\RetrogamingToolkit"
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
        print(f"Created {app_data_dir}")

    target_exe = os.path.join(app_data_dir, "chdman.exe")
    seven_za_path = os.path.join(app_data_dir, "7za.exe")

    # Clean up for test
    if os.path.exists(target_exe):
        try:
            os.remove(target_exe)
            print("Removed existing chdman.exe")
        except PermissionError:
            print("Cannot remove chdman.exe (in use?), continuing anyway...")
    
    if os.path.exists(seven_za_path):
        try:
            os.remove(seven_za_path)
            print("Removed existing 7za.exe")
        except:
            pass

    print("Starting download process...")

    # URL MAME
    MAME_URL = "https://github.com/mamedev/mame/releases/download/mame0284/mame0284b_x64.exe"
    mame_exe_path = os.path.join(tempfile.gettempdir(), "mame_setup.exe")

    print(f"Downloading MAME (90MB+) from {MAME_URL}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        with requests.get(MAME_URL, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(mame_exe_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=81920): 
                    f.write(chunk)
                    downloaded += len(chunk)
                    # print(f"Downloaded {downloaded/1024/1024:.2f} MB", end='\r')
        print("\nMAME download complete.")

        # 7za
        print("Downloading 7za...")
        url_7za = "https://www.7-zip.org/a/7za920.zip"
        zip_7za_path = os.path.join(tempfile.gettempdir(), "7za920.zip")
        
        r_7za = requests.get(url_7za, headers=headers, stream=True)
        r_7za.raise_for_status()
        with open(zip_7za_path, 'wb') as f:
            f.write(r_7za.content)
        
        with zipfile.ZipFile(zip_7za_path, 'r') as z:
            for file in z.namelist():
                if file == "7za.exe":
                    z.extract(file, app_data_dir)
                    break
        print(f"7za extracted to {seven_za_path}")

        # Extract
        print("Extracting chdman.exe...")
        # Command: 7za.exe e mame.exe -o{app_data_dir} chdman.exe -y
        cmd = [seven_za_path, 'e', mame_exe_path, f'-o{app_data_dir}', 'chdman.exe', '-y']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Extraction failed: {result.stderr}")
        else:
            print("Extraction command finished.")
        
        if os.path.exists(target_exe):
            size = os.path.getsize(target_exe)
            print(f"SUCCESS: chdman.exe found at {target_exe} (Size: {size/1024/1024:.2f} MB)")
        else:
            print("FAILURE: chdman.exe not found.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # cleanup
        if os.path.exists(mame_exe_path):
            os.remove(mame_exe_path)
            print("Removed temp mame exe")

if __name__ == "__main__":
    test_download()
