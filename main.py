# main.py

from ursina import Ursina, camera
from level import Level


app = Ursina()
camera.orthographic = True
camera.fov = 10
app.development_mode = False  # ← Отключаем hot-reload и Blender-зависимости

game = Level()


def update():
    game.run()


app.run()