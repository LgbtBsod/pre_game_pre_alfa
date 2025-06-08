# level.py
from ursina import scene
from ursina import Ursina, Entity, camera, Vec2, Vec3, time, Text, window, color, destroy
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
from helper.settings import *
from tile import Tile
from player import Player
from debug import DebugText
from helper.support import import_csv_layout, import_folder
from weapon import Weapon
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from anim_tile import AnimTile
from equip.equipment import Equipment
from UI.ui import UI
from effect import Effect
from save.save_load import save, load
import json

class Level(Entity):
    def __init__(self):
        super().__init__(parent=scene)

        # Инициализация
        self.player = None
        self.game_paused = False
        self.visible_sprites = []
        self.obstacle_sprites = []
        self.attack_sprites = []
        self.attackable_sprites = []

        # UI
        self.ui = UI()
        self.menu = UpgradeMenu(self.player) if self.player else None

        # Статистика игрока
        self.equip = Equipment(self.current_stats)

        # Частицы и магия
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # Создание карты
        self.create_map()

        # FPS отладка
        self.debug_text = DebugText()

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('map/test._block.csv'),
            'tree': import_csv_layout('map/test._tree.csv'),
            'lake': import_csv_layout('map/test._lake.csv'),
            'entities': import_csv_layout('map/test._entities.csv'),
        }

        graphics = {
            'tree': import_folder('graphics/Tree'),
            'lakes': import_folder('graphics/water/lake')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = -row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        elif style == 'tree':
                            random_grass_image = choice(graphics['tree'])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                 'tree', random_grass_image)
                        elif style == 'lake':
                            AnimTile((x, y), [self.visible_sprites, self.obstacle_sprites], 'lake')
                        elif style == 'entities':
                            if col == '164':
                                self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites,
                                                     self.create_attack, self.destroy_attack, self.create_magic)
                                self.menu = UpgradeMenu(self.player)
                            else:
                                monster_name = {
                                    '160': 'warrior',
                                    '131': 'necromancer'
                                }.get(col, 'squid')
                                Enemy(monster_name, (x, y),
                                      [self.visible_sprites, self.attackable_sprites],
                                      self.obstacle_sprites, self.damage_player,
                                      self.trigger_death_particles, self.add_exp, self.drops)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        elif style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if hasattr(self, 'current_attack') and self.current_attack:
            destroy(self.current_attack)
        self.current_attack = None

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            if self.player.health <= 0:
                self.player.health = 0
            self.player.vulnerable = False
            self.player.hurt_time = time.time()
            self.animation_player.create_particles(attack_type, self.player.position, self.visible_sprites)

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def drops(self, item):
        from equip.chance import chance
        if chance('70%'):
            self.equip.add_to_bag(item)

    def add_exp(self, amount):
        self.player.exp += amount

    def current_stats(self, modify):
        base_stats = self.player.base
        must_be = {}
        for item in modify:
            if item in ['crit_rate', 'crit_chance']:
                must_be[item] = modify[item]
            else:
                must_be[item] = modify[item] + 1
        for item in must_be:
            if item in ['crit_rate', 'crit_chance']:
                self.player.current_stats[item] = must_be[item] + base_stats[item]
            else:
                self.player.current_stats[item] *= must_be[item]
        must_be.clear()

    def run(self):
        # Обновление видимых спрайтов
        for sprite in self.visible_sprites:
            sprite.update()

        # Обновление UI
        self.ui.display(self.player)

        # Проверка паузы
        if held_keys['escape']:
            self.toggle()

        # Меню улучшений
        if self.game_paused:
            self.menu.show()
        else:
            self.menu.hide()

        # Логика атаки
            for attack_sprite in self.attack_sprites:
                colliders = attack_sprite.intersects().entities
                for target in colliders:
                    if hasattr(target, 'sprite_type') and target.sprite_type == 'tree':
                        pos = target.position
                        offset = Vec2(0, 75)
                        for _ in range(3, 6):
                            self.animation_player.create_grass_particles(pos - offset, self.visible_sprites)
                        destroy(target)
                    elif hasattr(target, 'get_damage'):
                        target.get_damage(self.player, attack_sprite.sprite_type)

    def toggle(self):
        self.game_paused = not self.game_paused

    def save_load(self):
        pos = list(self.player.position)
        exp = self.player.exp
        item = self.equip.equip
        save(pos, item, exp)

    def update(self):
        self.run()
        self.debug_text.text = f'FPS: {int(1 / (time.dt or 0.001))}'
        self.debug_text.update(int(1 / (time.dt or 0.001)))