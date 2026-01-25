import os
import sys
import time
import signal
import logging
import multiprocessing
import vlc

try:
    # Ensure plugins are found if locally embedded (optional, good practice)
    os.environ['VLC_PLUGIN_PATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vlc', 'plugins'))
except: pass

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
