import subprocess

def enable_long_paths():
    """
    Active le support des chemins longs sur un système Windows
    en modifiant le registre via une commande.
    """
    try:
        # Commande pour ajouter la clé de registre
        command = [
            "reg", "add",
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem",
            "/v", "LongPathsEnabled",
            "/t", "REG_DWORD",
            "/d", "1",
            "/f"
        ]

        # Exécution de la commande
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print("Modification réussie :", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la modification :", e.stderr)
    except Exception as e:
        print("Une erreur inattendue s'est produite :", str(e))

# Appeler la fonction
# enable_long_paths()
