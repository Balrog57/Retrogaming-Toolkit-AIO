import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import requests
from lxml import etree as ET

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def dl_official(path):
    try:
        r = requests.get("https://raw.githubusercontent.com/RetroBat-Official/retrobat/main/system/templates/emulationstation/es_systems.cfg")
        r.raise_for_status()
        with open(path, 'wb') as f: f.write(r.content)
        return True
    except: return False

def parse(path):
    if not os.path.exists(path): return []
    try:
        parser = ET.XMLParser(resolve_entities=False, no_network=True)
        return [{c.tag: c.text for c in s} for s in ET.parse(path, parser=parser).findall('./system')]
    except: return []

def process(cust_path, out_dir):
    if not cust_path or not out_dir: return messagebox.showerror("Err", "Champs vides")
    
    os.makedirs(out_dir, exist_ok=True)
    off_path = os.path.join(out_dir, "es_systems.cfg")
    
    if not dl_official(off_path): return messagebox.showerror("Err", "DL Fail")
    
    off_sys = parse(off_path)
    cust_sys = parse(cust_path)
    
    unique = [s for s in cust_sys if s not in off_sys]
    
    for s in unique:
        name = s.get('name')
        if name:
            root = ET.Element("systemList")
            sys_el = ET.SubElement(root, "system")
            for k,v in s.items(): ET.SubElement(sys_el, k).text = v
            
            with open(os.path.join(out_dir, f"es_systems_{name}.cfg"), "w", encoding="utf-8") as f:
                f.write(ET.tostring(root, pretty_print=True, encoding="unicode"))
    
    messagebox.showinfo("Succès", f"{len(unique)} systèmes extraits.")

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "ES Systems Extractor")
    else: root.title("ES Systems Extractor")
    
    root.geometry("500x250")
    
    cf = ctk.StringVar()
    od = ctk.StringVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)
    
    ctk.CTkLabel(fr, text="Custom CFG:").grid(row=0, column=0)
    ctk.CTkEntry(fr, textvariable=cf, width=300).grid(row=0, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: cf.set(filedialog.askopenfilename()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)

    ctk.CTkLabel(fr, text="Out Dir:").grid(row=1, column=0)
    ctk.CTkEntry(fr, textvariable=od, width=300).grid(row=1, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: od.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=1, column=2)
    
    ctk.CTkButton(fr, text="PROCESSER", command=lambda: process(cf.get(), od.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=2, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()