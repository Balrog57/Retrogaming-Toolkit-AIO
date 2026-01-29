import os
from lxml import etree as ET
import customtkinter as ctk
from tkinter import messagebox, filedialog
import time

try: import theme
except: theme=None

ctk.set_appearance_mode("dark")

def read_safe(fp):
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(fp, "r", encoding=enc) as f: return f.read().strip()
        except: pass
    return None

def merge(xml_path, story_dir):
    try:
        # 🛡️ Sentinel: Secure XML parsing to prevent XXE
        parser = ET.XMLParser(recover=True, resolve_entities=False, no_network=True)
        tree = ET.parse(xml_path, parser)
        root = tree.getroot()
        
        stories = {os.path.splitext(f)[0]: os.path.join(story_dir, f) for f in os.listdir(story_dir) if f.endswith(".txt")}
        count = 0
        
        for g in root.findall(".//game"):
            gn = g.get("name")
            if gn in stories:
                content = read_safe(stories[gn])
                if content:
                    se = g.find("story")
                    if se is None: se = ET.SubElement(g, "story")
                    se.text = content
                    count += 1
        
        out = os.path.join(os.path.dirname(xml_path), f"Updated_{os.path.basename(xml_path)}")
        tree.write(out, encoding="utf-8", xml_declaration=True, pretty_print=True)
        messagebox.showinfo("Succès", f"{count} mis à jour.\nSauvé: {out}")
        
    except Exception as e: messagebox.showerror("Err", str(e))

def main():
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "Story Integrator")
    else: root.title("Story Integrator")
    
    root.geometry("500x250")
    
    xf = ctk.StringVar()
    sf = ctk.StringVar()
    
    fr = ctk.CTkFrame(root, fg_color="transparent")
    fr.pack(padx=20, pady=20)
    
    ctk.CTkLabel(fr, text="XML:").grid(row=0, column=0)
    ctk.CTkEntry(fr, textvariable=xf, width=300).grid(row=0, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: xf.set(filedialog.askopenfilename()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=0, column=2)

    ctk.CTkLabel(fr, text="Story Dir:").grid(row=1, column=0)
    ctk.CTkEntry(fr, textvariable=sf, width=300).grid(row=1, column=1)
    ctk.CTkButton(fr, text="...", width=40, command=lambda: sf.set(filedialog.askdirectory()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else None).grid(row=1, column=2)
    
    ctk.CTkButton(fr, text="FUSIONNER", command=lambda: merge(xf.get(), sf.get()), fg_color=theme.COLOR_ACCENT_PRIMARY if theme else "blue").grid(row=2, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()