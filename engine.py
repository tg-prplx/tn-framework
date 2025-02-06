import os
import textwrap
import cv2
import numpy as np
from rich.console import Console
from rich.panel import Panel
from json import load, dump, JSONDecodeError
from rich.box import SQUARE
from lupa import LuaRuntime, lua_type
from getpass import getpass
import copy

SYMBOLS = np.array(list("▒▓▓█"))

def lua_table_to_dict(lua_table):
    if lua_type(lua_table) != 'table':
        return lua_table

    result = {}
    for key, value in lua_table.items():
        if lua_type(value) == 'table':
            result[key] = lua_table_to_dict(value)
        else:
            result[key] = value
    return result


class ThemeManager:
    def __init__(self) -> None:
        self.theme: dict = {}

    def load_theme(self, theme):
        if os.path.exists(theme):
            with open(theme, "r", encoding="utf-8") as f:
                self.theme = load(f)
        else:
            print(f"theme {theme} not found")

    def get_theme(self):
        return self.theme

class EngineBase:
    def __init__(self) -> None:
        self.console = Console()
        self.w, self.h = self.console.size
        self.theme_manager = ThemeManager()
        self.id: int = 1
        self.text: str = ""
        self.background: str = ""
        self.person: str = ""
        self.theme_manager.load_theme("main.theme")
        self.tab_height = 3
        self.lua = LuaRuntime(unpack_returned_tuples=True)

    def exit(self):
        self.console.clear()
        exit()

class RenderEngine(EngineBase):
    def get_scene(self):
        return {
            "id": self.id,
            "text": self.text,
            "background": self.background,
            "person": self.person
        }

    def render_tab(self):
        box_width = self.w - 2
        inner_width = box_width - 2
        if self.text:
            raw_lines = self.text.splitlines()
            text_lines = [
                wrapped_line
                for line in raw_lines
                for wrapped_line in textwrap.wrap(line, inner_width)
            ]
        else:
            text_lines = [""]
        panel_text = "\n".join(text_lines)
        panel = Panel(
            panel_text,
            border_style="white",
            box=SQUARE,
            title=f"Scene {self.id}",
            title_align="center",
            subtitle=self.person,
            subtitle_align="center",
        )
        self.tab_height = len(text_lines) + 2
        self.console.print(panel)

    def render_scene(self):
        file_path = self.background
        if not os.path.exists(file_path):
            return

        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"cv2 cant read {file_path}, corrupted?")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        term_width = min(self.w, image.shape[1])
        term_height = min(self.h, image.shape[0])
        resized_image = cv2.resize(image, (term_width, term_height - self.tab_height), interpolation=cv2.INTER_NEAREST)

        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_RGB2GRAY)
        indices = (gray_image * (len(SYMBOLS) / 256)).astype(np.int32)
        indices = np.clip(indices, 0, len(SYMBOLS) - 1)
        symbols = SYMBOLS[indices]

        output = [
            "".join(f"[#{r:02x}{g:02x}{b:02x} on #000000]{s}[/]"
                    for (r, g, b), s in zip(row_pixels, row_symbols))
            for row_pixels, row_symbols in zip(resized_image, symbols)
        ]

        self.console.print("\n".join(output), end="")

    def render(self):
        self.console.clear()
        self.render_scene()
        self.render_tab()

class LogicEngine(RenderEngine):
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.lua_env = self.lua.globals()
        self.choices = {}


    def next_scene(self):
        if self.id < len(self.scenes):
            self.id += 1
            self.load_scene(self.scenes[self.id - 1])
            self.apply_lua_logic()

    def apply_lua_logic(self, lua_function_name="modify_scene"):
        if lua_function_name in self.lua_env:

            if isinstance(self.choices, dict):
                self.choices = list(self.choices.values())

            if not isinstance(self.choices, list):
                self.choices = []

            for i, choice in enumerate(self.choices):
                if not isinstance(choice, dict):
                    self.choices[i] = {}

            lua_choices = copy.deepcopy(self.choices)

            try:
                lua_table_choices = self.lua.table_from([dict(choice) for choice in lua_choices])
            except TypeError as e:
                print(f"[ERROR] Ошибка при преобразовании choices: {e}")
                lua_table_choices = self.lua.table_from([])

            scene_data = {
                "id": self.id,
                "text": self.text,
                "background": self.background,
                "person": self.person,
                "choices": lua_table_choices,
            }

            lua_function = self.lua_env[lua_function_name]
            new_scene = lua_function(scene_data)

            if isinstance(new_scene, dict):
                self.text = new_scene.get("text", self.text)
                self.person = new_scene.get("person", self.person)
                self.background = new_scene.get("background", self.background)
                self.choices = lua_table_to_dict(new_scene.get("choices", self.choices))
            
            if lua_function_name == "post_scene":
                self.lua_env.post_scene = None

    def prev_scene(self):
        self.id -= 1
        if self.id < 1:
            self.id = 1
    
    def custom_scene(self, id: int):
        self.id = id
        if self.id < 1:
            self.id = 1
        elif self.id > len(self.scenes):
            self.id = len(self.scenes)
        self.load_scene(self.scenes[self.id - 1])

    def load_scene(self, scene: dict):
        self.id = scene["id"]
        self.text = scene["text"]
        self.background = scene["background"]
        self.person = scene["person"]
        if "script" in scene and os.path.exists(scene["script"]):
            with open(scene["script"], "r", encoding="utf-8") as f:
                lua_code = f.read()
            self.lua.execute(lua_code)

    def register_scenes(self):
        self.scenes = []
        for i in os.listdir("scenes"):
            if i.endswith(".json"):
                with open(os.path.join("scenes", i), "r", encoding="utf-8") as f:
                    self.scenes.append(load(f))
        self.scenes.sort(key=lambda x: x["id"])
        self.load_scene(self.scenes[0])
        return self.scenes

    def run(self):
        self.register_scenes()
        for _ in range(len(self.scenes)):
            self.apply_lua_logic()
            self.render()
            self.apply_lua_logic(lua_function_name="post_scene")
            getpass(prompt='')
            self.next_scene()
        
        print("the end")
