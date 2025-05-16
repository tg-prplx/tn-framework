(DEPRECATED)# 📖 **Документация по созданию новелл на движке**

## 🎭 **Общее описание**
Этот движок предназначен для создания текстовых новелл в терминале с поддержкой:
- **Сцен** 📜
- **Персонажей** 🎭
- **Фоновых изображений** 🖼 (рендеринг ASCII)
- **Lua-скриптов** 🖥 (изменение сцен, выборы, логика)
- **Музыки и звуков** 🎶 (через `pygame`)
- **Сохранения и загрузки** 💾

---

## 🛠 **Установка и подготовка**
1. Установите Python **3.8+**.
2. Установите зависимости:
   ```sh
   pip install rich numpy opencv-python lupa pygame
   ```
3. **Создайте структуру проекта**:
   ```
   ├── main.py               # Главный файл для запуска
   ├── main.theme            # Файл темы
   ├── scenes/               # Папка со сценами
   │   ├── scene1.json       # JSON-файл сцены
   │   ├── scene2.json
   ├── images/               # Фоновые изображения
   │   ├── nah.webp
   ├── scripts/              # Lua-скрипты для сцен
   │   ├── scene1.lua
   ├── audio/                # Музыка и звуки
   │   ├── background.mp3
   ├── save.json             # Файл сохранения
   ```

---

## 📌 **Создание сцен**
### 🔹 **Файл сцены (JSON)**
Каждая сцена — это JSON-файл, содержащий основные параметры.

#### **Пример: `scenes/scene1.json`**
```json
{
    "id": 1,
    "text": "I'm gently opening the door.",
    "person": "You",
    "background": "images/nah.webp",
    "script": "scripts/scene1.lua",
    "music": "audio/background.mp3"
}
```
**Параметры:**
- `id` — порядковый номер сцены.
- `text` — текст, который увидит игрок.
- `person` — имя говорящего персонажа.
- `background` — путь к фоновому изображению (рендерится в ASCII).
- `script` — Lua-скрипт для обработки логики сцены.
- `music` — путь к музыкальному файлу.

---

## 📝 **Lua-скрипты**
Lua-скрипты позволяют изменять сцену, добавлять выборы, а также взаимодействовать с движком.

### **Основная функция Lua**
#### **Пример скрипта `scripts/scene1.lua`**
```lua
function modify_scene(scene)
    if scene.id == 1 then
        scene.text = scene.text .. " But something feels off..."
        scene.person = "Narrator"
    end
    return scene
end
```
Этот скрипт:
- Добавляет текст к сцене **при её загрузке**.
- Меняет персонажа, который говорит текст.

---

## 🔥 **Движок доступен из Lua!**
Lua-скрипты могут вызывать методы движка **через объект `engine`**.

### **Примеры вызовов:**
```lua
-- Изменить сцену вручную
engine.custom_scene(2)  -- Переход к сцене 2

-- Вывести текст в консоль
engine.console.print("[bold red]Critical Error![/]")

-- Выйти из игры
engine.exit()

-- Включить музыку
engine.play_audio("audio/background.mp3")

-- Остановить музыку
engine.stop_audio()
```

### **Доступные функции:**
| Функция | Описание |
|---------|----------|
| `engine.exit()` | Завершает работу движка. |
| `engine.console.print(text)` | Выводит `text` в терминал (поддерживает Markdown). |
| `engine.next_scene()` | Переход к следующей сцене. |
| `engine.prev_scene()` | Возвращает игрока на предыдущую сцену. |
| `engine.custom_scene(id)` | Перемещает игрока в указанную `id` сцену. |
| `engine.render()` | Принудительно рендерит текущую сцену. |
| `engine.add_choice(name, choice)` | Добавляет выбор пользователя. |
| `engine.get_choice(name)` | Получает выбор, который был записан с помощью `add_choice()`. |
| `engine.delete_choice(name)` | Удаляет выбор из памяти. |
| `engine.play_audio(file_path)` | Воспроизводит аудиофайл. |
| `engine.stop_audio()` | Останавливает текущую музыку. |

---

## 🎭 **Выборы и ветвления**
Выборы могут быть реализованы через `engine.add_choice()` и `engine.get_choice()`.

### **Пример выбора:**
```lua
function modify_scene(scene)
    if scene.id == 1 then
        scene.text = "You stand before a dark door. What do you do?"
        engine.add_choice("door_choice", "open")
    elseif scene.id == 2 and engine.get_choice("door_choice") == "open" then
        scene.text = "You open the door and step inside..."
    end
    return scene
end
```
- `add_choice("door_choice", "open")` — записывает выбор.
- `get_choice("door_choice") == "open"` — проверяет выбор.

---

## 🎨 **Темы (main.theme)**
Файл `main.theme` позволяет изменить стиль отображения.

#### **Пример:**
```json
{
    "text_color": "white",
    "background_color": "black",
    "border_style": "double"
}
```

**Поддерживаемые параметры:**
- `text_color` — цвет текста.
- `background_color` — цвет фона.
- `border_style` — стиль рамки.

---

## 💾 **Сохранение и загрузка**
Движок **автоматически сохраняет** прогресс в `save.json`.

### **Структура сохранения:**
```json
{
    "id": 1,
    "text": "I'm gently opening the door.",
    "person": "You",
    "background": "images/nah.webp",
    "music": "audio/background.mp3",
    "choices": {}
}
```
**Автосохранение происходит перед загрузкой новой сцены.**

---

## 🚀 **Запуск**
Запустите игру:
```sh
python main.py
```
Движок загрузит сцену и будет ждать нажатия **Enter** для продолжения.

---

## 🎭 **Дополнительные возможности**
✅ **ASCII-рендеринг изображений** 🖼  
✅ **Выборы и альтернативные пути** 🔀  
✅ **Гибкая логика через Lua-скрипты** ⚡  
✅ **Фоновая музыка и звуки** 🎶  
✅ **Автосохранение и загрузка** 💾  

# TODO: 
Переносимые новеллы на общем движке, собственный формат файлов хранения новелл.
Реализация тем.
