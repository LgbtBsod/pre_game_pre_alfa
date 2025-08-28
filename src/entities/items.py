#!/usr/bin/env python3
"""
Базовые классы предметов для игры
"""

from panda3d.core import Vec3, Point3
from direct.actor.Actor import Actor
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

from ..systems.effects.effect_system import Effect, EffectCategory
from ..systems.effects.effect_system import EffectVisuals, EffectBalance

@dataclass
class ItemRequirements:
    """Требования для использования предмета"""
    level: int = 1
    strength: int = 0
    intelligence: int = 0
    agility: int = 0
    special_skills: List[str] = field(default_factory=list)

class Item:
    """Базовый класс для всех предметов в игре"""
    
    def __init__(self, name: str, item_type: str, rarity: str = "common", stack_size: int = 1):
        self.name = name
        self.item_type = item_type  # weapon, armor, consumable, etc.
        self.rarity = rarity
        self.stack_size = stack_size
        self.quantity = 1
        self.effects: List[Effect] = []
        self.requirements = ItemRequirements()
        self.visual_model = None  # 3D модель предмета
        self.icon = ""  # Путь к иконке
        self.description = ""
        self.value = 0  # Стоимость предмета
        
    def use(self, user) -> bool:
        """Использовать предмет"""
        if self.check_requirements(user):
            for effect in self.effects:
                effect.apply(user, user)
            return True
        return False
        
    def check_requirements(self, user) -> bool:
        """Проверить требования для использования"""
        if hasattr(user, 'level') and user.level < self.requirements.level:
            return False
        if hasattr(user, 'strength') and user.strength < self.requirements.strength:
            return False
        if hasattr(user, 'intelligence') and user.intelligence < self.requirements.intelligence:
            return False
        if hasattr(user, 'agility') and user.agility < self.requirements.agility:
            return False
        return True
        
    def create_visual(self, position: Vec3):
        """Создать визуальное представление предмета в мире"""
        if self.visual_model:
            item_node = self.visual_model.copyTo(render)
            item_node.setPos(position)
            return item_node
        return None
    
    def is_consumable(self) -> bool:
        """Проверить, является ли предмет расходником"""
        return self.item_type == "consumable"
    
    def can_stack_with(self, other: 'Item') -> bool:
        """Проверить, можно ли складывать с другим предметом"""
        return (self.name == other.name and 
                self.item_type == other.item_type and
                self.rarity == other.rarity)
    
    def add_effect(self, effect: Effect):
        """Добавить эффект к предмету"""
        self.effects.append(effect)
    
    def remove_effect(self, effect: Effect):
        """Удалить эффект с предмета"""
        if effect in self.effects:
            self.effects.remove(effect)

class Weapon(Item):
    """Класс оружия"""
    
    def __init__(self, name: str, damage: int, damage_type: str, attack_speed: float = 1.0):
        super().__init__(name, "weapon")
        self.damage = damage
        self.damage_type = damage_type
        self.attack_speed = attack_speed
        self.range = 1.0
        self.durability = 100
        self.max_durability = 100
        
        # Создаем эффект урона
        damage_effect = Effect(
            name=f"Урон от {name}",
            category=EffectCategory.DAMAGE,
            value={"damage": damage, "damage_type": damage_type},
            visuals=EffectVisuals(
                particle_effect="weapon_swing",
                sound_effect="weapon_hit"
            ),
            tags=["weapon", "damage"]
        )
        self.add_effect(damage_effect)
    
    def attack(self, user, target) -> bool:
        """Атака оружием"""
        if self.durability <= 0:
            return False
        
        # Применяем эффект урона
        for effect in self.effects:
            effect.apply(target, user)
        
        # Уменьшаем прочность
        self.durability = max(0, self.durability - 1)
        return True
    
    def repair(self, amount: int):
        """Починить оружие"""
        self.durability = min(self.max_durability, self.durability + amount)

