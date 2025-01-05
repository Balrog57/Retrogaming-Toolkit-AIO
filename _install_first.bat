@echo off

:: Vérification si Python est installé
echo Vérification de la présence de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé. Veuillez l'installer manuellement.
    pause
    exit /b
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
