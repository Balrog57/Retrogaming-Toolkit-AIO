import os
import sys
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

# Import theme
try:
    import theme
except ImportError:
    theme = None

class GameListApp:
    def __init__(self, root):
        self.root = root
        
        # Theme Init
        if theme:
            theme.apply_theme(root, "Gestion de liste de jeux (v3.1 - Robuste)")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_HOVER = theme.COLOR_ACCENT_HOVER
            self.COLOR_CARD = theme.COLOR_CARD_BG
            self.COLOR_SUCCESS = theme.COLOR_SUCCESS
            self.COLOR_ERROR = theme.COLOR_ERROR
        else:
            ctk.set_appearance_mode("dark")
            root.title("Gestion de liste de jeux (v3.1 - Robuste)")
            root.geometry("900x700")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_HOVER = "#144870"
            self.COLOR_CARD = None
            self.COLOR_SUCCESS = "green"
            self.COLOR_ERROR = "red"

        # Variables
        self.gamelist_path = ctk.StringVar()
        self.updated_gamelist_path = ctk.StringVar(value="updated_gamelist.xml")
        self.missing_games_path = ctk.StringVar(value="failed_games.txt")
        
        # Instructions file logic
        inst_filename = "instructions_assisted_gamelist_creator.txt"
        base_dir = os.path.dirname(__file__)
        inst_path = os.path.join(base_dir, inst_filename)
        if getattr(sys, 'frozen', False):
             exe_dir = os.path.dirname(sys.executable)
             inst_path = os.path.join(exe_dir, inst_filename)
        self.instructions_path = ctk.StringVar(value=inst_path)
        
        # API Vars
        self.api_key = ctk.StringVar(value="") 
        self.base_url = ctk.StringVar(value="https://generativelanguage.googleapis.com/v1beta/openai/") 
        self.model_name = ctk.StringVar(value="gemini-2.5-flash") 
        
        self.missing_games = []
        self.progress_value = ctk.DoubleVar(value=0.0)
        self.status_text = ctk.StringVar(value="Prêt")
        self.is_running = False
        self.openai_client = None
        self.instructions_content = ""

        # --- Frame 0: Configuration ---
        config_frame = ctk.CTkFrame(root, fg_color=self.COLOR_CARD)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        config_frame.columnconfigure(1, weight=1)

        # Title Font
        f_title = theme.get_font_title(16) if theme else ("Arial", 16)
        f_main = theme.get_font_main() if theme else ("Arial", 14)

        # Files
        ctk.CTkLabel(config_frame, text="Fichier Gamelist :", font=f_title).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_entry = ctk.CTkEntry(config_frame, textvariable=self.gamelist_path, width=400, font=f_main)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Parcourir...", command=self.browse_file, width=150, fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_HOVER).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(config_frame, text="Instructions IA :", font=f_title).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.instructions_entry = ctk.CTkEntry(config_frame, textvariable=self.instructions_path, width=400, font=f_main)
        self.instructions_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Parcourir...", command=self.browse_instructions_file, width=150, fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_HOVER).grid(row=1, column=2, padx=5, pady=5)

        # API
        url_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        url_frame.grid(row=2, column=0, padx=0, pady=5, sticky="w")
        ctk.CTkLabel(url_frame, text="URL API (OpenAI) :", font=f_title).pack(side="left", padx=(5, 2))
        
        ctk.CTkButton(url_frame, text="?", font=("Arial", 16, "bold"), width=30, height=30,
                      command=self.open_api_key_url, fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_HOVER).pack(side="left", padx=(2, 5))
                      
        self.base_url_entry = ctk.CTkEntry(config_frame, textvariable=self.base_url, width=400, font=f_main)
        self.base_url_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(config_frame, text="Modèle API :", font=f_title).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.model_name_entry = ctk.CTkEntry(config_frame, textvariable=self.model_name, width=400, font=f_main)
        self.model_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(config_frame, text="Clé API :", font=f_title).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.api_key_entry = ctk.CTkEntry(config_frame, textvariable=self.api_key, show="*", width=400, placeholder_text="Entrez votre clé API...", font=f_main)
        self.api_key_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # --- Frame 1: Console ---
        console_frame = ctk.CTkFrame(root, fg_color="transparent")
        console_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(console_frame, text="Journal des opérations :", font=f_title).grid(row=0, column=0, sticky="w")
        self.console = ctk.CTkTextbox(console_frame, width=880, height=200, state='disabled', font=("Consolas", 12), wrap="word")
        self.console.grid(row=1, column=0, sticky="nsew")

        # --- Frame 2: Progress ---
        progress_frame = ctk.CTkFrame(root, fg_color="transparent")
        progress_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        progress_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(progress_frame, text="Progression :", font=f_title).grid(row=0, column=0, sticky="w")
        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.progress_value, mode='determinate', fg_color=self.COLOR_HOVER, progress_color=self.COLOR_ACCENT)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=5)
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%", font=f_main)
        self.progress_label.grid(row=1, column=1, padx=5)

        # --- Frame 3: Controls ---
        ctrl_frame = ctk.CTkFrame(root, fg_color="transparent", height=50)
        ctrl_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.start_button = ctk.CTkButton(ctrl_frame, text="Démarrer", command=self.start_process, state="disabled", width=200, 
                                        fg_color=self.COLOR_SUCCESS, hover_color="#27ae60", font=(f_title[0], 14, "bold"))
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(ctrl_frame, text="Arrêter", command=self.stop_process, state="disabled", width=200, 
                                       fg_color=self.COLOR_ERROR, hover_color="#c0392b", font=(f_title[0], 14, "bold"))
        self.stop_button.pack(side="left", padx=5)

        # --- Frame 4: Status ---
        status_frame = ctk.CTkFrame(root, fg_color="transparent")
        status_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_text, anchor="w", font=f_main)
        self.status_label.pack(fill="x", expand=True)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

    # --- Methods (Logic preserved) ---

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("XML", "*.xml")])
        if f:
            self.gamelist_path.set(f)
            self.validate_file()

    def browse_instructions_file(self):
        f = filedialog.askopenfilename(filetypes=[("Txt", "*.txt")])
        if f:
            self.instructions_path.set(f)
            self.log_message(f"Instructions: {f}")

    @staticmethod
    def get_safe_parser():
        return etree.XMLParser(recover=True, encoding='utf-8', resolve_entities=False, no_network=True)

    def open_api_key_url(self):
        webbrowser.open_new_tab("https://aistudio.google.com/app/apikey")

    def validate_file(self):
        fp = self.gamelist_path.get()
        if os.path.exists(fp):
            try:
                base = os.path.dirname(fp)
                self.updated_gamelist_path.set(os.path.join(base, "updated_gamelist.xml"))
                self.missing_games_path.set(os.path.join(base, "failed_games.txt"))
                
                tree = etree.parse(fp, self.get_safe_parser())
                if tree.getroot().tag == "gameList":
                    self.start_button.configure(state="normal")
                    self.log_message(f"Fichier valide : {fp}")
                else:
                    self.start_button.configure(state="disabled")
                    self.log_message("XML Invalide (pas gameList)")
            except Exception as e:
                self.start_button.configure(state="disabled")
                self.log_message(f"Erreur XML: {e}")
        else:
            self.log_message("Fichier introuvable")

    def log_message(self, msg):
        self.console.configure(state='normal')
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.console.configure(state='disabled')
        self.console.yview(tk.END)

    def update_status(self, msg, type="info"):
        self.status_text.set(msg)
        c = theme.COLOR_TEXT_MAIN if theme else "white"
        if type == "error": c = theme.COLOR_ERROR if theme else "#FFB0B0"
        elif type == "success": c = theme.COLOR_SUCCESS if theme else "#B0FFB0"
        self.status_label.configure(text_color=c)

    def initialize_openai_client(self):
        k = self.api_key.get()
        u = self.base_url.get()
        if not k: return self.update_status("Erreur Clé API", "error")
        if not u: return self.update_status("Erreur URL", "error")
        try:
            self.openai_client = OpenAI(api_key=k, base_url=u)
            self.openai_client.models.list()
            self.log_message("Client OpenAI OK")
            return True
        except Exception as e:
            self.log_message(f"Erreur Init API: {e}")
            return False

    def load_instructions(self):
        p = self.instructions_path.get()
        if not os.path.exists(p): return False
        try:
            with open(p, 'r', encoding='utf-8') as f: self.instructions_content = f.read()
            return True
        except: return False

    def start_process(self):
        if self.is_running: return
        if not self.initialize_openai_client() or not self.load_instructions(): return
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self.process_missing_games, daemon=True).start()

    def stop_process(self):
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log_message("Arrêt demandé")

    def normalize_name(self, name):
        if not name: return ""
        name = re.sub(r'[&/\\-]', ' ', name)
        return re.sub(r'\s+', ' ', name.strip()).lower()

    def validate_utf8(self, tx):
        try: tx.encode('utf-8').decode('utf-8'); return True
        except: return False

    def get_normalized_names(self, root):
        return {self.normalize_name(g.find("name").text) for g in root.findall("game") if g.find("name") is not None and g.find("name").text}

    def merge_game_elements(self, base, enriched):
        for e in enriched:
            b = base.find(e.tag)
            if b is not None:
                if e.text: b.text = e.text
            else:
                base.append(deepcopy(e))

    def update_or_add_games(self, gl_root, upd_root, enr_root):
        upd_games = {self.normalize_name(g.find("name").text): g for g in upd_root.findall("game") if g.find("name") is not None and g.find("name").text}
        gl_games = {self.normalize_name(g.find("name").text): g for g in gl_root.findall("game") if g.find("name") is not None and g.find("name").text}
        
        count = 0
        for eg in enr_root.findall("game"):
            nm = eg.find("name")
            if nm is None or not nm.text: continue
            norm = self.normalize_name(nm.text)
            
            if norm in upd_games:
                self.merge_game_elements(upd_games[norm], eg)
                count += 1
            elif norm in gl_games:
                ng = deepcopy(gl_games[norm])
                self.merge_game_elements(ng, eg)
                ng.find('name').text = nm.text
                upd_root.append(ng)
                count += 1
        return count

    def process_missing_games(self):
        gl_root = self.load_xml(self.gamelist_path.get())
        if not gl_root: return self.stop_process()
        
        upd_path = self.updated_gamelist_path.get()
        upd_root = self.load_xml(upd_path) if os.path.exists(upd_path) else etree.Element('gameList')
        
        self.missing_games = []
        exist_names = self.get_normalized_names(upd_root)
        for g in gl_root.findall('game'):
            n = g.find('name')
            if n is not None and n.text and self.normalize_name(n.text) not in exist_names:
                self.missing_games.append(g)
                
        if not self.missing_games:
            self.stop_process()
            return self.update_status("Aucun jeu manquant.", "success")
            
        total = len(self.missing_games)
        try:
             with open(self.missing_games_path.get(), 'w', encoding='utf-8') as f: f.write("")
        except: pass

        processed = 0
        while processed < total and self.is_running:
            game = self.missing_games[processed]
            gn = game.find('name').text
            
            retries = 0; success = False; MAX=5
            while retries < MAX and self.is_running and not success:
               try:
                   self.update_status(f"Appel API {gn} ({retries+1})")
                   resp = self.openai_client.chat.completions.create(model=self.model_name.get(), messages=[
                       {"role": "system", "content": self.instructions_content},
                       {"role": "user", "content": gn}
                   ])
                   enr_data = resp.choices[0].message.content
                   if not self.validate_utf8(enr_data): raise ValueError("UTF8 Invalid")
                   
                   blocks = re.findall(r'(<game>.*?</game>)', enr_data, re.DOTALL)
                   if not blocks: raise ValueError("No valid game block")
                   
                   enr_root = etree.fromstring(f"<root>{''.join(blocks)}</root>", parser=self.get_safe_parser())
                   self.update_or_add_games(gl_root, upd_root, enr_root)
                   self.save_xml(upd_path, upd_root)
                   self.log_message(f"Succès: {gn}")
                   success = True
               except Exception as e:
                   self.log_message(f"Err {gn}: {e}")
                   retries+=1; time.sleep(2)
            
            if not success: self.log_failed_game(gn)
            processed += 1
            p = processed/total
            self.progress_value.set(p)
            self.progress_label.configure(text=f"{int(p*100)}%")
        
        self.stop_process()
        self.update_status("Fini", "success")

    def load_xml(self, p):
        try: return etree.parse(p, self.get_safe_parser()).getroot()
        except Exception as e: self.log_message(f"Err Load XML: {e}"); return None

    def save_xml(self, p, r):
        try: etree.ElementTree(r).write(p, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        except Exception as e: self.log_message(f"Err Save XML: {e}")

    def log_failed_game(self, gn):
        try: 
            with open(self.missing_games_path.get(), 'a', encoding='utf-8') as f: f.write(f"{gn}\n")
        except: pass

def main():
    root = ctk.CTk()
    app = GameListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()