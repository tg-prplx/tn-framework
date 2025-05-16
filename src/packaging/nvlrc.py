from ..config import *

class NVLRCParser:
    def __init__(self, name: str = '.nvlrc'):
        self.name = name
        self.scene_dir = ""
        self.nvl_name = ""
        self.save_file = ""

        logging.info("initialize nvlrc")

        if os.path.exists(name):
            with open(self.name, 'r') as f:
                args = f.read().splitlines()

                raw_pairs = [line.split("=", 1) for line in args if "=" in line]
                config = {k.strip(): v.strip() for k, v in raw_pairs}

                self.nvl_name = config.get("nvl-name", "")
                self.scene_dir = config.get("scene-dir", "")
                self.save_file = config.get("save-file", "")

                if not self.nvl_name:
                    logging.warning("novell name not setted in nvlrc, be care")
                if not self.scene_dir:
                    logging.critical("scene dir is not setted in nvlrc, novell cannot load")
                    exit(-1)
                if not self.save_file:
                    logging.critical("save file name not found")
                    exit(-1)

        else:
            logging.critical("nvlrc not found, maybe this not novell directory")
            exit(-1)

    def get_scene_dir(self) -> str:
        return self.scene_dir

    def get_nvl_name(self) -> str:
        return self.nvl_name

    def get_save_file(self) -> str:
        return self.save_file
