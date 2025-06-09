# main.py

from ursina import Ursina, camera, time, window
from ursina.prefabs.hot_reloader import HotReloader
from level import Level
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase


HotReloader().enabled = False  # ← отключаем hot_reload

app = Ursina()
camera.orthographic = True
camera.fov = 10
window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = 'Zelda Like RPG'
window.borderless = False
window.fullscreen = False

game = Level()
app.run()