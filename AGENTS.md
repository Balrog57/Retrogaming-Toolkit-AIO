# AGENTS.md - Retrogaming Toolkit AIO Development Guide

This document provides essential information for agentic coding agents working on the Retrogaming Toolkit AIO codebase.

## Project Overview

Retrogaming Toolkit is the central software that brings together all utility functions for managing retrogaming pack creation projects in one place. It is a modular Python desktop application built with CustomTkinter that provides over 25 tools for retro gaming enthusiasts. The application manages ROMs, media files, metadata, and system maintenance tasks for retro gaming frontends like RetroBat, EmulationStation, and HyperSpin.

## Build & Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download required VLC binaries (must be done before building)
python download_vlc.py
```

### Building the Application
```bash
# Build executable using PyInstaller
python build.py

# The build script:
# - Creates a one-directory bundle (--onedir)
# - Bundles all modules from Retrogaming-Toolkit-AIO/
# - Includes assets/ and VLC binaries
# - Generates hidden imports automatically
```

### Testing & Running
```bash
# Run main application during development
python main.py

# Run individual modules directly (for testing)
python Retrogaming-Toolkit-AIO/CHDManager.py
python Retrogaming-Toolkit-AIO/ImageConvert.py

# No formal test suite exists - testing is done manually by running modules
```

### Deployment & Release
```bash
# Create installer (requires Inno Setup on Windows)
iscc setup.iss

# GitHub Actions automatically builds and creates releases on:
# - Push to main branch
# - Version tags (v*)
# - Manual workflow_dispatch
```

## Code Style Guidelines

### Import Organization
- **Standard library imports first**: `os`, `sys`, `subprocess`, `threading`, `multiprocessing`
- **Third-party imports second**: `customtkinter`, `requests`, `PIL`, `lxml`, `yt-dlp`
- **Local imports last**: `utils`, `theme`, other modules from Retrogaming-Toolkit-AIO/
- **Error handling pattern**: Use try/except for optional imports with graceful fallbacks

```python
# Standard imports
import os
import sys
import subprocess
import threading

# Third-party imports
import customtkinter as ctk
from PIL import Image, ImageTk
import requests

# Local imports with fallbacks
try:
    import utils
except ImportError:
    utils = None

try:
    import theme
except ImportError:
    theme = None
```

### Naming Conventions
- **Functions**: `snake_case` with descriptive names, e.g., `parcourir_dossier_source`, `check_and_download_ffmpeg`
- **Variables**: `snake_case`, use meaningful names, e.g., `source_folder`, `destination_folder`
- **Classes**: `PascalCase`, often ending with `GUI` or `Manager`, e.g., `CHDmanGUI`, `DependencyManager`
- **Constants**: `UPPER_SNAKE_CASE`, e.g., `CHDMAN_URL`, `COLOR_ACCENT_PRIMARY`
- **File names**: `PascalCase.py` for modules (e.g., `CHDManager.py`), `snake_case.py` for utilities (e.g., `utils.py`)

### UI Framework Patterns

#### CustomTkinter Usage
- Always use dark mode: `ctk.set_appearance_mode("dark")`
- Apply consistent theme using `theme.apply_theme(window, title)`
- Use `StringVar`, `IntVar`, `BooleanVar` for data binding
- Layout primarily with `grid()` for precise control, `pack()` for simple containers

#### Theme Integration
```python
# Apply theme consistently
if theme:
    theme.apply_theme(root, "Module Title")
    accent_color = theme.COLOR_ACCENT_PRIMARY
    card_bg = theme.COLOR_CARD_BG
    text_main = theme.COLOR_TEXT_MAIN
else:
    # Fallback colors
    accent_color = "#1f6aa5"
    card_bg = "#2b2b2b"
    text_main = "#ffffff"
```

#### Layout Structure
```python
# Standard layout pattern
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

main_frame = ctk.CTkScrollableFrame(root, fg_color="transparent")
main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

# Card-style sections
card_frame = ctk.CTkFrame(main_frame, fg_color=theme.COLOR_CARD_BG if theme else None)
card_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
```

### Error Handling Patterns
- Use `try/except` blocks for external tool execution
- Implement proper logging for debugging
- Show user-friendly messages with `messagebox`
- Graceful degradation when dependencies are missing

```python
def process_file(file_path):
    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        return True, file_path, None
    except subprocess.CalledProcessError as e:
        return False, file_path, f"Tool error: {e.stderr.decode('utf-8', errors='ignore')}"
    except Exception as e:
        return False, file_path, str(e)
