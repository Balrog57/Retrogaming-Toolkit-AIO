import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MultiDiscM3UCreator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M3U Creator")
        self.geometry("800x600")

        self.tab_control = ctk.CTkTabview(self)
        self.tab_control.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab1 = self.tab_control.add("Multi-Disc M3U Creator")
        self.setup_tab1()

        self.tab2 = self.tab_control.add("Vita3k M3U Creator")
        self.setup_tab2()

    def setup_tab1(self):
        """Configure l'onglet Multi-Disc M3U Creator."""
        self.label_tab1 = ctk.CTkLabel(self.tab1, text="Select a folder containing multi-disc games:", font=("Arial", 16))
        self.label_tab1.pack(pady=20)

        self.button_select_folder_tab1 = ctk.CTkButton(
            self.tab1, text="Select Folder", command=self.select_folder_tab1, width=200, corner_radius=10
        )
        self.button_select_folder_tab1.pack(pady=10)

        self.button_create_m3u_tab1 = ctk.CTkButton(
            self.tab1, text="Create M3U", command=self.create_m3u_tab1, width=200, corner_radius=10
        )
        self.button_create_m3u_tab1.pack(pady=10)

    def setup_tab2(self):
        """Configure l'onglet Vita3k M3U Creator."""
        self.label_tab2 = ctk.CTkLabel(self.tab2, text="Select a folder to process for Vita3k:", font=("Arial", 16))
        self.label_tab2.pack(pady=20)

        self.button_select_folder_tab2 = ctk.CTkButton(
            self.tab2, text="Select Folder", command=self.select_folder_tab2, width=200, corner_radius=10
        )
        self.button_select_folder_tab2.pack(pady=10)

        self.button_create_m3u_tab2 = ctk.CTkButton(
            self.tab2, text="Create M3U", command=self.create_m3u_tab2, width=200, corner_radius=10
        )
        self.button_create_m3u_tab2.pack(pady=10)

    def select_folder_tab1(self):
        """Sélectionne un dossier pour l'onglet Multi-Disc M3U Creator."""
        self.folder_path_tab1 = filedialog.askdirectory()
        if self.folder_path_tab1:
            messagebox.showinfo("Folder Selected", f"Selected Folder: {self.folder_path_tab1}")

    def create_m3u_tab1(self):
        """Crée des fichiers M3U pour les jeux multi-disques."""
        if not hasattr(self, 'folder_path_tab1'):
            messagebox.showerror("Error", "Please select a folder first.")
            return

        games = {}
        for filename in os.listdir(self.folder_path_tab1):
            if "(Disc" in filename:
                game_name = filename.split("(Disc")[0].strip()
                if game_name not in games:
                    games[game_name] = []
                games[game_name].append(filename)

        for game_name, discs in games.items():
            m3u_filename = os.path.join(self.folder_path_tab1, f"{game_name}.m3u")
            with open(m3u_filename, "w") as m3u_file:
                for disc in sorted(discs):
                    m3u_file.write(f"{disc}\n")

        messagebox.showinfo("Success", "M3U files created successfully.")

    def select_folder_tab2(self):
        """Sélectionne un dossier pour l'onglet Vita3k M3U Creator."""
        self.folder_path_tab2 = filedialog.askdirectory()
        if self.folder_path_tab2:
            messagebox.showinfo("Folder Selected", f"Selected Folder: {self.folder_path_tab2}")

    def create_m3u_tab2(self):
        """Crée des fichiers M3U pour Vita3k."""
        if not hasattr(self, 'folder_path_tab2'):
            messagebox.showerror("Error", "Please select a folder first.")
            return

        # Chemin relatif vers le dossier contenant les fichiers CSV
        csv_folder = os.path.join(os.path.dirname(__file__), "m3u_creator")
        us_db = os.path.join(csv_folder, "Vita Game DB - US.csv")
        eu_db = os.path.join(csv_folder, "Vita Games DB - EU.csv")
        full_db = os.path.join(csv_folder, "Vita Game DB - FULL.csv")

        # Vérification de l'existence des fichiers CSV
        if not os.path.exists(us_db) or not os.path.exists(eu_db) or not os.path.exists(full_db):
            messagebox.showerror("Error", "CSV files not found in the m3u_creator folder.")
            return

        for title_id in os.listdir(self.folder_path_tab2):
            title_path = os.path.join(self.folder_path_tab2, title_id)
            if os.path.isdir(title_path):
                name_found = False
                name = "Name-Missing"

                # Recherche dans les fichiers CSV
                for csv_file in [us_db, eu_db, full_db]:
                    with open(csv_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith(title_id):
                                name = line.split(",")[1].strip()
                                name_found = True
                                break
                    if name_found:
                        break

                # Nettoyage du nom
                name = name.replace(":", "").replace("®", "").replace("™", "")

                # Création du fichier .m3u
                m3u_filename = os.path.join(self.folder_path_tab2, f"{name} [{title_id}].m3u")
                with open(m3u_filename, "w") as m3u_file:
                    m3u_file.write(title_id)

        messagebox.showinfo("Success", "M3U files created successfully.")

def main():
    app = MultiDiscM3UCreator()
    app.mainloop()

if __name__ == "__main__":
    main()