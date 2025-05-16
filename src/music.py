import pygame
import os
from ..config import *

class MusicManager:
    def play_audio(self, file_path):
        logging.debug(f"playing audio {file_path}")
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1)
        else:
            print(f"[ERROR] Аудиофайл {file_path} не найден")

    def stop_audio(self):
        logging.debug("stopping audio")
        pygame.mixer.music.stop()