class Armor(Item):
    """Класс брони"""
    
    def __init__(self, name: str, armor_type: str, defense: int):
        super().__init__(name, "armor")
        self.armor_type = armor_type  # head, chest, legs, etc.
        self.defense = defense
        self.weight = 1.0
        self.movement_penalty = 0.0
        
        # Создаем эффект защиты
        defense_effect = Effect(
            name=f"Защита от {name}",
            category=EffectCategory.BUFF,
            value={"defense": defense},
            tags=["armor", "defense"]
        )
        self.add_effect(defense_effect)
    
    def apply_defense(self, user):
        """Применить защиту"""
        for effect in self.effects:
            effect.apply(user, user)

class Consumable(Item):
    """Класс расходников"""
    
    def __init__(self, name: str, effect: Effect, cooldown: float = 0):
        super().__init__(name, "consumable")
        self.effects.append(effect)
        self.cooldown = cooldown
        self.last_used = 0
        self.uses_remaining = 1
        
    def can_use(self, current_time: float) -> bool:
        """Проверить, можно ли использовать"""
        if self.uses_remaining <= 0:
            return False
        if self.cooldown > 0 and (current_time - self.last_used) < self.cooldown:
            return False
        return True
        
    def use(self, user, current_time: float = 0) -> bool:
        """Использовать расходник"""
        if not self.can_use(current_time):
            return False
        
        # Применяем эффекты
        for effect in self.effects:
            effect.apply(user, user)
        
        # Обновляем время использования
        self.last_used = current_time
        
        # Уменьшаем количество использований
        self.uses_remaining -= 1
        
        return True

class Material(Item):
    """Класс материалов для крафтинга"""
    
    def __init__(self, name: str, material_type: str, quality: str = "normal"):
        super().__init__(name, "material")
        self.material_type = material_type
        self.quality = quality
        self.crafting_value = 1
        
    def get_crafting_bonus(self) -> float:
        """Получить бонус к крафтингу"""
        quality_bonuses = {
            "poor": 0.5,
            "normal": 1.0,
            "good": 1.5,
            "excellent": 2.0,
            "masterwork": 3.0
        }
        return quality_bonuses.get(self.quality, 1.0)

# Фабрика предметов
class ItemFactory:
    """Фабрика для создания предметов"""
    
    @staticmethod
    def create_weapon(weapon_type: str, level: int = 1) -> Weapon:
        """Создать оружие по типу и уровню"""
        weapons = {
            "sword": {"damage": 10, "damage_type": "physical", "attack_speed": 1.2},
            "axe": {"damage": 15, "damage_type": "physical", "attack_speed": 0.8},
            "bow": {"damage": 8, "damage_type": "physical", "attack_speed": 1.5, "range": 5.0},
            "staff": {"damage": 12, "damage_type": "magical", "attack_speed": 1.0}
        }
        
        if weapon_type not in weapons:
            weapon_type = "sword"
        
        weapon_data = weapons[weapon_type].copy()
        weapon_data["damage"] += (level - 1) * 2
        
        weapon = Weapon(f"{weapon_type.title()} +{level}", 
                       weapon_data["damage"], 
                       weapon_data["damage_type"], 
                       weapon_data["attack_speed"])
        
        if "range" in weapon_data:
            weapon.range = weapon_data["range"]
        
        return weapon
    
    @staticmethod
    def create_consumable(consumable_type: str, level: int = 1) -> Consumable:
        """Создать расходник по типу и уровню"""
        consumables = {
            "health_potion": {
                "effect": Effect(
                    name="Восстановление здоровья",
                    category=EffectCategory.HEAL,
                    value={"health": 50 + level * 10},
                    visuals=EffectVisuals(
                        particle_effect="heal_sparkle",
                        sound_effect="potion_use"
                    ),
                    tags=["heal", "consumable"]
                )
            },
            "mana_potion": {
                "effect": Effect(
                    name="Восстановление маны",
                    category=EffectCategory.HEAL,
                    value={"mana": 50 + level * 10},
                    visuals=EffectVisuals(
                        particle_effect="mana_restore",
                        sound_effect="potion_use"
                    ),
                    tags=["mana", "consumable"]
                )
            }
        }
        
        if consumable_type not in consumables:
            consumable_type = "health_potion"
        
        consumable_data = consumables[consumable_type]
        return Consumable(f"{consumable_type.replace('_', ' ').title()} +{level}", 
                         consumable_data["effect"])
