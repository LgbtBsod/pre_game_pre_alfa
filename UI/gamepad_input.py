# gamepad_input.py

from ursina import Ursina, GamePad
from player.player import LikePlayer


class GamePadHandler:
    def __init__(self, player):
        self.player = player
        self.gamepad = GamePad()
        self.setup_controls()

    def setup_controls(self):
        self.gamepad.on_button_down('a', self.on_a_press)
        self.gamepad.on_button_down('x', self.on_x_press)
        self.gamepad.on_button_down('y', self.on_y_press)

    def on_a_press(self):
        print('Нажата A')
        self.player.try_activate_effect('dash')

    def on_x_press(self):
        print('Нажата X')
        self.player.try_activate_effect('power_ring')

    def on_y_press(self):
        print('Нажата Y')
        self.player.try_activate_effect('heal')