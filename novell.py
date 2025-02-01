import getpass
from engine import LogicEngine, RenderEngine

eng = LogicEngine()
eng.register_scenes()
eng.render()
getpass.getpass(prompt="")
eng.next_scene()
eng.render()
getpass.getpass(prompt="")
eng.exit()