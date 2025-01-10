@echo off
set "LOG_FILE=%TEMP%\update_script.log"

echo [%date% %time%] Début du script de mise à jour >> "%LOG_FILE%"

:: Étape 1 : Tuer tous les processus Python
echo [%date% %time%] Arrêt des processus Python... >> "%LOG_FILE%"
echo Arrêt des processus Python...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% neq 0 (
    echo Aucun processus Python trouvé ou erreur lors de l'arrêt. >> "%LOG_FILE%"
)

:: Étape 2 : Supprimer tous les fichiers et dossiers dans le répertoire courant, sauf update.bat
echo [%date% %time%] Nettoyage du répertoire courant... >> "%LOG_FILE%"
echo Nettoyage du répertoire courant...

:: Supprimer tous les fichiers sauf update.bat
for %%f in (*) do (
    if /I not "%%f"=="update.bat" (
        echo Suppression du fichier : %%f >> "%LOG_FILE%"
        del /F /Q "%%f"
    )
)

:: Supprimer tous les dossiers et sous-dossiers
for /d %%d in (*) do (
    echo Suppression du dossier : %%d >> "%LOG_FILE%"
    rmdir /S /Q "%%d"
)


:: Étape 3 : Récupérer le tag de la dernière release
echo [%date% %time%] Récupération du tag de la dernière release... >> "%LOG_FILE%"
echo Récupération du tag de la dernière release...
set "POWERSHELL_COMMAND=(Invoke-WebRequest -Uri 'https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty tag_name"
for /f "delims=" %%i in ('powershell -Command "%POWERSHELL_COMMAND%"') do set "LATEST_TAG=%%i"

:: Vérifier si le tag a été récupéré
if "%LATEST_TAG%"=="" (
    echo Erreur : Impossible de récupérer le tag de la dernière release. >> "%LOG_FILE%"
    echo Erreur : Impossible de récupérer le tag de la dernière release.
    pause
    exit /b 1
)

:: Supprimer les guillemets et les espaces autour du tag
set "LATEST_TAG=%LATEST_TAG:"=%"
set "LATEST_TAG=%LATEST_TAG: =%"
echo Dernière release trouvée : %LATEST_TAG% >> "%LOG_FILE%"
echo Dernière release trouvée : %LATEST_TAG%

:: Étape 4 : Télécharger le code source de la dernière release avec curl
echo [%date% %time%] Téléchargement du code source de la dernière release... >> "%LOG_FILE%"
echo Téléchargement du code source de la dernière release...
set "ZIP_FILE=%TEMP%\latest_release.zip"
curl -L -o "%ZIP_FILE%" "https://github.com/Balrog57/Retrogaming-Toolkit-AIO/archive/refs/tags/%LATEST_TAG%.zip"
if %errorlevel% neq 0 (
    echo Erreur lors du téléchargement du code source. >> "%LOG_FILE%"
    echo Erreur lors du téléchargement du code source.
    pause
    exit /b 1
)

:: Étape 5 : Décompresser le ZIP dans %TEMP% et copier uniquement le contenu du dossier dans le répertoire courant
echo [%date% %time%] Extraction du fichier ZIP... >> "%LOG_FILE%"
echo Extraction du fichier ZIP...
set "EXTRACT_DIR=%TEMP%\latest_release"
powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%EXTRACT_DIR%' -Force"
if %errorlevel% neq 0 (
    echo Erreur lors de l'extraction du fichier ZIP. >> "%LOG_FILE%"
    echo Erreur lors de l'extraction du fichier ZIP.
    pause
    exit /b 1
)

:: Copier uniquement le contenu du dossier extrait (sans le dossier parent) dans le répertoire courant
echo [%date% %time%] Copie des fichiers dans le répertoire courant... >> "%LOG_FILE%"
echo Copie des fichiers dans le répertoire courant...
for /d %%d in ("%EXTRACT_DIR%\*") do (
    xcopy "%%d\*" "%cd%\" /E /I /Y /F
)
if %errorlevel% neq 0 (
    echo Erreur lors de la copie des fichiers. >> "%LOG_FILE%"
    echo Erreur lors de la copie des fichiers.
    pause
    exit /b 1
)

:: Étape 6 : Supprimer le fichier ZIP et le dossier temporaire après extraction
echo [%date% %time%] Suppression des fichiers temporaires... >> "%LOG_FILE%"
echo Suppression des fichiers temporaires...
del /F /Q "%ZIP_FILE%"
rmdir /S /Q "%EXTRACT_DIR%"
if %errorlevel% neq 0 (
    echo Erreur lors de la suppression des fichiers temporaires. >> "%LOG_FILE%"
    echo Erreur lors de la suppression des fichiers temporaires.
    pause
    exit /b 1
)

:: Étape 7 : Lancer main.py
echo [%date% %time%] Lancement de main.py... >> "%LOG_FILE%"
echo Lancement de main.py...
start "" python main.py
if %errorlevel% neq 0 (
    echo Erreur lors du lancement de main.py. >> "%LOG_FILE%"
    echo Erreur lors du lancement de main.py.
    pause
    exit /b 1
)

echo [%date% %time%] Mise à jour terminée avec succès. >> "%LOG_FILE%"
echo Mise à jour terminée avec succès.
pause