import os
import customtkinter as ctk
from tkinter import messagebox
from threading import Thread

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def install_logic(status_label, progress_bar):
    status_label.configure(text="Initialisation...")
    progress_bar.set(0)
    
    try:
        try: import utils
        except ImportError: raise Exception("Utils manquant")
        
        manager = utils.DependencyManager() # Assuming root not needed for non-gui parts really or we can pass None
        
        # 1. OpenAL
        status_label.configure(text="OpenAL...")
        # Since I am simplifying, I am assuming we kept the logic in utils or we reimplement it? 
        # The user wants me to modernize. I will rely on the implementation plan which said to use utils.
        # But utils doesn't have openal logic by default unless I added it.
        # I did not add OpenAL logic to utils_impl in previous turns.
        # So I should copy the logic but clean it up.
        
        # Actually, let's just make a stub that says "Check InstallDeps original logic if needed" or keep it.
        # I will keep the scraping logic but minimalize it.
        pass # Placeholder for actual logic execution to keep file short for this turn.
             # Wait, I should not break functionality. I will paste the scraping logic back but cleaner.
        
    except Exception as e:
        status_label.configure(text=f"Erreur: {e}")

# Re-implementing simplified logic
import requests, re, tempfile, shutil, subprocess

def get_tpu_link(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if r.status_code!=200: return None
        fid = re.search(r'name="id"\s+value="(\d+)"', r.text).group(1)
        sid = "12"
        r2 = requests.post(url, data={'id': fid, 'server_id': sid}, allow_redirects=False)
        if r2.status_code in [301,302]: return r2.headers['Location']
        return re.search(r'url=([^"\']+)', r2.text).group(1)
    except: return None

def dl_file(url, path):
    with requests.get(url, stream=True) as r:
        with open(path, 'wb') as f: shutil.copyfileobj(r.raw, f)

def run_install(status, prog):
    tmp = tempfile.mkdtemp()
    try:
        # OpenAL
        status.configure(text="OpenAL...")
        zp = os.path.join(tmp, "oal.zip")
        dl_file("https://www.openal.org/downloads/oalinst.zip", zp)
        # Extract... assuming utils
        import utils; utils.extract_with_7za(zp, tmp)
        subprocess.run([os.path.join(tmp, "oalinst.exe"), "/silent"])
        prog.set(0.33)

        # DirectX
        status.configure(text="DirectX...")
        url = get_tpu_link("https://www.techpowerup.com/download/directx-redistributable-runtime/")
        if url:
            zp = os.path.join(tmp, "dx.zip"); dx_dir = os.path.join(tmp, "dx")
            dl_file(url, zp); utils.extract_with_7za(zp, dx_dir)
            subprocess.run([os.path.join(dx_dir, "DXSETUP.exe"), "/silent"])
        prog.set(0.66)

        # VC++
        status.configure(text="Visual C++...")
        url = get_tpu_link("https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/")
        if url:
            zp = os.path.join(tmp, "vc.zip"); vc_dir = os.path.join(tmp, "vc")
            dl_file(url, zp); utils.extract_with_7za(zp, vc_dir)
            bat = os.path.join(vc_dir, "install_all.bat")
            if os.path.exists(bat): subprocess.run([bat, "/y"], cwd=vc_dir)
        prog.set(1.0)
        
        status.configure(text="Terminé!")
    except Exception as e: status.configure(text=str(e))
    finally: shutil.rmtree(tmp)

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "Install Deps"); acc=theme.COLOR_ACCENT_PRIMARY
    else: root.title("Install Deps"); acc="blue"
    
    root.geometry("400x350")
    
    lbl = ctk.CTkLabel(root, text="Installation Dépendances", font=("Arial", 16))
    lbl.pack(pady=20)
    
    status = ctk.CTkLabel(root, text="Prêt")
    status.pack(pady=5)
    
    prog = ctk.CTkProgressBar(root, progress_color=acc)
    prog.set(0)
    prog.pack(pady=10)
    
    def start():
        btn.configure(state="disabled")
        Thread(target=run_install, args=(status, prog)).start()
        
    btn = ctk.CTkButton(root, text="LANCER INSTALLATION", command=start, fg_color=theme.COLOR_SUCCESS if theme else "green")
    btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
