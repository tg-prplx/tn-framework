import numpy as np
from rich.console import Console
from lupa import LuaRuntime, lua_type
from .capatibilities.music import *
from .capatibilities.theming import *
from .config import *
from .packaging.nvlrc import NVLRCParser

class EngineBase:
    def __init__(self) -> None:
        logging.info("starting engine base")
        logging.info("starting nvlrc reading")
        self.parser = NVLRCParser()
        self.nvl_name = self.parser.get_nvl_name()
        self.scenes_dir = self.parser.get_scene_dir()
        self.save_dir  = self.parser.get_save_file()
        logging.info("console starting")
        self.console = Console()
        self.w, self.h = self.console.size
        logging.info("theme manager starting")
        self.theme_manager = ThemeManager()
        self.id: int = 1
        self.text: str = ""
        self.background: str = ""
        self.person: str = ""
        logging.info("loading theme")
        self.theme_manager.load_theme("main.theme")
        self.tab_height = 3
        logging.info("starting lua runtime")
        self.lua = LuaRuntime(unpack_returned_tuples=True) # type: ignore
        self.scenes = []
        self.show_tab = True
        self.lua_env = self.lua.globals()
        self.choices = {}
        self.music = ""
        logging.info("starting music mixer")
        pygame.mixer.init()

    def exit(self):
        logging.info('exiting...')
        self.console.clear()
        exit()
