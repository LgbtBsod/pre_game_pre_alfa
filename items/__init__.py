"""Модуль предметов и экипировки."""

try:
    from .item import Item
    from .weapon import Weapon, WeaponGenerator
    __all__ = ['Item', 'Weapon', 'WeaponGenerator']
except ImportError:
    # Если модули не найдены, создаем заглушки
    class Item:
        def __init__(self, item_id: str = "unknown"):
            self.item_id = item_id
            self.name = "Unknown Item"
    
    class Weapon(Item):
        def __init__(self, weapon_id: str = "unknown"):
            super().__init__(weapon_id)
            self.damage = 10
    
    class WeaponGenerator:
        @staticmethod
        def generate_weapon(level: int = 1):
            return Weapon(f"weapon_lvl_{level}")
    
    __all__ = ['Item', 'Weapon', 'WeaponGenerator']
