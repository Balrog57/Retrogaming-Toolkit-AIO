import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import xml.etree.ElementTree as ET
import os
import logging
import sys
import cv2
import freetype
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class XML2PNGApp:
    def __init__(self, master):
        self.master = master
        master.title("Convertisseur XML2PNG")

        # --- Variables ---
        self.file_path = tk.StringVar()
        self.is_xml = tk.BooleanVar(value=True)
        self.list_type = tk.StringVar(value="Hyperlist")
        self.background_image_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.font_family = tk.StringVar(value="Times New Roman")
        self.font_size = tk.IntVar(value=20)
        self.font_color = tk.StringVar(value="#000000")
        self.text_alignment = tk.StringVar(value="center")
        self.max_chars = tk.IntVar(value=0)
        self.text_x = tk.IntVar(value=0)
        self.text_y = tk.IntVar(value=0)
        self.text_width = tk.IntVar(value=128)
        self.text_height = tk.IntVar(value=128)
        self.bold = tk.BooleanVar(value=False)
        self.italic = tk.BooleanVar(value=False)
        self.underline = tk.BooleanVar(value=False)
        self.prepend_text = tk.StringVar()
        self.append_text = tk.StringVar()
        self.prepend_newline = tk.BooleanVar(value=False)
        self.append_newline = tk.BooleanVar(value=False)
        self.append_only_if_overflow = tk.BooleanVar(value=False)
        self.remove_brackets = tk.BooleanVar(value=False)

        # --- Notebook (Onglets) ---
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill="both")

        self.main_frame = ttk.Frame(self.notebook)
        self.options_frame = ttk.Frame(self.notebook)
        self.about_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text='Principal')
        self.notebook.add(self.options_frame, text='Options')
        self.notebook.add(self.about_frame, text='À Propos')

        # --- Main Frame ---
        self.create_main_frame()

        # --- Options Frame ---
        self.create_options_frame()

        # --- About Frame ---
        self.create_about_frame()

    def create_main_frame(self):
        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill="both", expand=True)

        # --- Left Column ---
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        # Type de fichier
        ttk.Label(left_frame, text="Type de fichier :").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(left_frame, text="Fichier XML", variable=self.is_xml, value=True).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(left_frame, text="Dossier d'images", variable=self.is_xml, value=False).grid(row=0, column=2, sticky="w", padx=5, pady=2)

        # Type de liste (uniquement pour XML)
        ttk.Label(left_frame, text="Type de liste :").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        list_type_menu = ttk.Combobox(left_frame, textvariable=self.list_type, values=["Hyperlist", "Gamelist"], state="readonly")
        list_type_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=2)

        # Chemin du fichier/dossier
        ttk.Label(left_frame, text="Chemin :").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(left_frame, textvariable=self.file_path, width=50).grid(row=2, column=1, columnspan=2, padx=5, pady=2)
        ttk.Button(left_frame, text="...", command=self.browse_file_or_folder).grid(row=2, column=3, padx=5, pady=2)

        # Image de fond
        ttk.Label(left_frame, text="Image de fond :").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(left_frame, textvariable=self.background_image_path, width=50).grid(row=3, column=1, columnspan=2, padx=5, pady=2)
        ttk.Button(left_frame, text="...", command=self.browse_background).grid(row=3, column=3, padx=5, pady=2)

        # Dossier de destination
        ttk.Label(left_frame, text="Destination :").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(left_frame, textvariable=self.output_dir_path, width=50).grid(row=4, column=1, columnspan=2, padx=5, pady=2)
        ttk.Button(left_frame, text="...", command=self.browse_output).grid(row=4, column=3, padx=5, pady=2)

        # Aperçu de l'image
        self.preview_image_label = tk.Label(left_frame, bd=2, relief="solid")
        self.preview_image_label.grid(row=5, column=0, columnspan=4, pady=10)

        # Bouton Créer
        ttk.Button(left_frame, text="Créer", command=self.generate_images).grid(row=6, column=0, columnspan=4, pady=10)

        # --- Right Column ---
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")

        # Famille de polices
        ttk.Label(right_frame, text="Famille de polices :").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        import tkinter.font as tkFont
        font_options = sorted(tkFont.families())
        ttk.Combobox(right_frame, textvariable=self.font_family, values=font_options, state="readonly").grid(row=0, column=1, padx=5, pady=2)

        # Taille de la police
        ttk.Label(right_frame, text="Taille de la police :").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.font_size, width=5).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Couleur de la police
        ttk.Label(right_frame, text="Couleur de la police :").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Button(right_frame, text="Définir", command=self.choose_color).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.color_frame = tk.Frame(right_frame, bg=self.font_color.get(), width=20, height=20)
        self.color_frame.grid(row=2, column=2, padx=5, pady=2)

        # Style de la police
        ttk.Checkbutton(right_frame, text="Gras", variable=self.bold).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(right_frame, text="Italique", variable=self.italic).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(right_frame, text="Souligné", variable=self.underline).grid(row=3, column=2, sticky="w", padx=5, pady=2)

        # Alignement du texte
        ttk.Label(right_frame, text="Alignement du texte :").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        ttk.Combobox(right_frame, textvariable=self.text_alignment, values=["gauche", "centre", "droite"], state="readonly").grid(row=4, column=1, padx=5, pady=2)

        # Caractères maximum
        ttk.Label(right_frame, text="Caractères max (0:max) :").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.max_chars, width=5).grid(row=5, column=1, sticky="w", padx=5, pady=2)

        # Position du texte
        ttk.Label(right_frame, text="Position du texte (X, Y, W, H) :").grid(row=6, column=0, sticky="w", padx=5, pady=2)

        # X
        ttk.Label(right_frame, text="X:").grid(row=7, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.text_x, width=5).grid(row=7, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(right_frame, text="+", command=lambda: self.adjust_position(1, 0, 'x')).grid(row=7, column=2, padx=2)
        ttk.Button(right_frame, text="-", command=lambda: self.adjust_position(-1, 0, 'x')).grid(row=7, column=3, padx=2)

        # Y
        ttk.Label(right_frame, text="Y:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.text_y, width=5).grid(row=8, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(right_frame, text="+", command=lambda: self.adjust_position(0, 1, 'y')).grid(row=8, column=2, padx=2)
        ttk.Button(right_frame, text="-", command=lambda: self.adjust_position(0, -1, 'y')).grid(row=8, column=3, padx=2)

        # Width
        ttk.Label(right_frame, text="W:").grid(row=9, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.text_width, width=5).grid(row=9, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(right_frame, text="+", command=lambda: self.adjust_position(1, 0, 'w')).grid(row=9, column=2, padx=2)
        ttk.Button(right_frame, text="-", command=lambda: self.adjust_position(-1, 0, 'w')).grid(row=9, column=3, padx=2)

        # Height
        ttk.Label(right_frame, text="H:").grid(row=10, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(right_frame, textvariable=self.text_height, width=5).grid(row=10, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(right_frame, text="+", command=lambda: self.adjust_position(0, 1, 'h')).grid(row=10, column=2, padx=2)
        ttk.Button(right_frame, text="-", command=lambda: self.adjust_position(0, -1, 'h')).grid(row=10, column=3, padx=2)

    def create_options_frame(self):
        frame = ttk.LabelFrame(self.options_frame, text="Options")
        frame.pack(padx=10, pady=5, fill="x")

        # Options de texte supplémentaires
        ttk.Label(frame, text="Texte préfixe :").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame, textvariable=self.prepend_text, width=30).grid(row=0, column=1, padx=5, pady=2)
        ttk.Checkbutton(frame, text="Nouvelle ligne", variable=self.prepend_newline).grid(row=0, column=2, sticky="w", padx=5, pady=2)

        ttk.Label(frame, text="Texte suffixe :").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame, textvariable=self.append_text, width=30).grid(row=1, column=1, padx=5, pady=2)
        ttk.Checkbutton(frame, text="Nouvelle ligne", variable=self.append_newline).grid(row=1, column=2, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame, text="Si dépassement", variable=self.append_only_if_overflow).grid(row=1, column=3, sticky="w", padx=5, pady=2)

        # Supprimer les crochets
        ttk.Checkbutton(frame, text="Supprimer [...] et (...)", variable=self.remove_brackets).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    def create_about_frame(self):
        about_text = """XML2PNG
        © 2021 par Langlois Romain © 2025 modifié par  Balrog57
        ****************
        Pour aider le developpeur de cette application :
        https://www.paypal.com/paypalme/r0man0
        ****************
        Plus d'applications et de contenus pour votre front-end sur :
        http://r0man0.free.fr
        ****************
        Profitez-en c'est tout folks !!
        """
        tk.Label(self.about_frame, text=about_text, justify=tk.LEFT).pack(padx=10, pady=10)

    def browse_file_or_folder(self):
        if self.is_xml.get():
            file_path = filedialog.askopenfilename(filetypes=[("Fichiers XML", "*.xml")])
        else:
            file_path = filedialog.askdirectory()
        if file_path:
            self.file_path.set(file_path)
            logging.info(f"Fichier ou dossier sélectionné : {file_path}")
            self.update_preview()

    def browse_background(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers PNG", "*.png")])
        if file_path:
            self.background_image_path.set(file_path)
            logging.info(f"Image de fond sélectionnée : {file_path}")
            self.update_preview()

    def browse_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir_path.set(dir_path)
            logging.info(f"Dossier de destination sélectionné : {dir_path}")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choisir une couleur")[1]
        if color:
            self.font_color.set(color)
            self.color_frame.config(bg=color)
            logging.info(f"Couleur de police sélectionnée : {color}")
            self.update_preview()

    def adjust_position(self, dx, dy, axis):
        if axis == 'x':
            self.text_x.set(self.text_x.get() + dx)
        elif axis == 'y':
            self.text_y.set(self.text_y.get() + dy)
        elif axis == 'w':
            self.text_width.set(self.text_width.get() + dx)
        elif axis == 'h':
            self.text_height.set(self.text_height.get() + dy)
        logging.info(f"Position ajustée : X={self.text_x.get()}, Y={self.text_y.get()}, W={self.text_width.get()}, H={self.text_height.get()}")
        self.update_preview()

    def update_preview(self):
        background_path = self.background_image_path.get()
        if not background_path:
            logging.warning("Aucune image de fond sélectionnée.")
            return

        try:
            # Charger l'image de fond
            background_image = cv2.imread(background_path)
            if background_image is None:
                raise FileNotFoundError(f"Impossible de charger l'image : {background_path}")

            # Dessiner un rectangle rouge pour les limites du texte avec OpenCV
            cv2.rectangle(background_image, (self.text_x.get(), self.text_y.get()),
                          (self.text_x.get() + self.text_width.get(), self.text_y.get() + self.text_height.get()),
                          (0, 0, 255), 2)  # Rouge

            # Obtenir le texte le plus long ou le nom de l'image la plus grande pour l'aperçu
            if self.is_xml.get():
                data = self.read_xml_file(self.file_path.get())
                if data:
                    longest_text = max([item.get("description", "") if "description" in item else item.get("name", "") for item in data], key=len) if data else "Texte d'exemple"
                    text = longest_text
                else:
                    text = "Texte d'exemple"
            else:
                folder_path = self.file_path.get()
                if folder_path:
                    image_files = [f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))]
                    if image_files:
                        # Afficher le nom du premier fichier image
                        text = image_files[0]
                    else:
                        text = "Aucune image"
                else:
                    text = "Aucun dossier"

            # Dessiner le texte avec OpenCV
            font_face = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (0, 0, 0)  # Noir
            thickness = 2

            text_size = cv2.getTextSize(text, font_face, font_scale, thickness)[0]
            text_x = self.text_x.get()
            text_y = self.text_y.get() + text_size[1]

            cv2.putText(background_image, text, (text_x, text_y), font_face, font_scale, font_color, thickness, cv2.LINE_AA)

            # Convertir l'image OpenCV en format compatible Tkinter
            background_image_rgb = cv2.cvtColor(background_image, cv2.COLOR_BGR2RGB)
            img = tk.PhotoImage(data=cv2.imencode('.png', background_image_rgb)[1].tobytes())
            self.preview_image_label.config(image=img)
            self.preview_image_label.image = img

            logging.info("Aperçu de l'image mis à jour avec succès.")

        except FileNotFoundError as fnf_error:
            logging.error(fnf_error)
            messagebox.showerror("Erreur", str(fnf_error))
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de l'aperçu : {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {str(e)}")

    def generate_images(self):
        if not self.file_path.get() or not self.background_image_path.get() or not self.output_dir_path.get():
            logging.error("Veuillez sélectionner un fichier/dossier, une image de fond et un dossier de destination.")
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier/dossier, une image de fond et un dossier de destination.")
            return

        try:
            # Simuler la progression
            progress_window = tk.Toplevel(self.master)
            progress_window.title("Progression")
            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", mode="determinate")
            progress_bar.pack(padx=10, pady=10)
            progress_bar.start(10)

            # Logique pour générer les images
            try:
                if self.is_xml.get():
                    data = self.read_xml_file(self.file_path.get())
                else:
                    data = self.read_image_folder(self.file_path.get())

                if not data:
                    raise ValueError("Aucune donnée à traiter.")

                output_dir = self.output_dir_path.get()
                background_path = self.background_image_path.get()

                for i, item in enumerate(data):
                    if "name" in item and "description" in item:
                        output_name = item["name"]
                        text = item["description"]
                    elif "path" in item and "name" in item:
                        output_name = os.path.splitext(os.path.basename(item["path"]))[0]
                        text = item["name"]
                    else:
                        logging.warning(f"Données invalides : {item}")
                        continue

                    text = self.format_text(text)
                    image = self.create_image(background_path, text)
                    if image is not None:
                        output_path = os.path.join(output_dir, f"{output_name}.png")
                        cv2.imwrite(output_path, image)
                        logging.info(f"Image créée : {output_path}")
                    else:
                        logging.warning(f"Impossible de créer l'image pour : {output_name}")

                self.master.after(100, progress_bar.stop)
                self.master.after(100, progress_window.destroy)
                self.master.after(100, lambda: messagebox.showinfo("Succès", "Les images ont été générées avec succès."))

                logging.info("Génération des images terminée avec succès.")

            except Exception as e:
                logging.error(f"Erreur lors de la génération des images : {str(e)}")
                messagebox.showerror("Erreur", f"Une erreur s'est produite : {str(e)}")
        except Exception as e:
            logging.error(f"Erreur globale lors de la génération des images : {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur globale s'est produite : {str(e)}")

    def read_xml_file(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            data = []

            # Gamelist type 1
            for game in root.findall(".//game"):
                name = game.get("name")
                description = game.find("description")
                if name and description is not None and description.text:
                    data.append({"name": name, "description": description.text})

            # Gamelist type 2
            for game in root.findall(".//game"):
                path = game.find("path")
                name = game.find("name")
                if path is not None and path.text and name is not None and name.text:
                    data.append({"path": path.text, "name": name.text})

            return data
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du fichier XML : {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier XML : {str(e)}")
            return []

    def read_image_folder(self, folder_path):
        try:
            data = []
            for filename in os.listdir(folder_path):
                if filename.endswith((".png", ".jpg", ".jpeg")):
                    data.append(filename)
            return data
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du dossier d'images : {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du dossier d'images : {str(e)}")
            return None

    def create_image(self, background_path, text):
        try:
            # Charger l'image de fond avec OpenCV
            background_image = cv2.imread(background_path)
            if background_image is None:
                raise FileNotFoundError(f"Impossible de charger l'image : {background_path}")

            # Initialiser FreeType
            face = freetype.Face(self.font_family.get())
            face.set_char_size(self.font_size.get() * 64)  # Taille en 1/64 de point

            # Couleur du texte
            text_color_bgr = tuple(int(self.font_color.get().lstrip('#')[i:i+2], 16) for i in (4, 2, 0))

            # Position du texte
            x, y = self.text_x.get(), self.text_y.get()

            # Dessiner le texte avec FreeType et OpenCV
            for i, line in enumerate(text.splitlines()):
                for char in line:
                    face.load_char(char)
                    bitmap = face.glyph.bitmap
                    bitmap_buffer = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.width)

                    # Convertir le bitmap en image couleur
                    char_image = cv2.cvtColor(bitmap_buffer, cv2.COLOR_GRAY2BGR)
                    char_image[bitmap_buffer > 0] = text_color_bgr

                    # Superposer le caractère sur l'image de fond
                    background_image[y:y+bitmap.rows, x:x+bitmap.width] = char_image

                    x += bitmap.width
                y += face.height / 64  # Espacement des lignes

            return background_image
        except Exception as e:
            logging.error(f"Erreur lors de la création de l'image : {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la création de l'image : {str(e)}")
            return None

    def format_text(self, text):
        # Ajouter du texte au début si nécessaire
        if self.prepend_text.get():
            if self.prepend_newline.get():
                text = f"{self.prepend_text.get()}\n{text}"
            else:
                text = f"{self.prepend_text.get()} {text}"

        # Ajouter du texte à la fin si nécessaire
        if self.append_text.get():
            if self.append_only_if_overflow.get() and len(text) > self.max_chars.get():
                if self.append_newline.get():
                    text = f"{text}\n{self.append_text.get()}"
                else:
                    text = f"{text} {self.append_text.get()}"
            elif not self.append_only_if_overflow.get():
                if self.append_newline.get():
                    text = f"{text}\n{self.append_text.get()}"
                else:
                    text = f"{text} {self.append_text.get()}"

        # Supprimer les crochets et parenthèses si nécessaire
        if self.remove_brackets.get():
            text = text.replace("[", "").replace("]", "").replace("(", "").replace(")", "")

        # Limiter le nombre de caractères
        if len(text) > self.max_chars.get():
            text = text[:self.max_chars.get()] + "..."

        return text

if __name__ == "__main__":
    root = tk.Tk()
    app = XML2PNGApp(root)
    root.mainloop()
