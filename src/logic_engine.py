from .render_engine import *
from getpass import getpass

class LogicEngine(RenderEngine, MusicManager):
    def __init__(self):
        super().__init__()
        self.lua.globals().engine = self # type: ignore
        self.await_input = True

    def add_choice(self, name: str, choice: str):
        logging.debug(f"adding choice: {name}={choice}")
        self.choices[name] = choice

    def get_choice(self, name: str):
        logging.debug(f"getting {name} choice")
        if name not in self.choices:
            return None
        return self.choices[name]
    
    def delete_choice(self, name: str):
        logging.debug("deleting {name} choice")
        if name not in self.choices:
            logging.critical(f"attempt delete of uncreated choice {name}")
            exit(-1)
        del self.choices[name]

    def load_scene(self, scene: dict, execute=True):
        self.id = scene["id"]
        self.text = scene["text"]
        self.background = scene["background"]
        self.person = scene["person"]
        if "music" in scene:
            self.music = scene["music"]
            logging.info(f"playing music {scene['music']}")
            self.play_audio(self.music)
        if "script" in scene and os.path.exists(scene["script"]) and execute:
            logging.debug(f"founded script {scene['script']}")
            with open(scene["script"], "r", encoding="utf-8") as f:
                lua_code = f.read()
            logging.info(f"executing {scene['script']}")
            self.lua.execute(lua_code)
        elif "script" in scene and not os.path.exists(scene['script']):
            logging.warning(f"script {scene['script']} entry founded in scene file, but file dont found")
    
    def default_scene(self, scene: dict):
        self.id = scene["id"]
        self.text = scene["text"]
        self.background = scene["background"]
        self.person = scene["person"]
        if "musin" in scene:
            self.music = scene["music"]

    def register_scenes(self):
        self.scenes = []
        for i in os.listdir("scenes"):
            if i.endswith(".json"):
                with open(os.path.join("scenes", i), "r", encoding="utf-8") as f:
                    self.scenes.append(load(f))
        self.scenes.sort(key=lambda x: x["id"])
        self.default_scene(self.scenes[self.id - 1])
        return self.scenes

    def get_scene(self):
        return {
            "id": self.id,
            "text": self.text,
            "background": self.background,
            "person": self.person,
            "choices": self.choices,
            "music": self.music,
        }

    def next_scene(self):
        logging.info("loading next scene")
        if self.id < len(self.scenes):
            self.id += 1
            self.load_scene(self.scenes[self.id - 1])
            self.apply_lua_logic()
        else:
            self.exit()

    def prev_scene(self):
        logging.info("loading previous scene")
        self.id -= 1
        if self.id < 1:
            self.id = 1
        self.load_scene(self.scenes[self.id - 1])
        self.apply_lua_logic()

    def custom_scene(self, id: int):
        logging.info("loading custom scene")
        self.id = id
        if self.id < 1:
            self.id = 1
        elif self.id > len(self.scenes):
            self.id = len(self.scenes)
        self.load_scene(self.scenes[self.id - 1])

    def apply_lua_logic(self, lua_function_name="modify_scene"):
        logging.debug(f"applying lua logic on id {self.id}")
        if lua_function_name in self.lua_env: # type: ignore
            scene_data = {
                "id": self.id,
                "text": self.text,
                "background": self.background,
                "person": self.person,
                "get_choice": self.get_choice,
                "delete_choice": self.delete_choice,
                "add_choice": self.add_choice,
                "cv": cv2,
                "music": self.music,
            }

            lua_function = self.lua_env[lua_function_name] # type: ignore
            try:
                new_scene = lua_function(scene_data)
            except Exception as e:
                logging.critical(f"Error in lua function: {e}")
                exit(-1)
            if isinstance(new_scene, dict):
                self.text = new_scene.get("text", self.text)
                self.person = new_scene.get("person", self.person)
                self.background = new_scene.get("background", self.background)
                self.choices = new_scene.get("choices", self.choices)
                self.show_tab = new_scene.get("show_tab", True)

            if lua_function_name == "post_scene":
                logging.debug("executing post scene script")
                self.lua_env.post_scene = None # type: ignore
        else:
            logging.warning(f"function {lua_function_name} not found in lua env, skipping script...")

    def save_game(self):
        logging.debug("saving...")
        save_data = {
            "id": self.id,
            "text": self.text,
            "background": self.background,
            "person": self.person,
            "music": self.music,
            "choices": self.choices,
        }

        with open(self.save_dir, "w", encoding="utf-8") as f:
            dump(save_data, f, indent=4)

    def load_game(self):
        logging.info("loading save")
        try:
            with open(self.save_dir, "r", encoding="utf-8") as f:
                save_data = load(f)

            self.id = save_data["id"]
            self.text = save_data["text"]
            self.background = save_data["background"]
            self.person = save_data["person"]
            self.choices = save_data["choices"]

            self.load_scene(self.scenes[self.id - 1])

        except (FileNotFoundError, JSONDecodeError) as e:
            logging.critical("error while loading save")
            self.choices = {}

    def run(self, register: bool = True, load_save: bool = True):
        logging.info("running game")
        if register:
            self.register_scenes()
        if load_save:
            if os.path.exists(self.save_dir):
                self.load_game()
        logging.info("entering game loop")
        for _ in range(len(self.scenes) - (self.id - 1)):
            self.save_game()
            self.apply_lua_logic()
            self.render(self.show_tab)
            self.apply_lua_logic(lua_function_name="post_scene")

            if self.await_input:
                getpass(prompt="")
            else:
                self.await_input = True

            self.next_scene()
