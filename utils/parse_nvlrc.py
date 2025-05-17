from ..config import *

class Parser:
    def __init__(self, name: str = './.nvlrc'):
        self.name = name
        self.scene_dir = ""
        self.nvl_name = ""
        logging.info("initialize nvlrc")
        if os.path.exists(name):
            with open(self.name, 'r') as f:
                args = f.read().split("\n")
                for i in args:
                    i = i.split("=")
                    if i[0] == "scene-dir":
                        if not os.path.exists(i[1]):
                            logging.critical("scenes dir setted in nvlrc but dir not found")
                            exit(-1)
                        self.scene_dir = i[1]
                    if i[0] == "novel-name":
                        self.nvl_name = i[1]
                if self.nvl_name == "":
                    logging.warning("novell name not setted in nvlrc, be care")
                if self.scene_dir == "":
                    logging.critical("scene dir is not setted in nvlrc, novell cannot load")
                    exit(-1)
        else:
            logging.critical("nvlrc not found, maybe this not novell directory")
            exit(-1)
    
    def get_scene_dir(self) -> str:
        return self.scene_dir
    
    def get_nvl_name(self) -> str:
        return self.nvl_name