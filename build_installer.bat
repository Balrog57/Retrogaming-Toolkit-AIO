@echo off
setlocal

:: Ensure we are in the script's directory
cd /d "%~dp0"

echo ========================================================
echo      Retrogaming Toolkit AIO - Build Installer
echo ========================================================

:: 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b 1
)

:: 2. Install Requirements
echo.
echo [1/3] Installation des dependances...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)

:: 3. Build EXE with PyInstaller
echo.
echo [2/3] Compilation de l'application (PyInstaller)...

:: 3. Build EXE with PyInstaller
echo.
echo [2/3] Compilation de l'application (PyInstaller)...

python build.py
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Echec de la compilation PyInstaller.
    pause
    exit /b 1
)

:: 4. Build Installer with Inno Setup
echo.
echo [3/3] Creation de l'installateur (Inno Setup)...

:: Try to find ISCC.exe (Inno Setup Command Line Compiler)
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined ISCC_PATH (
    "%ISCC_PATH%" setup.iss
    if %ERRORLEVEL% neq 0 (
        echo [ERREUR] Echec de la compilation Inno Setup.
        pause
        exit /b 1
    ) else (
        echo.
        echo [SUCCES] Installateur cree avec succes !
        echo Le fichier se trouve dans le dossier courant : RetrogamingToolkit_Setup.exe
    )
) else (
    echo [ATTENTION] Inno Setup ^(ISCC.exe^) n'a pas ete trouve.
    echo L'executable "portable" a ete cree dans dist\RetrogamingToolkit.
    echo Pour creer l'installateur final, veuillez installer Inno Setup 6 et relancer ce script,
    echo ou compiler manuellement "setup.iss".
)

echo.
echo Fin du processus.
pause
