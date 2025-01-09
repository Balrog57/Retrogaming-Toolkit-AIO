@echo off

:: Vérification si Python est installé
echo Vérification de la présence de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé. Tentative d'installation automatique...

    :: Téléchargement de l'installateur Python
    echo Téléchargement de l'installateur Python...
    curl -o python_installer.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe

    if %ERRORLEVEL% neq 0 (
        echo Échec du téléchargement de l'installateur Python.
        pause
        exit /b
    )

    :: Installation de Python
    echo Installation de Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe

    if %ERRORLEVEL% neq 0 (
        echo Échec de l'installation de Python.
        pause
        exit /b
    )

    echo Python a été installé avec succès.
) else (
    echo Python est correctement installé.
)

:: Vérification des dépendances
echo Installation ou vérification des dépendances depuis requirements.txt...
if not exist requirements.txt (
    echo Le fichier requirements.txt est introuvable !
    pause
    exit /b
)
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Une erreur s'est produite lors de l'installation des dépendances.
    pause
    exit /b
) else (
    echo Les dépendances ont été installées avec succès.
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
    echo Une erreur s'est produite lors de l'exécution de main.py !
    pause
    exit /b
) else (
    echo Le script main.py s'est terminé avec succès.
)

echo Processus terminé.
pause