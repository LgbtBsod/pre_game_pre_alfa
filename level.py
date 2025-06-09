# level.py

from ursina import Ursina, camera, time
from helper.settings import GAME_SETTINGS
from player.player import LikePlayer
from enemy import Enemy
from anim_tile import AnimTile
from tile import Tile
from UI.ui import UI
from equip.equipment import Equipment
from save.save_load import load, save


class Level:
    def __init__(self):
        self.visible_sprites = []
        self.obstacle_sprites = []
        self.attackable_sprites = []

        self.player = LikePlayer(position=(0, 0), obstacle_sprites=self.obstacle_sprites)
        self.ui = UI()
        self.equip = Equipment(self.player)

        self.create_map()

    def create_map(self):
        from helper.support import import_csv_layout

        layouts = {
            'boundary': import_csv_layout('assets/map/test._block.csv'),
            'tree': import_csv_layout('assets/map/test._tree.csv'),
            'entities': import_csv_layout('assets/map/test._entities.csv')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * GAME_SETTINGS['TILESIZE']
                    y = -row_index * GAME_SETTINGS['TILESIZE']

                    if col == '-1':
                        continue

                    if style == 'boundary':
                        Tile((x, y), [self.obstacle_sprites], 'invisible')
                    elif style == 'tree':
                        Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'tree')
                    elif style == 'entities':
                        if col == '164':  # ID игрока
                            self.player = LikePlayer((x, y), groups=[self.visible_sprites], obstacle_sprites=self.obstacle_sprites)
                        else:
                            monster_name = {
                                '160': 'warrior',
                                '131': 'necromancer'
                            }.get(col, 'squid')
                            Enemy(monster_name, (x, y), [self.visible_sprites, self.attackable_sprites],
                                  self.obstacle_sprites, self.damage_player, self.trigger_death_particles, self.add_exp, self.drops)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            if self.player.health <= 0:
                self.player.health = 0
            self.player.vulnerable = False
            self.player.hurt_time = time.time()

    def trigger_death_particles(self, pos, particle_type):
        pass

    def add_exp(self, amount):
        self.player.exp += amount

    def drops(self, item):
        print("Получено:", item)

    def run(self):
        # Обновление всех спрайтов
        for sprite in self.visible_sprites:
            sprite.update()
        self.ui.display(self.player)

    def toggle(self):
        pass