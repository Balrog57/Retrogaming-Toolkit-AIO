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
    if not is_admin():
        print("Élévation des privilèges nécessaire. Relancement en tant qu'administrateur...")
        try:
            result = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                __file__, 
                None, 
                1
            )
            if result <= 32:  # ShellExecute returns a value <= 32 on error
                raise Exception(f"Code d'erreur ShellExecute: {result}")
            sys.exit()
        except Exception as e:
            print(f"Erreur: Impossible d'obtenir les privilèges administrateur.\nDétails: {str(e)}")
            input("Appuyez sur Entrée pour quitter...")
            sys.exit(1)
    
    try:
        command = [
            "reg", "add",
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem",
            "/v", "LongPathsEnabled",
            "/t", "REG_DWORD",
            "/d", "1",
            "/f"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Modification réussie :", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la modification :", e.stderr)
    except Exception as e:
        print("Une erreur inattendue s'est produite :", str(e))

def main():
    enable_long_paths()

if __name__ == "__main__":
    main()
