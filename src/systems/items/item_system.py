#!/usr/bin/env python3
"""
Item System - Система предметов с поддержкой специальных эффектов
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from ..effects.effect_system import SpecialEffect, Effect, EffectVisuals, EffectBalance, DamageType

logger = logging.getLogger(__name__)

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"

@dataclass
class ItemStats:
    """Статистики предмета"""
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0
    armor: int = 0
    magic_resistance: int = 0
    damage: int = 0
    attack_speed: float = 1.0
    critical_chance: float = 0.0
    critical_damage: float = 1.5
    health: int = 0
    mana: int = 0
    health_regen: float = 0.0
    mana_regen: float = 0.0

class BaseItem:
    """Базовый класс для всех предметов"""
    
    def __init__(self, name: str, description: str, item_type: ItemType, rarity: ItemRarity):
        self.name = name
        self.description = description
        self.item_type = item_type
        self.rarity = rarity
        self.special_effects: List[SpecialEffect] = []
        self.required_level: int = 1
        self.stack_size: int = 1
        self.max_stack: int = 1
        self.icon: Optional[str] = None
        self.model: Optional[str] = None
        
    def add_special_effect(self, effect: SpecialEffect):
        """Добавляет специальный эффект к предмету"""
        self.special_effects.append(effect)
    
    def get_effects_for_trigger(self, trigger_type) -> List[SpecialEffect]:
        """Возвращает эффекты для определенного триггера"""
        return [effect for effect in self.special_effects if effect.trigger_condition == trigger_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация предмета"""
        return {
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "special_effects": [effect.to_dict() for effect in self.special_effects],
            "required_level": self.required_level,
            "stack_size": self.stack_size,
            "max_stack": self.max_stack,
            "icon": self.icon,
            "model": self.model
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseItem':
        """Десериализация предмета"""
        item = cls(
            name=data["name"],
            description=data["description"],
            item_type=ItemType(data["item_type"]),
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем специальные эффекты
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            item.add_special_effect(effect)
        
        # Восстанавливаем остальные свойства
        item.required_level = data.get("required_level", 1)
        item.stack_size = data.get("stack_size", 1)
        item.max_stack = data.get("max_stack", 1)
        item.icon = data.get("icon")
        item.model = data.get("model")
        
        return item

class Weapon(BaseItem):
    """Класс оружия"""
    
    def __init__(self, name: str, description: str, damage: int, attack_speed: float, 
                 damage_type: DamageType, slot: str, rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(name, description, ItemType.WEAPON, rarity)
        self.damage = damage
        self.attack_speed = attack_speed
        self.damage_type = damage_type
        self.slot = slot
        self.range: float = 1.0
        self.durability: int = 100
        self.max_durability: int = 100
        
    def calculate_damage(self, wielder_stats: Dict[str, Any]) -> float:
        """Рассчитывает урон оружия с учетом характеристик владельца"""
        base_damage = self.damage
        
        # Модификаторы от характеристик
        strength_bonus = wielder_stats.get("strength", 0) * 0.1
        agility_bonus = wielder_stats.get("agility", 0) * 0.05
        
        total_damage = (base_damage + strength_bonus + agility_bonus) * self.attack_speed
        
        return total_damage
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация оружия"""
        data = super().to_dict()
        data.update({
            "damage": self.damage,
            "attack_speed": self.attack_speed,
            "damage_type": self.damage_type.value,
            "slot": self.slot,
            "range": self.range,
            "durability": self.durability,
            "max_durability": self.max_durability
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Weapon':
        """Десериализация оружия"""
        weapon = cls(
            name=data["name"],
            description=data["description"],
            damage=data["damage"],
            attack_speed=data["attack_speed"],
            damage_type=DamageType(data["damage_type"]),
            slot=data["slot"],
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем специальные эффекты
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            weapon.add_special_effect(effect)
        
        # Восстанавливаем остальные свойства
        weapon.required_level = data.get("required_level", 1)
        weapon.range = data.get("range", 1.0)
        weapon.durability = data.get("durability", 100)
        weapon.max_durability = data.get("max_durability", 100)
        
        return weapon

class Armor(BaseItem):
    """Класс брони"""
    
    def __init__(self, name: str, description: str, armor_value: int, slot: str, 
                 rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(name, description, ItemType.ARMOR, rarity)
        self.armor_value = armor_value
        self.slot = slot
        self.stats = ItemStats()
        self.durability: int = 100
        self.max_durability: int = 100
        
    def calculate_armor(self, wearer_stats: Dict[str, Any]) -> float:
        """Рассчитывает защиту брони с учетом характеристик владельца"""
        base_armor = self.armor_value
        
        # Модификаторы от характеристик
        vitality_bonus = wearer_stats.get("vitality", 0) * 0.2
        
        total_armor = base_armor + vitality_bonus
        
        return total_armor
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация брони"""
        data = super().to_dict()
        data.update({
            "armor_value": self.armor_value,
            "slot": self.slot,
            "stats": self.stats.__dict__,
            "durability": self.durability,
            "max_durability": self.max_durability
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Armor':
        """Десериализация брони"""
        armor = cls(
            name=data["name"],
            description=data["description"],
            armor_value=data["armor_value"],
            slot=data["slot"],
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем специальные эффекты
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            armor.add_special_effect(effect)
        
        # Восстанавливаем статистики
        if "stats" in data:
            armor.stats = ItemStats(**data["stats"])
        
        # Восстанавливаем остальные свойства
        armor.required_level = data.get("required_level", 1)
        armor.durability = data.get("durability", 100)
        armor.max_durability = data.get("max_durability", 100)
        
        return armor

class Accessory(BaseItem):
    """Класс аксессуаров"""
    
    def __init__(self, name: str, description: str, slot: str, stats: Dict[str, Union[int, float]], 
                 rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(name, description, ItemType.ACCESSORY, rarity)
        self.slot = slot
        self.stats = stats
        
    def apply_stats(self, character_stats: Dict[str, Any]):
        """Применяет статистики аксессуара к персонажу"""
        for stat_name, stat_value in self.stats.items():
            if stat_name in character_stats:
                character_stats[stat_name] += stat_value
    
    def remove_stats(self, character_stats: Dict[str, Any]):
        """Удаляет статистики аксессуара с персонажа"""
        for stat_name, stat_value in self.stats.items():
            if stat_name in character_stats:
                character_stats[stat_name] -= stat_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация аксессуара"""
        data = super().to_dict()
        data.update({
            "slot": self.slot,
            "stats": self.stats
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Accessory':
        """Десериализация аксессуара"""
        accessory = cls(
            name=data["name"],
            description=data["description"],
            slot=data["slot"],
            stats=data["stats"],
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем специальные эффекты
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            accessory.add_special_effect(effect)
        
        # Восстанавливаем остальные свойства
        accessory.required_level = data.get("required_level", 1)
        
        return accessory

class Consumable(BaseItem):
    """Класс расходуемых предметов"""
    
    def __init__(self, name: str, description: str, effects: List[Effect], 
                 rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(name, description, ItemType.CONSUMABLE, rarity)
        self.effects = effects
        self.max_stack = 99  # Расходуемые предметы можно складывать
        
    def use(self, target: Any):
        """Использует расходуемый предмет"""
        for effect in self.effects:
            if effect.duration == 0:
                effect.apply_instant(self, target)
            else:
                if hasattr(target, 'add_effect'):
                    target.add_effect(effect, self)
        
        # Уменьшаем количество предметов
        self.stack_size -= 1
        
        logger.info(f"Использован предмет: {self.name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация расходуемого предмета"""
        data = super().to_dict()
        data.update({
            "effects": [effect.to_dict() for effect in self.effects]
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Consumable':
        """Десериализация расходуемого предмета"""
        effects = [Effect.from_dict(effect_data) for effect_data in data.get("effects", [])]
        
        consumable = cls(
            name=data["name"],
            description=data["description"],
            effects=effects,
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем специальные эффекты
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            consumable.add_special_effect(effect)
        
        # Восстанавливаем остальные свойства
        consumable.required_level = data.get("required_level", 1)
        consumable.stack_size = data.get("stack_size", 1)
        
        return consumable

class ItemFactory:
    """Фабрика для создания предметов"""
    
    @staticmethod
    def create_enhanced_fire_sword() -> Weapon:
        """Создает огненный меч с улучшенными спецэффектами"""
        from ..effects.effect_system import Effect, EffectVisuals, EffectBalance, TriggerType
        
        # Эффект поджига
        burn_effect = Effect(
            name="Ожог",
            category="dot",
            value=8,
            damage_types=[DamageType.FIRE],
            duration=5,
            period=1,
            scaling={"intelligence": 0.2},
            target_type="enemy",
            visuals=EffectVisuals(
                particle_effect="fire_burn",
                sound_effect="fire_crackle",
                color_overlay=(255, 100, 0, 0.3)
            ),
            tags=["fire", "dot"]
        )
        
        # Эффект взрыва
        explosion_effect = Effect(
            name="Огненный взрыв",
            category="instant",
            value=15,
            damage_types=[DamageType.FIRE],
            scaling={"intelligence": 0.3},
            target_type="area",
            area={"shape": "circle", "radius": 2},
            ignore_resistance=0.2,
            visuals=EffectVisuals(
                particle_effect="fire_explosion",
                sound_effect="explosion",
                screen_shake=0.5
            ),
            tags=["fire", "aoe"]
        )
        
        # Специальные эффекты оружия
        special_effects = [
            SpecialEffect(
                chance=0.25,
                effect=burn_effect,
                trigger_condition=TriggerType.ON_HIT,
                cooldown=0,
                max_procs=0,
                track_stats=True
            ),
            SpecialEffect(
                chance=0.1,
                effect=explosion_effect,
                trigger_condition=TriggerType.ON_CRIT,
                cooldown=5,
                max_procs=1,
                track_stats=True
            )
        ]
        
        weapon = Weapon(
            name="Пылающий клинок",
            description="Меч, наполненный мощью огненного элементаля",
            damage=35,
            attack_speed=1.1,
            damage_type=DamageType.FIRE,
            slot="main_hand",
            rarity=ItemRarity.EPIC
        )
        
        for effect in special_effects:
            weapon.add_special_effect(effect)
        
        weapon.required_level = 15
        
        return weapon
    
    @staticmethod
    def create_lightning_ring() -> Accessory:
        """Создает кольцо молний со спецэффектами"""
        from ..effects.effect_system import Effect, EffectVisuals, TriggerType, ElementCondition
        
        # Эффект цепи молний
        chain_effect = Effect(
            name="Цепь молний",
            category="instant",
            value=20,
            damage_types=[DamageType.LIGHTNING],
            scaling={"intelligence": 0.5},
            target_type="enemy",
            visuals=EffectVisuals(
                particle_effect="lightning_chain",
                sound_effect="lightning_strike"
            ),
            tags=["lightning", "chain"]
        )
        
        # Эффект проводимости
        conductivity_effect = Effect(
            name="Проводимость",
            category="debuff",
            value={"lightning_resistance": -0.2},
            duration=4,
            target_type="enemy",
            visuals=EffectVisuals(
                particle_effect="lightning_aura",
                color_overlay=(100, 100, 255, 0.2)
            ),
            tags=["lightning", "debuff"]
        )
        
        # Специальные эффекты аксессуара
        special_effects = [
            SpecialEffect(
                chance=0.15,
                effect=chain_effect,
                trigger_condition=TriggerType.ON_SPELL_CAST,
                cooldown=3,
                max_procs=0,
                track_stats=True
            ),
            SpecialEffect(
                chance=0.3,
                effect=conductivity_effect,
                trigger_condition=TriggerType.ON_ELEMENT_DAMAGE,
                cooldown=0,
                max_procs=0,
                conditions=[ElementCondition(DamageType.LIGHTNING)],
                track_stats=True
            )
        ]
        
        accessory = Accessory(
            name="Кольцо грозы",
            description="Увеличивает мощь заклинаний молнии",
            slot="ring",
            stats={"intelligence": 15, "spell_power": 0.1},
            rarity=ItemRarity.RARE
        )
        
        for effect in special_effects:
            accessory.add_special_effect(effect)
        
        accessory.required_level = 10
        
        return accessory
