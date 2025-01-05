Retrogaming-Toolkit-AIO

Une interface graphique centralisée regroupant des outils Python pour la gestion de jeux rétro.

Installation

Retrogaming-Toolkit-AIO est une interface graphique (GUI) centralisée qui regroupe une collection d'outils Python pour :

La gestion de jeux

La gestion de collections

La gestion de fichiers multimédias

Caractéristiques principales

Interface intuitive et moderne basée sur customtkinter.

Navigation fluide et simplifiée.

Utilisation sans recours à la ligne de commande.

Fonctionnalités principales

1. Assisted GameList Creator

Gère les fichiers XML existants ou en crée de nouveaux.

Identifie les jeux manquants et facilite leur intégration.

Fonctionnalités incluses :

Fusion

Sauvegarde

Génération de listes de jeux manquants

Interface avec barre de progression et logs en temps réel.

2. CHD Converter Tool

Conversion entre formats (ISO, CUE, GDI et CHD).

Vérification de l'intégrité des fichiers CHD.

Supporte les archives compressées (ZIP, RAR, 7Z).

Traitement multi-cœurs et téléchargement automatique de chdman si nécessaire.

3. Collection Builder

Création de collections personnalisées à partir de mots-clés.

Organisation automatique des structures de dossiers (artworks, logos, vidéos).

Gestion par thèmes ou genres.

4. Collection Extractor

Extraction et organisation de collections existantes.

Prise en charge des émulateurs (RetroArch, etc.).

Génération de rapports des fichiers extraits.

5. Enable Long Paths

Activation du support des chemins longs (260+ caractères) sur Windows.

Nécessite des droits d’administrateur.

6. Folder Name to TXT

Création de fichiers texte vides pour chaque fichier avec une extension spécifiée.

7. Folder to ZIP

Compression individuelle des fichiers d'un dossier en ZIP.

Suppression automatique des fichiers originaux après compression.

8. Game Batch Creator

Création de fichiers batch pour trois types de jeux : normaux, Steam, Epic Games.

Configuration simplifiée des chemins et exécutables.

9. Game Removal Tool

Suppression intuitive des jeux inutiles et de leurs fichiers associés.

10. Gamelist to Hyperlist

Conversion d’un fichier gamelist.xml en hyperlist.xml.

Extraction des métadonnées des jeux.

11. Hyperlist to Gamelist Converter

Transformation de fichiers hyperlist.xml en gamelist.xml.

Gestion des métadonnées (nom, année, développeur, genre, etc.).

12. Install Dependencies

Installation automatique des composants essentiels (Visual C++, DirectX, OpenAL).

13. Liste Fichier Simple

Exploration d'un répertoire pour lister tous les fichiers.

14. Liste Fichier Windows

Liste des fichiers et répertoires dans un fichier Liste.txt.

15. MaxCSO Compression Script

Compression des fichiers ISO en CSO ou DAX avec options flexibles.

Optimisation multi-cœurs.

16. Media Orphan Detector

Détection et déplacement des fichiers multimédias orphelins.

17. Merge Story Hyperlist

Intégration de fichiers texte dans des fichiers XML de type hyperlist.

18. RVZ/ISO Converter

Conversion intuitive entre formats ISO et RVZ.

19. Story Format Cleaner

Normalisation des fichiers texte pour compatibilité XML.

20. Video Converter

Conversion et rognage de vidéos par lot avec options personnalisables (débit, résolution, FPS).

Interface graphique

Technologie : customtkinter

Caractéristiques :

Interface moderne et responsive

Organisation des outils par sections

Notifications visuelles pour guider l’utilisateur

Utilisation

Lancement de l'application :

Exécutez le script principal pour ouvrir l'interface graphique.

Navigation :

Parcourez les outils disponibles via les onglets ou la barre de navigation.

Exécution des outils :

Sélectionnez un outil, configurez ses paramètres et lancez-le.

Gestion des erreurs :

Messages détaillés pour faciliter le dépannage.

Pré-requis

Python et les dépendances listées dans requirements.txt.

Commande d'installation :

pip install -r requirements.txt

Lancer _install_first.bat pour installer Python et les dépendances automatiquement.

Utilisez ensuite main.py pour démarrer l’application.

