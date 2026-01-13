import os
import threading
import time
import webbrowser
from lxml import etree
import customtkinter as ctk
from customtkinter import filedialog
import re
from copy import deepcopy
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GameListApp:
    """
    Application graphique pour enrichir un fichier gamelist.xml (type Recalbox/Batocera)
    en utilisant une API de type OpenAI (comme Google AI Studio) pour
    automatiser la recherche d'informations sur les jeux manquants.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de liste de jeux (v3.1 - Robuste)")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)

        # Variables de l'application
        self.gamelist_path = ctk.StringVar()
        self.updated_gamelist_path = ctk.StringVar(value="updated_gamelist.xml")
        self.missing_games_path = ctk.StringVar(value="failed_games.txt") # Log des jeux en échec
        
        # Logic to find instructions file (handles Clean vs Frozen paths)
        base_dir = os.path.dirname(__file__)
        inst_filename = "instructions_assisted_gamelist_creator.txt"
        inst_path = os.path.join(base_dir, inst_filename)
        
        # Check subfolder (common in PyInstaller --add-data with folder)
        if not os.path.exists(inst_path):
            alt_path = os.path.join(base_dir, "Retrogaming-Toolkit-AIO", inst_filename)
            if os.path.exists(alt_path):
                inst_path = alt_path
                
        self.instructions_path = ctk.StringVar(value=inst_path)
        
        # Variables API
        self.api_key = ctk.StringVar(value="") 
        self.base_url = ctk.StringVar(value="https://generativelanguage.googleapis.com/v1beta/openai/") 
        self.model_name = ctk.StringVar(value="gemini-1.5-flash") 
        
        # Variables d'état
        self.missing_games = [] # Liste des jeux à traiter
        self.progress_value = ctk.DoubleVar(value=0.0)
        self.status_text = ctk.StringVar(value="Prêt")
        self.is_running = False # Flag pour le thread
        self.openai_client = None
        self.instructions_content = "" # Contenu du prompt système

        # --- Configuration de l'interface (Frame 0: Configuration) ---
        config_frame = ctk.CTkFrame(root)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        config_frame.columnconfigure(1, weight=1)

        # Ligne 0: Fichier Gamelist
        ctk.CTkLabel(config_frame, text="Fichier Gamelist :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_entry = ctk.CTkEntry(config_frame, textvariable=self.gamelist_path, width=400, placeholder_text="Sélectionnez un fichier XML...", font=("Arial", 14))
        self.file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Parcourir...", command=self.browse_file, width=150, fg_color="#1f6aa5", hover_color="#144870", font=("Arial", 14)).grid(row=0, column=2, padx=5, pady=5)

        # Ligne 1: Fichier Instructions
        ctk.CTkLabel(config_frame, text="Instructions IA :", font=("Arial", 16)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.instructions_entry = ctk.CTkEntry(config_frame, textvariable=self.instructions_path, width=400, font=("Arial", 14))
        self.instructions_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Parcourir...", command=self.browse_instructions_file, width=150, fg_color="#1f6aa5", hover_color="#144870", font=("Arial", 14)).grid(row=1, column=2, padx=5, pady=5)

        # Ligne 2: URL API
        url_api_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        url_api_frame.grid(row=2, column=0, padx=0, pady=5, sticky="w")
        ctk.CTkLabel(url_api_frame, text="URL API (OpenAI) :", font=("Arial", 16)).pack(side="left", padx=(5, 2))
        help_button = ctk.CTkButton(url_api_frame, text="?", font=("Arial", 16, "bold"), width=30, height=30,
                                    command=self.open_api_key_url, fg_color="#1f6aa5", hover_color="#144870")
        help_button.pack(side="left", padx=(2, 5))
        self.base_url_entry = ctk.CTkEntry(config_frame, textvariable=self.base_url, width=400, font=("Arial", 14))
        self.base_url_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Ligne 3: Modèle API
        ctk.CTkLabel(config_frame, text="Modèle API :", font=("Arial", 16)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.model_name_entry = ctk.CTkEntry(config_frame, textvariable=self.model_name, width=400, font=("Arial", 14))
        self.model_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Ligne 4: Clé API
        ctk.CTkLabel(config_frame, text="Clé API :", font=("Arial", 16)).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.api_key_entry = ctk.CTkEntry(config_frame, textvariable=self.api_key, show="*", width=400, placeholder_text="Entrez votre clé API Google...", font=("Arial", 14))
        self.api_key_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # --- Frame 1: Console ---
        console_frame = ctk.CTkFrame(root)
        console_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(1, weight=1)
        ctk.CTkLabel(console_frame, text="Journal des opérations :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.console = ctk.CTkTextbox(console_frame, width=880, height=300, state='disabled', font=("Arial", 12), wrap="word")
        self.console.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # --- Frame 2: Progression ---
        progress_frame = ctk.CTkFrame(root)
        progress_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(progress_frame, text="Progression :", font=("Arial", 16)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.progress_value, mode='determinate', fg_color="#1f6aa5", progress_color="#144870")
        self.progress_bar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("Arial", 14), text_color="#ffffff")
        self.progress_label.grid(row=1, column=1, padx=5, pady=5)

        # --- Frame 3: Contrôles ---
        control_frame = ctk.CTkFrame(root)
        control_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        control_frame.pack_propagate(False) 
        control_frame.configure(height=50)
        self.start_button = ctk.CTkButton(control_frame, text="Démarrer", command=self.start_process, state="disabled", width=200, 
                                        fg_color="#1f6aa5", hover_color="#144870", font=("Arial", 14, "bold"))
        self.start_button.pack(side="left", padx=5, pady=5)
        self.stop_button = ctk.CTkButton(control_frame, text="Arrêter", command=self.stop_process, state="disabled", width=200, 
                                       fg_color="#a51f1f", hover_color="#701414", font=("Arial", 14, "bold"))
        self.stop_button.pack(side="left", padx=5, pady=5)

        # --- Frame 4: Status Bar ---
        status_frame = ctk.CTkFrame(root)
        status_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_text, anchor="w", font=("Arial", 14))
        self.status_label.pack(fill="x", expand=True, padx=5)

        # Configuration de la grille principale
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1) # La console (row 1) s'étend

    def browse_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier gamelist.xml."""
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers XML", "*.xml")])
        if file_path:
            self.gamelist_path.set(file_path)
            self.validate_file()

    def browse_instructions_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier d'instructions."""
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers Texte", "*.txt")])
        if file_path:
            self.instructions_path.set(file_path)
            self.log_message(f"Fichier d'instructions sélectionné : {file_path}")

    def open_api_key_url(self):
        """Ouvre le lien de création de clé API Google dans le navigateur."""
        self.log_message("Ouverture du site de création de clé API Google...")
        webbrowser.open_new_tab("https://aistudio.google.com/app/apikey")

    def validate_file(self):
        """Valide que le fichier XML sélectionné est un 'gameList'."""
        file_path = self.gamelist_path.get()
        if os.path.exists(file_path):
            try:
                tree = etree.parse(file_path)
                root = tree.getroot()
                if (root.tag == "gameList"):
                    self.start_button.configure(state="normal")
                    self.log_message("Fichier XML valide sélectionné.")
                else:
                    self.start_button.configure(state="disabled")
                    self.log_message("Erreur : Le fichier XML ne contient pas de balise <gameList>.")
            except etree.XMLSyntaxError as e:
                self.start_button.configure(state="disabled")
                self.log_message(f"Erreur de syntaxe XML : {e}")
        else:
            self.start_button.configure(state="disabled")
            self.log_message("Erreur : Le fichier sélectionné n'existe pas.")

    def log_message(self, message):
        """Affiche un message horodaté dans la console de l'interface."""
        self.console.configure(state='normal')
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.console.configure(state='disabled')
        self.console.yview(tk.END)

    def update_status(self, message, status_type="info"):
        """Met à jour la barre de statut avec un message et une couleur."""
        self.status_text.set(message)
        if status_type == "error":
            self.status_label.configure(text_color="#FFB0B0") 
        elif status_type == "success":
            self.status_label.configure(text_color="#B0FFB0") 
        else:
            self.status_label.configure(text_color="#FFFFFF") 

    def initialize_openai_client(self):
        """Initialise le client API et vérifie la connexion."""
        api_key = self.api_key.get()
        base_url = self.base_url.get()
        
        if not api_key:
            self.log_message("Erreur : Clé API manquante.")
            self.update_status("Erreur : Clé API manquante.", "error")
            return False
        if not base_url:
            self.log_message("Erreur : URL Serveur (Base URL) manquante.")
            self.update_status("Erreur : URL Serveur manquante.", "error")
            return False
            
        try:
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            # Test de connexion en listant les modèles
            self.openai_client.models.list() 
            self.log_message(f"Client OpenAI initialisé (Serveur: {base_url}).")
            return True
        except Exception as e:
            self.log_message(f"Erreur d'initialisation OpenAI : {e}")
            self.update_status("Erreur connexion API", "error")
            return False

    def load_instructions(self):
        """Charge le fichier d'instructions (prompt système) en mémoire."""
        inst_path = self.instructions_path.get()
        if not os.path.exists(inst_path):
            self.log_message(f"Erreur : Le fichier d'instructions '{inst_path}' n'existe pas.")
            self.update_status("Fichier instructions manquant", "error")
            return False
        
        try:
            with open(inst_path, 'r', encoding='utf-8') as f:
                self.instructions_content = f.read()
            self.log_message("Fichier d'instructions chargé.")
            return True
        except Exception as e:
            self.log_message(f"Erreur lors de la lecture du fichier d'instructions : {e}")
            self.update_status("Erreur instructions", "error")
            return False

    def start_process(self):
        """Valide les prérequis et lance le thread de traitement."""
        if self.is_running:
            return

        # Initialisations
        if not self.initialize_openai_client():
            return
        if not self.load_instructions():
            return

        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_status("Traitement en cours...", "info")
        
        # Lance le traitement lourd dans un thread séparé
        threading.Thread(target=self.process_missing_games, daemon=True).start()

    def stop_process(self):
        """Positionne le drapeau d'arrêt pour le thread de traitement."""
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.update_status("Arrêté par l'utilisateur", "error")
        self.log_message("Processus arrêté par l'utilisateur.")

    def normalize_name(self, name):
        """Nettoie un nom de jeu pour une comparaison 'floue'."""
        if name is None:
            return ""
        name = re.sub(r'[&/\\-]', ' ', name) # Remplace les séparateurs par des espaces
        return re.sub(r'\s+', ' ', name.strip()).lower() # Met en minuscule et supprime les espaces doubles

    def validate_utf8(self, text):
        """Vérifie si une chaîne est encodée en UTF-8 valide."""
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False

    def get_normalized_names(self, root):
        """Retourne un 'set' de tous les noms normalisés présents dans un XML."""
        names = {
            self.normalize_name(game.find("name").text)
            for game in root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }
        return names

    def merge_game_elements(self, base_game, enriched_game):
        """Fusionne les données d'un jeu enrichi dans un jeu de base."""
        for enriched_elem in enriched_game:
            base_elem = base_game.find(enriched_elem.tag)
            if base_elem is not None:
                # Met à jour le texte si le jeu enrichi a du contenu
                if enriched_elem.text: 
                    base_elem.text = enriched_elem.text
            else:
                # Ajoute l'élément s'il n'existe pas dans le jeu de base
                new_elem = deepcopy(enriched_elem)
                base_game.append(new_elem)

    def update_or_add_games(self, gamelist_root, updated_root, enriched_root):
        """
        Met à jour la structure XML 'updated_root' avec les jeux de 'enriched_root'.
        Utilise 'gamelist_root' comme source pour les jeux non modifiés.
        """
        # Dictionnaire des jeux déjà présents dans 'updated_gamelist.xml'
        updated_games = {
            self.normalize_name(game.find("name").text): game
            for game in updated_root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }

        # Dictionnaire des jeux sources (originaux)
        gamelist_games = {
            self.normalize_name(game.find("name").text): game
            for game in gamelist_root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }

        games_added_or_updated = 0
        for enriched_game in enriched_root.findall("game"):
            enriched_name_element = enriched_game.find("name")
            if enriched_name_element is None or not enriched_name_element.text:
                self.log_message("Avertissement : Jeu enrichi sans balise <name> ignoré.")
                continue
                
            enriched_name_normalized = self.normalize_name(enriched_name_element.text)
            
            # Cas 1: Le jeu est déjà dans updated_gamelist.xml
            existing_game = updated_games.get(enriched_name_normalized)
            if existing_game is not None:
                self.merge_game_elements(existing_game, enriched_game)
                games_added_or_updated += 1
            else:
                # Cas 2: Le jeu n'est pas dans updated_gamelist.xml, mais il est dans le gamelist.xml source
                base_game = gamelist_games.get(enriched_name_normalized)
                if base_game is not None:
                    # On crée une copie du jeu source (pour garder 'path', 'image', etc.)
                    new_game = deepcopy(base_game)
                    # On fusionne les nouvelles infos (desc, rating, etc.)
                    self.merge_game_elements(new_game, enriched_game)
                    # On s'assure que le nom est bien celui retourné par l'IA (gestion de la casse)
                    new_game.find('name').text = enriched_name_element.text
                    updated_root.append(new_game)
                    games_added_or_updated += 1
                else:
                    # Cas 3: L'IA retourne un jeu inconnu (ne devrait pas arriver)
                     self.log_message(f"Avertissement : L'IA a retourné le jeu '{enriched_name_element.text}' qui n'est pas dans la liste source.")

        return games_added_or_updated


    def process_missing_games(self):
        """
        Processus principal (exécuté dans un thread).
        Identifie les jeux manquants et les traite un par un via l'API.
        Inclut une logique de tentatives (retry) et de gestion des échecs.
        """
        
        # 1. Chargement des XML
        gamelist_root = self.load_xml(self.gamelist_path.get())
        if gamelist_root is None:
            self.log_message("Erreur : Impossible de charger le gamelist.xml source.")
            self.stop_process()
            return

        updated_gamelist_path = self.updated_gamelist_path.get()
        updated_gamelist_root = self.load_xml(updated_gamelist_path) if os.path.exists(updated_gamelist_path) else etree.Element('gameList')

        # 2. Identification des jeux manquants
        self.missing_games = []
        existing_games_names = self.get_normalized_names(updated_gamelist_root)
        for game in gamelist_root.findall('game'):
            name_elem = game.find('name')
            if name_elem is not None and name_elem.text:
                if self.normalize_name(name_elem.text) not in existing_games_names:
                    self.missing_games.append(game)

        if not self.missing_games:
            self.log_message("Aucun jeu manquant trouvé. 'updated_gamelist.xml' est déjà à jour.")
            self.update_status("Terminé (aucun jeu manquant)", "success")
            self.is_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure("disabled")
            return

        total_games = len(self.missing_games)
        self.log_message(f"{total_games} jeux manquants à traiter.")
        
        # 3. Initialisation du fichier de log des échecs
        try:
            with open(self.missing_games_path.get(), 'w', encoding='utf-8') as f:
                f.write("") # Crée ou vide le fichier
            self.log_message(f"Fichier des échecs ({self.missing_games_path.get()}) initialisé.")
        except IOError as e:
            self.log_message(f"Avertissement : Impossible d'initialiser le fichier des échecs : {e}")

        
        # 4. Boucle de traitement principale
        total_games_processed = 0
        while total_games_processed < total_games and self.is_running:
            
            game = self.missing_games[total_games_processed]
            
            name_elem = game.find('name')
            if name_elem is None or not name_elem.text:
                self.log_message(f"Jeu {total_games_processed + 1} ignoré (nom manquant).")
                total_games_processed += 1
                continue
                
            game_name = name_elem.text
            self.log_message(f"Traitement du jeu ({total_games_processed + 1}/{total_games}) : {game_name}")
            
            # 5. Boucle de tentatives (Retry)
            retries = 0
            success = False
            MAX_RETRIES = 5
            
            while retries < MAX_RETRIES and self.is_running and not success:
                
                if retries > 0:
                    self.log_message(f"Nouvelle tentative ({retries + 1}/{MAX_RETRIES}) pour : {game_name}")

                try:
                    # 6. Appel API
                    self.update_status(f"Appel API pour {game_name} (Essai {retries + 1})", "info")
                    
                    response = self.openai_client.chat.completions.create(
                        model=self.model_name.get(),
                        messages=[
                            {"role": "system", "content": self.instructions_content}, # Instructions
                            {"role": "user", "content": game_name} # Nom du jeu
                        ]
                    )
                    enriched_data = response.choices[0].message.content

                    if not self.validate_utf8(enriched_data):
                        raise ValueError("La réponse de l'IA n'est pas en UTF-8 valide.")

                    # 7. Parsing XML Robuste (gestion du "bavardage" de l'IA)
                    game_blocks = re.findall(r'(<game>.*?</game>)', enriched_data, re.DOTALL)
                    
                    if not game_blocks:
                        raise ValueError("Aucun bloc <game> valide trouvé dans la réponse de l'IA.")
                        
                    valid_xml_data = "".join(game_blocks)
                    enriched_root = etree.fromstring(f"<root>{valid_xml_data}</root>")
                    
                    # Validation du contenu retourné
                    valid_games_found = 0
                    for enriched_game in enriched_root.findall('game'):
                        if enriched_game.find('name') is not None and enriched_game.find('name').text:
                            valid_games_found += 1
                    
                    if valid_games_found == 0:
                        raise etree.XMLSyntaxError("L'IA n'a retourné aucun jeu valide (nom manquant).")

                    # 8. Fusion et Sauvegarde
                    games_processed = self.update_or_add_games(gamelist_root, updated_gamelist_root, enriched_root)
                    self.save_xml(updated_gamelist_path, updated_gamelist_root)
                    self.log_message(f"{games_processed} jeu mis à jour/ajouté pour '{game_name}'.")
                    
                    success = True # Sort de la boucle de tentatives

                # 9. Gestion des erreurs (Retry)
                except (etree.XMLSyntaxError, ValueError) as e:
                    self.log_message(f"Erreur (XML/Données) : {e}. Tentative {retries + 1}/{MAX_RETRIES}.")
                    self.update_status("Erreur XML, réessai...", "error")
                    retries += 1
                    time.sleep(10)
                except RateLimitError as e:
                    self.log_message(f"Erreur API (Quota) : {e}. Pause de 60s. Tentative {retries + 1}/{MAX_RETRIES}.")
                    self.update_status("Quota API atteint, pause...", "error")
                    retries += 1
                    time.sleep(60)
                except APIConnectionError as e:
                    self.log_message(f"Erreur API (Connexion) : {e}. Pause de 15s. Tentative {retries + 1}/{MAX_RETRIES}.")
                    self.update_status("Erreur Connexion API...", "error")
                    retries += 1
                    time.sleep(15)
                except APIStatusError as e:
                    self.log_message(f"Erreur API (Statut) : {e}. Code: {e.status_code}. Pause de 15s. Tentative {retries + 1}/{MAX_RETRIES}.")
                    self.update_status(f"Erreur API {e.status_code}...", "error")
                    retries += 1
                    time.sleep(15)
                except Exception as e:
                    self.log_message(f"Erreur API Inconnue : {e}. Pause de 15s. Tentative {retries + 1}/{MAX_RETRIES}.")
                    self.update_status("Erreur API, réessai...", "error")
                    retries += 1
                    time.sleep(15)
            
            # 10. Gestion de l'échec définitif (après 5 tentatives)
            if not success and self.is_running:
                self.log_message(f"ÉCHEC DÉFINITIF : '{game_name}' n'a pas pu être traité après {MAX_RETRIES} tentatives.")
                self.log_failed_game(game_name) # Écrit dans failed_games.txt
            
            # On passe au jeu suivant (que ce soit un succès ou un échec)
            total_games_processed += 1

            # 11. Mise à jour de la progression
            progress_percent = (total_games_processed / total_games)
            self.progress_value.set(progress_percent)
            self.progress_label.configure(text=f"{int(progress_percent * 100)}%")
            self.root.update_idletasks() # Force la MàJ de l'UI

        # 12. Fin du processus
        if self.is_running:
            self.log_message("Traitement terminé.")
            self.update_status("Terminé !", "success")
        else:
            self.log_message("Traitement interrompu.")
            self.update_status("Arrêté.", "error")

        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def load_xml(self, file_path):
        """Charge un fichier XML et retourne l'élément racine."""
        try:
            # recover=True tente de parser même si le XML est légèrement malformé
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            tree = etree.parse(file_path, parser)
            return tree.getroot()
        except etree.XMLSyntaxError as e:
            self.log_message(f"Erreur de syntaxe XML dans {file_path} : {e}")
            return None
        except IOError as e:
            self.log_message(f"Erreur I/O : Impossible de lire {file_path} : {e}")
            return None
        except Exception as e:
            self.log_message(f"Erreur inconnue lors du chargement de {file_path} : {e}")
            return None

    def save_xml(self, file_path, root):
        """Sauvegarde l'élément racine dans un fichier XML."""
        try:
            tree = etree.ElementTree(root)
            tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        except IOError as e:
            self.log_message(f"Erreur I/O : Impossible d'écrire dans {file_path} : {e}")
        except Exception as e:
            self.log_message(f"Erreur inconnue lors de la sauvegarde de {file_path} : {e}")

    def log_failed_game(self, game_name):
        """Ajoute un jeu échoué au fichier 'failed_games.txt'."""
        log_path = self.missing_games_path.get()
        try:
            # 'a' pour 'append' (ajouter à la fin)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{game_name}\n")
        except IOError as e:
            self.log_message(f"Erreur I/O : Impossible d'écrire dans {log_path} : {e}")
        except Exception as e:
            self.log_message(f"Erreur inconnue lors de l'écriture dans {log_path} : {e}")


def main():
    root = ctk.CTk()
    app = GameListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()