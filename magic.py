# magic.py

from ursina import Entity, Vec2, time
import random


class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups=None):
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost
            if player.health >= player.current_stats['health']:
                player.health = player.current_stats['health']
            self.animation_player.create_particles('aura', player.position, groups)
            self.animation_player.create_particles('heal', player.position, groups)

    def flame(self, player, cost, groups=None):
        if player.energy >= cost:
            player.energy -= cost

            direction = {
                'right': Vec2(1, 0),
                'left': Vec2(-1, 0),
                'up': Vec2(0, -1),
                'down': Vec2(0, 1)
            }.get(player.status.split('_')[0], Vec2(0, 0))

            for i in range(1, 6):
                offset = random.uniform(-TILESIZE // 3, TILESIZE // 3)
                if direction.x != 0:  # горизонтальное направление
                    x = player.x + direction.x * i * TILESIZE + offset
                    y = player.y + offset
                else:  # вертикальное направление
                    x = player.x + offset
                    y = player.y + direction.y * i * TILESIZE + offset
                self.animation_player.create_particles('flame', (x, y), groups)