```

### Threading & Concurrency
- Use `ThreadPoolExecutor` for parallel processing
- CPU-intensive tasks should use `multiprocessing`
- UI updates must be done on the main thread
- Progress reporting via callbacks or queues

```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = {executor.submit(process_item, item): item for item in items}
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        # Handle result
```

### Resource Management
- Use `utils.resource_path()` for file paths (works in dev and PyInstaller)
- Use `utils.get_binary_path()` for external tools
- Download dependencies automatically via `DependencyManager`
- Clean up temporary files and processes

## Module Development Patterns

### Standard Module Structure
```python
import os
import sys
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar

# Import shared utilities
try:
    import utils
    import theme
except ImportError:
    utils = None
    theme = None

class ModuleGUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
    
    def setup_ui(self):
        # Apply theme
        if theme:
            theme.apply_theme(self.root, "Module Title")
        
        # Setup layout
        self.root.geometry("800x600")
        # ... UI components
    
    def process_files(self):
        # Main processing logic
        pass

def main():
    root = ctk.CTk()
    app = ModuleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

### Integration Points
- **Main launcher**: Modules are launched from `main.py` via `module_runner.py`
- **Icons**: Each module has corresponding icon in `assets/` (e.g., `CHDManager.ico`)
- **Descriptions**: Module descriptions defined in `main.py` `SCRIPT_DESCRIPTIONS` dictionary
- **Categories**: Modules categorized in `SCRIPT_CATEGORIES` mapping

## External Dependencies

### Required Tools (auto-downloaded)
- `ffmpeg.exe` - Media processing
- `chdman.exe` - CHD compression (MAME)
- `7za.exe` - Archive extraction
- `DolphinTool.exe` - GameCube/Wii conversion
- `maxcso.exe` - ISO compression for PSP/PS2

### Python Libraries
- `customtkinter` - Modern UI framework
- `tkinterdnd2` - Drag & drop support
- `Pillow` - Image processing
- `requests` - HTTP client
- `yt-dlp` - YouTube downloader
- `openai` - AI integration
- `PyMuPDF` - PDF processing

## PyInstaller Configuration

### Build Process
1. **Build Script**: `build.py` handles PyInstaller execution
2. **Spec File**: `RetrogamingToolkit.spec` contains detailed configuration
3. **Hidden Imports**: All modules automatically added as hidden imports
4. **Data Files**: Assets and modules bundled automatically
5. **VLC**: Binaries included if present in `Retrogaming-Toolkit-AIO/vlc/`

### Key Build Settings
- `--onedir`: Creates directory distribution (easier for debugging)
- `--windowed`: No console window
- `--clean`: Clean cache before building
- Bundles entire `Retrogaming-Toolkit-AIO/` directory
- Includes `assets/` with icons and images

## Localization & Internationalization

### Multi-language Support
- Primary language: French (FR)
- Supported languages: EN, ES, IT, DE, PT
- Translation dictionaries in `main.py`
- UI labels and messages use `TRANSLATIONS[CURRENT_LANG]["key"]`

### Adding New Translations
1. Add language code to `TRANSLATIONS` dictionary
2. Translate all UI strings and messages
3. Update module descriptions in `SCRIPT_DESCRIPTIONS`

## File Organization

```
/
├── main.py                    # Main launcher application
├── build.py                   # PyInstaller build script
├── requirements.txt           # Python dependencies
├── setup.iss                 # Inno Setup installer script
├── assets/                   # Icons, images, UI resources
├── Retrogaming-Toolkit-AIO/   # Module directory
│   ├── utils.py              # Shared utilities
│   ├── theme.py              # UI theme definitions
│   ├── module_runner.py      # Module execution wrapper
│   └── *.py                  # Individual module files
├── dist/                     # PyInstaller output (build artifacts)
└── build/                    # PyInstaller build cache
```

## Common Gotchas & Solutions

### Path Handling
- Always use `utils.resource_path()` for bundled files
- Use `utils.get_binary_path()` for external executables
- Remember PyInstaller changes the working directory

### Threading Issues
- Never update UI from worker threads
- Use `root.after()` or queues for UI updates
- Be careful with daemon processes that might terminate early

### Theme Fallbacks
- Always check if `theme` module is available
- Provide fallback colors and fonts
- Test with and without theme system

### External Tools
- Implement automatic download/update logic
- Check for tool existence before use
- Handle version compatibility issues

This guide should provide all the essential information for working effectively with the Retrogaming Toolkit AIO codebase.