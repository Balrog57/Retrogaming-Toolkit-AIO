import os
import glob
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

class GameDeletionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Suppression de Jeux (CORE-TYPE R)")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_BG = theme.COLOR_BG
        else:
            self.title("Suppression de Jeux")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_BG = None
            
        self.geometry("800x600")

        self.base_dir = ""
        self.selected_main = ""
        self.selected_system = ""
        
        # UI
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(top, text="Dossier Base:", font=("Arial", 14)).grid(row=0, column=0, padx=5)
        ctk.CTkButton(top, text="Parcourir", command=self.sel_base, width=100, fg_color=self.COLOR_ACCENT).grid(row=0, column=1)

        ctk.CTkLabel(top, text="Main Menu:", font=("Arial", 14)).grid(row=1, column=0, padx=5, pady=5)
        self.combo_main = ctk.CTkOptionMenu(top, values=[], width=200, fg_color=self.COLOR_ACCENT)
        self.combo_main.grid(row=1, column=1)
        ctk.CTkButton(top, text="→", width=40, command=self.confirm_main, fg_color=self.COLOR_ACCENT).grid(row=1, column=2, padx=5)

        ctk.CTkLabel(top, text="System:", font=("Arial", 14)).grid(row=2, column=0, padx=5, pady=5)
        self.combo_system = ctk.CTkOptionMenu(top, values=[], width=200, state="disabled", fg_color=self.COLOR_ACCENT)
        self.combo_system.grid(row=2, column=1)
        self.btn_sys = ctk.CTkButton(top, text="→", width=40, command=self.confirm_system, state="disabled", fg_color=self.COLOR_ACCENT)
        self.btn_sys.grid(row=2, column=2, padx=5)

        # Games List
        ctk.CTkLabel(self, text="Jeux à supprimer:", font=("Arial", 14)).pack(pady=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=700, height=350)
        self.scroll_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        self.checks = []

        self.btn_del = ctk.CTkButton(self, text="SUPPRIMER SÉLECTION", command=self.delete_games, state="disabled", fg_color=theme.COLOR_ERROR if theme else "red")
        self.btn_del.pack(pady=20)

    def sel_base(self):
        self.base_dir = filedialog.askdirectory()
        if self.base_dir:
            p = os.path.join(self.base_dir, "collections", "Main", "menu")
            if os.path.exists(p):
                self.combo_main.configure(values=[f[:-4] for f in os.listdir(p) if f.endswith(".txt")])
                self.combo_main.set("")
            else: messagebox.showerror("Err", "Structure invalide (Main/menu missing)")

    def confirm_main(self):
        self.selected_main = self.combo_main.get()
        if not self.selected_main: return
        p = os.path.join(self.base_dir, "collections", self.selected_main, "menu")
        if os.path.exists(p):
            self.combo_system.configure(values=[f[:-4] for f in os.listdir(p) if f.endswith(".txt")], state="normal")
            self.combo_system.set("")
            self.btn_sys.configure(state="normal")

    def confirm_system(self):
        self.selected_system = self.combo_system.get()
        if not self.selected_system: return
        self.load_games()
        self.btn_del.configure(state="normal")

    def load_games(self):
        for c in self.checks: c.destroy()
        self.checks = []
        p = os.path.join(self.base_dir, "collections", self.selected_system, "roms")
        if os.path.exists(p):
            games = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
            for g in games:
                cb = ctk.CTkCheckBox(self.scroll_frame, text=g)
                cb.pack(anchor="w", pady=2)
                self.checks.append(cb)

    def delete_games(self):
        sel = [c.cget("text") for c in self.checks if c.get() == 1]
        if not sel: return
        if not messagebox.askyesno("Confirm", f"Supprimer {len(sel)} jeux ?"): return
        
        rp = os.path.join(self.base_dir, "collections", self.selected_system, "roms")
        mp = os.path.join(self.base_dir, "collections", self.selected_system, "medium_artwork")
        
        for g in sel:
            # Rom
            try: os.remove(os.path.join(rp, g))
            except: pass
            # Media
            bn = os.path.splitext(g)[0]
            for mf in glob.glob(os.path.join(mp, "**", f"{bn}.*"), recursive=True):
                try: os.remove(mf)
                except: pass
        
        messagebox.showinfo("Fini", "Suppression terminée.")
        self.load_games()

def main():
    app = GameDeletionApp()
    app.mainloop()

if __name__ == "__main__":
    main()