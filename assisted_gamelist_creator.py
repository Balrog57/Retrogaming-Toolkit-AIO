import os
import threading
import pyperclip
from lxml import etree
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import re
from copy import deepcopy

class GameListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de liste de jeux")
        self.root.geometry("900x700")  # Taille de la fenêtre augmentée
        self.root.minsize(900, 700)   # Taille minimale ajustée
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.gamelist_path = tk.StringVar()
        self.updated_gamelist_path = tk.StringVar(value="updated_gamelist.xml")
        self.missing_games_path = tk.StringVar(value="missing_games.txt")
        self.missing_games = []
        self.progress_value = tk.DoubleVar(value=0.0)
        self.status_text = tk.StringVar(value="Ready")
        self.is_running = False
        self.is_paused = False
        self.chunk_size = tk.IntVar(value=5)  # Taille des groupes de jeux à traiter
        self.prefix_phrase = tk.StringVar(value="Répondre en Français, toujours remplacer & par &amp; :")  # Phrase mise à jour

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Thème moderne

        # File Configuration
        file_frame = ttk.LabelFrame(root, text="File Configuration", padding=10)
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(file_frame, text="Game List:").grid(row=0, column=0, padx=5, pady=5)
        self.file_entry = ttk.Entry(file_frame, textvariable=self.gamelist_path, width=70)  # Largeur augmentée
        self.file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        # Chunk Size Configuration
        chunk_frame = ttk.LabelFrame(root, text="Taille des groupes de jeux", padding=10)
        chunk_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(chunk_frame, text="Taille des groupes:").grid(row=0, column=0, padx=5, pady=5)
        self.chunk_entry = ttk.Entry(chunk_frame, textvariable=self.chunk_size, width=10)
        self.chunk_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Prefix Phrase Configuration
        prefix_frame = ttk.LabelFrame(root, text="Phrase d'introduction", padding=10)
        prefix_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(prefix_frame, text="Phrase :").grid(row=0, column=0, padx=5, pady=5)
        self.prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_phrase, width=80)  # Largeur augmentée
        self.prefix_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Console Output
        console_frame = ttk.LabelFrame(root, text="Console Output", padding=10)
        console_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.console = ScrolledText(console_frame, width=100, height=20, state='disabled', font=("Courier", 10))  # Taille augmentée
        self.console.pack(fill="both", expand=True)

        # Progress Bar
        progress_frame = ttk.LabelFrame(root, text="Progress", padding=10)
        progress_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value, mode='determinate')
        self.progress_bar.pack(fill="x", expand=True, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack()

        # Control Buttons
        control_frame = ttk.Frame(root, padding=10)
        control_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_process, state=tk.DISABLED)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_process, state=tk.DISABLED)
        self.pause_button.pack(side="left", padx=5)

        # Status Bar
        status_frame = ttk.Frame(root, padding=10)
        status_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", expand=True)

        # Configuration de la grille
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)  # La console prend plus d'espace

    def browse_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier gamelist.xml."""
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers XML", "*.xml")])
        if file_path:
            self.gamelist_path.set(file_path)
            self.validate_file()

    def validate_file(self):
        """Valide le fichier XML sélectionné."""
        file_path = self.gamelist_path.get()
        if os.path.exists(file_path):
            try:
                tree = etree.parse(file_path)
                root = tree.getroot()
                if root.tag == "gameList":
                    self.start_button.config(state=tk.NORMAL)
                    self.log_message("Fichier XML valide sélectionné.")
                else:
                    self.log_message("Erreur : Le fichier XML ne contient pas de balise <gameList>.")
            except etree.XMLSyntaxError as e:
                self.log_message(f"Erreur de syntaxe XML : {e}")
        else:
            self.log_message("Erreur : Le fichier sélectionné n'existe pas.")

    def log_message(self, message):
        """Affiche un message dans la console."""
        self.console.config(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.config(state='disabled')
        self.console.yview(tk.END)

    def update_status(self, message, status_type="info"):
        """Met à jour la barre de statut avec un message."""
        self.status_text.set(message)
        if status_type == "error":
            self.status_label.config(background="#ffcccc")
        elif status_type == "success":
            self.status_label.config(background="#ccffcc")
        else:
            self.status_label.config(background="#f0f0f0")

    def start_process(self):
        """Démarre le traitement des jeux manquants."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.update_status("Processing...", "info")
            threading.Thread(target=self.process_missing_games, daemon=True).start()

    def stop_process(self):
        """Arrête le traitement des jeux manquants."""
        self.is_running = False
        self.is_paused = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.update_status("Stopped", "error")

    def pause_process(self):
        """Met en pause ou reprend le traitement."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Resume")
            self.update_status("Paused", "info")
        else:
            self.pause_button.config(text="Pause")
            self.update_status("Processing...", "info")

    def normalize_name(self, name):
        """Normalise le nom du jeu pour la correspondance."""
        if name is None:
            return ""
        # Remplacer les caractères spéciaux par des espaces
        name = re.sub(r'[&/\\-]', ' ', name)
        # Supprimer les espaces superflus et mettre en minuscules
        return re.sub(r'\s+', ' ', name.strip()).lower()

    def validate_utf8(self, text):
        """Valide que le texte est en UTF-8."""
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False

    def get_normalized_names(self, root):
        """Extrait les noms des jeux normalisés."""
        names = {
            self.normalize_name(game.find("name").text)
            for game in root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }
        return names

    def merge_game_elements(self, base_game, enriched_game):
        """Fusionne les balises d'un jeu enrichi avec un jeu existant."""
        for enriched_elem in enriched_game:
            base_elem = base_game.find(enriched_elem.tag)
            if base_elem is not None:
                base_elem.text = enriched_elem.text
            else:
                new_elem = deepcopy(enriched_elem)
                base_game.append(new_elem)

    def update_or_add_games(self, gamelist_root, updated_root, enriched_root):
        """Met à jour ou ajoute les jeux dans la liste mise à jour."""
        updated_games = {
            self.normalize_name(game.find("name").text): game
            for game in updated_root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }

        gamelist_games = {
            self.normalize_name(game.find("name").text): game
            for game in gamelist_root.findall("game")
            if game.find("name") is not None and game.find("name").text
        }

        for enriched_game in enriched_root.findall("game"):
            enriched_name_element = enriched_game.find("name")
            if enriched_name_element is None:
                continue
            enriched_name_normalized = self.normalize_name(enriched_name_element.text)
            existing_game = updated_games.get(enriched_name_normalized)

            if existing_game is not None:
                self.merge_game_elements(existing_game, enriched_game)
            else:
                base_game = gamelist_games.get(enriched_name_normalized)
                if base_game is not None:
                    new_game = deepcopy(enriched_game)
                    for elem in base_game:
                        if new_game.find(elem.tag) is None:
                            new_game.append(deepcopy(elem))
                    updated_root.append(new_game)

    def process_missing_games(self):
        """Traite les jeux manquants de manière asynchrone."""
        gamelist_root = self.load_xml(self.gamelist_path.get())
        updated_gamelist_root = self.load_xml(self.updated_gamelist_path.get()) if os.path.exists(self.updated_gamelist_path.get()) else etree.Element('gameList')

        if gamelist_root is not None:
            self.missing_games = []
            existing_games = self.get_normalized_names(updated_gamelist_root)
            for game in gamelist_root.findall('game'):
                if self.normalize_name(game.find('name').text) not in existing_games:
                    self.missing_games.append(game)

            total_games = len(self.missing_games)
            chunk_size = self.chunk_size.get()

            i = 0
            while i < total_games:
                if not self.is_running:
                    break
                while self.is_paused:
                    if not self.is_running:
                        break
                    self.root.update()

                chunk = self.missing_games[i:i + chunk_size]
                names = [game.find('name').text for game in chunk]
                prefix_phrase = self.prefix_phrase.get()
                pyperclip.copy(f"{prefix_phrase}\n" + '\n'.join(names))
                self.log_message(f"Coller les informations pour les jeux suivants : {', '.join(names)}")

                # Attendre que l'utilisateur colle les données enrichies
                enriched_data = None
                while enriched_data is None:
                    enriched_data = pyperclip.paste()
                    if enriched_data.strip() == f"{prefix_phrase}\n" + '\n'.join(names):
                        enriched_data = None  # Ignorer la copie initiale
                    self.root.update()

                try:
                    # Vérifier la conformité UTF-8
                    if not self.validate_utf8(enriched_data):
                        raise ValueError("Les données ne sont pas au format UTF-8.")

                    # Valider le format XML collé
                    enriched_root = etree.fromstring(f"<root>{enriched_data}</root>")
                    for enriched_game in enriched_root.findall('game'):
                        if enriched_game.find('name') is None:
                            raise etree.XMLSyntaxError("Données XML invalides : balise <name> manquante.")

                    # Fusionner les données enrichies
                    self.update_or_add_games(gamelist_root, updated_gamelist_root, enriched_root)
                    self.save_xml(self.updated_gamelist_path.get(), updated_gamelist_root)
                    self.log_message(f"Jeux traités : {', '.join(names)}")
                    i += chunk_size  # Passer au groupe suivant
                except (etree.XMLSyntaxError, ValueError) as e:
                    self.log_message(f"Erreur : {e}. Veuillez coller des données valides.")
                    # Réessayer avec le même groupe de jeux

                self.progress_value.set((i) / total_games * 100)
                self.progress_label.config(text=f"{int((i) / total_games * 100)}%")
                self.root.update()

        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.update_status("Ready", "success")

    def load_xml(self, file_path):
        """Charge un fichier XML et retourne l'élément racine."""
        if os.path.exists(file_path):
            try:
                tree = etree.parse(file_path)
                return tree.getroot()
            except etree.XMLSyntaxError as e:
                self.log_message(f"Erreur de syntaxe XML : {e}")
                return None
        else:
            self.log_message(f"Le fichier {file_path} n'existe pas.")
            return None

    def save_xml(self, file_path, root):
        """Sauvegarde l'élément racine dans un fichier XML."""
        tree = etree.ElementTree(root)
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

if __name__ == "__main__":
    root = tk.Tk()
    app = GameListApp(root)
    root.mainloop()