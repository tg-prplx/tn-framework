-- main.lua

-- НЕ нужно: local engine = require("engine_stub")

local secret_number = 7

local scene_intro = {
    id = 1,
    text = "Привет! Давай сыграем в угадайку. Введи число от 1 до 10:",
    background = "bg_intro.txt",
    person = "AI",
}

local scene_win = {
    id = 2,
    text = "Красава! Ты угадал! 🎉",
    background = "bg_win.txt",
    person = "AI",
}

local scene_lose = {
    id = 3,
    text = "Мимо! Было загадано: " .. secret_number .. " 😭",
    background = "bg_lose.txt",
    person = "AI",
}

engine.scenes[1] = scene_intro
engine.scenes[2] = scene_win
engine.scenes[3] = scene_lose

function modify_scene()
    engine.show_tab = false
end

function post_scene()
    local i = io.read()
    local n = tonumber(i)
    if n == secret_number then
        engine.custom_scene(2)
    else
        engine.custom_scene(3)
    end
end

engine.load_scene(scene_intro)
engine.run()
