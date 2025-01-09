@echo off

:: Étape 1 : Vérifier si Python est installé
echo Vérification de l'installation de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé.
    echo Veuillez installer Python manuellement depuis https://www.python.org/downloads/windows/.
    echo Une fois Python installé, relancez ce script.
    pause
    exit /b
) else (
    echo Python est déjà installé.
)

:: Étape 2 : Vérifier et installer les dépendances
echo Vérification des dépendances dans requirements.txt...
if not exist "%~dp0requirements.txt" (
    echo Le fichier requirements.txt est introuvable dans le dossier : %~dp0
    echo Veuillez placer requirements.txt dans le même dossier que ce script.
    pause
    exit /b
)

echo Installation des dépendances...
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo Une erreur s'est produite lors de l'installation des dépendances.
    echo Essayez d'installer manuellement les dépendances problématiques.
    pause
    exit /b
) else (
    echo Les dépendances ont été installées avec succès.
)

:: Étape 3 : Lancer main.py si tout est correct
echo Lancement de main.py...
if not exist "%~dp0main.py" (
    echo Le fichier main.py est introuvable dans le dossier : %~dp0
    echo Veuillez placer main.py dans le même dossier que ce script.
    pause
    exit /b
)

python "%~dp0main.py"
if %ERRORLEVEL% neq 0 (
    echo Une erreur s'est produite lors de l'exécution de main.py !
    pause
    exit /b
) else (
    echo Le script main.py s'est terminé avec succès.
)

echo Processus terminé.
pause