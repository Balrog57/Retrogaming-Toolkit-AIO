## 2025-02-18 - FFmpeg Syntax Mismatch
**Erreur :** Le filtre `scale` de FFmpeg a reçu une résolution au format `1920x1080` au lieu de `1920:1080`, causant un échec silencieux ou explicite de la conversion.
**Cause :** Validation de l'entrée utilisateur (`regex ^\d+x\d+$`) alignée sur l'UX ("WxH") mais passée brute à une commande système attendant un format différent ("W:H").
**Prévention :** Toujours découpler le format de validation UX du format de commande système via une étape de normalisation explicite avant l'exécution.
