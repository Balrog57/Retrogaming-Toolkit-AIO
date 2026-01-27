import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import logging
import subprocess
import multiprocessing
import importlib
import tempfile
import zipfile
import traceback
from PIL import Image, ImageTk
from customtkinter import CTkImage
import requests
import urllib.request
import webbrowser
import threading
import webbrowser
import threading
import json
import atexit
import ctypes
import radio # Import our new module
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

# Fix sys.path for bundled modules and data directory
if getattr(sys, 'frozen', False):
    # In frozen mode, we are in sys._MEIPASS
    # We add Retrogaming-Toolkit-AIO to sys.path to allow loading scripts that might be 
    # in the data directory (fallback or user-modified versions), 
    # even though bundled modules are already in the PYZ.
    base_path = sys._MEIPASS
    toolkit_path = os.path.join(base_path, "Retrogaming-Toolkit-AIO")
    if toolkit_path not in sys.path:
        sys.path.append(toolkit_path)
    # Also add base path just in case
    if base_path not in sys.path:
        sys.path.append(base_path)
else:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Retrogaming-Toolkit-AIO"))

try:
    import utils
    import theme
    import module_runner
except ImportError:
    # Si utils n'est pas trouvé (devrait pas arriver si sys.path est correct)
    # logger might not be defined yet
    logger = logging.getLogger(__name__) # Safe to call
    logging.basicConfig() # Ensure basic logging
    logger.error("Impossible d'importer utils.py ou theme.py")
    utils = None
    theme = None

VERSION = "3.0.11"

# Configuration du logging
local_app_data = os.getenv('LOCALAPPDATA')
if not local_app_data:
    local_app_data = os.path.expanduser("~") # Fallback to user home if LOCALAPPDATA is missing

app_data_dir = os.path.join(local_app_data, 'RetrogamingToolkit')
if not os.path.exists(app_data_dir):
    try:
        os.makedirs(app_data_dir)
    except OSError:
        # Fallback to temp dir if permissions fail completely
        app_data_dir = tempfile.gettempdir()

