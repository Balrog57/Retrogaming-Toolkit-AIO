from lxml import etree as ET
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def convert(src, out_dir):
    try:
        parser = ET.XMLParser(resolve_entities=False, no_network=True)
        tree = ET.parse(src, parser=parser)
        root = tree.getroot()
        
        menu = ET.Element('menu')
        hyper_name = os.path.splitext(os.path.basename(src))[0]
        desc_dir = os.path.join(out_dir, hyper_name)
        os.makedirs(desc_dir, exist_ok=True)
        
        for g in root.findall('game'):
            def t(tag):
                n = g.find(tag)
                return n.text if n is not None else ""
            
            nm = t('name')
            ge = ET.SubElement(menu, 'game', name=nm)
            ET.SubElement(ge, 'manufacturer').text = t('developer')
            ET.SubElement(ge, 'year').text = (t('releasedate')[:4] if len(t('releasedate'))>=4 else "")
            ET.SubElement(ge, 'description').text = nm
            
            dtxt = t('desc')
            if dtxt:
                with open(os.path.join(desc_dir, f"{nm}.txt"), "w", encoding="utf-8") as f: f.write(dtxt)

        out_xml = os.path.join(out_dir, f"{hyper_name}_hyperlist.xml")
        ET.ElementTree(menu).write(out_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)
        messagebox.showinfo("Succès", f"Créé: {out_xml}")
        
    except Exception as e: messagebox.showerror("Err", str(e))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        if theme: theme.apply_theme(self, "Gamelist -> HyperList")
        else: self.title("Gamelist -> HyperList")
        
        self.geometry("500x250")
        
        self.src = ctk.StringVar()
        self.out = ctk.StringVar()
        
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(padx=20, pady=20)
        
        ctk.CTkLabel(main, text="Gamelist XML:").grid(row=0, column=0, sticky="e")
        ctk.CTkEntry(main, textvariable=self.src, width=300).grid(row=0, column=1)
        ctk.CTkButton(main, text="...", width=40, command=lambda: self.src.set(filedialog.askopenfilename()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)

        ctk.CTkLabel(main, text="Output Dir:").grid(row=1, column=0, sticky="e")
        ctk.CTkEntry(main, textvariable=self.out, width=300).grid(row=1, column=1)
        ctk.CTkButton(main, text="...", width=40, command=lambda: self.out.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=1, column=2)

        ctk.CTkButton(main, text="CONVERTIR", command=lambda: convert(self.src.get(), self.out.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=2, column=1, pady=20)

def main():
    App().mainloop()

if __name__ == '__main__':
    main()