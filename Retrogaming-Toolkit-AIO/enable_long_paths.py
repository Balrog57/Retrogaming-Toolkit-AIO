import subprocess
import sys
import ctypes

def is_admin():
    """Vérifie si le script est exécuté avec les privilèges administrateur."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def enable_long_paths():
    """Active le support des chemins longs sur un système Windows."""
    # Commande REG
    reg_cmd = 'ADD "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f'
    
    if not is_admin():
        # print("Élévation des privilèges nécessaire...")
        # Lancer la commande REG directement en tant qu'admin
        # On utilise cmd.exe /c pour exécuter la commande interne REG
        try:
             # ShellExecuteW: hwnd, operation, file, parameters, directory, showcmd
             # operation="runas" demande l'élévation
             ret = ctypes.windll.shell32.ShellExecuteW(
                 None, "runas", "cmd.exe", f"/c reg {reg_cmd}", None, 0 # 0 = SW_HIDE
             )
             if ret <= 32:
                 raise Exception(f"Erreur ShellExecute: {ret}")
             
             # On ne peut pas facilement capturer la sortie de ShellExecute runas, 
             # mais si ça ne lève pas d'exception, l'UAC a été accepté (ou ignoré).
             print("Demande de modification du registre envoyée.")
        except Exception as e:
            print(f"Erreur lors de la demande d'élévation : {e}")
    else:
        # Si on est déjà admin, on utilise subprocess
        try:
            command = ["reg"] + reg_cmd.split()[1:] # Remove ADD, split parts
            # But the string handling is annoying. Let's reconstruct list.
            command = [
                "reg", "add",
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem",
                "/v", "LongPathsEnabled",
                "/t", "REG_DWORD",
                "/d", "1",
                "/f"
            ]
            subprocess.run(command, capture_output=True, text=True, check=True)
            print("Modification réussie (Admin).")
        except subprocess.CalledProcessError as e:
            print("Erreur :", e.stderr)
        except Exception as e:
            print("Erreur inattendue :", str(e))

def main():
    enable_long_paths()

if __name__ == "__main__":
    main()
