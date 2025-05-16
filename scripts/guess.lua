function post_scene(scene)
    local guess = engine.get_choice("player_guess")
    local secret = engine.get_choice("secret_number")
    if guess == secret then
        engine.custom_scene(2)
    else
        engine.custom_scene(3)
    end
    return scene
end
