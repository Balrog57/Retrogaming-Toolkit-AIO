import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

class MultiDiscM3UCreator(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "M3U Creator")
            self.COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_BG = theme.COLOR_BG
        else:
            self.title("M3U Creator")
            self.COLOR_ACCENT = "#1f6aa5"
            self.COLOR_BG = None
            
        self.geometry("800x600")

        self.tab = ctk.CTkTabview(self, fg_color="transparent")
        self.tab.pack(expand=True, fill="both", padx=10, pady=10)

        self.t1 = self.tab.add("Multi-Disc")
        self.setup_t1()

        self.t2 = self.tab.add("Vita3k")
        self.setup_t2()

    def setup_t1(self):
        ctk.CTkLabel(self.t1, text="Create M3U for multi-disc games", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self.t1, text="Select Folder", command=self.sel_t1, width=200, fg_color=self.COLOR_ACCENT).pack(pady=10)
        ctk.CTkButton(self.t1, text="CREATE M3U", command=self.run_t1, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

    def setup_t2(self):
        ctk.CTkLabel(self.t2, text="Create M3U for Vita3k", font=theme.get_font_title(16) if theme else ("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self.t2, text="Select Folder", command=self.sel_t2, width=200, fg_color=self.COLOR_ACCENT).pack(pady=10)
        ctk.CTkButton(self.t2, text="CREATE M3U", command=self.run_t2, width=200, fg_color=theme.COLOR_SUCCESS if theme else "green").pack(pady=10)

    def sel_t1(self):
        self.fp1 = filedialog.askdirectory()
        if self.fp1: messagebox.showinfo("Info", f"Sel: {self.fp1}")

    def run_t1(self):
        if not hasattr(self, 'fp1') or not self.fp1: return messagebox.showerror("Err", "Select folder first")
        
        games = {}
        for f in os.listdir(self.fp1):
            if "(Disc" in f:
                gn = f.split("(Disc")[0].strip()
                if gn not in games: games[gn] = []
                games[gn].append(f)
        
        for gn, discs in games.items():
            with open(os.path.join(self.fp1, f"{gn}.m3u"), "w") as f:
                for d in sorted(discs): f.write(f"{d}\n")
        
        messagebox.showinfo("Success", "M3U Created")

    def sel_t2(self):
        self.fp2 = filedialog.askdirectory()
        if self.fp2: messagebox.showinfo("Info", f"Sel: {self.fp2}")

    def run_t2(self):
        if not hasattr(self, 'fp2') or not self.fp2: return messagebox.showerror("Err", "Select folder first")
        
        csv_dir = os.path.join(os.path.dirname(__file__), "m3u_creator")
        dbs = [os.path.join(csv_dir, f) for f in ["Vita Game DB - US.csv", "Vita Games DB - EU.csv", "Vita Game DB - FULL.csv"]]
        if not all(os.path.exists(f) for f in dbs): return messagebox.showerror("Err", "CSV DB missing")

        for tid in os.listdir(self.fp2):
            tp = os.path.join(self.fp2, tid)
            if os.path.isdir(tp):
                name = "Name-Missing"
                found = False
                for db in dbs:
                    try:
                        with open(db, "r", encoding="utf-8") as f:
                            for l in f:
                                if l.startswith(tid):
                                    name = l.split(",")[1].strip()
                                    found = True; break
                    except: pass
                    if found: break
                
                name = name.replace(":", "").replace("®", "").replace("™", "")
                with open(os.path.join(self.fp2, f"{name} [{tid}].m3u"), "w") as f: f.write(tid)
        
        messagebox.showinfo("Success", "Vita M3U Created")

def main():
    MultiDiscM3UCreator().mainloop()

if __name__ == "__main__":
    main()