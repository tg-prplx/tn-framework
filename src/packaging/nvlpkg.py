from ..config import *
from .nvlrc import NVLRCParser
import zipfile

class NVLPKGBuilder:
    def __init__(self) -> None:
        self.parser = NVLRCParser()
        self.dirs = ''
        if not os.path.exists('.include-dirs'):
            print('Warning: .include-dirs file not exist. Including standard dirs.')
        else:
            with open('.include-dirs', 'r') as f:
                self.dirs = f.read().split('\n')
    
    def build(self, out_name: str = "MyNovella.nvlpkg") -> None:
        print(f"Building {out_name} ...")

        include_dirs = self.dirs or ['scenes', 'images']
        files_to_add = []

        required_files = ['metadata.json', 'config.json', 'save.json']
        for rf in required_files:
            if os.path.exists(rf):
                files_to_add.append((rf, rf))
            else:
                print(f"Warning: {rf} not found, skipping.")

        for folder in include_dirs:
            if not os.path.exists(folder):
                print(f"Warning: dir {folder} not found, skipping.")
                continue
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, '.')
                    files_to_add.append((full_path, rel_path))

        with zipfile.ZipFile(out_name, 'w', zipfile.ZIP_DEFLATED) as archive:
            for full_path, arcname in files_to_add:
                archive.write(full_path, arcname)
                print(f"➕ added: {arcname}")

        print(f"Done! {out_name} created.")


