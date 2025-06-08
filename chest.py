# chest.py

from ursina import Entity, color, destroy
from interactive import UseSprite
import random
from equip.chance import chance


class Chest(UseSprite):
    def __init__(self, position, group=None):
        super().__init__(position=position, groups=group)
        self.sprite_type = 'chest'
        self.texture = 'graphics/player/down_idle/down.png'  # Текстура сундука
        self.opened = False

    def loot_in_chest(self, amount=3):
        """Создание лута при открытии сундука"""
        loot = []
        while len(loot) < amount:
            for x in range(random.randint(0, 5)):
                loot.append('exp')
            for y in range(random.randint(0, 10)):
                loot.append('gold')

            if chance('50%'):
                loot.append('common')
            elif chance('20%'):
                loot.append('rare')
            elif chance('10%'):
                loot.append('legendary')
            elif chance('1%'):
                loot.append('eternal')

        print("Полученный лут:", loot)

    def update(self):
        from main import player  # Предполагаем, что игрок доступен через main
        if not self.obstacle_sprites:
            self.obstacle_sprites = [e for e in scene.entities if hasattr(e, 'sprite_type') and e.sprite_type == 'tree']

        distance = self.get_distance(player)

        if distance < 50 and not self.opened:
            if held_keys['e']:  # Открытие сундука по нажатию E
                self.opened = True
                self.loot_in_chest()
                destroy(self)  # Уничтожаем сундук после открытия
                