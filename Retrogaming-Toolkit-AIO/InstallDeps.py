import ctypes
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
from threading import Thread

import customtkinter as ctk
import requests

try:
    import theme
except Exception:
    theme = None


ctk.set_appearance_mode("dark")


def is_running_as_admin():
    if os.name != "nt":
        return True

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    if os.name != "nt" or is_running_as_admin():
        return True

    if getattr(sys, "frozen", False):
        executable = sys.executable
        arguments = sys.argv[1:]
    else:
        executable = sys.executable
        arguments = [os.path.abspath(__file__), *sys.argv[1:]]

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        subprocess.list2cmdline(arguments),
        None,
        1,
    )

    if result <= 32:
        ctypes.windll.user32.MessageBoxW(
            None,
            "L'installation des dépendances nécessite les droits administrateur.",
            "Installation annulée",
            0x10,
        )
        return False

    return False


def get_tpu_link(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None

        match = re.search(r'name="id"\s+value="(\d+)"', response.text)
        if not match:
            return None

        download_response = requests.post(
            url,
            data={"id": match.group(1), "server_id": "12"},
            headers=headers,
            timeout=15,
            allow_redirects=False,
        )

        if download_response.status_code in (301, 302):
            return download_response.headers.get("Location")

        redirect_match = re.search(r'url=([^"\']+)', download_response.text)
        return redirect_match.group(1) if redirect_match else None
    except Exception:
        return None


def download_file(url, path):
    with requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()
        with open(path, "wb") as handle:
            shutil.copyfileobj(response.raw, handle)


def run_installer(command, cwd=None):
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        startupinfo=startupinfo,
    )

    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip()
        if details:
            raise RuntimeError(
                f"{os.path.basename(command[0])} a échoué ({result.returncode}) : {details[:400]}"
            )
        raise RuntimeError(
            f"{os.path.basename(command[0])} a échoué ({result.returncode})"
        )

    return result


