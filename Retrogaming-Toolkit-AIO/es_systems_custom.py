import customtkinter as ctk
import tkinter.messagebox
import tkinter.filedialog
import xml.etree.ElementTree as ET
import os
import requests
import logging
from xml.dom import minidom  # Import minidom

# Configuration du logging (console only)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def download_official_es_systems_cfg(output_path):
    """Downloads the official es_systems.cfg file from RetroBat's GitHub."""
    url = "https://github.com/RetroBat-Official/retrobat-setup/blob/master/system/templates/emulationstation/es_systems.cfg?raw=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Official file downloaded and saved to: {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading official file: {e}")
        return False

def parse_systems(file_path):
    """Parses an es_systems.cfg file, returns list of system dictionaries."""
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return []
        tree = ET.parse(file_path)
        return [
            {child.tag: child.text for child in system}
            for system in tree.findall('./system')
        ]
    except ET.ParseError as e:
        print(f"Error: XML parsing error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error: General error parsing {file_path}: {e}")
        return []


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def process_files(custom_file_path, output_dir_path):
    """Main processing function."""

    if not custom_file_path or not output_dir_path:
        tkinter.messagebox.showerror("Error", "Please select a custom file and an output directory.")
        return

    os.makedirs(output_dir_path, exist_ok=True)

    official_file_path = os.path.join(output_dir_path, "es_systems.cfg")
    if not download_official_es_systems_cfg(official_file_path):
        tkinter.messagebox.showerror("Error", "Failed to download the official es_systems.cfg file.")
        return

    official_systems = parse_systems(official_file_path)
    custom_systems = parse_systems(custom_file_path)

    if official_systems is None or custom_systems is None:
        tkinter.messagebox.showerror("Error", "Failed to parse one or both es_systems.cfg files.")
        return

    unique_systems = []
    for custom_system in custom_systems:
        if custom_system not in official_systems:
            unique_systems.append(custom_system)

    print(f"Found {len(unique_systems)} unique or different systems.")

    # Create individual system files ONLY for unique systems
    for system_dict in unique_systems:
        system_name = system_dict.get('name')
        if system_name:
            output_file_path = os.path.join(output_dir_path, f"es_systems_{system_name}.cfg")
            root = ET.Element("systemList")
            system_element = ET.Element("system")
            for tag, text in system_dict.items():
                child = ET.SubElement(system_element, tag)
                child.text = text
            root.append(system_element)

            try:
                # Use prettify_xml to format the output
                pretty_xml = prettify_xml(root)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(pretty_xml)
                print(f"Created: {output_file_path}")
            except Exception as e:
                print(f"Error writing to {output_file_path}: {e}")
        else:
            print("Skipping system: No 'name' element found.")

    tkinter.messagebox.showinfo("Success", "Processing complete!")

def create_gui():
    """Creates the GUI, resembling the first script's layout."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("es_systems.cfg Processor")

    font_titre = ("Arial", 16, "bold")  # Use bold font

    # Frame for file selections
    frame_files = ctk.CTkFrame(root)
    frame_files.pack(pady=20, padx=20, fill="x")

    # Custom File Selection (row 0)
    label_custom = ctk.CTkLabel(frame_files, text="Custom es_systems.cfg:", font=font_titre)
    label_custom.grid(row=0, column=0, sticky="w", pady=5, padx=5)
    entry_custom = ctk.CTkEntry(frame_files, width=300)
    entry_custom.grid(row=0, column=1, padx=5, pady=5)
    button_custom = ctk.CTkButton(frame_files, text="Browse",
                                   command=lambda: entry_custom.insert(0, tkinter.filedialog.askopenfilename(
                                       filetypes=[("CFG Files", "*.cfg"), ("All Files", "*.*")]
                                   )), width=100)
    button_custom.grid(row=0, column=2, padx=5, pady=5)

    # Output Directory Selection (row 1)
    label_output = ctk.CTkLabel(frame_files, text="Output Directory:", font=font_titre)
    label_output.grid(row=1, column=0, sticky="w", pady=5, padx=5)
    entry_output = ctk.CTkEntry(frame_files, width=300)
    entry_output.grid(row=1, column=1, padx=5, pady=5)
    button_output = ctk.CTkButton(frame_files, text="Browse",
                                   command=lambda: entry_output.insert(0, tkinter.filedialog.askdirectory()),
                                   width=100)
    button_output.grid(row=1, column=2, padx=5, pady=5)

    # Process Button (separate pack)
    button_process = ctk.CTkButton(root, text="Process Files",
                                    command=lambda: process_files(entry_custom.get(), entry_output.get()),
                                    width=200)
    button_process.pack(pady=20)


    root.mainloop()

if __name__ == "__main__":
    create_gui()