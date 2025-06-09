# debug.py

from ursina import Text, color, camera


class DebugText:
    def __init__(self):
        self.text = Text(
            text='',
            position=(-0.85, 0.45),
            scale=1.5,
            color=color.white,
            parent=camera
        )

    def update(self, info):
        self.text.text = f'FPS: {int(info)}'