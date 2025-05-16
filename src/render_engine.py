from .base import *
import textwrap
import cv2

cv2.ocl.setUseOpenCL(True)

class RenderEngine(EngineBase):
    def render_tab(self):
        logging.debug("rendering tab" + str(self.id))
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
        logging.debug(f'rendering scene: {self.id}')
        file_path = self.background
        if not os.path.exists(file_path):
            logging.warning("background isn't exist, skiping...")
            return

        image = cv2.imread(file_path)
        if image is None:
            logging.critical(f"cv2 cant read {file_path}, corrupted?")
            exit(-1)

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
                for (r, g, b), (rb, gb, bb), s in zip(row_pixels, row_avg_colors, row_symbols) # type: ignore
            )
            for row_pixels, row_avg_colors, row_symbols in zip(resized_image, avg_colors, symbols)
        ]

        self.console.print("\n".join(output), end="")

    def render(self, render_tab: bool):
        logging.info(f"rendering: {self.id}")
        self.console.clear()
        self.render_scene()
        if self.show_tab:
            self.render_tab()