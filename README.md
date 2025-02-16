**Retrogaming Toolkit AIO**  
Une interface graphique centralisée regroupant des outils pour la gestion de jeux rétro, de collections et de fichiers multimédias.  
---
### **Fonctionnalités principales**  
#### **Gestion des jeux**  
1. **assisted_gamelist_creator**  
   - Crée ou met à jour des fichiers XML, identifie les jeux manquants, fusionne et sauvegarde les listes.  
2. **CHD_Converter_Tool**  
   - Conversion entre formats (ISO, CUE, GDI, CHD), vérification d’intégrité, support des archives compressées (ZIP, RAR, 7Z).  
3. **game_batch_creator**  
   - Génère des fichiers batch pour jeux normaux, Steam et Epic Games.  
4. **game_removal**  
   - Supprime les jeux et leurs fichiers associés (ROMs, sauvegardes, etc.).  
5. **gamelist_to_hyperlist**  
   - Convertit un fichier `gamelist.xml` en `hyperlist.xml`.  
6. **hyperlist_to_gamelist**  
   - Transforme les hyperlist en gamelist, avec gestion des métadonnées.  
---
#### **Gestion des collections**  
7. **collection_builder**  
   - Crée des collections personnalisées via mots-clés et organise les dossiers (artworks, logos, vidéos).  
8. **collection_extractor**  
   - Extrait des collections existantes, compatible avec RetroArch et autres émulateurs.  
---
#### **Gestion des médias**  
9. **media_orphan_detector**  
   - Détecte et déplace les fichiers multimédias sans ROM correspondante.  
10. **merge_story_hyperlist**  
    - Intègre des fichiers texte dans des hyperlist XML.  
11. **story_format_cleaner**  
    - Nettoie les fichiers texte pour une compatibilité XML optimale.  
12. **video_converter**  
    - Convertit et rogne des vidéos par lot (réglage du débit, résolution, FPS).  
13. **folder_name_to_txt**  
    - Génère un fichier texte vide par fichier avec une extension spécifique.  
14. **folder_to_zip**  
    - Compresse individuellement des fichiers en ZIP et supprime les originaux.  
15. **rvz_iso_convert**  
    - Conversion bidirectionnelle entre ISO et RVZ.  
16. **MaxCSO_Compression_Script**  
    - Compresse des ISO en CSO/DAX avec optimisation multicœur.  
---
#### **Outils système**  
17. **enable_long_paths**  
    - Active les chemins longs (>260 caractères) sous Windows.  
18. **install_dependencies**  
    - Installe automatiquement les composants système (Visual C++, DirectX, etc.).  
19. **liste_fichier_simple**  
    - Liste tous les fichiers d’un répertoire.  
20. **liste_fichier_windows**  
    - Exporte la liste des fichiers/dossiers dans un fichier `Liste.txt`.  
21. **folder_cleaner**  
    - Supprime les dossiers vides et leurs sous-dossiers.  
22. **cbzkiller**  
    - Convertit des fichiers PDF/CBR en CBZ.  
23. **empty_generator**  
    - Crée des fichiers vides avec des extensions spécifiques.  
24. **YT_Download**  
    - Télécharge des vidéos, playlists et chaînes YouTube.  
25. **cover_extractor**  
    - Extrait la première image des fichiers CBZ, CBR et PDF.  
26. **m3u_creator**  
    - Génère des fichiers M3U pour jeux multi-disques et Vita3k.  
27. **BGBackup**  
    - Sauvegarde les fichiers gamelist.xml.  
---
### **Interface graphique**  
- **Technologie** : customtkinter  
- **Caractéristiques** :  
  - Interface moderne, réactive et organisée en sections.  
  - Notifications visuelles pour guider l’utilisateur.  
---
### **Utilisation**  
1. **Lancement** : Exécutez `main.py` pour ouvrir l’interface.  
2. **Navigation** : Accédez aux outils via les onglets ou la barre latérale.  
3. **Exécution** : Sélectionnez un outil, configurez les paramètres, puis lancez-le.  
4. **Gestion des erreurs** : Des messages détaillés aident au dépannage.  
---
### **Prérequis**  
- Exécutez `_install_first.bat` pour installer automatiquement les dépendances.  
- Si besoin, installez manuellement avec :  
  ```bash  
  pip install -r requirements.txt  
  ```  