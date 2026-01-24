import customtkinter as ctk
import tkinter as tk # Needed for Toplevel (Ghost) and misc
from tkinter import filedialog, messagebox
import os
import re
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageTk

# Import shared theme
try:
    import theme
except ImportError:
    # Fallback if running standalone and theme not found (shouldn't happen in proper env)
    theme = None

class DraggableListFrame(ctk.CTkScrollableFrame):
    """
    A CustomTkinter ScrollableFrame that mimics a Listbox with Drag & Drop.
    Items are represented by CTkButtons (for hover/click style).
    """
    def __init__(self, master, connected_frames=None, highlight_color=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.connected_frames = connected_frames if connected_frames else []
        self.highlight_color = highlight_color
        
        # Determine colors from theme or defaults
        self.default_bg = self.cget("fg_color") # save original fg_color
        if theme:
             self.bg_color_normal = theme.COLOR_CARD_BG
             self.item_fg_color = "transparent"
             self.item_hover_color = theme.COLOR_ACCENT_HOVER
             self.item_text_color = theme.COLOR_TEXT_MAIN
        else:
             self.bg_color_normal = "#2b2b2b"
             self.item_fg_color = "transparent"
             self.item_hover_color = "#1f538d"
             self.item_text_color = "white"
             
        self.configure(fg_color=self.bg_color_normal)

        self.items = [] # List of strings
        self.item_widgets = [] # List of CTkButtons
        
        self.drag_data = {"item_index": None, "original_frame": None, "text": None}
        self.ghost_window = None
        self.current_hover_frame = None

    def connect(self, frame):
        if frame not in self.connected_frames:
            self.connected_frames.append(frame)
        if self not in frame.connected_frames:
            frame.connected_frames.append(self)

    def set_items(self, new_items):
        self.items = new_items
        self._render_items()

    def get_items(self):
        return self.items

    def add_item(self, text):
        self.items.append(text)
        self._render_items()
        
    def clear(self):
        self.items = []
        self._render_items()

    def _render_items(self):
        # Clear existing widgets
        for w in self.item_widgets:
            w.destroy()
        self.item_widgets = []
        
        for idx, text in enumerate(self.items):
            # Use Button for easy hover/click visual, but styled like a label item
            btn = ctk.CTkButton(
                self, 
                text=text, 
                fg_color=self.item_fg_color, 
                text_color=self.item_text_color,
                hover_color=self.item_hover_color,
                anchor="w",
                height=24,
                font=theme.get_font_main() if theme else ("Roboto", 13)
            )
            btn.pack(fill="x", pady=1, padx=2)
            
            # Bind events
            btn.bind("<Button-1>", lambda e, i=idx: self._on_drag_start(e, i))
            btn.bind("<B1-Motion>", self._on_drag_motion)
            btn.bind("<ButtonRelease-1>", self._on_drag_stop)
            
            self.item_widgets.append(btn)

    def _on_drag_start(self, event, index):
        self.drag_data["item_index"] = index
        self.drag_data["original_frame"] = self
        self.drag_data["text"] = self.items[index]
        self.configure(cursor="hand2")

    def _create_ghost(self, text, x, y):
        if self.ghost_window: return
        
        self.ghost_window = tk.Toplevel(self)
        self.ghost_window.overrideredirect(True)
        self.ghost_window.attributes('-alpha', 0.8)
        self.ghost_window.attributes('-topmost', True)
        
        # Simple label inside
        lbl = tk.Label(self.ghost_window, text=text, bg=theme.COLOR_ACCENT_PRIMARY if theme else "#333", fg="white")
        lbl.pack()
        
        self.ghost_window.geometry(f"+{x+15}+{y+15}")

    def _on_drag_motion(self, event):
        if self.drag_data["item_index"] is None: return

        x_root, y_root = event.x_root, event.y_root
        
        # Create/Update Ghost
        if not self.ghost_window:
            self._create_ghost(self.drag_data["text"], x_root, y_root)
        else:
             self.ghost_window.geometry(f"+{x_root+15}+{y_root+15}")

        # Check for target
        target = self._find_frame_under_mouse(x_root, y_root)
        
        if target != self.current_hover_frame:
            # Clear invalid hover
            if self.current_hover_frame:
                self.current_hover_frame.configure(fg_color=self.bg_color_normal)
            
            # Set new hover
            if target and target.highlight_color:
                target.configure(fg_color=target.highlight_color)
            elif target: # Self or no highlight color
                 pass 
            
            self.current_hover_frame = target

    def _on_drag_stop(self, event):
        self.configure(cursor="")
        if self.ghost_window:
            self.ghost_window.destroy()
            self.ghost_window = None

        if self.current_hover_frame:
            self.current_hover_frame.configure(fg_color=self.bg_color_normal)

        target = self.current_hover_frame
        src_idx = self.drag_data["item_index"]
        
        if src_idx is not None and target:
            text = self.drag_data["text"]
            
            # Logic: Remove from self, Add to target
            # If target is self, reorder
            
            # 1. Remove from source
            del self.items[src_idx]
            self._render_items()
            
            # 2. Insert into target
            # Ideal: find index based on Y. 
            # Simplified: Add to end for now, or approximate.
            # Unlike Listbox, ScrollableFrame doesn't inherently give index by Y easily without calculation.
            # We can rely on target.item_widgets bbox.
            
            insert_idx = len(target.items) # Default: append
            
            # Try to find insertion point
            # Map event root y to target-relative y? No event.y_root is simple.
            # Iterate widgets in target
            mouse_y = event.y_root
            for i, w in enumerate(target.item_widgets):
                if mouse_y < w.winfo_rooty() + w.winfo_height()/2:
                    insert_idx = i
                    break
            
            target.items.insert(insert_idx, text)
            target._render_items()
            
        # Reset
        self.drag_data = {"item_index": None, "original_frame": None, "text": None}
        self.current_hover_frame = None

    def _find_frame_under_mouse(self, x, y):
        # Check connected frames + self
        candidates = [self] + self.connected_frames
        for f in candidates:
            # Check coords
            fx = f.winfo_rootx()
            fy = f.winfo_rooty()
            fw = f.winfo_width()
            fh = f.winfo_height()
            
            if fx <= x <= fx + fw and fy <= y <= fy + fh:
                return f
        return None


class UniversalRomCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Theme Setup ---
        if theme:
            theme.apply_theme(self, "Universal ROM Cleaner (Fork Python)")
        else:
            ctk.set_appearance_mode("dark")
            self.title("Universal ROM Cleaner (Fork Python)")
            
        self.geometry("1100x700")

        # Icons
        self._load_icons()

        self.rom_directory = ""
        self.all_files = [] 
        self.all_attributes = set()

        self._setup_ui()

    def _load_icons(self):
        # Use theme-like logic or existing logic
        try:
             if getattr(sys, 'frozen', False):
                 base_path = os.path.join(sys._MEIPASS, "assets")
             else:
                 # Should be able to find assets in parent/assets if running via module
                 # or ../assets if relative
                 base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
                 
             self.icon_1g1r = self._load_image(os.path.join(base_path, "icon_1g1r.png"))
             self.icon_folder = self._load_image(os.path.join(base_path, "icon_folder.png"))
        except Exception:
            self.icon_1g1r = None
            self.icon_folder = None

    def _load_image(self, path):
        if os.path.exists(path):
            return ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(32, 32))
        return None

    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        # 1. Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        self.path_entry = ctk.CTkEntry(header_frame, placeholder_text="Sélectionner le dossier de ROMs...", height=35)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Styled Button
        load_btn = ctk.CTkButton(
            header_frame, 
            text="Parcourir", 
            command=self.load_directory, 
            width=120, height=35,
            fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None,
            hover_color=theme.COLOR_ACCENT_HOVER if theme else None
        )
        load_btn.pack(side="left")

        # 2. Main Content
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        main_content.grid_columnconfigure(0, weight=1, uniform="group1") 
        main_content.grid_columnconfigure(1, weight=1, uniform="group1")
        main_content.grid_rowconfigure(0, weight=1)

        # --- Left Column: Priority ---
        left_frame = ctk.CTkFrame(main_content, fg_color=theme.COLOR_CARD_BG if theme else None, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="Ordre de Priorité", font=theme.get_font_title(16) if theme else ("Roboto", 16, "bold"), anchor="w", text_color=theme.COLOR_ACCENT_PRIMARY if theme else "white").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        self.priority_list = DraggableListFrame(left_frame, width=300) # Width is ignored by sticky nsew usually but good init
        self.priority_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # --- Right Column: Splits ---
        right_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1) # Suppress
        right_frame.grid_rowconfigure(1, weight=1) # Ignore

        # Suppress
        suppress_container = ctk.CTkFrame(right_frame, fg_color=theme.COLOR_CARD_BG if theme else None, corner_radius=10)
        suppress_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        suppress_container.grid_rowconfigure(1, weight=1)
        suppress_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(suppress_container, text="Attributs à supprimer", font=theme.get_font_title(16) if theme else None, anchor="w", text_color=theme.COLOR_ACCENT_PRIMARY if theme else "white").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Red highlight for suppress
        self.suppress_list = DraggableListFrame(suppress_container, highlight_color="#550000")
        self.suppress_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Ignore
        ignore_container = ctk.CTkFrame(right_frame, fg_color=theme.COLOR_CARD_BG if theme else None, corner_radius=10)
        ignore_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        ignore_container.grid_rowconfigure(1, weight=1)
        ignore_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ignore_container, text="Attributs ignorés", font=theme.get_font_title(16) if theme else None, anchor="w", text_color=theme.COLOR_ACCENT_PRIMARY if theme else "white").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Blue highlight for ignore
        self.ignore_list = DraggableListFrame(ignore_container, highlight_color="#0e365c") 
        self.ignore_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Connect Drag & Drop
        self.priority_list.connect(self.suppress_list)
        self.priority_list.connect(self.ignore_list)
        self.suppress_list.connect(self.priority_list)
        self.ignore_list.connect(self.priority_list)

        # 3. Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        # Mode Selector
        self.mode_var = ctk.StringVar(value="Mode 1G1R")
        self.mode_btn = ctk.CTkButton(
            footer_frame, 
            text="Mode 1G1R",  # Default Text
            image=self.icon_1g1r, 
            width=140, 
            height=40,
            command=self.toggle_mode,
            fg_color="transparent",
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER if theme else "gray",
            hover_color=theme.COLOR_GHOST_HOVER if theme else "#333"
        )
        self.mode_btn.pack(side="left", padx=(0, 20))
        
        # Switches
        self.move_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(footer_frame, text="Déplacer les fichiers", variable=self.move_var, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(side="left", padx=(0, 20))
        
        self.region_sort_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(footer_frame, text="Trier par Région", variable=self.region_sort_var, progress_color=theme.COLOR_ACCENT_PRIMARY if theme else None).pack(side="left", padx=(0, 20))

        # Actions
        ctk.CTkButton(footer_frame, text="Nettoyer / Exécuter", fg_color=theme.COLOR_SUCCESS if theme else "green", 
                      hover_color="#27ae60", height=40,
                      command=lambda: self.process_roms(simulate=False)).pack(side="right", padx=10)
                      
        ctk.CTkButton(footer_frame, text="Simulation", fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue",
                      hover_color=theme.COLOR_ACCENT_HOVER if theme else "darkblue", height=40,
                      command=lambda: self.process_roms(simulate=True)).pack(side="right", padx=10)
        
        ctk.CTkButton(footer_frame, text="Reset", fg_color=theme.COLOR_ERROR if theme else "red", 
                      hover_color="#c0392b", width=80, height=40,
                      command=self.scan_files).pack(side="right", padx=10)

    def toggle_mode(self):
        current = self.mode_var.get()
        if current == "Mode 1G1R":
            self.mode_var.set("Mode Dossier")
            self.mode_btn.configure(image=self.icon_folder, text="Mode Dossier")
        else:
            self.mode_var.set("Mode 1G1R")
            self.mode_btn.configure(image=self.icon_1g1r, text="Mode 1G1R")

    def load_directory(self):
        path = filedialog.askdirectory(title="Sélectionner le dossier de ROMs")
        if path:
            self.rom_directory = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.scan_files()

    def scan_files(self):
        if not self.rom_directory: return
        
        self.priority_list.clear() # method of DraggableListFrame
        self.suppress_list.clear()
        self.ignore_list.clear()
        
        try:
            files = [f for f in os.listdir(self.rom_directory) if os.path.isfile(os.path.join(self.rom_directory, f))]
            self.all_files = files
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'accéder au dossier : {e}")
            return
            
        # Analysis
        tag_stats = {}
        self.all_attributes.clear()
        
        for f in files:
            matches = re.finditer(r'[\(\[\{](.*?)[\)\]\}]', f)
            for i, m in enumerate(matches):
                tag = m.group(1).strip()
                if not tag: continue
                self.all_attributes.add(tag)
                
                if tag not in tag_stats: tag_stats[tag] = {'total_pos': 0, 'count': 0}
                tag_stats[tag]['total_pos'] += i
                tag_stats[tag]['count'] += 1
        
        all_tags = list(self.all_attributes)
        all_tags.sort(key=str.lower, reverse=True)
        all_tags.sort(key=lambda t: tag_stats[t]['total_pos'] / tag_stats[t]['count'])
        
        self.priority_list.set_items(all_tags)

    def get_game_name(self, filename):
        match = re.match(r'^(.*?)[\(\[\{]', filename)
        if match: return match.group(1).strip()
        return os.path.splitext(filename)[0].strip()

    def get_region_from_filename(self, filename):
        match = re.search(r'[\(\[\{](.*?)[\)\]\}]', filename)
        if match: return match.group(1).strip()
        return "Autre"

    def process_roms(self, simulate=True):
        if not self.rom_directory:
            messagebox.showwarning("Attention", "Aucune ROM chargée.")
            return

        priority_attrs = self.priority_list.get_items()
        suppress_attrs = self.suppress_list.get_items()
        ignore_attrs = self.ignore_list.get_items()
        
        current_mode = self.mode_var.get()
        game_groups = {}
        
        # Grouping Logic
        for f in self.all_files:
            if "1G1R" in current_mode:
                is_ignored = False
                for ig in ignore_attrs:
                    if f"({ig})" in f or f"[{ig}]" in f:
                        is_ignored = True; break
                if is_ignored: continue
                game_name = self.get_game_name(f)
            else:
                game_name = f
            
            if game_name not in game_groups: game_groups[game_name] = []
            game_groups[game_name].append(f)
            
        kept_files_count = 0
        actions_log = []
        output_dir = os.path.join(self.rom_directory, "CLEAN_ROM")
        
        for game, files in game_groups.items():
            if not files: continue
            
            # Filter suppress
            candidates = []
            for f in files:
                is_suppressed = False
                for sup in suppress_attrs:
                    if f"({sup})" in f or f"[{sup}]" in f:
                        is_suppressed = True; break
                if not is_suppressed: candidates.append(f)
            
            if not candidates:
                actions_log.append(f"[KO][SUPPRIME] {game}")
                continue
                
            # Selection
            winner = None
            if len(candidates) == 1: winner = candidates[0]
            elif not priority_attrs: winner = candidates[0]
            else:
                best_score = 9999
                for f in candidates:
                    current_score = 9999
                    for idx, attr in enumerate(priority_attrs):
                        if f"({attr})" in f or f"[{attr}]" in f:
                             current_score = idx; break
                    
                    if winner is None or current_score < best_score:
                        winner = f; best_score = current_score

            if winner:
                kept_files_count += 1
                dest_subfolder = ""
                if self.region_sort_var.get():
                     dest_subfolder = self.get_region_from_filename(winner)
                
                full_dest_dir = os.path.join(output_dir, dest_subfolder)
                actions_log.append(f"[OK] {winner} ({dest_subfolder})")
                
                if not simulate:
                    try:
                        if not os.path.exists(full_dest_dir): os.makedirs(full_dest_dir)
                        src = os.path.join(self.rom_directory, winner)
                        dst = os.path.join(full_dest_dir, winner)
                        if self.move_var.get(): shutil.move(src, dst)
                        else: shutil.copy2(src, dst)
                    except Exception as e:
                        actions_log.append(f"   [ERREUR] {e}")

        if simulate:
            self.show_log(actions_log)
        else:
            messagebox.showinfo("Terminé", f"Nettoyage terminé. Fichiers conservés : {kept_files_count}")

    def show_log(self, logs):
        log_win = ctk.CTkToplevel(self)
        log_win.title("Rapport de Simulation")
        log_win.geometry("800x600")
        if theme: theme.apply_theme(log_win, "Rapport de Simulation")
        
        log_win.grab_set()
        
        txt = ctk.CTkTextbox(log_win, font=("Consolas", 12))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("0.0", "\n".join(logs))

def main():
    app = UniversalRomCleanerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
