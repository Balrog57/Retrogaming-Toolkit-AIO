@echo off
echo Mise à jour en cours...

:: Étape 1 : Tuer tous les processus Python en cours
taskkill /f /im python.exe /t >nul 2>&1
if %errorlevel%==0 (
    echo Tous les processus Python ont été terminés.
) else (
    echo Aucun processus Python en cours d'exécution.
)

:: Étape 2 : Récupérer l'URL de la dernière release
echo Récupération de l'URL de la dernière release...
for /f "tokens=*" %%i in ('curl -s https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest ^| powershell -Command "ConvertFrom-Json | Select-Object -ExpandProperty zipball_url"') do set DOWNLOAD_URL=%%i

if "%DOWNLOAD_URL%"=="" (
    echo Erreur : Impossible de récupérer l'URL de la dernière release.
    pause
    exit /b 1
)

:: Étape 3 : Télécharger le code source de la dernière release
echo Téléchargement du code source de la dernière release...
curl -L -o latest_release.zip "%DOWNLOAD_URL%"
if %errorlevel% neq 0 (
    echo Erreur lors du téléchargement du code source.
    pause
    exit /b 1
)

:: Étape 4 : Extraire le fichier zip
echo Extraction des fichiers...
powershell -Command "Expand-Archive -Force latest_release.zip ."
if %errorlevel% neq 0 (
    echo Erreur lors de l'extraction des fichiers.
    pause
    exit /b 1
)

:: Étape 5 : Déplacer les fichiers extraits dans le répertoire courant
echo Déplacement des fichiers...
for /d %%i in ("Balrog57-Retrogaming-Toolkit-AIO-*") do (
    move "%%i\*" .
    rmdir /s /q "%%i"
)
if %errorlevel% neq 0 (
    echo Erreur lors du déplacement des fichiers.
    pause
    exit /b 1
)

:: Étape 6 : Supprimer le fichier zip
echo Nettoyage des fichiers temporaires...
del latest_release.zip
if %errorlevel% neq 0 (
    echo Erreur lors de la suppression du fichier zip.
    pause
    exit /b 1
)

:: Étape 7 : Redémarrer l'application
echo Redémarrage de l'application...
start main.py

echo Mise à jour terminée avec succès.
pause