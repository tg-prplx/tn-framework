![image](https://github.com/user-attachments/assets/adb85674-d807-4730-b709-425b57069f12)

# 📚 Terminal Novell Framework (TNF)
**TNF (Terminal Novell Framework)** is an engine for creating **interactive text visual novels** that run directly in your terminal.
> Shows ASCII art, plays music, supports choices, Lua logic, and saves games — all in a minimalistic CLI style.

---

## 🚀 Quick Start

### 📦 Requirements

_Python_ **3.11+**

### 📥 Installing dependencies

```bash
pip install -r requirements.txt
```

### ⏱ Setting up aliases

```bash
source path.sh
```

Now you have convenient commands:

```bash
tf-novell run folder . --from 1
scene-ide
```

---

## 🗂️ Project Structure

```plaintext
./
├── .nvlrc               # Visual novel config
├── scenes/              # Scene JSON files (1.json, 2.json, ...)
├── images/              # Background images
├── music/               # Music files
├── scripts/             # Lua scripts for scene logic
└── save.json            # Save file
```

---

## ⚙️ Configuration (`.nvlrc`)
```ini
nvl-name=My First Novel
scene-dir=scenes
save-file=save.json
```
| Key        | Description        |
| ---------- | ------------------|
| `nvl-name` | Name of the novel |
| `scene-dir`| Scene folder      |
| `save-file`| Save file path    |

---

## 🎬 Creating a Scene

Every scene is a `.json` file:

### 💡 Example

```json
{
  "id": 1,
  "text": "Hi, this is my first scene!",
  "person": "Main Character",
  "background": "images/room.png",
  "music": "music/theme.mp3",
  "script": "scripts/scene1.lua"
}
```

### 🧱 Required fields

| Field       | Type | Description                     |
| ----------- | ---- | ------------------------------ |
| `id`        | int  | Scene number                   |
| `text`      | str  | Scene text                     |
| `person`    | str  | Speaker’s name                 |
| `background`| str  | Path to background image        |

### 🧩 Optional fields

| Field    | Type | Description         |
| -------- | ---- | ------------------ |
| `music`  | str  | Path to music file |
| `script` | str  | Lua logic script   |

---

## 🔧 Lua Scripts

The engine has integrated **Lua 5.1** via `lupa`. You can add custom logic to scenes.

### 🔄 Main hooks

```lua
function modify_scene(scene)
    -- Called BEFORE the scene is shown
    return scene
end
function post_scene(scene)
    -- Called AFTER the scene is shown
    return scene
end
```

---

## 📘 Engine Lua API

### 📍 Main methods

| Method                           | Args                                 | Returns    | Description                        |
| -------------------------------- | ------------------------------------ | ---------- | -----------------------------------|
| `engine.get_scene()`             | –                                    | `table`    | Gets current scene as a Lua table  |
| `engine.load_scene(scene, exec)` | `scene`, `execute?` (bool)           | –          | Loads a scene and applies logic    |
| `engine.next_scene()`            | –                                    | –          | Next scene                         |
| `engine.prev_scene()`            | –                                    | –          | Previous scene                     |
| `engine.custom_scene(id)`        | `id` (int)                           | –          | Load a scene by ID                 |
| `engine.apply_lua_logic(name)`   | `name` (str, default `modify_scene`) | –          | Runs a Lua function by name        |

---

### 🎮 Working with Choices

| Method                           | Args                      | Returns | Description                  |
| -------------------------------- | ------------------------- | ------- | ---------------------------- |
| `engine.add_choice(name, txt)`   | `name` (str), `txt` (str) | –       | Adds a choice                |
| `engine.get_choice(name)`        | `name` (str)              | `str`   | Gets the text of a choice    |
| `engine.delete_choice(name)`     | `name` (str)              | –       | Deletes a choice             |

---

### 🎵 Audio Controls

| Method                     | Args           | Returns | Description                      |
| -------------------------- | -------------- | ------- | ---------------------------------|
| `engine.play_audio(path)`  | `file_path`    | –       | Plays music                      |
| `engine.stop_audio()`      | –              | –       | Stops music playback             |

---

### 💾 Saving

| Method                         | Args                | Returns | Description                              |
| ------------------------------ | ------------------- | ------- | -----------------------------------------|
| `engine.save_game(name?)`      | `filename` (str,opt)| –       | Saves to file (default: `save.json`)     |
| `engine.load_game(name?)`      | `filename` (str,opt)| –       | Loads the save file                      |

---

### 🖼️ Rendering

| Method                   | Args     | Returns | Description              |
| ------------------------ | -------- | ------- | ------------------------|
| `engine.render_tab()`    | –        | –       | Draws the bottom panel  |
| `engine.render_scene()`  | –        | –       | Renders ASCII background|
| `engine.render()`        | –        | –       | Full scene rendering    |

---

### 🖥️ Console Utilities

| Method                        | Args         | Returns | Description                           |
| ----------------------------- | ------------ | ------- | ------------------------------------- |
| `engine.console.clear()`      | –            | –       | Clear the terminal                    |
| `engine.console.print(text)`  | `text` (str) | –       | Print formatted text                  |

---

### ▶️ Running Game Loop

```lua
engine.run()
```

---

## 🔁 Lua Logic Examples

### 1. Changing text

```lua
function modify_scene(scene)
    scene.text = "This text is replaced"
    return scene
end
```

### 2. User input

```lua
function post_scene(scene)
    io.write("Enter a number: ")
    engine.add_choice("choice_rand", io.read())
    engine.await_input = false
    return scene
end
```

### 3. Handling choice

```lua
function modify_scene(scene)
    local last = engine.get_choice("choice_rand")
    if last == "42" then
        scene.text = "You picked 42! Awesome choice!"
    else
        scene.text = "Strange choice... but OK."
    end
    return scene
end
```

---

## 🧪 Helper Commands

### ✅ Validation

```bash
tf-novell validate
```
Checks project structure and file presence.

### 👁️ Scene Preview

```bash
tf-novell preview --scene 2
```
Shows the chosen scene in your terminal.

### ▶️ Run the Novel

```bash
tf-novell run folder . --from 1
```

---

## 🛠 Scene-IDE

Mini-editor for quick scene editing/creation:

```bash
scene-ide
```
* Edits `.json` dialogue files
* Visual path selection for backgrounds, music, and scripts
* Saves files in the required folder

---

## 💡 Tips
* _Always use_ *relative paths*  
* _Check_ *UTF-8 encoding* in your JSON scene files
* Run `validate` before running the novel
* Don’t overuse ASCII art—terminals can lag 😅

---

## 📦 Novel Packaging

(Coming soon) Ability to build a `.nvlpkg` archive to distribute your novel.

---

# FIXME:
If you use a script in one scene, it will persist for subsequent scenes until modify_scene or post_scene is overridden by new script files.
