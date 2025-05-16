function modify_scene(scene)
    if not engine.get_choice("secret_number") then
        math.randomseed(os.time())
        local secret = tostring(math.random(1, 5))
        engine.add_choice("secret_number", secret)
    end
    return scene
end

function post_scene(scene)
    io.write("Введи число от 1 до 5: ")
    local guess = io.read()
    engine.add_choice("player_guess", guess)
    engine.await_input = false
    return scene
end
