from lxml import etree as ET
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def convert(src, ext, out_dir):
    try:
        # 🛡️ Sentinel: Secure XML parsing to prevent XXE
        parser = ET.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = ET.parse(src, parser)
        root = tree.getroot()
        
        gr = ET.Element('gameList')
        
        for g in root.findall('game'):
            nm = g.get('name')
            if not nm: continue
            
            ng = ET.SubElement(gr, 'game')
            ET.SubElement(ng, 'path').text = f"./{nm}{ext}"
            ET.SubElement(ng, 'name').text = nm
            
            s = g.find('story'); d = s.text if s is not None else ""
            ET.SubElement(ng, 'desc').text = d
            
            m = g.find('manufacturer'); dev = m.text if m is not None else ""
            ET.SubElement(ng, 'developer').text = dev
            
            y = g.find('year'); yr = y.text if y is not None else ""
            ET.SubElement(ng, 'releasedate').text = (yr+"0101" if yr and len(yr)==4 else "")

        out_xml = os.path.join(out_dir, f"gamelist_{os.path.basename(src)}")
        ET.ElementTree(gr).write(out_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)
        messagebox.showinfo("Succès", f"Créé: {out_xml}")
        
    except Exception as e: messagebox.showerror("Err", str(e))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        if theme: theme.apply_theme(self, "HyperList -> Gamelist")
        else: self.title("HyperList -> Gamelist"); self.geometry("500x250")
        
        self.src = ctk.StringVar()
        self.ext = ctk.StringVar(value=".zip")
        self.out = ctk.StringVar()
        
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(padx=20, pady=20)
        
        ctk.CTkLabel(main, text="HyperList XML:").grid(row=0, column=0, sticky="e")
        ctk.CTkEntry(main, textvariable=self.src, width=300).grid(row=0, column=1)
        ctk.CTkButton(main, text="...", width=40, command=lambda: self.src.set(filedialog.askopenfilename()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)

        ctk.CTkLabel(main, text="Extension ROM:").grid(row=1, column=0, sticky="e")
        ctk.CTkEntry(main, textvariable=self.ext, width=300).grid(row=1, column=1)

        ctk.CTkLabel(main, text="Output Dir:").grid(row=2, column=0, sticky="e")
        ctk.CTkEntry(main, textvariable=self.out, width=300).grid(row=2, column=1)
        ctk.CTkButton(main, text="...", width=40, command=lambda: self.out.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=2, column=2)

        ctk.CTkButton(main, text="CONVERTIR", command=lambda: convert(self.src.get(), self.ext.get(), self.out.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=3, column=1, pady=20)

def main():
    App().mainloop()

if __name__ == '__main__':
    main()