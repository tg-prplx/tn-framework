import os
from .valid_ers import *

class NVLRCParser:
    def __init__(self, name: str = '.nvlrc'):
        self.name = name
        self.scene_dir = ""
        self.nvl_name = ""
        self.save_file = ""

        if os.path.exists(name):
            with open(self.name, 'r') as f:
                args = f.read().splitlines()

                raw_pairs = [line.split("=", 1) for line in args if "=" in line]
                config = {
                    k.strip().replace("-", "_"): v.strip()
                    for k, v in raw_pairs
                }

                self.nvl_name = config.get("novel_name", "")
                self.scene_dir = config.get("scene_dir", "")
                self.save_file = config.get("save_file", "")

                if not self.nvl_name:
                    raise ValidationError("Name of novell not setted in nvlrc.")
                if not self.scene_dir:
                    raise ValidationError("Dir of scenes not setted in nvlrc.")
                if not self.save_file:
                    raise ValidationError("Path of save file not setted in nvlrc.")

        else:
            raise NVLRCNotFound("NVLRC not found at default path.")

    def get_scene_dir(self) -> str:
        return self.scene_dir

    def get_nvl_name(self) -> str:
        return self.nvl_name

    def get_save_file(self) -> str:
        return self.save_file
