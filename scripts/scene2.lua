function modify_scene(scene)
    local last_choice = engine.get_choice("choice_rand")
    if last_choice == "42" then
      scene.text = "ты выбрал 42! офигенный выбор!"
    else
      scene.text = "странный выбор... но ладно."
    end
    return scene
end