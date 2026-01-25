import PyInstaller.__main__
import os
import glob
import shutil

def build():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    toolkit_dir = os.path.join(base_dir, "Retrogaming-Toolkit-AIO")

    # Check for VLC binaries first
    vlc_lib_path = os.path.join(toolkit_dir, "vlc", "libvlc.dll")
    if not os.path.exists(vlc_lib_path):
        print(f"ERROR: VLC binaries not found at {vlc_lib_path}")
        print("Please run download_vlc.py first.")
        return

    
    # Collect all python modules in Retrogaming-Toolkit-AIO for hidden imports
    hidden_imports = []
    py_files = glob.glob(os.path.join(toolkit_dir, "*.py"))
    for py_file in py_files:
        filename = os.path.basename(py_file)
        if filename != "__init__.py":
            module_name = filename[:-3] # Remove .py
            hidden_imports.append(module_name)
    
    if "utils" not in hidden_imports:
        hidden_imports.append("utils")

    # Explicitly add new modules
    hidden_imports.append("radio")
    hidden_imports.append("vlc")

    hidden_imports.append("yt_dlp")
    hidden_imports.append("imageio_ffmpeg")
    hidden_imports.append("pytubefix")
    hidden_imports.append("openai")
    hidden_imports.append("fitz") # PyMuPDF
    hidden_imports.append("lxml")
    hidden_imports.append("tqdm")
    hidden_imports.append("pyperclip")
    hidden_imports.append("pygame")

    print(f"Found {len(hidden_imports)} modules to include as hidden imports.")

    # Define PyInstaller arguments
    args = [
        'main.py',                           # Script principal
        '--name=RetrogamingToolkit',         # Nom de l'exe
        '--onedir',                          # Dossier unique (plus facile pour debug/updates)
        '--windowed',                        # Pas de console
        '--noconfirm',                       # Ne pas demander confirmation pour écraser
        '--clean',                           # Nettoyer le cache
        
        # Paths to search for imports (so 'import utils' works)
        f'--paths={toolkit_dir}',
        
        # Icon
        f'--icon={os.path.join(base_dir, "assets", "Retrogaming-Toolkit-AIO.ico")}',
    ]

    # Add VLC binaries if present
    vlc_dir = os.path.join(toolkit_dir, "vlc")
    if os.path.exists(vlc_dir):
         print("Found VLC directory, bundling it...")
         args.append(f'--add-data={vlc_dir}{os.pathsep}vlc')
    else:
         print("Warning: VLC directory not found. The app may fail to run without local VLC installation.")

    # Add hidden imports

    hidden_imports.append("ImageConvert")
    for hidden in hidden_imports:
        args.append(f'--hidden-import={hidden}')

    # Collect certifi data
    from PyInstaller.utils.hooks import collect_all
    tmp_ret = collect_all('certifi')
    for d in tmp_ret[0]: # datas
         args.append(f'--add-data={d[0]}{os.pathsep}{d[1]}')

    # Collect tkinterdnd2 data
    tmp_ret = collect_all('tkinterdnd2')
    for d in tmp_ret[0]: # datas
         args.append(f'--add-data={d[0]}{os.pathsep}{d[1]}')
    for b in tmp_ret[1]: # binaries
         args.append(f'--add-binary={b[0]}{os.pathsep}{b[1]}')
    for h in tmp_ret[2]: # hiddenimports
        args.append(f'--hidden-import={h}')

    # Add data files
    # Format: src;dest
    # We copy the ENTIRE Retrogaming-Toolkit-AIO folder
    args.append(f'--add-data={toolkit_dir}{os.pathsep}Retrogaming-Toolkit-AIO')
    # Use ABSOLUTE path for assets source to be safe, dest is 'assets'
    assets_dir = os.path.join(base_dir, "assets")
    args.append(f'--add-data={assets_dir}{os.pathsep}assets')

    # Binaries (ffmpeg, chdman, etc.) are NOT bundled anymore.
    # The tools will download them on demand if missing.
    # This keeps the installer size small and the repo clean.

    print("Running PyInstaller with arguments:")
    for arg in args:
        print(f"  {arg}")

    PyInstaller.__main__.run(args)

    # Post-build: Copy instructions file to the root of the dist folder (next to exe)
    print("Post-build: Copying instructions file to dist root...")
    dist_dir = os.path.join(base_dir, "dist", "RetrogamingToolkit")
    inst_source = os.path.join(toolkit_dir, "instructions_assisted_gamelist_creator.txt")
    if os.path.exists(dist_dir) and os.path.exists(inst_source):
        shutil.copy2(inst_source, dist_dir)
        print(f"Copied {inst_source} to {dist_dir}")
    else:
        print(f"Warning: Could not copy instructions file. Source or Dest missing.\nSrc: {inst_source}\nDst: {dist_dir}")

if __name__ == "__main__":
    build()
