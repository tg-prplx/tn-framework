from json import load, dump, JSONDecodeError
import os
from ..config import *


class ThemeManager:
    def __init__(self) -> None:
        self.theme: dict = {}

    def load_theme(self, theme):
        if os.path.exists(theme):
            with open(theme, "r", encoding="utf-8") as f:
                self.theme = load(f)
        else:
            logging.warning(f"theme {theme} not found")

    def get_theme(self):
        return self.theme