def find_existing(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def detect_openal():
    windir = os.environ.get("WINDIR", r"C:\Windows")
    return find_existing(
        [
            os.path.join(windir, "System32", "OpenAL32.dll"),
            os.path.join(windir, "SysWOW64", "OpenAL32.dll"),
        ]
    )


def detect_directx_legacy():
    windir = os.environ.get("WINDIR", r"C:\Windows")
    markers = [
        "d3dx9_43.dll",
        "d3dcompiler_43.dll",
        "XAudio2_7.dll",
        "XInput1_3.dll",
    ]
    for folder in ("System32", "SysWOW64"):
        for marker in markers:
            candidate = os.path.join(windir, folder, marker)
            if os.path.exists(candidate):
                return candidate
    return None


def push_log(log_queue, message):
    log_queue.put(("log", message))


def set_status(log_queue, message):
    log_queue.put(("status", message))


def set_progress(log_queue, value):
    log_queue.put(("progress", value))


def run_install(status_queue):
    tmp_dir = tempfile.mkdtemp(prefix="balrog_installdeps_")
    try:
        import utils

        push_log(status_queue, "Démarrage de l'installation des dépendances.")
        push_log(status_queue, f"Dossier temporaire: {tmp_dir}")

        openal_before = detect_openal()
        directx_before = detect_directx_legacy()

        if openal_before:
            push_log(status_queue, f"OpenAL déjà détecté: {openal_before}")
        else:
            push_log(status_queue, "OpenAL non détecté avant installation.")

        if directx_before:
            push_log(status_queue, f"DirectX legacy déjà détecté: {directx_before}")
        else:
            push_log(status_queue, "DirectX legacy non détecté avant installation.")

        set_status(status_queue, "OpenAL...")
        openal_zip = os.path.join(tmp_dir, "oalinst.zip")
        push_log(status_queue, "Téléchargement de OpenAL...")
        download_file("https://www.openal.org/downloads/oalinst.zip", openal_zip)
        push_log(status_queue, f"Archive OpenAL téléchargée: {openal_zip}")
        utils.extract_with_7za(openal_zip, tmp_dir)
        openal_exe = os.path.join(tmp_dir, "oalinst.exe")
        if not os.path.exists(openal_exe):
            raise FileNotFoundError("oalinst.exe introuvable après extraction.")
        push_log(status_queue, "Lancement de l'installateur OpenAL en silencieux (/S)...")
        run_installer([openal_exe, "/S"], cwd=tmp_dir)
        openal_after = detect_openal()
        if not openal_after:
            raise RuntimeError("OpenAL n'a pas été détecté après l'installation.")
        push_log(status_queue, f"OpenAL installé: {openal_after}")
        set_progress(status_queue, 0.33)

        set_status(status_queue, "DirectX...")
        push_log(status_queue, "Récupération du lien DirectX...")
        directx_url = get_tpu_link(
            "https://www.techpowerup.com/download/directx-redistributable-runtime/"
        )
        if not directx_url:
            raise RuntimeError("Impossible de récupérer le lien de téléchargement DirectX.")
        push_log(status_queue, f"Lien DirectX obtenu: {directx_url}")
        directx_zip = os.path.join(tmp_dir, "directx.zip")
        directx_dir = os.path.join(tmp_dir, "directx")
        push_log(status_queue, "Téléchargement de DirectX...")
        download_file(directx_url, directx_zip)
        push_log(status_queue, f"Archive DirectX téléchargée: {directx_zip}")
        utils.extract_with_7za(directx_zip, directx_dir)
        dxsetup = os.path.join(directx_dir, "DXSETUP.exe")
        if not os.path.exists(dxsetup):
            raise FileNotFoundError("DXSETUP.exe introuvable après extraction.")
        push_log(status_queue, "Lancement de DXSETUP.exe /silent...")
        run_installer([dxsetup, "/silent"], cwd=directx_dir)
        directx_after = detect_directx_legacy()
        if not directx_after:
            raise RuntimeError("DirectX legacy n'a pas été détecté après l'installation.")
        push_log(status_queue, f"DirectX legacy détecté: {directx_after}")
        set_progress(status_queue, 0.66)

        set_status(status_queue, "Visual C++...")
        push_log(status_queue, "Récupération du lien Visual C++...")
        vc_url = get_tpu_link(
            "https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/"
        )
        if not vc_url:
            raise RuntimeError("Impossible de récupérer le lien Visual C++.")
        push_log(status_queue, f"Lien Visual C++ obtenu: {vc_url}")
        vc_zip = os.path.join(tmp_dir, "vcpp.zip")
        vc_dir = os.path.join(tmp_dir, "vcpp")
        push_log(status_queue, "Téléchargement de Visual C++...")
        download_file(vc_url, vc_zip)
        push_log(status_queue, f"Archive Visual C++ téléchargée: {vc_zip}")
        utils.extract_with_7za(vc_zip, vc_dir)
        install_all = os.path.join(vc_dir, "install_all.bat")
        if not os.path.exists(install_all):
            raise FileNotFoundError("install_all.bat introuvable après extraction.")
        push_log(status_queue, "Lancement de install_all.bat /y...")
        run_installer([install_all, "/y"], cwd=vc_dir)
        push_log(status_queue, "Visual C++ exécuté avec succès.")
        set_progress(status_queue, 1.0)
        set_status(status_queue, "Terminé !")
        push_log(status_queue, "Installation terminée sans erreur.")
    except Exception as exc:
        set_status(status_queue, f"Erreur: {exc}")
        push_log(status_queue, f"Erreur: {exc}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        push_log(status_queue, "Nettoyage du dossier temporaire terminé.")
        status_queue.put(("done", None))


def main():
    if not relaunch_as_admin():
        return

    root = ctk.CTk()
    if theme:
        theme.apply_theme(root, "Install Deps")
        accent = theme.COLOR_ACCENT_PRIMARY
        success_color = theme.COLOR_SUCCESS
    else:
        root.title("Install Deps")
        accent = "blue"
        success_color = "green"

    root.geometry("720x520")

    title_label = ctk.CTkLabel(root, text="Installation Dépendances", font=("Arial", 18))
    title_label.pack(pady=(20, 10))

    status_label = ctk.CTkLabel(root, text="Prêt")
    status_label.pack(pady=(0, 10))

    progress_bar = ctk.CTkProgressBar(root, progress_color=accent, width=620)
    progress_bar.set(0)
    progress_bar.pack(pady=(0, 12))

    log_box = ctk.CTkTextbox(root, width=660, height=300)
    log_box.pack(padx=20, pady=(0, 16), fill="both", expand=True)
    log_box.insert("end", "Journal prêt.\n")
    log_box.configure(state="disabled")

    event_queue = queue.Queue()

    def append_log(message):
        log_box.configure(state="normal")
        log_box.insert("end", f"{message}\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def process_events():
        while True:
            try:
                event_type, payload = event_queue.get_nowait()
            except queue.Empty:
                break

            if event_type == "log":
                append_log(payload)
            elif event_type == "status":
                status_label.configure(text=payload)
            elif event_type == "progress":
                progress_bar.set(payload)
            elif event_type == "done":
                start_button.configure(state="normal")

        root.after(150, process_events)

    def start_install():
        start_button.configure(state="disabled")
        progress_bar.set(0)
        status_label.configure(text="Initialisation...")
        append_log("Nouvelle exécution demandée.")
        Thread(target=run_install, args=(event_queue,), daemon=True).start()

    start_button = ctk.CTkButton(
        root,
        text="LANCER INSTALLATION",
        command=start_install,
        fg_color=success_color,
    )
    start_button.pack(pady=(0, 20))

    process_events()
    root.mainloop()


if __name__ == "__main__":
    main()
