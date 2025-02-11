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
import pygame

cv2.ocl.setUseOpenCL(True)

SYMBOLS = np.array(list("▒▓▓█"))

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


class MusicManager:
    def play_audio(self, file_path):
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1)
        else:
            print(f"[ERROR] Аудиофайл {file_path} не найден")

    def stop_audio(self):
        pygame.mixer.music.stop()


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
        self.scenes = []
        self.show_tab = True
        self.lua_env = self.lua.globals()
        self.choices = {}
        self.music = ""
        pygame.mixer.init()

    def exit(self):
        self.console.clear()
        exit()


class RenderEngine(EngineBase):
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
        resized_image = cv2.resize(
            image,
            (term_width, term_height - self.tab_height),
            interpolation=cv2.INTER_NEAREST,
        )

        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_RGB2GRAY)
        indices = (gray_image * (len(SYMBOLS) / 256)).astype(np.int32)
        indices = np.clip(indices, 0, len(SYMBOLS) - 1)
        symbols = SYMBOLS[indices]

        avg_colors = np.zeros_like(resized_image)

        for y in range(resized_image.shape[0]):
            for x in range(resized_image.shape[1] - 1):
                left_pixel = resized_image[y, x]
                right_pixel = resized_image[y, x + 1]

                avg_pixel = np.sqrt((left_pixel.astype(np.float32) ** 2 + right_pixel.astype(np.float32) ** 2) / 2)
                avg_colors[y, x] = avg_pixel.astype(np.uint8)

        avg_colors[:, -1] = avg_colors[:, -2]

        output = [
            "".join(
                f"[#{r:02x}{g:02x}{b:02x} on #{rb:02x}{gb:02x}{bb:02x}]{s}[/]"
                for (r, g, b), (rb, gb, bb), s in zip(row_pixels, row_avg_colors, row_symbols)
            )
            for row_pixels, row_avg_colors, row_symbols in zip(resized_image, avg_colors, symbols)
        ]

        self.console.print("\n".join(output), end="")

    def render(self, render_tab: bool):
        self.console.clear()
        self.render_scene()
        self.render_tab()


class LogicEngine(RenderEngine, MusicManager):
    def __init__(self):
        super().__init__()
        self.lua.globals().engine = self
        self.await_input = True

    def add_choice(self, name: str, choice: str):
        self.choices[name] = choice

    def get_choice(self, name: str):
        return self.choices[name]
    
    def delete_choice(self, name: str):
        del self.choices[name]

    def load_scene(self, scene: dict, execute=True):
        self.id = scene["id"]
        self.text = scene["text"]
        self.background = scene["background"]
        self.person = scene["person"]
        if "music" in scene:
            self.music = scene["music"]
            self.play_audio(self.music)
        if "script" in scene and os.path.exists(scene["script"]) and execute:
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
        if self.id < len(self.scenes):
            self.id += 1
            self.load_scene(self.scenes[self.id - 1])
            self.apply_lua_logic()

    def prev_scene(self):
        self.id -= 1
        if self.id < 1:
            self.id = 1
        self.load_scene(self.scenes[self.id - 1])
        self.apply_lua_logic()

    def custom_scene(self, id: int):
        self.id = id
        if self.id < 1:
            self.id = 1
        elif self.id > len(self.scenes):
            self.id = len(self.scenes)
        self.load_scene(self.scenes[self.id - 1])

    def apply_lua_logic(self, lua_function_name="modify_scene"):
        if lua_function_name in self.lua_env:

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

            lua_function = self.lua_env[lua_function_name]
            new_scene = lua_function(scene_data)

            if isinstance(new_scene, dict):
                self.text = new_scene.get("text", self.text)
                self.person = new_scene.get("person", self.person)
                self.background = new_scene.get("background", self.background)
                self.choices = new_scene.get("choices", self.choices)
                self.show_tab = new_scene.get("show_tab", True)

            if lua_function_name == "post_scene":
                self.lua_env.post_scene = None

    def save_game(self, filename="save.json"):

        save_data = {
            "id": self.id,
            "text": self.text,
            "background": self.background,
            "person": self.person,
            "music": self.music,
            "choices": self.choices
        }

        with open(filename, "w", encoding="utf-8") as f:
            dump(save_data, f, indent=4)

    def load_game(self, filename="save.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                save_data = load(f)

            self.id = save_data["id"]
            self.text = save_data["text"]
            self.background = save_data["background"]
            self.person = save_data["person"]
            self.choices = save_data["choices"]

            self.load_scene(self.scenes[self.id - 1])

        except (FileNotFoundError, JSONDecodeError) as e:
            print(f"Ошибка загрузки сохранения: {e}")
            self.choices = {}

    def run(self):
        self.register_scenes()
        if os.path.exists("save.json"):
            self.load_game()

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
