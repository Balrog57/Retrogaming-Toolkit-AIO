import customtkinter as ctk
from tkinter import messagebox
import subprocess
import ctypes
import sys

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def check_long_paths():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem")
        val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        return val == 1
    except: return False

def enable_long_paths(lbl_status):
    reg_cmd = ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem', '/v', 'LongPathsEnabled', '/t', 'REG_DWORD', '/d', '1', '/f']
    
    if not is_admin():
        try:
            cmd_str = " ".join(reg_cmd)
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {cmd_str}", None, 1)
            if ret > 32:
                messagebox.showinfo("Info", "Demande envoyée. Vérification...")
                # We can't immediately verify because runas is async/separate process typically, but let's try
                import time; time.sleep(1) # Give it a sec
                if check_long_paths():
                   lbl_status.configure(text="STATUT ACTUEL: ACTIVÉ ✅", text_color=theme.COLOR_SUCCESS if theme else "green")
                   messagebox.showinfo("Succès", "Activé avec succès !")
                else:
                   messagebox.showwarning("Info", "Verifiez si la valeur a changé (un redémarrage peut être requis).")
            else:
                messagebox.showerror("Err", "Élévation refusée ou erreur.")
        except Exception as e:
            messagebox.showerror("Err", str(e))
    else:
        try:
            subprocess.run(reg_cmd, check=True, capture_output=True)
            if check_long_paths():
                lbl_status.configure(text="STATUT ACTUEL: ACTIVÉ ✅", text_color=theme.COLOR_SUCCESS if theme else "green")
                messagebox.showinfo("Succès", "LongPathsEnabled activé !")
            else:
                messagebox.showerror("Err", "La valeur n'a pas pu être vérifiée.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Err", f"Erreur Registre: {e}")
        except Exception as e:
            messagebox.showerror("Err", str(e))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if theme:
            theme.apply_theme(self, "Activation Long Paths")
            self.COLOR_BTN = theme.COLOR_ACCENT_PRIMARY
            self.COLOR_SUCCESS = theme.COLOR_SUCCESS
        else:
            self.title("Activation Long Paths")
            self.geometry("400x250")
            self.COLOR_BTN = "blue"
            self.COLOR_SUCCESS = "green"
            
        self.geometry("400x300")
        
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main, text="Activer le support des chemins longs\n(> 260 caractères) dans Windows.", font=("Arial", 14), wraplength=350).pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(main, text="STATUT: ...", font=("Arial", 12, "bold"))
        self.lbl_status.pack(pady=10)
        
        if check_long_paths():
             self.lbl_status.configure(text="STATUT ACTUEL: ACTIVÉ ✅", text_color=self.COLOR_SUCCESS)
        else:
             self.lbl_status.configure(text="STATUT ACTUEL: DÉSACTIVÉ ❌", text_color="red")
        
        ctk.CTkButton(main, text="ACTIVER LONG PATHS", command=lambda: enable_long_paths(self.lbl_status), height=50, fg_color=self.COLOR_BTN).pack(pady=20, fill="x")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
