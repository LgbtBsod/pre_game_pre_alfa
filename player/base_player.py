# player/base_player.py

from ursina import Entity, Vec2, time
from effects.buff_manager import BuffManager
from equip.equipment import Equipment
from equip.equipment import ItemsData
from typing import Dict, List


class BasePlayer(Entity):
    def __init__(self, position=(0, 0), groups=None, obstacle_sprites=None):
        if isinstance(position, (list, tuple)) and len(position) >= 2:
            pos = Vec2(position[0], position[1])
        elif isinstance(position, Vec2):
            pos = position
        else:
            pos = Vec2(0, 0)
        self.animations = {}  # Убедитесь, что это словарь с объектами анимаций
        self.current_animation = None   
        super().__init__(
            model='quad',
            texture='graphics/player/down_idle/down.png',
            position=pos,
            z=-1,
            collider='box'
        )

        # Базовые статы
        self.base_stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 2,
            'speed': 1,
            'strength': 2,
            'agility': 2,
            'stamina': 200,
            'hp_regen': 0.1,
            'crit_chance': 10,
            'crit_rate': 1.2,
            'defense': 5
        }

        self.current_stats = self.base_stats.copy()

        # Уровень и опыт
        self.level = 1
        self.exp = 0
        self.exp_to_level = 1000

        # Экипировка и эффекты
        self.reactive_effects = {}
        self.active_effects = {}
        self.inventory: List[str] = []  # Хранит только имена предметов
        self.equipment = Equipment(self)
        self.items_data = ItemsData()
        
        # Баффы
        self.buff_manager = BuffManager(self)

        # Состояние игрока
        self.attacking = False
        self.can_move = True
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 0.5

        # Движение
        self.direction = Vec2(0, 0)
        self.speed = self.current_stats['speed'] * self.current_stats['agility']
        self.obstacle_sprites = obstacle_sprites or []

    def move(self):
        """Движение персонажа"""
        if not self.can_move:
            return

        self.position += self.direction * self.speed * time.dt

    def take_damage(self, amount, attack_type):
        """Получение урона с учётом защиты и реактивных эффектов"""
        for name, func in self.reactive_effects.items():
            amount = func(player=self, amount=amount, attack_type=attack_type)

        self.current_stats['health'] = max(
            self.current_stats['health'] - amount,
            0
        )
        print(f'[Урон] Получено: {amount}, осталось здоровья: {self.current_stats["health"]}')

        if not self.vulnerable:
            return

        self.vulnerable = False
        self.hurt_time = time.time()

    def update(self):
        """Обновление состояния игрока"""
        # Удаляем вызов super().update() так как Entity не имеет этого метода
        self.move()
        
        # Проверка неуязвимости после получения урона
        if not self.vulnerable and time.time() - self.hurt_time > self.invulnerability_duration:
            self.vulnerable = True

    def to_dict(self):
        """Сохраняет состояние игрока в словарь для сериализации через JSON"""
        return {
            'position': list(self.position),
            'base_stats': self.base_stats,
            'current_stats': self.current_stats,
            'level': self.level,
            'exp': self.exp,
            'equip': self.equip,
            'weapon_index': getattr(self, 'weapon_index', 0),
            'magic_index': getattr(self, 'magic_index', 0)
        }

    @classmethod
    def from_dict(cls, data):
        """Восстанавливает игрока из словаря"""
        position = data.get('position', [0, 0])
        
        if isinstance(position, (list, tuple)) and len(position) >= 2:
            pos = Vec2(position[0], position[1])
        elif isinstance(position, Vec2):
            pos = position
        else:
            pos = Vec2(0, 0)

        instance = cls(position=pos, groups=[], obstacle_sprites=[])

        instance.base_stats = data.get('base_stats', instance.base_stats)
        instance.current_stats = data.get('current_stats', instance.base_stats.copy())
        instance.level = data.get('level', 1)
        instance.exp = data.get('exp', 0)
        instance.equip = data.get('equip', [])
        instance.weapon_index = data.get('weapon_index', 0)
        instance.magic_index = data.get('magic_index', 0)

        instance.update_current_stats()
        instance.update_status()

        return instance

    def update_current_stats(self):
        """Обновляет текущие статы после загрузки"""
        self.current_stats = self.base_stats.copy()

    def update_status(self):
        """Можно использовать для обновления статуса или анимации"""
        pass
    
    def toggle_inventory(self):
        """Переключает видимость инвентаря"""
        if hasattr(self, 'inventory_ui'):
            self.inventory_ui.enabled = not self.inventory_ui.enabled
            print('[Input] Инвентарь:', 'открыт' if self.inventory_ui.enabled else 'закрыт')
        else:
            print('[Warning] Inventory UI not initialized')

    def input(self, key=None):
        """Обработка ввода"""
        if key == 'i':
            self.toggle_inventory()
            
    def add_item(self, item_name: str) -> bool:
        """Добавляет предмет в инвентарь"""
        if not self.items_data.item_exists(item_name):
            return False
            
        self.inventory.append(item_name)
        return True
    
    def remove_item(self, item_name: str) -> bool:
        """Удаляет предмет из инвентаря"""
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        """Проверяет наличие предмета"""
        return item_name in self.inventory