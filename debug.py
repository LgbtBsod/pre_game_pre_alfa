# debug.py

from ursina import Text

class DebugText:
    def __init__(self):
        self.text = Text(text='', position=(-0.85, 0.45), scale=1.5, color=color.white)

    def update(self, info):
        self.text.text = f'FPS: {info}'