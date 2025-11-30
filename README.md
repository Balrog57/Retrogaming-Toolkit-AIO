# 🕹️ Retrogaming Toolkit AIO

![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

**La boîte à outils pour les passionnés d'émulation et de retrogaming.**

**Retrogaming Toolkit AIO** est une suite logicielle centralisée regroupant plus de 25 outils puissants pour automatiser, nettoyer et optimiser votre collection de jeux. Conçu pour fonctionner main dans la main avec des frontends comme **RetroBat**, **EmulationStation**, **Batocera** ou **HyperSpin**, ce programme modulaire vous fait gagner un temps précieux dans la gestion de vos ROMs, de vos médias et de vos fichiers de configuration.

---

## 📋 Table des Matières

- [✨ Fonctionnalités Principales](#-fonctionnalités-principales)
- [🛠️ Liste des Modules](#️-liste-des-modules)
  - [Gestion des Jeux & ROMs](#gestion-des-jeux--roms)
  - [Métadonnées & Gamelists](#métadonnées--gamelists)
  - [Multimédia & Artworks](#multimédia--artworks)
  - [Organisation & Collections](#organisation--collections)
  - [Maintenance Système](#maintenance-système)
- [🚀 Installation](#-installation)
- [💻 Utilisation](#-utilisation)
- [🔄 Mises à jour](#-mises-à-jour)

---

## ✨ Fonctionnalités Principales

* **Interface Unifiée :** Une GUI moderne et sombre (basée sur `customtkinter`) qui regroupe tous les scripts en un seul endroit.
* **Modulaire :** Chaque outil est indépendant. Lancez uniquement ce dont vous avez besoin.
* **Documentation Intégrée :** Chaque module dispose de son propre bouton "Lisez-moi" directement dans l'interface.
* **Optimisation :** Des outils conçus pour le multithreading (utilisation de tous les cœurs CPU) pour les tâches lourdes comme la compression.
* **Mise à jour automatique :** Un système intégré vérifie et installe les dernières versions de la suite depuis GitHub.

---

## 🛠️ Liste des Modules

### Gestion des Jeux & ROMs
Optimisez votre stockage et gérez vos fichiers de jeux.

* **💿 CHD Converter Tool :** Convertissez vos images disques (ISO, CUE, GDI) au format compressé CHD (et inversement). Supporte les archives ZIP/RAR/7Z en entrée.
* **🗜️ MaxCSO Compression :** Compresse vos ISO (PSP/PS2) en format CSO ou ZSO pour réduire drastiquement leur taille.
* **🐬 RVZ/ISO Converter :** Conversion sans perte pour GameCube/Wii entre les formats ISO et RVZ (via DolphinTool).
* **📦 Folder to ZIP :** Compresse chaque jeu d'un dossier dans une archive ZIP individuelle et supprime l'original.
* **🚀 Game Batch Creator :** Génère automatiquement les scripts `.bat` pour lancer vos jeux PC (Windows, Steam, Epic) via votre frontend.
* **🗑️ Game Removal :** Supprime proprement un jeu et **tous** ses médias associés (images, vidéos) pour ne laisser aucune trace.

### Métadonnées & Gamelists
Manipulez vos fichiers XML pour RetroBat, EmulationStation et HyperSpin.

* **🤖 Assisted Gamelist Creator :** Utilise une IA pour remplir automatiquement les descriptions manquantes dans vos `gamelist.xml`.
* **🔄 Gamelist to Hyperlist :** Convertit vos fichiers `gamelist.xml` (RetroBat) vers le format `hyperlist.xml` (HyperSpin).
* **↩️ Hyperlist to Gamelist :** Migrez vos bases de données HyperSpin vers le format standard `gamelist.xml`.
* **🛡️ BGBackup :** Scanne et sauvegarde tous vos fichiers `gamelist.xml` dans une archive ZIP de sécurité.
* **📝 Merge Story Hyperlist :** Fusionne des fichiers textes (synopsis) directement dans vos XML HyperList.
* **🧹 Story Format Cleaner :** Nettoie et normalise les fichiers textes (encodage, caractères spéciaux) pour éviter les erreurs XML.
* **⚙️ ES Systems Custom :** Compare votre configuration `es_systems.cfg` avec l'officielle et extrait vos systèmes personnalisés.

### Multimédia & Artworks
Gérez vos images et vidéos pour une bibliothèque visuellement parfaite.

* **📺 YT Download :** Téléchargez des vidéos, playlists ou chaînes YouTube entières (Audio ou Vidéo 4K).
* **🎥 Video Converter :** Convertissez, redimensionnez et coupez vos vidéos en masse (avec téléchargement auto de FFmpeg).
* **🖼️ Convert Images :** Convertissez des dossiers entiers d'images vers un format cible (PNG, JPG, WEBP...).
* **📖 Cover Extractor :** Extrait automatiquement la première page de vos PDF, CBZ et CBR pour créer des couvertures.
* **🧹 Media Orphan Detector :** Scanne vos dossiers `medium_artwork` et déplace les images qui ne correspondent à aucun jeu (fichiers orphelins).
* **📚 CBZ Killer :** Convertit vos PDF et CBR en format CBZ standardisé.

### Organisation & Collections
Structurez votre ludothèque.

* **📂 Collection Builder :** Crée des collections thématiques (ex: "Zelda", "Mario") en scannant les mots-clés dans vos listes.
* **📦 Collection Extractor :** Extrait une collection complète (roms + médias + configs) vers un dossier autonome.
* **💿 M3U Creator :**
    * Génère les fichiers `.m3u` pour les jeux multi-disques (PS1, Dreamcast...).
    * Crée les `.m3u` pour l'émulateur Vita3K en renommant les ID de jeux.
* **🧹 Folder Cleaner :** Supprime récursivement tous les dossiers vides de votre arborescence.
* **📄 Folder Name to TXT :** Crée un fichier texte vide portant le nom de chaque fichier d'un dossier (utile pour certains scrappers).
* **📄 Empty Generator :** Génère des fichiers vides (ex: `.scummvm`) dans toute une structure de dossiers.

### Maintenance Système
Outils pratiques pour l'environnement Windows.

* **🛣️ Enable Long Paths :** Modifie le registre Windows pour supporter les chemins de fichiers supérieurs à 260 caractères.
* **🛠️ Install Dependencies :** Installe en un clic les Runtime Visual C++, DirectX et OpenAL nécessaires au bon fonctionnement des émulateurs.
* **📝 Liste Fichier Simple/Windows :** Génère des inventaires textuels du contenu de vos dossiers.

---

## 🚀 Installation

1.  **Télécharger :** Clonez ce dépôt ou téléchargez la dernière [Release](https://github.com/Balrog57/Retrogaming-Toolkit-AIO/releases).
2.  **Prérequis :** Assurez-vous d'avoir [Python 3.x](https://www.python.org/downloads/) installé sur votre machine.
3.  **Installation Automatique :**
    * Double-cliquez sur le fichier `_install_first.bat` (si présent) pour installer automatiquement les dépendances Python requises.
    * *Alternative manuelle :* Ouvrez un terminal dans le dossier et tapez :
        ```bash
        pip install -r requirements.txt
        ```
4.  **Démarrage :** Lancez le fichier `main.py` (ou l'exécutable si fourni) pour ouvrir l'interface.

---

## 💻 Utilisation

L'interface est conçue pour être intuitive :

1.  Lancez **Retrogaming Toolkit AIO**.
2.  Naviguez entre les pages de modules avec les boutons **Précédent** et **Suivant**.
3.  Chaque module est présenté avec son icône et une description courte.
4.  Cliquez sur **"Lisez-moi"** à droite d'un module pour afficher son manuel d'utilisation spécifique.
5.  Cliquez sur le **Nom du module** pour le lancer. Une nouvelle fenêtre s'ouvrira pour l'outil sélectionné.

> **Note :** La plupart des outils vérifient eux-mêmes leurs dépendances externes (comme `ffmpeg`, `chdman`, `maxcso`, etc.) et proposent de les télécharger automatiquement s'ils sont manquants.

---

## 🔄 Mises à jour

Le programme intègre un vérificateur de mise à jour automatique.
Au démarrage, l'application compare votre version locale avec la dernière version disponible sur GitHub.

* Si une mise à jour est disponible, un message vert apparaît en bas de la fenêtre principale.
* Cliquez simplement sur le bouton **"Mettre à jour"** pour télécharger et installer la nouvelle version automatiquement.

---
*Fait avec passion pour la communauté du Retrogaming.*