import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

LAST_SCENE_PATH = ".last-scene.json"
SCENE_DIR = "scenes"
ROOT_DIR = os.getcwd()  # корень новеллы, откуда запускается IDE

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class SceneEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TFN Scene Mini-IDE")
        self.geometry("740x500")
        self.resizable(False, False)

        self.vars = {
            "id": ctk.StringVar(),
            "text": ctk.StringVar(),
            "person": ctk.StringVar(),
            "background": ctk.StringVar(),
            "script": ctk.StringVar(),
            "music": ctk.StringVar()
        }

        self.preview_img = None

        self._build_ui()
        self.bind_shortcuts()
        self.autoload_last()

    def _build_ui(self):
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkButton(btn_frame, text="New", command=self.clear, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Load", command=self.load, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=self.save, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Duplicate", command=self.duplicate, width=100).pack(side="left", padx=5)

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        row = 0
        for key, var in self.vars.items():
            ctk.CTkLabel(form, text=f"{key}:", width=100, anchor="w").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(form, textvariable=var, width=400, placeholder_text=f"enter {key}...")
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            if key in ("background", "script", "music"):
                browse_btn = ctk.CTkButton(form, text="📁", width=40, command=lambda k=key: self.browse_file(k))
                browse_btn.grid(row=row, column=2, padx=5)
            row += 1

        self.preview_label = ctk.CTkLabel(form, text="🎞 background preview", anchor="center")
        self.preview_label.grid(row=row, column=0, columnspan=3, pady=10)

    def bind_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-o>", lambda e: self.load())
        self.bind("<Control-n>", lambda e: self.clear())
        self.bind("<Control-d>", lambda e: self.duplicate())

    def browse_file(self, key):
        filetypes = [("All files", "*.*")]
        if key == "music":
            filetypes = [("Audio", "*.mp3 *.ogg *.wav")]
        elif key == "background":
            filetypes = [("Images", "*.jpg *.png *.jpeg *.webp")]
        elif key == "script":
            filetypes = [("Lua", "*.lua")]

        path = filedialog.askopenfilename(title=f"Select {key}", filetypes=filetypes, initialdir=ROOT_DIR)
        if path:
            rel_path = os.path.relpath(path, ROOT_DIR)
            self.vars[key].set(rel_path)
            if key == "background":
                self.update_preview(path)

    def update_preview(self, path):
        # path приходит относительный — делаем абсолютный для загрузки
        abs_path = os.path.join(ROOT_DIR, path) if not os.path.isabs(path) else path
        if not os.path.exists(abs_path):
            self.preview_label.configure(text="🚫 image not found", image=None)
            return
        try:
            img = Image.open(abs_path)
            img.thumbnail((300, 200))
            self.preview_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=self.preview_img, text="")
        except Exception:
            self.preview_label.configure(text="❌ failed to load image", image=None)

    def clear(self):
        self._auto_id()
        for key in self.vars:
            if key != "id":
                self.vars[key].set("")
        self.preview_label.configure(image=None, text="🎞 background preview")

    def _auto_id(self):
        os.makedirs(SCENE_DIR, exist_ok=True)
        existing = [int(f.split(".")[0]) for f in os.listdir(SCENE_DIR) if f.endswith(".json") and f.split(".")[0].isdigit()]
        next_id = max(existing) + 1 if existing else 1
        self.vars["id"].set(str(next_id))

    def duplicate(self):
        self.vars["id"].set("")
        self._auto_id()

    def load(self):
        path = filedialog.askopenfilename(title="Open scene", filetypes=[("JSON", "*.json")], initialdir=SCENE_DIR)
        if not path: return
        try:
            data = json.load(open(path, "r", encoding="utf-8"))
            for key in self.vars:
                val = data.get(key, "")
                # если путь — делаем относительным
                if key in ("background", "script", "music") and val:
                    val = os.path.relpath(val, ROOT_DIR) if os.path.isabs(val) else val
                self.vars[key].set(str(val))
            self.update_preview(self.vars["background"].get())
            with open(LAST_SCENE_PATH, "w") as f:
                json.dump({"last": path}, f)
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def save(self):
        try:
            id_val = int(self.vars["id"].get())
            scene = {
                "id": id_val,
                "text": self.vars["text"].get(),
                "person": self.vars["person"].get(),
                "background": self.vars["background"].get()
            }

            for key in scene:
                if key != "id" and not scene[key]:
                    raise ValueError(f"{key} is required.")

            for key in ("script", "music"):
                val = self.vars[key].get()
                if val:
                    scene[key] = val

            os.makedirs(SCENE_DIR, exist_ok=True)
            path = os.path.join(SCENE_DIR, f"{id_val}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(scene, f, indent=4, ensure_ascii=False)

            with open(LAST_SCENE_PATH, "w") as f:
                json.dump({"last": path}, f)

            messagebox.showinfo("Saved", f"Scene saved to: {path}")
        except ValueError as e:
            messagebox.showwarning("Validation error", str(e))
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def autoload_last(self):
        if os.path.exists(LAST_SCENE_PATH):
            try:
                data = json.load(open(LAST_SCENE_PATH, "r"))
                path = data.get("last", "")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        scene = json.load(f)
                        for key in self.vars:
                            val = scene.get(key, "")
                            if key in ("background", "script", "music") and val:
                                val = os.path.relpath(val, ROOT_DIR) if os.path.isabs(val) else val
                            self.vars[key].set(str(val))
                        self.update_preview(self.vars["background"].get())
            except:
                pass

if __name__ == "__main__":
    app = SceneEditor()
    app.mainloop()
