

def build():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    toolkit_dir = os.path.join(base_dir, "Retrogaming-Toolkit-AIO")
    
    # Collect all python modules in Retrogaming-Toolkit-AIO for hidden imports
    hidden_imports = []
    py_files = glob.glob(os.path.join(toolkit_dir, "*.py"))
    for py_file in py_files:
        filename = os.path.basename(py_file)
        if filename != "__init__.py":
            module_name = filename[:-3] # Remove .py
            hidden_imports.append(module_name)
    
    # Also add utils explicitly if not caught (though it should be)
    if "utils" not in hidden_imports:
        hidden_imports.append("utils")

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
        f'--icon={os.path.join(toolkit_dir, "icons", "GameBatch.ico")}',
    ]

    # Add hidden imports

    hidden_imports.append("ImageConvert")
    for hidden in hidden_imports:
        args.append(f'--hidden-import={hidden}')

    # Collect certifi data
    from PyInstaller.utils.hooks import collect_all
    tmp_ret = collect_all('certifi')
    for d in tmp_ret[0]: # datas
         args.append(f'--add-data={d[0]}{os.pathsep}{d[1]}')

    # Add data files
    # Format: src;dest
    # We copy the ENTIRE Retrogaming-Toolkit-AIO folder to ensure all scripts and resources are available
    # This solves issues where child processes (multiprocessing) fail to import modules from PYZ.
    args.append(f'--add-data={toolkit_dir};Retrogaming-Toolkit-AIO')

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