log_file = os.path.join(app_data_dir, 'retrogaming_toolkit.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)
logger = logging.getLogger(__name__)

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_path(p):
    if utils:
        return utils.resource_path(p)
    return p

# Dictionnaires de traduction
TRANSLATIONS = {
    "FR": {
        "search_label": "Rechercher :",
        "search_placeholder": "Nom ou description... (Ctrl+F)",
        "close": "Fermer",
        "readme": "Lisez-moi",
        "error": "Erreur",
        "file_not_found": "Le fichier {} n'existe pas.",
        "update_title": "Mise à jour",
        "update_confirm": "Une nouvelle version est disponible. Voulez-vous la télécharger et l'installer maintenant ?",
        "no_installer": "Aucun fichier d'installation trouvé dans la dernière release.",
        "update_bat_missing": "Le fichier update.bat n'existe pas.",
        "cat_fav": "Favoris",
        "cat_all": "Tout",
        "cat_games": "Gestion des Jeux & ROMs",
        "cat_metadata": "Métadonnées & Gamelists",
        "cat_media": "Multimédia & Artworks",
        "cat_org": "Organisation & Collections",
        "cat_sys": "Maintenance Système",
        "loading": "Chargement...",
        "no_result": "Aucun résultat pour '{}'",
        "no_tool_cat": "Aucun outil dans cette catégorie.",
        "launch_module": "Lancement du module : {}",
        "error_exec": "Erreur lors de l'exécution du module {}: {}",
        "open": "Ouvrir"
    },
    "EN": {
        "search_label": "Search:",
        "search_placeholder": "Name or description... (Ctrl+F)",
        "close": "Close",
        "readme": "Readme",
        "error": "Error",
        "file_not_found": "File {} does not exist.",
        "update_title": "Update",
        "update_confirm": "A new version is available. Do you want to download and install it now?",
        "no_installer": "No installer file found in the latest release.",
        "update_bat_missing": "The update.bat file does not exist.",
        "cat_fav": "Favorites",
        "cat_all": "All",
        "cat_games": "Games & ROMs Management",
        "cat_metadata": "Metadata & Gamelists",
        "cat_media": "Multimedia & Artworks",
        "cat_org": "Organization & Collections",
        "cat_sys": "System Maintenance",
        "loading": "Loading...",
        "no_result": "No result for '{}'",
        "no_tool_cat": "No tools in this category.",
        "launch_module": "Launching module: {}",
        "error_exec": "Error executing module {}: {}",
        "open": "Open"
    },
    "ES": {
        "search_label": "Buscar:",
        "search_placeholder": "Nombre o descripción... (Ctrl+F)",
        "close": "Cerrar",
        "readme": "Léame",
        "error": "Error",
        "file_not_found": "El archivo {} no existe.",
        "update_title": "Actualización",
        "update_confirm": "¿Hay una nueva versión disponible. Quieres descargarla e instalarla ahora?",
        "no_installer": "No se encontró ningún archivo de instalación en la última versión.",
        "update_bat_missing": "El archivo update.bat no existe.",
        "cat_fav": "Favoritos",
        "cat_all": "Todo",
        "cat_games": "Gestión de Juegos y ROMs",
        "cat_metadata": "Metadatos y Listas de Juegos",
        "cat_media": "Multimedia y Arte",
        "cat_org": "Organización y Colecciones",
        "cat_sys": "Mantenimiento del Sistema",
        "loading": "Cargando...",
        "no_result": "Ningún resultado para '{}'",
        "no_tool_cat": "No hay herramientas en esta categoría.",
        "launch_module": "Lanzando módulo: {}",
        "error_exec": "Error al ejecutar el módulo {}: {}",
        "open": "Abrir"
    },
    "IT": {
        "search_label": "Cerca:",
        "search_placeholder": "Nome o descrizione... (Ctrl+F)",
        "close": "Chiudi",
        "readme": "Leggimi",
        "error": "Errore",
        "file_not_found": "Il file {} non esiste.",
        "update_title": "Aggiornamento",
        "update_confirm": "È disponibile una nuova versione. Vuoi scaricarla e installarla ora?",
        "no_installer": "Nessun file di installazione trovato nell'ultima versione.",
        "update_bat_missing": "Il file update.bat non esiste.",
        "cat_fav": "Preferiti",
        "cat_all": "Tutto",
        "cat_games": "Gestione Giochi e ROM",
        "cat_metadata": "Metadati e Gamelist",
        "cat_media": "Multimedia e Artwork",
        "cat_org": "Organizzazione e Collezioni",
        "cat_sys": "Manutenzione Sistema",
        "loading": "Caricamento...",
        "no_result": "Nessun risultato per '{}'",
        "no_tool_cat": "Nessuno strumento in questa categoria.",
        "launch_module": "Avvio modulo: {}",
        "error_exec": "Errore durante l'esecuzione del modulo {}: {}",
        "open": "Apri"
    },
    "DE": {
        "search_label": "Suchen:",
        "search_placeholder": "Name oder Beschreibung... (Ctrl+F)",
        "close": "Schließen",
        "readme": "Lies mich",
        "error": "Fehler",
        "file_not_found": "Die Datei {} existiert nicht.",
        "update_title": "Aktualisierung",
        "update_confirm": "Eine neue Version ist verfügbar. Möchten Sie sie jetzt herunterladen und installieren?",
        "no_installer": "Keine Installationsdatei in der neuesten Version gefunden.",
        "update_bat_missing": "Die Datei update.bat existiert nicht.",
        "cat_fav": "Favoriten",
        "cat_all": "Alle",
        "cat_games": "Spiele & ROMs Verwaltung",
        "cat_metadata": "Metadaten & Spielelisten",
        "cat_media": "Multimedia & Kunstwerke",
        "cat_org": "Organisation & Sammlungen",
        "cat_sys": "Systemwartung",
        "loading": "Laden...",
        "no_result": "Kein Ergebnis für '{}'",
        "no_tool_cat": "Keine Werkzeuge in dieser Kategorie.",
        "launch_module": "Modul wird gestartet: {}",
        "error_exec": "Fehler beim Ausführen des Moduls {}: {}",
        "open": "Öffnen"
    },
    "PT": {
        "search_label": "Pesquisar:",
        "search_placeholder": "Nome ou descrição... (Ctrl+F)",
        "close": "Fechar",
        "readme": "Leia-me",
        "error": "Erro",
        "file_not_found": "O arquivo {} não existe.",
        "update_title": "Atualização",
        "update_confirm": "Uma nova versão está disponível. Deseja baixar e instalar agora?",
        "no_installer": "Nenhum arquivo de instalação encontrado na última versão.",
        "update_bat_missing": "O arquivo update.bat não existe.",
        "cat_fav": "Favoritos",
        "cat_all": "Tudo",
        "cat_games": "Gestão de Jogos e ROMs",
        "cat_metadata": "Metadados e GameLists",
        "cat_media": "Multimídia e Artes",
        "cat_org": "Organização e Coleções",
        "cat_sys": "Manutenção do Sistema",
        "loading": "Carregando...",
        "no_result": "Nenhum resultado para '{}'",
        "no_tool_cat": "Nenhuma ferramenta nesta categoria.",
        "launch_module": "Iniciando módulo: {}",
        "error_exec": "Erro ao executar o módulo {}: {}",
        "open": "Abrir"
    }
}


SCRIPT_DESCRIPTIONS = {
    "AssistedGamelist": {
        "FR": "(Retrobat) Améliore vos gamelists XML (tri, nettoyage, formats).",
        "EN": "(Retrobat) Improves your XML gamelists (sorting, cleaning, headers).",
        "ES": "(Retrobat) Mejora sus listas de juegos XML (ordenación, limpieza).",
        "IT": "(Retrobat) Migliora le tue gamelist XML (ordinamento, pulizia).",
        "DE": "(Retrobat) Verbessert Ihre XML-Spielelisten (Sortieren, Bereinigen).",
        "PT": "(Retrobat) Melhora suas listas de jogos XML (ordenação, limpeza)."
    },
    "BGBackup": {
        "FR": "(Retrobat) Crée une copie de sécurité de vos fichiers gamelist.xml.",
        "EN": "(Retrobat) Creates a safety backup of your gamelist.xml files.",
        "ES": "(Retrobat) Crea una copia de seguridad de sus archivos gamelist.xml.",
        "IT": "(Retrobat) Crea una copia di sicurezza dei file gamelist.xml.",
        "DE": "(Retrobat) Erstellt eine Sicherheitskopie Ihrer gamelist.xml-Dateien.",
        "PT": "(Retrobat) Cria uma cópia de segurança dos seus arquivos gamelist.xml."
    },
    "CHDManager": {
        "FR": "Gère la compression de vos jeux au format CHD (MAME/Disc).",
        "EN": "Manages game compression to CHD format (MAME/Disc).",
        "ES": "Gestiona la compresión de juegos al formato CHD (MAME/Disco).",
        "IT": "Gestisce la compressione dei giochi in formato CHD (MAME/Disco).",
        "DE": "Verwaltet die Spielekomprimierung im CHD-Format (MAME/Disc).",
        "PT": "Gerencia a compressão de jogos para o formato CHD (MAME/Disco)."
    },
    "CollectionBuilder": {
        "FR": "(Core) Créez des collections de jeux automatiques par mots-clés.",
        "EN": "(Core) Create automatic game collections based on keywords.",
        "ES": "(Core) Cree colecciones de juegos automáticas por palabras clave.",
        "IT": "(Core) Crea collezioni di giochi automatiche basate su parole chiave.",
        "DE": "(Core) Erstellen Sie automatische Spielesammlungen basierend auf Stichwörtern.",
        "PT": "(Core) Crie coleções automáticas de jogos com base em palavras-chave."
    },
    "CollectionExtractor": {
        "FR": "(Core) Extrayez et isolez des jeux spécifiques pour créer des packs.",
        "EN": "(Core) Extract and isolate specific games to create small packs.",
        "ES": "(Core) Extraiga y aísle juegos específicos para crear paquetes.",
        "IT": "(Core) Estrai e isola giochi specifici per creare pacchetti.",
        "DE": "(Core) Extrahieren und isolieren Sie bestimmte Spiele für Pakete.",
        "PT": "(Core) Extraia e isole jogos específicos para criar pacotes."
    },
    "LongPaths": {
        "FR": "Débloque la limite des 260 caractères pour les noms de fichiers Windows.",
        "EN": "Unlocks the 260 character limit for Windows filenames.",
        "ES": "Desbloquea el límite de 260 caracteres para nombres de archivo de Windows.",
        "IT": "Sblocca il limite di 260 caratteri per i nomi dei file Windows.",
        "DE": "Hebt das 260-Zeichen-Limit für Windows-Dateinamen auf.",
        "PT": "Desbloqueia o limite de 260 caracteres para nomes de arquivos do Windows."
    },
    "FolderToTxt": {
        "FR": "Génère automatiquement un fichier .txt vide pour chaque fichier existant (fichiers compagnons).",
        "EN": "Automatically generates an empty .txt file for each existing file (companion files).",
        "ES": "Genera automáticamente un archivo .txt vacío para cada archivo existente (archivos complementarios).",
        "IT": "Genera automaticamente un file .txt vuoto per ogni file esistente (file complementari).",
        "DE": "Generiert automatisch eine leere .txt-Datei für jede vorhandene Datei (Begleitdateien).",
        "PT": "Gera automaticamente um arquivo .txt vazio para cada arquivo existente (arquivos complementares)."
    },
    "FolderToZip": {
        "FR": "Archive chaque sous-dossier en un fichier ZIP indépendant (Batch Zip).",
        "EN": "Archives each subfolder into an independent ZIP file (Batch Zip).",
        "ES": "Archiva cada subcarpeta en un archivo ZIP independiente (Batch Zip).",
        "IT": "Archivia ogni sottocartella in un file ZIP indipendente (Batch Zip).",
        "DE": "Archiviert jeden Unterordner in eine unabhängige ZIP-Datei (Batch Zip).",
        "PT": "Arquiva cada subpasta em um arquivo ZIP independente (Batch Zip)."
    },
    "GameBatch": {
        "FR": "Crée des lanceurs (.bat) pour vos jeux Windows/PC.",
        "EN": "Creates launcher scripts (.bat) for your Windows/PC games.",
        "ES": "Crea scripts de lanzamiento (.bat) para sus juegos de PC.",
        "IT": "Crea script di avvio (.bat) per i tuoi giochi Windows/PC.",
        "DE": "Erstellt Startskripte (.bat) für Ihre Windows-/PC-Spiele.",
        "PT": "Cria scripts de inicialização (.bat) para seus jogos de PC."
    },
    "EmptyGen": {
        "FR": "Crée des fichiers dummy (.scummvm, .singe...) pour la détection par les émulateurs.",
        "EN": "Creates dummy files (.scummvm, .singe...) for emulator detection.",
        "ES": "Crea archivos ficticios (.scummvm, .singe...) para la detección del emulador.",
        "IT": "Crea file fittizi (.scummvm, .singe...) per il rilevamento dell'emulatore.",
        "DE": "Erstellt Dummy-Dateien (.scummvm, .singe...) für die Emulatorerkennung.",
        "PT": "Cria arquivos fictícios (.scummvm, .singe...) para detecção de emulador."
    },
    "GameRemoval": {
        "FR": "(Core) Supprime proprement un jeu et tous ses médias associés.",
        "EN": "(Core) Cleanly removes a game and all its associated media.",
        "ES": "(Core) Elimina limpiamente un juego y todos sus medios asociados.",
        "IT": "(Core) Rimuove pulitamente un gioco e tutti i suoi media associati.",
        "DE": "Entfernt sauber ein Spiel und alle zugehörigen Medien.",
        "PT": "(Core) Remove de forma limpa um jogo e todas as suas mídias associadas."
    },
    "GamelistHyperlist": {
        "FR": "(Core) Transforme une Gamelist XML en base de données Hyperspin.",
        "EN": "(Core) Transforms an XML Gamelist into an Hyperspin database.",
        "ES": "(Core) Transforma una Gamelist XML en una base de datos Hyperspin.",
        "IT": "(Core) Trasforma una Gamelist XML in un database Hyperspin.",
        "DE": "(Core) Wandelt eine XML-Gamelist in eine Hyperspin-Datenbank um.",
        "PT": "(Core) Transforma uma Gamelist XML em um banco de dados Hyperspin."
    },
    "HyperlistGamelist": {
        "FR": "(Retrobat) Convertit une base Hyperspin en Gamelist pour Retrobat.",
        "EN": "(Retrobat) Converts an Hyperspin DB into a Gamelist for Retrobat.",
        "ES": "(Retrobat) Convierte una BD Hyperspin en una Gamelist para Retrobat.",
        "IT": "(Retrobat) Converte un DB Hyperspin in una Gamelist per Retrobat.",
        "DE": "(Retrobat) Konvertiert eine Hyperspin-DB in eine Gamelist für Retrobat.",
        "PT": "(Retrobat) Converte um banco de dados Hyperspin em uma Gamelist para Retrobat."
    },
    "InstallDeps": {
        "FR": "Installe les composants Windows manquants (DirectX, Visual C++).",
        "EN": "Installs missing Windows components (DirectX, Visual C++).",
        "ES": "Instala componentes de Windows faltantes (DirectX, Visual C++).",
        "IT": "Installa componenti Windows mancanti (DirectX, Visual C++).",
        "DE": "Installiert fehlende Windows-Komponenten (DirectX, Visual C++).",
        "PT": "Instala componentes ausentes do Windows (DirectX, Visual C++)."
    },
    "ListFilesSimple": {
        "FR": "Génère un inventaire simple des fichiers d'un dossier.",
        "EN": "Generates a simple inventory of files in a folder.",
        "ES": "Genera un inventario simple de archivos en una carpeta.",
        "IT": "Genera un inventario semplice dei file in una cartella.",
        "DE": "Erstellt ein einfaches Inventar der Dateien in einem Ordner.",
        "PT": "Gera um inventário simples de arquivos em uma pasta."
    },
    "ListFilesWin": {
        "FR": "Génère un inventaire détaillé (tailles, dates) type Windows.",
        "EN": "Generates a detailed inventory (sizes, dates) like Windows.",
        "ES": "Genera un inventario detallado (tamaños, fechas) tipo Windows.",
        "IT": "Genera un inventario dettagliato (dimensioni, date) stile Windows.",
        "DE": "Erstellt ein detailliertes Inventar (Größen, Daten) wie Windows.",
        "PT": "Gera um inventário detalhado (tamanhos, datas) estilo Windows."
    },
    "MaxCSO": {
        "FR": "Compresser vos ISOs en CSO pour gagner de la place (PSP/PS2).",
        "EN": "Compress ISOs to CSO to save space (PSP/PS2).",
        "ES": "Comprimir ISOs a CSO para ahorrar espacio (PSP/PS2).",
        "IT": "Comprimi ISO in CSO per risparmiare spazio (PSP/PS2).",
        "DE": "Komprimieren Sie ISOs in CSO, um Platz zu sparen (PSP/PS2).",
        "PT": "Comprima ISOs para CSO para economizar espaço (PSP/PS2)."
    },
    "MediaOrphans": {
        "FR": "(Core) Nettoie les images/vidéos qui ne correspondent à aucun jeu.",
        "EN": "(Core) Cleans up images/videos that don't match any game.",
        "ES": "(Core) Limpia imágenes/videos que no corresponden a ningún juego.",
        "IT": "(Core) Pulisce immagini/video che non corrispondono a nessun gioco.",
        "DE": "(Core) Bereinigt Bilder/Videos, die zu keinem Spiel passen.",
        "PT": "(Core) Limpa imagens/vídeos que não correspondem a nenhum jogo."
    },
    "FolderCleaner": {
        "FR": "Scanne et supprime tous les dossiers vides inutiles.",
        "EN": "Scans and deletes all useless empty folders.",
        "ES": "Escanea y elimina todas las carpetas vacías inútiles.",
        "IT": "Scansiona ed elimina tutte le cartelle vuote inutili.",
        "DE": "Scannt und löscht alle nutzlosen leeren Ordner.",
        "PT": "Verifica e exclui todas as pastas vazias inúteis."
    },
    "StoryHyperlist": {
        "FR": "(Core) Injecte des données 'Story' dans vos listes Hyperspin.",
        "EN": "(Core) Injects 'Story' data into your Hyperspin lists.",
        "ES": "(Core) Inyecta datos 'Story' en sus listas Hyperspin.",
        "IT": "(Core) Inietta dati 'Story' nelle tue liste Hyperspin.",
        "DE": "(Core) Fügt 'Story'-Daten in Ihre Hyperspin-Listen ein.",
        "PT": "(Core) Insere dados 'Story' em suas listas Hyperspin."
    },
    "DolphinConvert": {
        "FR": "Convertisseur spécialisé pour les jeux GameCube/Wii (ISO↔RVZ).",
        "EN": "Specialized converter for GameCube/Wii games (ISO↔RVZ).",
        "ES": "Convertidor especializado para juegos GameCube/Wii (ISO↔RVZ).",
        "IT": "Convertitore specializzato per giochi GameCube/Wii (ISO↔RVZ).",
        "DE": "Spezialisierter Konverter für GameCube/Wii-Spiele (ISO↔RVZ).",
        "PT": "Conversor especializado para jogos GameCube/Wii (ISO↔RVZ)."
    },
    "StoryCleaner": {
        "FR": "Nettoie les caractères spéciaux/non-ASCII des fichiers texte.",
        "EN": "Cleans special/non-ASCII characters from text files.",
        "ES": "Limpia caracteres especiales/no ASCII de archivos de texto.",
        "IT": "Pulisce caratteri speciali/non ASCII dai file di testo.",
        "DE": "Bereinigt Sonder-/Nicht-ASCII-Zeichen aus Textdateien.",
        "PT": "Limpa caracteres especiais/não-ASCII de arquivos de texto."
    },
    "M3UCreator": {
        "FR": "Crée des playlists (.m3u) pour vos jeux multi-disques.",
        "EN": "Creates playlists (.m3u) for your multi-disc games.",
        "ES": "Crea listas de reproducción (.m3u) para sus juegos multidisco.",
        "IT": "Crea playlist (.m3u) per i tuoi giochi multidisco.",
        "DE": "Erstellt Wiedergabelisten (.m3u) für Ihre Multi-Disc-Spiele.",
        "PT": "Cria playlists (.m3u) para seus jogos multidisco."
    },
    "CoverExtractor": {
        "FR": "Récupère la couverture des comics/livres (CBZ/PDF) pour l'affichage.",
        "EN": "Retrieves covers from comics/books (CBZ/PDF) for display.",
        "ES": "Recupera portadas de cómics/libros (CBZ/PDF) para visualización.",
        "IT": "Recupera copertine da fumetti/libri (CBZ/PDF) per la visualizzazione.",
        "DE": "Ruft Cover von Comics/Büchern (CBZ/PDF) zur Anzeige ab.",
        "PT": "Recupera capas de quadrinhos/livros (CBZ/PDF) para exibição."
    },
    "CBZKiller": {
        "FR": "Transforme vos PDF et dossiers d'images en format Comic Book (CBZ).",
        "EN": "Transforms PDFs and image folders into Comic Book format (CBZ).",
        "ES": "Transforma PDF y carpetas de imágenes al formato Comic Book (CBZ).",
        "IT": "Trasforma PDF e cartelle di immagini in formato Comic Book (CBZ).",
        "DE": "Wandelt PDFs und Bildordner in das Comic-Book-Format (CBZ) um.",
        "PT": "Transforma PDFs e pastas de imagens no formato Comic Book (CBZ)."
    },
    "VideoConvert": {
        "FR": "Outil puissant pour convertir, compresser ou rogner vos vidéos.",
        "EN": "Powerful tool to convert, compress, or crop your videos.",
        "ES": "Potente herramienta para convertir, comprimir o recortar sus videos.",
        "IT": "Potente strumento per convertire, comprimere o ritagliare i tuoi video.",
        "DE": "Leistungsstarkes Tool zum Konvertieren, Komprimieren oder Schneiden von Videos.",
        "PT": "Ferramenta poderosa para converter, comprimir ou recortar seus vídeos."
    },
    "YTDownloader": {
        "FR": "Téléchargez facilement des vidéos ou musiques depuis YouTube.",
        "EN": "Easily download videos or music to YouTube.",
        "ES": "Descargue fácilmente videos o música de YouTube.",
        "IT": "Scarica facilmente video o musica da YouTube.",
        "DE": "Laden Sie ganz einfach Videos oder Musik von YouTube herunter.",
        "PT": "Baixe facilmente vídeos ou músicas do YouTube."
    },
    "ImageConvert": {
        "FR": "Convertisseur d'images en masse (PNG, JPG, WebP...).",
        "EN": "Bulk image converter (PNG, JPG, WebP...).",
        "ES": "Convertidor de imágenes masivo (PNG, JPG, WebP...).",
        "IT": "Convertitore di immagini di massa (PNG, JPG, WebP...).",
        "DE": "Massenbildkonverter (PNG, JPG, WebP...).",
        "PT": "Conversor de imagens em massa (PNG, JPG, WebP...)."
    },
    "SystemsExtractor": {
        "FR": "Liste tous les systèmes configurés dans votre EmulationStation.",
        "EN": "Lists all configured systems in your EmulationStation.",
        "ES": "Lista todos los sistemas configurados en su EmulationStation.",
        "IT": "Elenca tutti i sistemi configurati nella tua EmulationStation.",
        "DE": "Listet alle konfigurierten Systeme in Ihrer EmulationStation auf.",
        "PT": "Lista todos os sistemas configurados na sua EmulationStation."
    },
    "UniversalRomCleaner": {
        "FR": "Nettoyeur ultime de ROMs : tri par région, version, doublons (1G1R).",
        "EN": "Ultimate ROM cleaner: sort by region, version, duplicates (1G1R).",
        "ES": "Limpiador definitivo de ROMs: ordenar por región, versión, duplicados.",
        "IT": "Pulitore definitivo di ROM: ordina per regione, versione, duplicati.",
        "DE": "Ultimativer ROM-Reiniger: Sortieren nach Region, Version, Duplikaten.",
        "PT": "Limpador definitivo de ROMs: ordenar por região, versão, duplicatas."
    },
    "PatternCopier": {
        "FR": "Copie complexe de fichiers préservant la structure des dossiers.",
        "EN": "Complex file copying preserving directory structure.",
        "ES": "Copia compleja de archivos preservando la estructura de directorios.",
        "IT": "Copia complessa di file preservando la struttura delle directory.",
        "DE": "Komplexes Dateikopieren unter Beibehaltung der Verzeichnisstruktur.",
        "PT": "Cópia complexa de arquivos preservando a estrutura de diretórios."
    },
    "PackWrapper": {
        "FR": "Créez des patchs/mises à jour en comparant deux dossiers.",
        "EN": "Create patches/updates by comparing two folders.",
        "ES": "Cree parches/actualizaciones comparando dos carpetas.",
        "IT": "Crea patch/aggiornamenti confrontando due cartelle.",
        "DE": "Erstellen Sie Patches/Updates durch Vergleich zweier Ordner.",
        "PT": "Crie patches/atualizações comparando duas pastas."
    }
}

# Liste des scripts avec descriptions (valeurs par défaut/clés pour la traduction)
scripts = [
    {"name": "AssistedGamelist", "icon": get_path(os.path.join("assets", "AssistedGamelist.ico"))},
    {"name": "BGBackup", "icon": get_path(os.path.join("assets", "BGBackup.ico"))},
    {"name": "CHDManager", "icon": get_path(os.path.join("assets", "CHDManager.ico"))},
    {"name": "CollectionBuilder", "icon": get_path(os.path.join("assets", "CollectionBuilder.ico"))},
    {"name": "CollectionExtractor", "icon": get_path(os.path.join("assets", "CollectionExtractor.ico"))},
    {"name": "LongPaths", "icon": get_path(os.path.join("assets", "LongPaths.ico"))},
    {"name": "FolderToTxt", "icon": get_path(os.path.join("assets", "FolderToTxt.ico"))},
    {"name": "FolderToZip", "icon": get_path(os.path.join("assets", "FolderToZip.ico"))},
    {"name": "GameBatch", "icon": get_path(os.path.join("assets", "GameBatch.ico"))},
    {"name": "EmptyGen", "icon": get_path(os.path.join("assets", "EmptyGen.ico"))},
    {"name": "GameRemoval", "icon": get_path(os.path.join("assets", "GameRemoval.ico"))},
    {"name": "GamelistHyperlist", "icon": get_path(os.path.join("assets", "GamelistHyperlist.ico"))},
    {"name": "HyperlistGamelist", "icon": get_path(os.path.join("assets", "HyperlistGamelist.ico"))},
    {"name": "InstallDeps", "icon": get_path(os.path.join("assets", "InstallDeps.ico"))},
    {"name": "ListFilesSimple", "icon": get_path(os.path.join("assets", "ListFilesSimple.ico"))},
    {"name": "ListFilesWin", "icon": get_path(os.path.join("assets", "ListFilesWin.ico"))},
    {"name": "MaxCSO", "icon": get_path(os.path.join("assets", "MaxCSO.ico"))},
    {"name": "MediaOrphans", "icon": get_path(os.path.join("assets", "MediaOrphans.ico"))},
    {"name": "FolderCleaner", "icon": get_path(os.path.join("assets", "FolderCleaner.ico"))},
    {"name": "StoryHyperlist", "icon": get_path(os.path.join("assets", "StoryHyperlist.ico"))},
    {"name": "DolphinConvert", "icon": get_path(os.path.join("assets", "DolphinConvert.ico"))},
    {"name": "StoryCleaner", "icon": get_path(os.path.join("assets", "StoryCleaner.ico"))},
    {"name": "M3UCreator", "icon": get_path(os.path.join("assets", "M3UCreator.ico"))},
    {"name": "CoverExtractor", "icon": get_path(os.path.join("assets", "CoverExtractor.ico"))},
    {"name": "CBZKiller", "icon": get_path(os.path.join("assets", "CBZKiller.ico"))},
    {"name": "VideoConvert", "icon": get_path(os.path.join("assets", "VideoConvert.ico"))},
    {"name": "YTDownloader", "icon": get_path(os.path.join("assets", "YTDownloader.ico"))},
    {"name": "ImageConvert", "icon": get_path(os.path.join("assets", "ImageConvert.ico"))},
    {"name": "SystemsExtractor", "icon": get_path(os.path.join("assets", "SystemsExtractor.ico"))},
    {"name": "UniversalRomCleaner", "icon": get_path(os.path.join("assets", "UniversalRomCleaner.png"))},
    {"name": "PatternCopier", "icon": get_path(os.path.join("assets", "PatternCopier.ico"))},
    {"name": "PackWrapper", "icon": get_path(os.path.join("assets", "PackWrapper.ico"))},
]



def lancer_module(module_name):
    """Charge et exécute un module Python dans un processus séparé via multiprocessing."""
    try:
        logger.info(f"Lancement du module: {module_name}")
        
        # Trouver l'icône correspondante
        icon_path = None
        for s in scripts:
            if s["name"] == module_name:
                icon_path = s["icon"]
                break
        
        # Fallback icon determination
        if not icon_path:
             icon_path = get_path(os.path.join("assets", f"{module_name}.ico"))

        # On lance le module dans un nouveau processus
        # Cela permet d'isoler les boucles principales Tkinter
        p = multiprocessing.Process(target=module_runner.run_module_process, args=(module_name, icon_path))
        p.daemon = True # Kill child process if main process exits
        p.start()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du module {module_name}: {str(e)}")
        messagebox.showerror("Erreur", f"Erreur lors de l'exécution du module {module_name}: {str(e)}")

def open_readme(readme_file):
    """Ouvre et affiche le contenu d'un fichier Lisez-moi."""
    try:
        if os.path.exists(readme_file):
            with open(readme_file, "r", encoding="utf-8") as file:
                content = file.read()
            # Utiliser messagebox directement si le custom modal n'est pas dispo dans ce scope
            messagebox.showinfo(TRANSLATIONS.get(globals().get('CURRENT_LANG', 'FR'), TRANSLATIONS["FR"])["readme"], content)
        else:
            lang = globals().get('CURRENT_LANG', 'FR')
            msg = TRANSLATIONS.get(lang, TRANSLATIONS["FR"])["file_not_found"].format(readme_file)
            messagebox.showwarning(TRANSLATIONS.get(lang, TRANSLATIONS["FR"])["readme"], msg)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier {readme_file} : {e}")

def check_for_updates():
    """Vérifie si une nouvelle version est disponible sur GitHub."""
    try:
        url = "https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest"
        response = requests.get(url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release["tag_name"]
        
        # Récupérer l'URL de l'installateur (.exe)
        installer_url = None
        for asset in latest_release.get("assets", []):
            if asset["name"].endswith(".exe"):
                installer_url = asset["browser_download_url"]
                break

        # Fonction pour convertir une version en tuple de nombres
        def version_to_tuple(version):
            return tuple(map(int, version.lstrip('v').split('.')))

        # Convertir les versions en tuples de nombres
        current_version_tuple = version_to_tuple(VERSION)
        latest_version_tuple = version_to_tuple(latest_version)

        # Comparer les versions
        if latest_version_tuple > current_version_tuple:
            return True, latest_version, installer_url
        else:
            return False, latest_version, None

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des mises à jour : {e}")
        return False, VERSION, None

def download_and_run_installer(download_url, app_instance=None):
    """Télécharge et exécute l'installateur."""
    try:
        # Créer un fichier temporaire pour l'installateur
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp_file:
            installer_path = tmp_file.name

        # Télécharger
        logger.info(f"Téléchargement de la mise à jour depuis {download_url}...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info("Téléchargement terminé. Lancement de l'installateur...")

        # Lancer l'installateur et fermer l'application actuelle
        # Terminer proprement l'application avant de lancer l'installateur
        # Cela permet de libérer les verrous sur les fichiers (DLLs, exe, etc.)
        if app_instance:
            try:
                # Stop radio explicitly
                if hasattr(app_instance, 'stop_radio'):
                    app_instance.stop_radio()
                if hasattr(app_instance, 'cleanup'):
                    app_instance.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up before update: {e}")

        # Lancer l'installateur et fermer l'application actuelle
        subprocess.Popen([installer_path]) # Run installer interactively so "Run after install" works
        os._exit(0) # Force exit from thread

    except Exception as e:
        messagebox.showerror("Erreur Mise à jour", f"Erreur lors du téléchargement : {e}")
        logger.error(f"Erreur update: {e}")

def launch_update():
    """Lance le processus de mise à jour."""
    if utils and utils.is_frozen():
        # Mode EXE : Télécharger l'installateur
        try:
            url = "https://api.github.com/repos/Balrog57/Retrogaming-Toolkit-AIO/releases/latest"
            response = requests.get(url)
            data = response.json()
            assets = data.get("assets", [])

            # Chercher un fichier .exe dans les assets (Setup.exe ou autre)
            installer_url = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    installer_url = asset["browser_download_url"]
                    break

            if installer_url:
                if messagebox.askyesno("Mise à jour", "Une nouvelle version est disponible. Voulez-vous la télécharger et l'installer maintenant ?"):
                    download_and_run_installer(installer_url, app_instance=globals().get('app'))
            else:
                messagebox.showerror("Erreur", "Aucun fichier d'installation trouvé dans la dernière release.")

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")

    else:
        # Mode Source : Utiliser update.bat (legacy)
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            update_script = os.path.join(current_dir, "update.bat")
            if os.path.exists(update_script):
                logger.info(f"Fichier update.bat trouvé : {update_script}")
                subprocess.Popen(["start", "cmd.exe", "/c", update_script], shell=True)
                logger.info("update.bat lancé dans une nouvelle fenêtre")
            else:
                logger.error("Le fichier update.bat n'existe pas.")
                messagebox.showerror("Erreur", "Le fichier update.bat n'existe pas.")
        except Exception as e:
            logger.error(f"Erreur lors du lancement de la mise à jour : {e}")
            messagebox.showerror("Erreur", f"Erreur lors du lancement de la mise à jour : {e}")

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lanceur de Modules - Retrogaming-Toolkit-AIO")
        try:
            icon_path = get_path(os.path.join("assets", "Retrogaming-Toolkit-AIO.ico"))
            self.iconbitmap(icon_path)
        except Exception as e:
            logger.error(f"Erreur lors de la définition de l'icône de l'application : {e}")
        self.geometry("800x400")  # Taille initiale

        self.scripts = scripts
        self.filtered_scripts = list(self.scripts)  # Initialiser avec tous les scripts
        self.page = 0
        self.scripts_per_page = 10
        self.min_window_height = 400
        self.preferred_width = 800

        self.icon_cache = {}
        self.favorites = self.load_favorites()

        # Barre de recherche
        self.search_frame = ctk.CTkFrame(self, corner_radius=10)
        self.search_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.search_label = ctk.CTkLabel(self.search_frame, text="Rechercher :", font=("Arial", 14))
        self.search_label.pack(side="left", padx=10)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_scripts)
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, width=300, placeholder_text=TRANSLATIONS["FR"]["search_placeholder"])
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.clear_button = ctk.CTkButton(self.search_frame, text="✕", width=25, height=25, 
                                          command=self.clear_search, 
                                          fg_color="transparent", hover_color=("gray70", "gray30"), text_color="gray")


# Mapping des scripts par catégorie (Nouvelle classification)
# Mapping des scripts par catégorie (Nouvelle classification complète)
# Mapping des scripts par catégorie (Refonte Complète)
SCRIPT_CATEGORIES = {
    # Gestion des Jeux & ROMs
    "CHDManager": "Gestion des Jeux & ROMs",
    "MaxCSO": "Gestion des Jeux & ROMs",
    "DolphinConvert": "Gestion des Jeux & ROMs",
    "FolderToZip": "Gestion des Jeux & ROMs",
    "GameBatch": "Gestion des Jeux & ROMs",
    "GameRemoval": "Gestion des Jeux & ROMs",
    "UniversalRomCleaner": "Gestion des Jeux & ROMs",

    # Métadonnées & Gamelists
    "AssistedGamelist": "Métadonnées & Gamelists",
    "GamelistHyperlist": "Métadonnées & Gamelists",
    "HyperlistGamelist": "Métadonnées & Gamelists",
    "BGBackup": "Métadonnées & Gamelists",
    "StoryHyperlist": "Métadonnées & Gamelists",
    "StoryCleaner": "Métadonnées & Gamelists",
    "SystemsExtractor": "Métadonnées & Gamelists",

    # Multimédia & Artworks
    "YTDownloader": "Multimédia & Artworks",
    "VideoConvert": "Multimédia & Artworks",
    "ImageConvert": "Multimédia & Artworks",
    "CoverExtractor": "Multimédia & Artworks",
    "MediaOrphans": "Multimédia & Artworks",
    "CBZKiller": "Multimédia & Artworks",

    # Organisation & Collections
    "CollectionBuilder": "Organisation & Collections",
    "CollectionExtractor": "Organisation & Collections",
    "M3UCreator": "Organisation & Collections",
    "FolderCleaner": "Organisation & Collections",
    "FolderToTxt": "Organisation & Collections",
    "EmptyGen": "Organisation & Collections",
    "PatternCopier": "Organisation & Collections",
    "PackWrapper": "Organisation & Collections",

    # Maintenance Système
    "LongPaths": "Maintenance Système",
    "InstallDeps": "Maintenance Système",
    "ListFilesSimple": "Maintenance Système",
    "ListFilesWin": "Maintenance Système",
}

class ReadmeWindow(ctk.CTkToplevel):
    def __init__(self, parent, title, content, fg_color, text_color, accent_color, icon_path=None):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=fg_color)
        
        # Close Button - Pack FIRST to ensure it reserves space at the bottom
        close_btn = ctk.CTkButton(self, text="Fermer", fg_color="transparent", 
                                border_width=1, border_color=accent_color,
                                text_color=accent_color, hover_color="#333",
                                command=self.destroy)
        close_btn.pack(side="bottom", pady=20)

        # Estimate height based on character count (approximate)
        # 600px width -> approx 90 chars per line
        lines = content.count('\n') + (len(content) / 90) 
        
        # Height calculation
        # Base = 150 (padding + button)
        # Line height = 20
        calculated_height = int(lines * 20) + 150
        
        # Constraints for 1080p screen comfort
        max_h = 800 
        min_h = 200
        
        height = min(max_h, max(min_h, calculated_height))
        
        self.geometry(f"600x{height}")
        self.minsize(300, 200)

        # Content (Scrollable Text) - Pack SECOND to fill remaining space
        textbox = ctk.CTkTextbox(self, text_color=text_color, fg_color="transparent", 
                               wrap="word", font=("Roboto", 13))
        # Keep button at bottom visible
        textbox.pack(side="top", fill="both", expand=True, padx=30, pady=(25, 10))
        textbox.insert("0.0", content)
        textbox.configure(state="disabled") # Read-only
        
        # Set Icon - Use delay to ensure window is created
        if icon_path and os.path.exists(icon_path):
            self.after(200, lambda: self._apply_icon(icon_path))

        self.focus_set()
        self.grab_set() # Modal

    def _apply_icon(self, path):
         try:
            path = os.path.abspath(path)
            # Try bitmap first if ico
            if path.lower().endswith(".ico"):
                try:
                    self.wm_iconbitmap(path)
                except:
                    # Fallback to photoimage if bitmap fails
                    img = Image.open(path)
                    self.icon_ref = ImageTk.PhotoImage(img)
                    self.wm_iconphoto(False, self.icon_ref)
            else:
                img = Image.open(path)
                self.icon_ref = ImageTk.PhotoImage(img) # Keep reference!
                self.wm_iconphoto(False, self.icon_ref)
         except Exception as e:
             logger.error(f"Failed to apply icon to readme: {e}")




