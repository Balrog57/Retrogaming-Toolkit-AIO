@echo off
setlocal enabledelayedexpansion
set "LOG_FILE=%~dp0update.log"

:: Initialisation du fichier de log
echo [%date% %time%] Début du script de mise à jour >> "%LOG_FILE%"
echo Début du script de mise à jour...

:: Étape 1 : Fermer tous les processus Python en cours
echo [%date% %time%] Fermeture des processus Python en cours... >> "%LOG_FILE%"
echo Fermeture des processus Python en cours...
taskkill /F /IM python.exe /T >nul 2>&1
if %errorlevel%==0 (
    echo Tous les processus Python ont été fermés. >> "%LOG_FILE%"
    echo Tous les processus Python ont été fermés.
) else (
    echo Aucun processus Python en cours d'exécution. >> "%LOG_FILE%"
    echo Aucun processus Python en cours d'exécution.
)

:: Étape 2 : Supprimer tous les fichiers du dossier courant, sauf update.bat et update.log
echo [%date% %time%] Nettoyage du dossier courant... >> "%LOG_FILE%"
echo Nettoyage du dossier courant...
for %%f in ("%~dp0*") do (
    if /i not "%%~nxf"=="update.bat" if /i not "%%~nxf"=="update.log" (
        echo Suppression de %%f... >> "%LOG_FILE%"
        del /q "%%f" 2>&1 >> "%LOG_FILE%"
        if %errorlevel% neq 0 (
            echo Erreur : Impossible de supprimer %%f. >> "%LOG_FILE%"
            echo Erreur : Impossible de supprimer %%f.
            pause
            exit /b 1
        )
    )
)

:: Supprimer tous les sous-dossiers, sauf celui contenant update.bat et update.log
for /d %%d in ("%~dp0*") do (
    echo Suppression du dossier %%d... >> "%LOG_FILE%"
    rmdir /s /q "%%d" 2>&1 >> "%LOG_FILE%"
    if %errorlevel% neq 0 (
        echo Erreur : Impossible de supprimer le dossier %%d. >> "%LOG_FILE%"
        echo Erreur : Impossible de supprimer le dossier %%d.
        pause
        exit /b 1
    )
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

:: Étape 5 : Extraire le fichier zip dans un dossier temporaire
echo [%date% %time%] Extraction des fichiers dans un dossier temporaire... >> "%LOG_FILE%"
echo Extraction des fichiers dans un dossier temporaire...
set "EXTRACTED_DIR=%TEMP%\Retrogaming-Toolkit-AIO-%LATEST_TAG%"
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%EXTRACTED_DIR%' -Force"
if %errorlevel% neq 0 (
    echo Erreur lors de l'extraction des fichiers. >> "%LOG_FILE%"
    echo Erreur lors de l'extraction des fichiers.
    pause
    exit /b 1
)

:: Étape 6 : Déplacer uniquement le contenu du dossier extrait vers le dossier courant
echo [%date% %time%] Déplacement des fichiers vers le dossier courant... >> "%LOG_FILE%"
echo Déplacement des fichiers vers le dossier courant...
for /r "%EXTRACTED_DIR%" %%f in (*) do (
    set "RELATIVE_PATH=%%f"
    set "RELATIVE_PATH=!RELATIVE_PATH:%EXTRACTED_DIR%\=!"
    set "DESTINATION_PATH=%~dp0!RELATIVE_PATH!"

    :: Vérifier si le fichier est update.bat ou update.log
    if /i not "!RELATIVE_PATH!"=="update.bat" if /i not "!RELATIVE_PATH!"=="update.log" (
        echo Déplacement de %%f vers !DESTINATION_PATH!... >> "%LOG_FILE%"
        if not exist "!DESTINATION_PATH!\.." mkdir "!DESTINATION_PATH!\.."
        if exist "!DESTINATION_PATH!" (
            echo Le fichier existe déjà : !DESTINATION_PATH! >> "%LOG_FILE%"
            echo Le fichier existe déjà : !DESTINATION_PATH!
        ) else (
            move /y "%%f" "!DESTINATION_PATH!" 2>&1 >> "%LOG_FILE%"
            if %errorlevel% neq 0 (
                echo Erreur : Impossible de déplacer %%f. >> "%LOG_FILE%"
                echo Erreur : Impossible de déplacer %%f.
                pause
                exit /b 1
            )
        )
    )
)

:: Étape 7 : Supprimer le dossier temporaire
echo [%date% %time%] Suppression du dossier temporaire... >> "%LOG_FILE%"
echo Suppression du dossier temporaire...
rmdir /s /q "%EXTRACTED_DIR%"
if %errorlevel% neq 0 (
    echo Erreur : Impossible de supprimer le dossier temporaire. >> "%LOG_FILE%"
    echo Erreur : Impossible de supprimer le dossier temporaire.
    pause
    exit /b 1
)

:: Étape 8 : Supprimer le fichier zip après extraction
echo [%date% %time%] Suppression du fichier zip... >> "%LOG_FILE%"
echo Suppression du fichier zip...
del /q "%ZIP_FILE%" 2>&1 >> "%LOG_FILE%"
if %errorlevel% neq 0 (
    echo Erreur : Impossible de supprimer le fichier zip. >> "%LOG_FILE%"
    echo Erreur : Impossible de supprimer le fichier zip.
    pause
    exit /b 1
)

:: Étape 9 : Redémarrer l'application
echo [%date% %time%] Redémarrage de l'application... >> "%LOG_FILE%"
echo Redémarrage de l'application...
cd /d "%~dp0"
if exist "main.py" (
    start main.py
) else (
    echo Erreur : Le fichier main.py n'existe pas. >> "%LOG_FILE%"
    echo Erreur : Le fichier main.py n'existe pas.
    pause
    exit /b 1
)

:: Étape 10 : Nettoyage final
echo [%date% %time%] Nettoyage final... >> "%LOG_FILE%"
echo Nettoyage final...
timeout /t 2 /nobreak >nul

:: Fin du script
echo [%date% %time%] Mise à jour terminée avec succès. >> "%LOG_FILE%"
echo Mise à jour terminée avec succès.
pause