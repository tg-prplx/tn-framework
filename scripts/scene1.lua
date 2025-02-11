function modify_scene(scene)
    scene.show_tab = false
    return scene
end

function post_scene(scene)
  io.write("Введите число: ")
  engine.add_choice("ch", io.read())
  engine.await_input = false
  return scene
end
