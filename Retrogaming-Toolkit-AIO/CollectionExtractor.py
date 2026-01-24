# Module généré automatiquement à partir de collection_extractor.py

def main():
    import os
    import shutil
    import customtkinter as ctk
    from tkinter import filedialog, messagebox, ttk
    
    # Theme Import
    try: import theme
    except: theme=None

    class ScrollableCTkComboBox(ctk.CTkFrame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, fg_color="transparent")
            self.combobox = ctk.CTkComboBox(self, **kwargs)
            self.combobox.pack(fill="both", expand=True)
            self.combobox.bind("<MouseWheel>", self._on_mousewheel)
            
        def configure(self, **kwargs):
            if 'values' in kwargs: self.combobox.configure(values=kwargs['values'])
            else: super().configure(**kwargs)
                
        def cget(self, key):
            if key == 'values': return self.combobox.cget('values')
            return super().cget(key)
            
        def _on_mousewheel(self, event):
            vals = self.cget("values")
            if not vals: return
            delta = -1 if event.delta > 0 else 1
            idx = max(0, min(len(vals)-1, self.combobox.current() + delta)) # Access internal index properly or use current() wrapper
            # current() is mostly Tkinter. CTkComboBox has specific methods.
            # Usually .set(vals[idx])
            try:
                self.combobox.set(vals[idx])
                self.combobox.event_generate("<<ComboboxSelected>>")
            except: pass
            return "break"

    if theme:
        # We handle global theme in main app init usually, but okay here
        pass
    else:
        ctk.set_appearance_mode("dark")
        
    COLOR_ACCENT = theme.COLOR_ACCENT_PRIMARY if theme else "#1f6aa5"

    # --- Logic (Condensed) ---
    def list_parent_menus(base_path):
        p = os.path.join(base_path, "collections/Main/menu")
        if not os.path.exists(p): return []
        return [os.path.splitext(f)[0] for f in os.listdir(p) if f.endswith(".txt")]
    
    def list_collections(base_path, parent):
        p = os.path.join(base_path, f"collections/{parent}/menu")
        if not os.path.exists(p): return []
        return [os.path.splitext(f)[0] for f in os.listdir(p) if f.endswith(".txt")]
    
    def parse_settings_file(base_path, collection_name):
        sp = os.path.join(base_path, f"collections/{collection_name}/settings.conf")
        if not os.path.exists(sp): return None
        with open(sp, 'r') as f:
            for l in f:
                if l.strip().startswith('launcher'): return l.split('=')[1].strip()

    def parse_launcher_file(base_path, launcher_name):
        lcp = os.path.join(base_path, f"launchers.windows/{launcher_name}.conf")
        if not os.path.exists(lcp): return None
        with open(lcp, 'r') as f:
            for l in f:
                if l.strip().startswith('executable'): return l.split('=')[1].strip()

    def create_and_move_files(base_path, collection, parent, collection_type, emulator_type, launcher=None):
        fp = f"CTP - {collection}"
        os.makedirs(fp, exist_ok=True)
        errs = []
        try:
            # Helper for move
            def move_if(src, dst_dir):
                if os.path.exists(src):
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.move(src, dst_dir)
                else: errs.append(f"Missing: {src}")

            move_if(os.path.join(base_path, f"collections/{parent}/menu/{collection}.txt"), os.path.join(fp, f"collections/{parent}/menu/"))

            if collection_type == "Système":
                if emulator_type == "RetroArch":
                    cn = launcher.split('[lr-')[1].split(']')[0]
                    move_if(os.path.join(base_path, f"./emulators/retroarch/cores/{cn}_libretro.dll"), os.path.join(fp, f"emulators/retroarch/cores/"))
                    move_if(os.path.join(base_path, f"launchers.windows/{collection} [lr-{cn}].conf"), os.path.join(fp, f"launchers.windows/"))
                elif emulator_type == "Autre":
                    exc = parse_launcher_file(base_path, collection)
                    if exc:
                         edn = exc.split('\\')[1]
                         move_if(os.path.join(base_path, f"./emulators/{edn}"), os.path.join(fp, f"emulators/{edn}"))
                         move_if(os.path.join(base_path, f"launchers.windows/{collection}.conf"), os.path.join(fp, f"launchers.windows/"))

                move_if(os.path.join(base_path, f"collections/{collection}"), os.path.join(fp, f"collections/"))
                move_if(os.path.join(base_path, f"layouts/TITAN/collections/{collection}"), os.path.join(fp, f"layouts/TITAN/collections/"))
                move_if(os.path.join(base_path, f"meta/hyperlist/{collection}.xml"), os.path.join(fp, f"meta/hyperlist/"))
                move_if(os.path.join(base_path, f"Readme/{collection}.txt"), os.path.join(fp, f"Readme/"))

            elif collection_type == "Collections":
                move_if(os.path.join(base_path, f"collections/{collection}"), os.path.join(fp, f"collections/{collection}"))
                move_if(os.path.join(base_path, f"collections/COLLECTIONS/medium_artwork/logo/{collection}.png"), os.path.join(fp, f"collections/COLLECTIONS/medium_artwork/logo/"))
                move_if(os.path.join(base_path, f"layouts/TITAN/collections/{collection}"), os.path.join(fp, f"layouts/TITAN/collections/"))

            with open(os.path.join(fp, f"{collection}-rapport.txt"), "w") as rf:
                rf.write(f"Report {collection}:\n" + ("\n".join(errs) if errs else "OK"))

            messagebox.showinfo("Succès", "Extraction terminée.")
        except Exception as e: messagebox.showerror("Err", str(e))

    def run_script():
        bp = base_path_var.get()
        if not bp: return messagebox.showerror("Err", "Base path empty")
        create_and_move_files(bp, collection_var.get(), parent_var.get(), collection_type_var.get(), emulator_type_var.get(), parse_settings_file(bp, collection_var.get()))

    # GUI
    root = ctk.CTk()
    if theme: theme.apply_theme(root, "CTP - Collection Extractor")
    else: root.title("CTP - Collection Extractor")
    
    base_path_var = ctk.StringVar()
    parent_var = ctk.StringVar()
    collection_var = ctk.StringVar()
    collection_type_var = ctk.StringVar(value="Système")
    emulator_type_var = ctk.StringVar(value="RetroArch")

    main = ctk.CTkFrame(root, fg_color="transparent")
    main.pack(padx=20, pady=20)

    # Input
    # Input
    ctk.CTkLabel(main, text="Dossier de Base :").grid(row=0, column=0)
    ctk.CTkEntry(main, textvariable=base_path_var, width=300).grid(row=0, column=1)
    ctk.CTkButton(main, text="...", width=50, command=lambda: (base_path_var.set(filedialog.askdirectory()), update_parent_menus()), fg_color=COLOR_ACCENT).grid(row=0, column=2, padx=5)

    def update_parent_menus():
        p = list_parent_menus(base_path_var.get())
        pmd.combobox.configure(values=p)
        if p: parent_var.set(p[0]); update_collections()

    def update_collections():
        c = list_collections(base_path_var.get(), parent_var.get())
        cd.combobox.configure(values=c)
        if c: collection_var.set(c[0])

    ctk.CTkLabel(main, text="Parent :").grid(row=1, column=0)
    pmd = ScrollableCTkComboBox(main, variable=parent_var, command=lambda _: update_collections(), width=300)
    pmd.grid(row=1, column=1)

    ctk.CTkLabel(main, text="Collection :").grid(row=2, column=0)
    cd = ScrollableCTkComboBox(main, variable=collection_var, width=300)
    cd.grid(row=2, column=1)

    ctk.CTkLabel(main, text="Type :").grid(row=3, column=0)
    tr = ctk.CTkFrame(main, fg_color="transparent")
    tr.grid(row=3, column=1, sticky="w")
    ctk.CTkRadioButton(tr, text="Système", variable=collection_type_var, value="Système", fg_color=COLOR_ACCENT).pack(side="left")
    ctk.CTkRadioButton(tr, text="Collection", variable=collection_type_var, value="Collections", fg_color=COLOR_ACCENT).pack(side="left")

    ctk.CTkLabel(main, text="Émulateur :").grid(row=4, column=0)
    er = ctk.CTkFrame(main, fg_color="transparent")
    er.grid(row=4, column=1, sticky="w")
    ctk.CTkRadioButton(er, text="RetroArch", variable=emulator_type_var, value="RetroArch", fg_color=COLOR_ACCENT).pack(side="left")
    ctk.CTkRadioButton(er, text="Autre", variable=emulator_type_var, value="Autre", fg_color=COLOR_ACCENT).pack(side="left")

    ctk.CTkButton(main, text="EXÉCUTER", command=run_script, width=200, fg_color=COLOR_ACCENT).grid(row=5, column=1, pady=20)

    root.mainloop()

if __name__ == '__main__':
    main()
