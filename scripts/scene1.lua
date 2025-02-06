function modify_scene(scene)
    scene.text = "эээ"
    return scene
end


function post_scene(scene)
  if not scene.choices then
    scene.choices = {}
  end
  table.insert(scene.choices, { picked_path = tonumber(io.read()) })
  engine.await_input = false
  return scene
end
