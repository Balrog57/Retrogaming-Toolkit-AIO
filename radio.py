import os
import sys
import time
import signal
import logging
import multiprocessing
# --- VLC LOCAL PATH SETUP ---
try:
    # Get the directory where the script/exe is located
    if getattr(sys, 'frozen', False):
        # If frozen with PyInstaller
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    else:
        # If running as script
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Path to local vlc folder
    vlc_path = os.path.join(base_path, 'vlc')
    if not os.path.exists(vlc_path):
        # Try checking in Retrogaming-Toolkit-AIO subdirectory (if running from main.py context)
        fallback_path = os.path.join(base_path, 'Retrogaming-Toolkit-AIO', 'vlc')
        if os.path.exists(fallback_path):
             vlc_path = fallback_path
    
    # If the folder exists, add it to DLL search path (Windows)
    if os.path.exists(vlc_path):
        # For Windows 8+ and Python 3.8+ DLL loading security:
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(vlc_path)
            
        # Also set VLC_PLUGIN_PATH env var
        plugin_path = os.path.join(vlc_path, 'plugins')
        if os.path.exists(plugin_path):
            os.environ['VLC_PLUGIN_PATH'] = plugin_path
            
        # Fallback/Additional path env
        os.environ['PATH'] = vlc_path + os.pathsep + os.environ['PATH']

except Exception as e:
    print(f"Warning: Failed to setup local VLC path: {e}")
# -----------------------------

import vlc

# --- VLC LOCAL PATH SETUP ---


# Configure logging
logger = logging.getLogger("RadioProcess")

def setup_logger():
    try:
        import tempfile
        log_path = os.path.join(tempfile.gettempdir(), 'balrog_radio_debug.log')
        handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    except: pass

class VLCPlayer:
    """
    Wrapper pour VLC (python-vlc).
    Implémentation légère et robuste pour le streaming.
    """
    def __init__(self):
        self.instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.instance.media_player_new()
        self._volume = 100 # VLC uses 0-100 normally
        
    def play(self, url):
        try:
            # Create new media
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            
            # Restore volume
            self.player.audio_set_volume(self._volume)
            
            logger.info(f"VLC playing: {url}")
            return True
        except Exception as e:
            logger.error(f"VLC Play Error: {e}")
            return False

    def stop(self):
        try:
            self.player.stop()
            logger.info("VLC stopped")
        except Exception as e:
            logger.error(f"VLC Stop Error: {e}")

    def mute(self):
        self.player.audio_set_mute(True)

    def unmute(self):
        self.player.audio_set_mute(False)
        
    def release(self):
        try:
            self.player.release()
            self.instance.release()
        except: pass

def run_radio_process(command_queue):
    """
    Processus isolé qui gère le player VLC.
    """
    setup_logger()
    logger.info("Radio Process Started (VLC Engine)")
    
    try:
        player = VLCPlayer()
    except Exception as e:
        logger.critical(f"Failed to load VLC: {e}")
        return

    while True:
        try:
            command = command_queue.get()
            logger.info(f"Command received: {command}")
            
            if command == "EXIT":
                player.stop()
                break
                
            elif command == "STOP":
                player.stop()
                
            elif command == "MUTE":
                player.mute()
                
            elif command == "UNMUTE":
                player.unmute()
                
            elif command.startswith("PLAY:"):
                url = command.split("PLAY:", 1)[1]
                player.play(url)

        except Exception as e:
            logger.error(f"Loop Error: {e}")
            break
            
    # Final cleanup
    player.stop()
    player.release()
    logger.info("Radio Process Exiting")
