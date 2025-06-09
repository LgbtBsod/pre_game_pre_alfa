# player/player.py

from base_player import BasePlayer
from helper.settings import WEAPON_DATA


class LikePlayer(BasePlayer):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None):
        super().__init__(
            position=position,
            groups=groups,
            obstacle_sprites=obstacle_sprites
        )

        # Базовые статы персонажа
        self.base_stats.update({
            'health': 150,
            'energy': 80,
            'attack': 15,
            'magic': 4,
            'speed': 1,
            'strength': 3,
            'agility': 2,
            'stamina': 200,
            'hp_regen': 0.2,
            'crit_chance': 10,
            'crit_rate': 120
        })

    
        # Уровень, опыт и стоимость улучшений
        self.exp = 900
        self.upgrade_cost = {stat: 100 for stat in self.base_stats}

        # Оружие
        self.weapon_index = 0
        self.can_switch_weapon = True
        self.switch_duration_cooldown = 0.2
        self.weapon_data = WEAPON_DATA  # Подгружаем из JSON
        self.weapon = list(self.weapon_data.keys())[self.weapon_index]

        # Магия
        self.magic_index = 0
        self.can_switch_magic = True
        self.magic_data = {
            'heal': {'graphic': 'graphics/particles/heal/heal.png', 'strength': 20, 'cost': 10},
            'flame': {'graphic': 'graphics/particles/flame/fire.png', 'strength': 10, 'cost': 20}
        }
        self.magic = list(self.magic_data.keys())[self.magic_index]

        # Анимация
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.import_player_assets()

    def import_player_assets(self):
        """Импортируем анимации игрока"""
        from helper.support import import_folder
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }

        for animation in self.animations:
            folder_path = f'graphics/player/{animation}'
            frames_count = len(os.listdir(folder_path))
            self.animations[animation] = [
                Animation(f'{folder_path}/{i}', autoplay=False, loop=False, fps=12, scale=1, enabled=False)
                for i in range(frames_count)
            ]

    def input(self):
        """Логика ввода для игрока"""
        if not self.attacking:
            self.direction = Vec2(
                int(held_keys['d']) - int(held_keys['a']),
                int(held_keys['s']) - int(held_keys['w'])
            )
            if self.direction.length() > 0:
                self.direction = self.direction.normalized()

            # Атака
            if held_keys['space']:
                self.attacking = True
                self.attack_time = time.time()
                self.create_attack()

            # Магия
            if held_keys['control left']:
                self.attacking = True
                self.attack_time = time.time()
                style = list(self.magic_data.keys())[self.magic_index]
                strength = list(self.magic_data.values())[self.magic_index]['strength'] + self.current_stats['magic']
                cost = list(self.magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            # Переключение оружия
            if held_keys['q'] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = time.time()
                self.weapon_index = (self.weapon_index + 1) % len(self.weapon_data)
                self.weapon = list(self.weapon_data.keys())[self.weapon_index]

            # Переключение магии
            if held_keys['e'] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = time.time()
                self.magic_index = (self.magic_index + 1) % len(self.magic_data)
                self.magic = list(self.magic_data.keys())[self.magic_index]

    def get_damage(self, attack_type='sword'):
        weapon_damage = self.weapon_data[self.weapon]['damage']
        damage = weapon_damage * self.current_stats['strength']

        if chance(self.current_stats['crit_chance']):
            modify = convert_to_num(self.current_stats['crit_rate'])
            print('Crit!', damage * modify)
            return damage * modify
        else:
            return damage

    def get_full_magic_damage(self):
        base_damage = self.current_stats['magic']
        spell_damage = self.magic_data[self.magic]['strength']
        return spell_damage * self.power

    def update_current_stats(self):
        """Обновляем текущие статы на основе базовых"""
        self.current_stats = self.base_stats.copy()
        self.health = self.current_stats['health']
        self.energy = self.current_stats['energy']
        self.speed = self.current_stats['speed'] * self.current_stats['agility']