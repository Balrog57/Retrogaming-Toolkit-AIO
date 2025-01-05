@echo off
:: Vérification si Python est installé
echo Vérification de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé. Téléchargement de Python...
    
    :: Définir l'URL de téléchargement de l'installateur de Python
    set "python_url=https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
    set "python_installer=python-installer.exe"
    
    :: Télécharger l'installateur
    powershell -Command "Invoke-WebRequest -Uri %python_url% -OutFile %python_installer%"
    
    if not exist %python_installer% (
        echo Échec du téléchargement de l'installateur de Python !
        pause
        exit /b
    )
    
    :: Installer Python en mode silencieux
    echo Installation de Python...
    start /wait %python_installer% /quiet InstallAllUsers=1 PrependPath=1
    
    :: Vérifier à nouveau si Python est correctement installé
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Échec de l'installation de Python !
        pause
        exit /b
    )
    echo Python a été installé avec succès.
)

:: Installer les dépendances depuis requirements.txt
echo Installation des dépendances...
if not exist requirements.txt (
    echo Le fichier requirements.txt est introuvable !
    pause
    exit /b
)
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Erreur lors de l'installation des dépendances !
    pause
    exit /b
)

:: Lancer le script Python main.py
echo Lancement de main.py...
if not exist main.py (
    echo Le fichier main.py est introuvable !
    pause
    exit /b
)
python main.py
if %ERRORLEVEL% neq 0 (
    echo Erreur lors de l'exécution de main.py !
    pause
    exit /b
)

echo Processus terminé avec succès.
pause