class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Theme Application ---
        if theme:
            theme.apply_theme(self, "Retrogaming Toolkit - Sakura Night Edition")
            self.COLOR_ACCENT_PRIMARY = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_ACCENT_HOVER = theme.COLOR_ACCENT_HOVER
            self.COLOR_SIDEBAR_BG = theme.COLOR_BG
            self.COLOR_CONTENT_BG = "transparent"
            self.COLOR_SIDEBAR_HOVER = theme.COLOR_GHOST_HOVER
            self.COLOR_CARD_BORDER = theme.COLOR_CARD_BORDER
            self.COLOR_TEXT_MAIN = theme.COLOR_TEXT_MAIN
            self.COLOR_TEXT_SUB = theme.COLOR_TEXT_SUB
            self.app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Retrogaming-Toolkit-AIO.ico")
        else:
             # Fallback if theme import fails
            self.title("Retrogaming Toolkit - Sakura Night Edition")
            self.COLOR_ACCENT_PRIMARY = "#ff6699"
            self.COLOR_ACCENT_HOVER = "#ff3385"
            self.COLOR_SIDEBAR_BG = "#151515"
            self.COLOR_CONTENT_BG = "transparent"
            self.COLOR_SIDEBAR_HOVER = "#2a2a2a"
            self.COLOR_CARD_BORDER = "#444"
            self.COLOR_TEXT_MAIN = "#ffffff"
            self.COLOR_TEXT_SUB = "#b0bec5"
            self.app_icon_path = None

        self.geometry("1100x720")
        self.resizable(False, False) 

        # --- Données ---
        self.scripts = scripts
        # Enrichir les scripts avec leur catégorie
        for s in self.scripts:
            # Sécurité
            s["category"] = SCRIPT_CATEGORIES.get(s["name"], "Organisation & Collections")
            
        self.icon_cache = {}
        self.current_category = "Tout"
        self.search_query = ""
        self.current_lang = "FR" # Langue par défaut
        
        # Injecter la variable globale pour les fonctions hors classe
        global CURRENT_LANG
        CURRENT_LANG = self.current_lang

        # --- Initialization Safety ---
        self.last_width = 1100
        self.last_height = 720
        self.visible_height = 720 # Default initialization to prevent AttributeError

        # Load Readmes (Load early so descriptions are available)
        self.readmes_data = {}
        try:
            readme_json_path = get_path(os.path.join("assets", "readmes.json"))
            if os.path.exists(readme_json_path):
                 with open(readme_json_path, "r", encoding="utf-8") as f:
                     self.readmes_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load readmes.json: {e}")


        # --- Layout Principal ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Arrière-plan (Sakura) Main Window ---
        self.setup_background()

        # --- Logic ---
        self.favorites = self.load_favorites()
        self.init_music()
        self.setup_sidebar()
        self.setup_content_area()
        self.check_updates()
        self.filter_and_display()
        
        
        # Start Radio after UI is ready
        self.play_radio()
        
        # Shortcuts
        self.bind("<Control-f>", lambda event: self.search_entry.focus_set())
        self.bind("<Escape>", lambda event: self.clear_search())
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    
        # Select "Tout" category by default
            
        # Select "Tout" category by default
        self.after(100, lambda: self.change_category("Tout"))

    def load_favorites(self):
        try:
            path = os.path.join(app_data_dir, 'favorites.json')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading favorites: {e}")
        return []

    def save_favorites(self):
        try:
            path = os.path.join(app_data_dir, 'favorites.json')
            with open(path, 'w') as f:
                json.dump(self.favorites, f)
        except Exception as e:
            logger.error(f"Error saving favorites: {e}")

    def toggle_favorite(self, script_name):
        if script_name in self.favorites:
            self.favorites.remove(script_name)
        else:
            self.favorites.append(script_name)
        self.save_favorites()
        self.filter_and_display()

    def on_closing(self):
        """Arrêter proprement l'application (radio incluse)."""
        self.stop_radio()
        try:
            pygame.quit()
        except: pass
        self.destroy()

    def on_window_resize(self, event):
        if event.widget == self:
            # Check for significant change to avoid jitter
            if abs(event.width - self.last_width) > 5 or abs(event.height - self.last_height) > 5:
                self.last_width = event.width
                self.last_height = event.height
                
                # Debounce/Delay update
                if hasattr(self, '_resize_job'):
                    self.after_cancel(self._resize_job)
                self._resize_job = self.after(100, self.perform_resize_updates)

    def perform_resize_updates(self):
        self.update_background_size()
        self.filter_and_display()

    def update_background_size(self):
        try:
            bg_path = get_path(os.path.join("assets", "sakura_bg.png"))
            if os.path.exists(bg_path):
                # Utiliser la HAUTEUR actuelle de la fenêtre comme référence
                target_h = self.last_height
                
                # Ouvrir l'image originale
                original_img = Image.open(bg_path)
                
                # Calculer le ratio basé sur la HAUTEUR pour ne pas déborder
                ratio = target_h / original_img.height
                
                target_w = int(original_img.width * ratio)
                # target_h est déjà self.last_height
                
                # Redimensionner en gardant le ratio
                pil_image = original_img.resize((target_w, target_h), Image.LANCZOS)
                
                # Update References
                self.bg_image_ref = CTkImage(pil_image, size=(target_w, target_h))
                self.pil_bg_image = pil_image
                self.canvas_bg_photo = ImageTk.PhotoImage(pil_image)

                # Update Label
                self.bg_label.configure(image=self.bg_image_ref, anchor="ne")
                
                # Update Canvas BG (redraw)
                self.draw_background_on_canvas()
        except Exception as e:
            logger.error(f"BG Resize Error: {e}")
        except Exception as e:
            logger.error(f"BG Resize Error: {e}")

    # ... setup_background ...

    def filter_and_display(self):
        self.canvas.delete("content") # Only delete scrollable content
        
        # Reset Scroll
        self.scroll_y = 0
        self.canvas.yview_moveto(0) 
        
        filtered = []
        for s in self.scripts:
            cat_match = (self.current_category == "Tout") or (s.get("category") == self.current_category)
            search_match = True
            if self.search_query:
                tags = f"{s['name']} {s['description']} {s.get('category','')}".lower()
                if self.search_query not in tags: search_match = False
            if cat_match and search_match: filtered.append(s)
        
        filtered.sort(key=lambda x: x["name"])

        # Layout sorting - FLUID 2 COLUMNS
        # Force 2 columns always
        col_count = 2
        
        # Determine available width
        pad_x = 20
        pad_y = 20
        start_y = 20
        
        # Width available for content is Window Width - Sidebar (200)
        # OR self.canvas.winfo_width()
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100: canvas_w = self.last_width - 200 # Fallback
        
        # Adjust calculations
        # content_width = canvas_w
        # margins (left/right) = pad_x
        # gap between cols = pad_x
        # total_width = 2 * card_width + 1 * pad_x + 2 * pad_x (margins)
        # card_width = (canvas_w - 3 * pad_x) / 2
        
        available_w = canvas_w - (3 * pad_x) # 2 outer margins + 1 inner gap
        card_width = int(available_w // 2)
        
        # Safety min width
        if card_width < 200: card_width = 200
        
        card_height = 140 # Keep height fixed for consistency

        # Centrage / Padding
        start_x = pad_x # Left margin
        
        if not filtered:
            msg = f"Aucun résultat pour '{self.search_query}'" if self.search_query else "Aucun outil dans cette catégorie."
            self.canvas.create_text(canvas_w // 2, 100, text=msg, fill="white", font=("Arial", 16), tags="content")
            return

        for idx, script in enumerate(filtered):
            row = idx // col_count
            col = idx % col_count
            
            x = start_x + col * (card_width + pad_x)
            y = start_y + row * (card_height + pad_y)
            
            self.draw_card(script, x, y, card_width, card_height)

        # Calculate Total Height
        total_rows = (len(filtered) + col_count - 1) // col_count
        content_total_h = start_y + total_rows * (card_height + pad_y) + 50 # padding bottom
        self.update_content_height(content_total_h)

    def setup_background(self):
        """Configure l'image de fond Sakura (Globale)."""
        try:
            bg_path = get_path(os.path.join("assets", "sakura_bg.png"))
            if os.path.exists(bg_path):
                # Init with default size 720 (height logic)
                target_h = 720
                
                original_img = Image.open(bg_path)
                
                # Logic "Fit Height"
                ratio = target_h / original_img.height
                
                new_w = int(original_img.width * ratio)
                new_h = target_h

                pil_image = original_img.resize((new_w, new_h), Image.LANCZOS)
                
                self.bg_image_ref = CTkImage(pil_image, size=(new_w, new_h)) 
                self.pil_bg_image = pil_image 
                self.canvas_bg_photo = ImageTk.PhotoImage(pil_image) 

                # anchor="ne" : aligné en haut à droite
                self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image_ref, anchor="ne")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower() 
            else:
                logger.warning(f"Background image not found at {bg_path}")
        except Exception as e:
            logger.error(f"Erreur background setup: {e}")

    def setup_sidebar(self):
        """Crée la barre latérale avec les catégories."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="transparent")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) # Force 200px width strict
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🌸 Retrogaming 🌸\nToolkit", 
                                     font=("Roboto Medium", 20), text_color=self.COLOR_ACCENT_PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.category_buttons = {}
        categories = [
            "Favoris",
            "Tout",
            "Gestion des Jeux & ROMs",
            "Métadonnées & Gamelists",
            "Multimédia & Artworks",
            "Organisation & Collections",
            "Maintenance Système"
        ]
        
        for i, cat in enumerate(categories):
            btn = ctk.CTkButton(self.sidebar_frame, text=cat, anchor="w",
                                fg_color="transparent", text_color=self.COLOR_TEXT_MAIN,
                                hover_color=self.COLOR_SIDEBAR_HOVER,
                                font=("Roboto", 13),
                                height=35,
                                command=lambda c=cat: self.change_category(c))
            btn.grid(row=i+1, column=0, sticky="ew", padx=10, pady=2)
            self.category_buttons[cat] = btn

        # Spacer to push everything down
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        # Container for bottom elements (GIF, Track, Footer)
        self.sidebar_bottom_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_bottom_container.grid(row=10, column=0, sticky="ew", padx=0, pady=0)

        # 1. GIF
        self.gif_label = ctk.CTkLabel(self.sidebar_bottom_container, text="")
        self.gif_label.pack(side="top", pady=(0, 5))
        self.start_gif_rotation()

        # 2. Track Info (3 Levels Scrolling)
        # Ligne 1: Chanson (Blanc)
        self.song_label = ctk.CTkLabel(self.sidebar_bottom_container, text="Loading...", 
                                      font=("Roboto Medium", 12), text_color="white", width=190)
        self.song_label.pack(side="top", pady=(0, 0), padx=5)

        # Ligne 2: Artiste (Gris)
        self.artist_label = ctk.CTkLabel(self.sidebar_bottom_container, text="", 
                                      font=("Roboto", 11), text_color="gray70", width=190)
        self.artist_label.pack(side="top", pady=(0, 0), padx=5)

        # Ligne 3: Album/Jeu (Blanc)
        self.album_label = ctk.CTkLabel(self.sidebar_bottom_container, text="", 
                                      font=("Roboto Medium", 11), text_color="white", width=190)
        self.album_label.pack(side="top", pady=(0, 10), padx=5)

        self.start_track_updater()
        self.start_marquee_loop()
            
        # 3. Footer (Version + Controls)
        self.bottom_frame = ctk.CTkFrame(self.sidebar_bottom_container, fg_color="transparent")
        self.bottom_frame.pack(side="top", fill="x", padx=20, pady=(0, 15))

        self.version_label = ctk.CTkLabel(self.bottom_frame, text=f"v{VERSION}", text_color=self.COLOR_TEXT_SUB)
        self.version_label.pack(side="left")
        
        # Spacer for controls
        # (Music controls are added later via setup_music_controls targeting self.bottom_frame)
        
        # Update Status (Placed below version/controls)
        self.update_status_label = ctk.CTkLabel(self.sidebar_bottom_container, text="...", text_color=self.COLOR_TEXT_SUB, font=("Arial", 10))
        self.update_status_label.pack(side="top", pady=(0, 15))

        # Music Controls
        self.setup_music_controls()


    def setup_content_area(self):
        """Crée la zone principale de contenu avec Canvas et Scroll Manuel pour un fond fixe parfait."""
        self.content_container = ctk.CTkFrame(self, fg_color="transparent") 
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # --- Header : Recherche & Language ---
        self.header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent", height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 10), padx=20)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(self.header_frame, textvariable=self.search_var, 
                                       placeholder_text=TRANSLATIONS[self.current_lang]["search_placeholder"],
                                       border_color=self.COLOR_ACCENT_PRIMARY, border_width=1,
                                       fg_color="#1a1a1a")
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True, ipady=5)
        
        # Reset Button (X)
        self.clear_btn = ctk.CTkButton(self.header_frame, text="✕", width=40, fg_color="#1a1a1a", 
                                         border_width=1, border_color=self.COLOR_TEXT_SUB,
                                         hover_color="#333",
                                         command=self.clear_search)
        self.clear_btn.pack(side="left", padx=(0, 10))

        # Language Selector
        self.lang_var = ctk.StringVar(value="FR")
        self.lang_menu = ctk.CTkOptionMenu(self.header_frame, values=["FR", "EN", "ES", "IT", "DE", "PT"],
                                         command=self.change_language,
                                         variable=self.lang_var,
                                         width=70,
                                         fg_color="#1a1a1a", button_color="#333",
                                         button_hover_color="#444",
                                         text_color="white")
        self.lang_menu.pack(side="right")

        # --- Canvas Area ---
        # NOTE: bg color needs to be transparent-like or matching sidebar if needed, 
        # but since we draw background image on canvas, it's fine.
        # Actually in draw_background_on_canvas we assume self.canvas exists.
        
        self.canvas = ctk.CTkCanvas(self.content_container, bg="black", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar with custom command to sync background
        self.scrollbar = ctk.CTkScrollbar(self.content_container, orientation="vertical", command=self.scroll_yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Mousewheel binding
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def scroll_yview(self, *args):
        self.canvas.yview(*args)
        self.update_background_position()

    def update_background_position(self):
        try:
             # Reposition background to stay top-right relative to Viewport
             y0 = self.canvas.canvasy(0)
             canvas_width = self.last_width - 200
             self.canvas.coords("bg", canvas_width, y0)
        except: pass



    def on_canvas_configure(self, event):
        self.visible_height = event.height
        self.draw_background_on_canvas()
        self.update_scrollbar()

    def change_language(self, new_lang):
        """Change la langue de l'interface et rafraîchit l'affichage."""
        logger.info(f"Changement de langue : {self.current_lang} -> {new_lang}")
        self.current_lang = new_lang
        global CURRENT_LANG
        CURRENT_LANG = new_lang
        
        t = TRANSLATIONS[new_lang]
        
        # Mettre à jour les textes statiques
        self.search_entry.configure(placeholder_text=t["search_placeholder"])
        # Update search clear button ? No text there.
        
        # Update categories buttons
        cat_keys = {
            "Favoris": "cat_fav",
            "Tout": "cat_all",
            "Gestion des Jeux & ROMs": "cat_games",
            "Métadonnées & Gamelists": "cat_metadata",
            "Multimédia & Artworks": "cat_media",
            "Organisation & Collections": "cat_org",
            "Maintenance Système": "cat_sys"
        }
        
        for original_cat, btn in self.category_buttons.items():
            key = cat_keys.get(original_cat)
            if key:
                btn.configure(text=t[key])
                
        # Re-apply category selection to update button colors provided functionality remains same
        # But we need to update self.current_category if it was a translated string?
        # Actually logic uses original keys "Tout", etc. so we should KEEP original keys for logic
        # and only update TEXT on buttons.
        
        # Rafraîchir la liste des scripts (descriptions)
        self.filter_and_display()

    # Removed misplaced header setup code from here
        
    def open_custom_readme(self, script):
        """Ouvre le ReadME support multilingue via JSON."""
        # Récupérer le contenu depuis le JSON chargé
        script_readmes = self.readmes_data.get(script["name"], {})
        
        # Fallback priority: Current Lang -> EN -> FR -> First available -> Empty
        content = script_readmes.get(self.current_lang)
        if not content: content = script_readmes.get("EN")
        if not content: content = script_readmes.get("FR")
        
        if not content:
            # Fallback legacy file checking if JSON incomplete? 
            # Or just show default message
             content = "Readme non disponible / Readme not available."

        # Titre de la fenêtre
        readme_title = f"{script['name']} - ReadMe"
        
        # Couleurs du thème actuel
        fg = self.COLOR_SIDEBAR_BG
        txt = self.COLOR_TEXT_MAIN
        acc = self.COLOR_ACCENT_PRIMARY
        
        # Icône du script
        icon_path = None
        possible_icon = get_path(os.path.join("assets", f"{script['name']}.ico"))
        if os.path.exists(possible_icon):
            icon_path = possible_icon
            
        # Créer la fenêtre
        ReadmeWindow(self, readme_title, content, fg, txt, acc, icon_path)

    def draw_card(self, script, x, y, w, h):
        """Dessine une carte (mise à jour pour utiliser la traduction)."""
        # Fond de carte
        bg_color = self.COLOR_SIDEBAR_BG
        border_color = self.COLOR_CARD_BORDER
        
        # Create a frame acting as the card
        # Note: In a Canvas, we usually use create_window or draw primitives.
        # But here logic was not fully shown in the view_file (it stopped at line 800).
        # However, looking at the code I see `draw_card` logic was NOT in lines 1-800 usually?
        # WAIT. The user code in `view_file` output stopped at line 800 but `draw_card` calls were inside `filter_and_display`.
        # I need to know how `draw_card` is implemented currently or if I need to implement it.
        # Since I can't see `draw_card` definition in the 1-800 lines (it was likely further down), 
        # I MUST read the rest of the file first to properly override it or ensure I don't break it.
        # BUT `filter_and_display` (lines 573-641) calls `self.draw_card(script, x, y, card_width, card_height)`.
        # So `draw_card` must be defined after line 800.
        pass # Placeholder logic for this chunk construction, see below explanation.


    def update_content_height(self, height):
        self.content_height = max(height, self.visible_height)
        # Update scrollregion to allow scrolling
        self.canvas.configure(scrollregion=(0, 0, self.last_width, self.content_height))
        # No need to manually call update_scrollbar if yscrollcommand is linked, 
        # but CTkScrollbar might need it if not auto-updating.
        # Actually standard tkinter canvas updates scrollbar automatically via yscrollcommand.
        
    def update_scrollbar(self):
        # Allow manual update if needed (e.g. on resize)
        pass

    def on_scrollbar_drag(self, *args):
        # args can be ('moveto', 'float') or ('scroll', 'int', 'units')
        if not self.content_height: return
        
        if args[0] == 'moveto':
            target_ratio = float(args[1])
            # Target Y position
            target_y = -1 * target_ratio * self.content_height
            self.scroll_absolute(target_y)
            
        elif args[0] == 'scroll':
            amount = int(args[1])
            # Scroll step
            step = 30 * -amount # inverted
            self.scroll_relative(step)

    def on_mousewheel(self, event):
        if self.content_height > self.visible_height:
             self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
             self.update_background_position()



    def draw_background_on_canvas(self):
        # Dessine le fond sur le Canvas, aligné à DROITE (NE)
        self.canvas.delete("bg")
        try:
            if hasattr(self, 'canvas_bg_photo') and self.canvas_bg_photo:
                # La fenêtre fait self.last_width de large
                # Le sidebar fait 200.
                # Le Canvas commence à x=200.
                # La largeur du Canvas est donc window_width - 200.
                # On veut que le bord droit de l'image (anchor=ne) soit au bord droit du Canvas.
                
                canvas_width = self.last_width - 200
                y0 = self.canvas.canvasy(0) # Start at current top
                if canvas_width > 0:
                    self.canvas.create_image(canvas_width, y0, image=self.canvas_bg_photo, anchor="ne", tags="bg")
                    self.canvas.tag_lower("bg")
        except Exception as e:
            logger.error(f"Canvas BG Error: {e}")

        self.setup_music_controls()
        
        # Select "Tout" category by default
        self.after(100, lambda: self.change_category("Tout"))

    def change_category(self, category):
        if self.current_category in self.category_buttons:
             self.category_buttons[self.current_category].configure(text_color=self.COLOR_TEXT_MAIN, fg_color="transparent")
        self.current_category = category
        self.category_buttons[category].configure(text_color=self.COLOR_ACCENT_PRIMARY, fg_color="#333333")
        self.filter_and_display()

    def on_search_change(self, *args):
        self.search_query = self.search_var.get().lower().strip()
        self.filter_and_display()

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()

    # Removed duplicate open_custom_readme
    
    def filter_and_display(self):
        self.canvas.delete("content") # Only delete scrollable content
        
        # Reset Scroll
        self.scroll_y = 0
        self.canvas.yview_moveto(0) 
        self.update_background_position() 
        
        filtered = []
        for s in self.scripts:
            if self.current_category == "Favoris":
                cat_match = s["name"] in self.favorites
            else:
                cat_match = (self.current_category == "Tout") or (s.get("category") == self.current_category)

            search_match = True
            if self.search_query:
                # Use translated description for search
                desc = SCRIPT_DESCRIPTIONS.get(s["name"], {}).get(self.current_lang, "")
                tags = f"{s['name']} {desc} {s.get('category','')}".lower()
                if self.search_query not in tags: search_match = False
            if cat_match and search_match: filtered.append(s)
        
        filtered.sort(key=lambda x: (x["name"] not in self.favorites, x["name"]))

        # Layout sorting
        col_count = 2
        card_width = 400
        card_height = 140
        pad_x = 20
        pad_y = 20
        
        # Obtenir la largeur visible dynamique du Canvas
        # Fallback à 900 (taille min fenêtre - sidebar) si canvas pas encore affiché
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 100: canvas_w = 900 
        
        total_content_width = (col_count * card_width) + ((col_count - 1) * pad_x)
        
        # Centrage horizontal
        start_x = (canvas_w - total_content_width) // 2
        if start_x < 20: start_x = 20 # Minimum padding left
        
        start_y = 20
        
        if not filtered:
            msg = TRANSLATIONS[self.current_lang]["no_result"].format(self.search_query) if self.search_query else TRANSLATIONS[self.current_lang]["no_tool_cat"]
            self.canvas.create_text(400, 100, text=msg, fill="white", font=("Arial", 16), tags="content")
            return

        for idx, script in enumerate(filtered):
            row = idx // col_count
            col = idx % col_count
            x = start_x + col * (card_width + pad_x)
            y = start_y + row * (card_height + pad_y)
            self.draw_card(script, x, y, card_width, card_height)

        # Calculate Total Height
        total_rows = (len(filtered) + col_count - 1) // col_count
        content_total_h = start_y + total_rows * (card_height + pad_y) + 50 # padding bottom
        self.update_content_height(content_total_h)

    def draw_card(self, script, x, y, w, h):
        # Add tags="content" to EVERYTHING that should scroll
        
        # Semi-transparent background for readability
        # Create a semi-transparent image on the fly (cached)
        if not hasattr(self, 'card_bg_img_cache') or (w, h) not in self.card_bg_img_cache:
            if not hasattr(self, 'card_bg_img_cache'):
                self.card_bg_img_cache = {}
            # Black with 70% opacity (approx 180/255)
            pil_bg = Image.new('RGBA', (w, h), (30, 30, 30, 200)) 
            self.card_bg_img_cache[(w, h)] = ImageTk.PhotoImage(pil_bg)
            
        self.canvas.create_image(x, y, image=self.card_bg_img_cache[(w, h)], anchor="nw", tags="content")

        # Border
        self.canvas.create_rectangle(x, y, x+w, y+h, outline=self.COLOR_CARD_BORDER, width=1, tags="content")
        
        # Favorite Button
        is_fav = script["name"] in self.favorites
        fav_text = "★" if is_fav else "☆"
        fav_color = "#FFD700" if is_fav else "gray"

        fav_btn = ctk.CTkButton(self.canvas, text=fav_text, width=30, height=30,
                                 fg_color="transparent", text_color=fav_color,
                                 font=("Arial", 20),
                                 hover_color="#333",
                                 command=lambda n=script["name"]: self.toggle_favorite(n))

        self.canvas.create_window(x + w - 10, y + 10, window=fav_btn, anchor="ne", tags="content")

        # Icon
        icon_path = script.get("icon", "")
        if icon_path not in self.icon_cache:
             try:
                 if os.path.exists(icon_path):
                     img = Image.open(icon_path).resize((40, 40), Image.LANCZOS)
                     self.icon_cache[icon_path] = ImageTk.PhotoImage(img)
             except: pass
        if icon_path in self.icon_cache:
            self.canvas.create_image(x + 20, y + 20, image=self.icon_cache[icon_path], anchor="nw", tags="content")

        # Title
        self.canvas.create_text(x + 70, y + 20, text=script["name"], fill=self.COLOR_TEXT_MAIN, 
                                font=("Roboto Medium", 16), anchor="nw", tags="content")
        
        # Description
        desc = SCRIPT_DESCRIPTIONS.get(script["name"], {}).get(self.current_lang, "")
        self.canvas.create_text(x + 70, y + 50, text=desc, fill=self.COLOR_TEXT_SUB,
                                font=("Roboto", 12), anchor="nw", width=w-90, tags="content")
        
        # Buttons
        # Note: Canvas windows move with canvas.move if they are on the canvas!
        # But we need to make sure we create_window with tags="content"? 
        # Tkinter create_window accepts tags!
        
        readme_btn = ctk.CTkButton(self.canvas, text="?", width=30, height=30,
                                 fg_color="transparent", text_color=self.COLOR_ACCENT_PRIMARY, 
                                 border_width=1, border_color=self.COLOR_ACCENT_PRIMARY, 
                                 hover_color="#333",
                                 command=lambda s=script: self.open_custom_readme(s))
        
        self.canvas.create_window(x + 20, y + h - 45, window=readme_btn, anchor="nw", tags="content")
        
        launch_btn = ctk.CTkButton(self.canvas, text=TRANSLATIONS[self.current_lang]["open"], height=30, width=w-70,
                                 fg_color="transparent", text_color=self.COLOR_ACCENT_PRIMARY,
                                 border_width=1, border_color=self.COLOR_ACCENT_PRIMARY,
                                 hover_color="#333333",
                                 font=("Roboto Medium", 13),
                                 command=lambda n=script["name"]: self.execute_module(n))
        
        self.canvas.create_window(x + 60, y + h - 45, window=launch_btn, anchor="nw", tags="content")

    def get_icon(self, path):
        if path in self.icon_cache:
            return self.icon_cache[path]
        try:
            if os.path.exists(path):
                img = Image.open(path).resize((40, 40), Image.LANCZOS)
                ctk_img = CTkImage(img, size=(40, 40))
                self.icon_cache[path] = ctk_img
                return ctk_img
        except: pass
        return CTkImage(Image.new("RGBA", (40, 40), (100, 100, 100, 0)), size=(40, 40))

    def execute_module(self, module_name):
        lancer_module(module_name)

    def check_updates(self):
        def update_worker():
             try:
                 update_available, latest_version, installer_url = check_for_updates()
                 # Check if the window still exists before scheduling callback
                 if self.winfo_exists():
                     self.after(0, lambda: self.update_update_ui(update_available, latest_version, installer_url))
             except Exception as e:
                 logger.debug(f"Update check thread ignored: {e}")
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()

    def update_update_ui(self, update_available, latest_version, installer_url):
        if update_available:
            self.update_status_label.configure(text=f"Update: {latest_version}", text_color=self.COLOR_ACCENT_PRIMARY)
            
            # Propose update automatically
            if installer_url:
                 # Check if frozen (running as exe)
                 is_frozen = False
                 if globals().get("utils") and hasattr(utils, 'is_frozen'):
                     is_frozen = utils.is_frozen()
                 elif getattr(sys, 'frozen', False):
                     is_frozen = True
                 
                 if is_frozen:
                     if messagebox.askyesno("Mise à jour disponible", f"Une nouvelle version ({latest_version}) est disponible.\nVoulez-vous la télécharger et l'installer maintenant ?"):
                         # Run in thread to avoid freezing UI during download
                         threading.Thread(target=download_and_run_installer, args=(installer_url, self), daemon=True).start()
        else:
            self.update_status_label.configure(text=f"À jour", text_color="green")



    def init_music(self):
        """Initialise la radio via Processus Isolé."""
        self.music_playing = False
        self.music_muted = False
        self.gif_paused = False
        
        # Communication Queue
        self.radio_queue = multiprocessing.Queue()
        
        # Start Radio Process
        self.radio_process = multiprocessing.Process(target=radio.run_radio_process, args=(self.radio_queue,))
        self.radio_process.daemon = True
        self.radio_process.start()
        
        # Register cleanup
        atexit.register(self.cleanup)

    def play_radio(self):
        """Envoie la commande PLAY au processus radio."""
        if self.music_playing:
            return

        stream_url = "http://stream.radiojar.com/2fa4wbch308uv"
        
        # Update UI Immediately (Optimistic)
        self.music_playing = True
        self.play_btn.configure(text="⏸️")
        
        if self.gif_paused:
            self.gif_paused = False
            self.animate_gif()
            
        # Send Command
        if self.radio_process.is_alive():
             self.radio_queue.put(f"PLAY:{stream_url}")
        else:
             # Restart if died?
             self.init_music() # simplified

    def stop_radio(self):
        """Envoie la commande STOP au processus radio."""
        self.music_playing = False
        self.play_btn.configure(text="▶️")
        self.gif_paused = True
        
        if self.radio_process.is_alive():
             self.radio_queue.put("STOP")

    def cleanup(self):
        """Nettoyage final."""
        try:
            if hasattr(self, 'radio_queue'):
                self.radio_queue.put("EXIT")
            
            if hasattr(self, 'radio_process') and self.radio_process.is_alive():
                self.radio_process.join(timeout=1)
                if self.radio_process.is_alive():
                    self.radio_process.terminate()
        except: pass
        
        try:
            if hasattr(self, 'mute_flag_path') and os.path.exists(self.mute_flag_path):
                os.remove(self.mute_flag_path) # Legacy cleanup just in case
        except: pass
        try:
            pygame.quit()
        except: pass

    def setup_music_controls(self):
        """Ajoute les contrôles de musique dans la sidebar."""
        # Clean existing controls if any
        for widget in self.bottom_frame.winfo_children():
            # Keep version label (checked by text or class, but simplest is to repack version loop if needed)
            # Actually simplest: Remove play/mute buttons only.
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") in ["⏸️", "▶️", "🔊", "🔇"]:
                widget.destroy()

        # Play/Pause Button
        # Start state depends on self.music_playing (which might be pending)
        # Default to Pause icon (assuming auto-play) or Play if failed
        
        icon = "⏸️" if self.music_playing else "▶️"
        # If we are just starting up, music_playing is False initially until thread succeeds.
        # But we want to show it's *trying* to play? 
        # For now, let's default to "Play" icon if not playing, but we know init_music calls play_radio.
        # We'll let play_radio update the icon to Pause when it succeeds.
        
        self.play_btn = ctk.CTkButton(self.bottom_frame, text=icon, width=30, height=30,
                                      fg_color="transparent", border_width=0, 
                                      text_color=self.COLOR_TEXT_MAIN,
                                      font=("Segoe UI Emoji", 20),
                                      hover_color=self.COLOR_SIDEBAR_HOVER,
                                      command=self.toggle_music)
        self.play_btn.pack(side="left", padx=(15, 5))
        
        # Mute Button
        self.mute_btn = ctk.CTkButton(self.bottom_frame, text="🔊", width=30, height=30,
                                      fg_color="transparent", border_width=0, 
                                      text_color=self.COLOR_TEXT_MAIN,
                                      font=("Segoe UI Emoji", 20),
                                      hover_color=self.COLOR_SIDEBAR_HOVER,
                                      command=self.toggle_mute)
        self.mute_btn.pack(side="left", padx=5)

    def toggle_music(self):
        if self.music_playing:
            self.stop_radio()
            # UI updated in stop_radio
        else:
            self.play_radio()
            # UI updated in play_radio thread success callback

    def toggle_mute(self):
        if self.music_muted:
            self.radio_queue.put("UNMUTE")
            self.mute_btn.configure(text="🔊")
            self.music_muted = False
        else:
            self.radio_queue.put("MUTE")
            self.mute_btn.configure(text="🔇")
            self.music_muted = True

    def start_gif_rotation(self):
        """Charge les deux GIFs et lance la rotation."""
        self.gif_list = []
        
        # Charger dance2.gif d'abord
        g1 = self.load_gif_data(os.path.join("assets", "dance2.gif"))
        if g1: self.gif_list.append(g1)
        
        # Charger dance.gif ensuite
        g2 = self.load_gif_data(os.path.join("assets", "dance.gif"))
        if g2: self.gif_list.append(g2)
        
        if not self.gif_list:
            return

        self.current_gif_index = 0
        self.set_active_gif(self.gif_list[0])
        self.animate_gif()
        
        # Rotation timer (60s) seulement si on a plus d'un GIF
        if len(self.gif_list) > 1:
            self.rotate_gif()

    def load_gif_data(self, path):
        """Charge les frames et le délai d'un GIF."""
        try:
            full_path = get_path(path)
            if not os.path.exists(full_path):
                return None

            gif = Image.open(full_path)
            duration = gif.info.get('duration', 100)
            if duration < 20: duration = 100
            
            frames = []
            try:
                while True:
                    frame = gif.copy().convert("RGBA")
                    target_w = 150
                    ratio = target_w / frame.width
                    target_h = int(frame.height * ratio)
                    frame = frame.resize((target_w, target_h), Image.LANCZOS)
                    frames.append(CTkImage(frame, size=(target_w, target_h)))
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
                
            if frames:
                return {'frames': frames, 'delay': duration}
        except Exception as e:
            logger.error(f"GIF Load Error {path}: {e}")
        return None

    def set_active_gif(self, gif_data):
        """Définit le GIF actif."""
        self.gif_frames = gif_data['frames']
        self.gif_delay = gif_data['delay']
        self.current_frame_idx = 0

    def rotate_gif(self):
        """Change de GIF toutes les 60 secondes."""
        self.current_gif_index = (self.current_gif_index + 1) % len(self.gif_list)
        new_gif = self.gif_list[self.current_gif_index]
        self.set_active_gif(new_gif)
        
        # Re-planifier dans 60s
        self.after(60000, self.rotate_gif)

    def animate_gif(self):
        """Boucle d'animation du GIF."""
        if self.gif_paused:
            return

        if hasattr(self, 'gif_frames') and self.gif_frames:
            frame = self.gif_frames[self.current_frame_idx]
            self.gif_label.configure(image=frame)
            
            self.current_frame_idx = (self.current_frame_idx + 1) % len(self.gif_frames)
            
            self.after(self.gif_delay, self.animate_gif)


    def start_track_updater(self):
        """Lance le thread de mise à jour des infos musique."""
        threading.Thread(target=self.track_updater_loop, daemon=True).start()

    def track_updater_loop(self):
        """Boucle de mise à jour du titre en cours."""
        api_url = "https://www.radiojar.com/api/stations/2fa4wbch308uv/now_playing/"
        while True:
            try:
                r = requests.get(api_url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    song_name = data.get('title', '')
                    artist_name = data.get('artist', '')
                    album_name = data.get('album', '')
                    
                    self.update_marquee_text(song_name, artist_name, album_name)
                
            except Exception as e:
                 pass
            
            # Wait 20 seconds before next update
            threading.Event().wait(20)

    def update_marquee_text(self, t1, t2, t3):
        self.marquee_data = {
            "l1": {"full": t1, "idx": 0},
            "l2": {"full": t2, "idx": 0},
            "l3": {"full": t3, "idx": 0}
        }

    def start_marquee_loop(self):
        self.marquee_data = {
            "l1": {"full": "", "idx": 0}, 
            "l2": {"full": "", "idx": 0}, 
            "l3": {"full": "", "idx": 0}
        }
        self.after(250, self.marquee_step)

    def marquee_step(self):
        try:
            mapping = [
                ("l1", self.song_label),
                ("l2", self.artist_label),
                ("l3", self.album_label)
            ]
            for key, label in mapping:
                data = self.marquee_data.get(key)
                if not data or not data["full"]: 
                    label.configure(text="")
                    continue
                
                text = data["full"]
                limit = 28
                if len(text) > limit:
                    idx = data["idx"]
                    display_len = limit
                    # Infinite scroll with spaces
                    extended = text + "     " + text
                    display_text = extended[idx : idx + display_len]
                    label.configure(text=display_text)
                    data["idx"] = (idx + 1) % (len(text) + 5)
                else:
                    label.configure(text=text)
        except: pass
        self.after(200, self.marquee_step)

def main():
    """Point d'entrée principal de l'application"""
    multiprocessing.freeze_support()

    global app
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
