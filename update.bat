@echo off
echo Mise à jour en cours...

:: Étape 1 : Tuer tous les processus Python en cours
taskkill /f /im python.exe /t >nul 2>&1
if %errorlevel%==0 (
    echo Tous les processus Python ont été terminés.
) else (
    echo Aucun processus Python en cours d'exécution.
)

:: Étape 2 : Télécharger la dernière version depuis GitHub
echo Téléchargement de la dernière version...
curl -L -o update.zip https://github.com/Balrog57/Retrogaming-Toolkit-AIO/releases/latest/download/update.zip
if %errorlevel% neq 0 (
    echo Erreur lors du téléchargement de la mise à jour.
    pause
    exit /b 1
)

:: Étape 3 : Extraire le fichier zip
echo Extraction des fichiers...
powershell -Command "Expand-Archive -Force update.zip ."
if %errorlevel% neq 0 (
    echo Erreur lors de l'extraction des fichiers.
    pause
    exit /b 1
)

:: Étape 4 : Supprimer le fichier zip après extraction
del update.zip
if %errorlevel% neq 0 (
    echo Erreur lors de la suppression du fichier zip.
    pause
    exit /b 1
)

:: Étape 5 : Redémarrer l'application
echo Redémarrage de l'application...
start main.py

echo Mise à jour terminée avec succès.
pause