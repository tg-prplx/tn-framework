function modify_scene(scene)
    if not scene.choices or #scene.choices == 0 then
      scene.text = "у тебя вообще нет выбора, как ты сюда попал?"
      return scene
    end
    
    local last_choice = scene.choices[#scene.choices].picked_path
    if last_choice == 42 then
      scene.text = "ты выбрал 42! офигенный выбор!"
    else
      scene.text = "странный выбор... но ладно."
    end
    
    return scene
end