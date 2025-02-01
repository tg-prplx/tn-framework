import os
import textwrap
import cv2
import numpy as np
from rich.console import Console
from rich.panel import Panel
from json import load, dump, JSONDecodeError
from rich.box import SQUARE
import fcntl

SYMBOLS = np.array(list("▒▓▓█"))

class ChoicesStorage:
    FILE_PATH = "choices.json"

    def __init__(self) -> None:
        self.choices = self.__load()

    def __load(self):
        if not os.path.exists(self.FILE_PATH):
            return []

        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)  # Блокировка на чтение (Linux/macOS)
                data = load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
        except (JSONDecodeError, FileNotFoundError):
            return []

    def __save(self):
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # Блокировка на запись (Linux/macOS)
            dump(self.choices, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)

    def add_choice(self, choice: dict[str, int]):
        self.choices.append(choice)
        self.__save()

    def get_choices(self):
        return self.choices

    def clear(self):
        self.choices.clear()
        self.__save()
        os.remove(self.FILE_PATH)


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
            raise FileNotFoundError(f"file {file_path} isnt found XD")

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
    def next_scene(self):
        self.id += 1
        if self.id > len(self.scenes):
            self.id = len(self.scenes)
    
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

    def register_scenes(self):
        self.scenes = []
        for i in os.listdir("scenes"):
            if i.endswith(".json"):
                with open(os.path.join("scenes", i), "r", encoding="utf-8") as f:
                    self.scenes.append(load(f))
        self.scenes.sort(key=lambda x: x["id"])
        self.load_scene(self.scenes[0])
        return self.scenes
