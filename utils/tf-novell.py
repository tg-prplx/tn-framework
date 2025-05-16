from .nvlrc_nodebug import NVLRCParser
from .valid_ers import *
import sys
import os
from json import loads, JSONDecodeError, load
import argparse

class TNFDevTools:
    def __init__(self) -> None:
        self.parser = NVLRCParser()
        self.scenes_dir = self.parser.get_scene_dir()
        self.save_file = self.parser.get_save_file()
        self.args = sys.argv[1:]
        self.count = 0
    
    def is_valid_json(self, text: str) -> bool:
        try:
            file = loads(text)
            self.validate_requirements(file)
            return True
        except JSONDecodeError:
            return False
    
    def validate_requirements(self, scene: dict, base_path: str = "."):
        required_keys = ['music', 'script', 'background']
        for key in required_keys:
            if key in scene:
                file_path = os.path.join(base_path, scene[key])
                if not os.path.exists(file_path):
                    raise RequirementsError(
                        f"{key.capitalize()} file \"{scene[key]}\" not found for scene with ID = {scene.get('id', '?')}"
                    )

    def validate(self) -> None:
        if not os.path.exists(self.scenes_dir):
            raise ScenesStructureError("Path of scenes dir does not exist.")

        if not os.path.isdir(self.scenes_dir):
            raise ScenesStructureError("Scenes path exists, but is not a directory.")

        scene_ids = []

        for root, _, files in os.walk(self.scenes_dir):
            json_files = [f for f in files if f.endswith(".json")]
            self.count = len(json_files)

            if self.count == 0:
                raise ScenesStructureError("Scenes directory is empty or has no .json files.")

            for filename in json_files:
                path = os.path.join(root, filename)
                if not os.path.isfile(path):
                    continue

                try:
                    scene_id = int(os.path.splitext(filename)[0])
                    scene_ids.append(scene_id)
                except ValueError:
                    raise SceneFormatError(f"Scene file {filename} must be named as an integer (e.g., 1.json, 2.json, ...).")
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if not self.is_valid_json(content):
                            raise SceneFormatError(f"Invalid JSON in scene: {path}")
                except SceneFormatError as e:
                    raise SceneFormatError(f"Failed to read or parse {path}: {e}")

        expected_ids = set(range(1, self.count + 1))
        actual_ids = set(scene_ids)
        if expected_ids != actual_ids:
            missing = expected_ids - actual_ids
            extra = actual_ids - expected_ids
            raise SceneFormatError(f"Scene IDs mismatch. Missing: {sorted(missing)}; Unexpected: {sorted(extra)}")
        print(f"🎉 All {self.count} scenes validated!")

    def preview(self, id: int):
        self.validate()
        if id > self.count + 1:
            raise InvalidIDError("ID which you can play, dont exist.")
        from .src.logic_engine import LogicEngine, getpass
        eng = LogicEngine()
        eng.register_scenes()
        eng.custom_scene(id)
        eng.apply_lua_logic()
        eng.render(True)
        eng.apply_lua_logic(lua_function_name="post_scene")
        getpass(prompt='')
        eng.exit()
    
    def run(self, package: str = '', folder: str = '', from_id: int = 1):
        self.validate()
        from .src.logic_engine import LogicEngine
        eng = LogicEngine()
        eng.register_scenes()
        if from_id != 1:
            eng.custom_scene(from_id)
        if package != '':
            pass
        else:
            eng.run(register=False, load_save=False)



class CLITFN(TNFDevTools):
    def __init__(self) -> None:
        super().__init__()
        parser = argparse.ArgumentParser(description="TerminalNovellFramerork tools.")
        subparsers = parser.add_subparsers(dest="command", required=True)
        play_parser = subparsers.add_parser("preview", help="Prewiev custom scene.")
        play_parser.add_argument("--scene", required=True, help="ID of scene.")

        validate_parser = subparsers.add_parser("validate", help="проверить папку со сценами")

        run_parser = subparsers.add_parser("run", help="Run novell package or folder")
        run_subparsers = run_parser.add_subparsers(dest="run_command", required=True)
        package_parser = run_subparsers.add_parser("package", help="Run from .nvlpkg file")
        package_parser.add_argument("pkg_path", help="Path to .nvlpkg file")
        package_parser.add_argument("--from", dest="from", help="From which ID novell starts.", default=None)


        folder_parser = run_subparsers.add_parser("folder", help="Run from folder")
        folder_parser.add_argument("folder_path", help="Path to unpacked novell folder")
        folder_parser.add_argument("--from", dest="from_id", help="From which ID novell starts.", default=None)

        self.args = parser.parse_args()
    
    def _run(self):
        if self.args.command == "preview":
            self.preview(int(self.args.scene))
        elif self.args.command == "validate":
            self.validate()
        elif self.args.command == "run":
            if self.args.run_command == "package":
                pkg_path = self.args.pkg_path
                from_id  = self.args.from_id
                pass
            elif self.args.run_command == "folder":
                folder_path = self.args.folder_path
                from_id     = int(self.args.from_id)
                self.run(from_id=from_id)
            else:
                print("Error: unknown 'run' subcomand.")
            


if __name__ == "__main__":
    cli = CLITFN()
    cli._run()