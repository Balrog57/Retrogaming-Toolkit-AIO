import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import shutil
from pathlib import Path

# Set appearance to match "Balrog Toolkit"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DragDropListbox(tk.Listbox):
    """
    A Tkinter Listbox with Drag & Drop reordering, cross-list transfer, 'Ghost' visual feedback,
    and hover highlighting.
    """
    def __init__(self, master, connected_listboxes=None, highlight_color=None, **kwargs):
        # Default Dark Theme styling for the Listbox
        kwargs.setdefault('bg', '#2b2b2b')
        kwargs.setdefault('fg', '#ffffff')
        kwargs.setdefault('selectbackground', '#1f538d') # CTk Blue-ish
        kwargs.setdefault('selectforeground', '#ffffff')
        kwargs.setdefault('highlightthickness', 0)
        kwargs.setdefault('borderwidth', 0)
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('font', ("Roboto", 11))
        kwargs.setdefault('activestyle', 'none')
        
        super().__init__(master, **kwargs)
        
        self.connected_listboxes = connected_listboxes if connected_listboxes else []
        self.highlight_color = highlight_color
        self.default_bg = kwargs['bg']
        
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_drop)
        
        self.cur_index = None
        self.ghost_window = None
        self.current_hover_widget = None

    def connect(self, listbox):
        if listbox not in self.connected_listboxes:
            self.connected_listboxes.append(listbox)
        if self not in listbox.connected_listboxes:
            listbox.connected_listboxes.append(self)

    def on_click(self, event):
        try:
            self.cur_index = self.nearest(event.y)
            bbox = self.bbox(self.cur_index)
            if not bbox: 
                self.cur_index = None
                return
            if event.y > bbox[1] + bbox[3]: 
                self.cur_index = None
                return
        except Exception:
            self.cur_index = None

    def create_ghost(self, text, x, y):
        if self.ghost_window:
            return
        self.ghost_window = tk.Toplevel(self)
        self.ghost_window.overrideredirect(True)
        self.ghost_window.attributes('-alpha', 0.6) # Semi-transparent
        self.ghost_window.attributes('-topmost', True)
        
        width = len(text) * 8 + 20
        self.ghost_window.geometry(f"{width}x25+{x+15}+{y+15}")
        
        label = tk.Label(self.ghost_window, text=text, bg='#1f538d', fg='white', font=("Roboto", 11), relief='solid', borderwidth=1)
        label.pack(fill='both', expand=True)

    def update_ghost(self, x, y):
        if self.ghost_window:
            self.ghost_window.geometry(f"+{x+15}+{y+15}")

    def destroy_ghost(self):
        if self.ghost_window:
            self.ghost_window.destroy()
            self.ghost_window = None

    def set_bg(self, color):
        self.configure(bg=color)

    def on_drag(self, event):
        if self.cur_index is None:
            return
        
        self.config(cursor="hand2")
        
        text = self.get(self.cur_index)
        self.create_ghost(text, event.x_root, event.y_root)
        self.update_ghost(event.x_root, event.y_root)

        # Helper to find target listbox
        x, y = event.x_root, event.y_root
        target = None
        
        # Check connected listboxes (and self)
        potential_targets = self.connected_listboxes + [self]
        for lb in potential_targets:
            # Simple bbox check on screen?
            # winfo_containing is easiest but can be tricky with overlays
            widget_under = lb.winfo_containing(x, y)
            if widget_under == lb:
                target = lb
                break
        
        # Handle Highlight state
        if target != self.current_hover_widget:
            # Unhighlight previous
            if self.current_hover_widget and isinstance(self.current_hover_widget, DragDropListbox):
                self.current_hover_widget.set_bg(self.current_hover_widget.default_bg)
            
            # Highlight new
            if target and isinstance(target, DragDropListbox) and target.highlight_color:
                target.set_bg(target.highlight_color)
            
            self.current_hover_widget = target


    def on_drop(self, event):
        self.config(cursor="arrow")
        self.destroy_ghost()
        
        # Reset highlight
        if self.current_hover_widget and isinstance(self.current_hover_widget, DragDropListbox):
            self.current_hover_widget.set_bg(self.current_hover_widget.default_bg)
        self.current_hover_widget = None

        if self.cur_index is None:
            return

        x, y = event.x_root, event.y_root
        
        # Check if dropped on self
        target_self = self.winfo_containing(x, y)
        if target_self == self:
            new_index = self.nearest(event.y)
            if new_index != self.cur_index:
                text = self.get(self.cur_index)
                self.delete(self.cur_index)
                self.insert(new_index, text)
                self.see(new_index)
                self.selection_clear(0, tk.END)
                self.selection_set(new_index)
            self.cur_index = None
            return

        # Check connect listboxes
        for lb in self.connected_listboxes:
            target = lb.winfo_containing(x, y)
            if target == lb:
                text = self.get(self.cur_index)
                self.delete(self.cur_index)
                
                local_y = y - lb.winfo_rooty()
                drop_index = lb.nearest(local_y)
                
                # Intelligent Insert
                if lb.size() == 0:
                    lb.insert(tk.END, text)
                else:
                     bbox = lb.bbox(drop_index)
                     if bbox:
                         if local_y > bbox[1] + bbox[3]/2:
                             drop_index += 1
                     lb.insert(drop_index, text)
                     lb.see(drop_index)
                
                self.cur_index = None
                return

        self.cur_index = None


class UniversalRomCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Universal ROM Cleaner (Fork Python)")
        self.geometry("1100x700")
        
        # Data
        self.rom_directory = ""
        self.all_files = [] 
        self.all_attributes = set()

        self._setup_ui()

    def _setup_ui(self):
        # Configure layout
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        # 1. Header (Folder Selection)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.path_entry = ctk.CTkEntry(header_frame, placeholder_text="Sélectionner le dossier de ROMs...", height=30)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        load_btn = ctk.CTkButton(header_frame, text="Parcourir", command=self.load_directory, width=100, height=30)
        load_btn.pack(side="left")

        # 2. Main Content
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        main_content.grid_columnconfigure(0, weight=1, uniform="group1") # Left Col
        main_content.grid_columnconfigure(1, weight=1, uniform="group1") # Right Col
        main_content.grid_rowconfigure(0, weight=1)

        # --- Left Column: Priority ---
        left_frame = ctk.CTkFrame(main_content)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="Ordre de Priorité (Glisser pour ordonner)", font=("Roboto", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.priority_list = DragDropListbox(left_frame)
        self.priority_list.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # --- Right Column: Splits (Suppress / Ignore) ---
        right_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1) # Suppress
        right_frame.grid_rowconfigure(1, weight=1) # Ignore

        # Top Right: Suppress (RED HIGHLIGHT)
        suppress_container = ctk.CTkFrame(right_frame)
        suppress_container.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        suppress_container.grid_rowconfigure(1, weight=1)
        suppress_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(suppress_container, text="Attributs à supprimer", font=("Roboto", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        # highlight_color="#550000" (Red background when hovering)
        self.suppress_list = DragDropListbox(suppress_container, highlight_color="#550000")
        self.suppress_list.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Bottom Right: Ignore (BLUE HIGHLIGHT)
        ignore_container = ctk.CTkFrame(right_frame)
        ignore_container.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        ignore_container.grid_rowconfigure(1, weight=1)
        ignore_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ignore_container, text="Attributs ignorés (Non utilisés pour le tri)", font=("Roboto", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        # highlight_color="#002244" (Blue background when hovering)
        self.ignore_list = DragDropListbox(ignore_container, highlight_color="#002244")
        self.ignore_list.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Connect Drag & Drop
        self.priority_list.connect(self.suppress_list)
        self.priority_list.connect(self.ignore_list)
        self.suppress_list.connect(self.priority_list)
        self.ignore_list.connect(self.priority_list)

        # 3. Footer (Options & Actions)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Options
        self.move_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(footer_frame, text="Déplacer les fichiers (au lieu de copier)", variable=self.move_var).pack(side="left", padx=(10, 20))
        
        self.region_sort_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(footer_frame, text="Trier par Région (Dossiers)", variable=self.region_sort_var).pack(side="left", padx=20)
        
        # Actions
        ctk.CTkButton(footer_frame, text="Nettoyer / Exécuter", fg_color="green", hover_color="darkgreen", 
                      command=lambda: self.process_roms(simulate=False)).pack(side="right", padx=10)
        ctk.CTkButton(footer_frame, text="Simulation", command=lambda: self.process_roms(simulate=True)).pack(side="right", padx=10)
        # Reset button visible (Red/Orange)
        ctk.CTkButton(footer_frame, text="Reset", fg_color="#d63031", hover_color="#b71c1c",
                      command=self.scan_files, width=80).pack(side="right", padx=10)

    def load_directory(self):
        path = filedialog.askdirectory(title="Sélectionner le dossier de ROMs")
        if path:
            self.rom_directory = path
            self.path_entry.configure(placeholder_text=path)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.scan_files()

    def scan_files(self):
        if not self.rom_directory:
            return
            
        self.priority_list.delete(0, tk.END)
        self.suppress_list.delete(0, tk.END)
        self.ignore_list.delete(0, tk.END)
        
        try:
            files = [f for f in os.listdir(self.rom_directory) if os.path.isfile(os.path.join(self.rom_directory, f))]
            self.all_files = files
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'accéder au dossier : {e}")
            return
        
        # Tag Analysis
        tag_stats = {} # tag -> {'total_pos': 0, 'count': 0}
        
        self.all_attributes.clear()
        
        for f in files:
            # Find all (...) or [...] groups
            matches = re.finditer(r'[\(\[\{](.*?)[\)\]\}]', f)
            for i, m in enumerate(matches):
                tag = m.group(1).strip()
                if not tag: continue
                
                self.all_attributes.add(tag)
                
                if tag not in tag_stats:
                    tag_stats[tag] = {'total_pos': 0, 'count': 0}
                
                tag_stats[tag]['total_pos'] += i
                tag_stats[tag]['count'] += 1
        
        # Sorter Logic:
        # 1. Primary: Position Average (Ascending) -> Tags that usually appear first are at top
        # 2. Secondary: Alphabetical (Descending Z-A) -> As requested
        
        def get_sort_key(tag):
            stats = tag_stats.get(tag, {'total_pos': 0, 'count': 1})
            avg_pos = stats['total_pos'] / stats['count']
            return (avg_pos, tag) # Tuple comparison

        # To get Z-A for the second part, we sort normally then can't easily reverse just secondary.
        # Python sort is stable. 
        # Strategy: Sort by Name DESC first, then by Position ASC.
        
        all_tags = list(self.all_attributes)
        
        # 1. Sort by Name Z-A
        all_tags.sort(key=str.lower, reverse=True)
        
        # 2. Sort by Avg Position (Stable sort maintains Z-A for ties/close groups)
        all_tags.sort(key=lambda t: tag_stats[t]['total_pos'] / tag_stats[t]['count'])

        for attr in all_tags:
            self.priority_list.insert(tk.END, attr)

    def get_list_content(self, listbox):
        return list(listbox.get(0, tk.END))

    def get_game_name(self, filename):
        match = re.match(r'^(.*?)[\(\[\{]', filename)
        if match:
            return match.group(1).strip()
        return os.path.splitext(filename)[0].strip()

    def get_region_from_filename(self, filename):
        # User requested: Take the FIRST tag as the Region folder
        match = re.search(r'[\(\[\{](.*?)[\)\]\}]', filename)
        if match:
            return match.group(1).strip()
        return "Autre"

    def process_roms(self, simulate=True):
        if not self.rom_directory or not self.all_files:
            messagebox.showwarning("Attention", "Aucune ROM chargée.")
            return

        priority_attrs = self.get_list_content(self.priority_list)
        suppress_attrs = self.get_list_content(self.suppress_list)
        ignore_attrs = self.get_list_content(self.ignore_list)

        game_groups = {}
        
        # Classification
        for f in self.all_files:
            # Check ignore
            is_ignored = False
            for ig in ignore_attrs:
                if f"({ig})" in f or f"[{ig}]" in f:
                    is_ignored = True
                    break
            if is_ignored: continue

            game_name = self.get_game_name(f)
            if game_name not in game_groups:
                game_groups[game_name] = []
            game_groups[game_name].append(f)

        kept_files_count = 0
        actions_log = []
        output_dir = os.path.join(self.rom_directory, "CLEAN_ROM")
        
        for game, files in game_groups.items():
            if not files: continue

            # Filter suppressed
            candidates = []
            for f in files:
                is_suppressed = False
                for sup in suppress_attrs:
                    if f"({sup})" in f or f"[{sup}]" in f:
                        is_suppressed = True
                        break
                if not is_suppressed:
                    candidates.append(f)

            if not candidates:
                actions_log.append(f"[KO][SUPPRIME] {game}")
                continue

            # Determine winner
            winner = None
            if not priority_attrs:
                winner = candidates[0]
            else:
                best_score = 9999
                for f in candidates:
                    current_score = 9999
                    for idx, attr in enumerate(priority_attrs):
                         if f"({attr})" in f or f"[{attr}]" in f:
                            current_score = idx
                            break
                    
                    if winner is None or current_score < best_score:
                        winner = f
                        best_score = current_score
            
            if winner:
                kept_files_count += 1
                dest_subfolder = ""
                if self.region_sort_var.get():
                    dest_subfolder = self.get_region_from_filename(winner)
                
                full_dest_dir = os.path.join(output_dir, dest_subfolder)
                actions_log.append(f"[OK] {game} -> {winner} ({dest_subfolder})")
                
                if not simulate:
                    try:
                        if not os.path.exists(full_dest_dir):
                            os.makedirs(full_dest_dir)
                        src = os.path.join(self.rom_directory, winner)
                        dst = os.path.join(full_dest_dir, winner)
                        if self.move_var.get():
                            shutil.move(src, dst)
                        else:
                            shutil.copy2(src, dst)
                    except Exception as e:
                        actions_log.append(f"   [ERREUR] {e}")

        # Report logic
        if simulate:
            self.show_log(actions_log)
        else:
            messagebox.showinfo("Terminé", f"Nettoyage terminé pour {len(game_groups)} jeux.\nFichiers conservés : {kept_files_count}")

    def show_log(self, logs):
        log_win = ctk.CTkToplevel(self)
        log_win.title("Rapport de Simulation")
        log_win.geometry("800x600")
        log_win.attributes('-topmost', True)
        log_win.grab_set() # Make modal
        log_win.focus_force()
        
        txt = ctk.CTkTextbox(log_win)
        txt.pack(fill="both", expand=True)
        txt.insert("0.0", "\n".join(logs))

def main():
    app = UniversalRomCleanerApp()
    app.minsize(1100, 700) # Ensure content fits without squeezing
    app.mainloop()

if __name__ == "__main__":
    main()
