#!/usr/bin/env python3
"""
Enhanced Item System - Улучшенная система предметов
Отвечает за управление предметами с поддержкой спецэффектов
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..effects.effect_system import Effect, SpecialEffect, DamageType, EffectCategory, TargetType

logger = logging.getLogger(__name__)

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class ItemSlot(Enum):
    """Слоты для экипировки"""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    NECKLACE = "necklace"
    CLOAK = "cloak"

@dataclass
class ItemStats:
    """Статистика предмета"""
    strength: float = 0.0
    agility: float = 0.0
    intelligence: float = 0.0
    vitality: float = 0.0
    armor: float = 0.0
    magic_resistance: float = 0.0
    damage: float = 0.0
    attack_speed: float = 0.0
    crit_chance: float = 0.0
    crit_multiplier: float = 1.0
    movement_speed: float = 0.0
    health_regen: float = 0.0
    mana_regen: float = 0.0

class BaseItem:
    """Базовый класс для всех предметов"""
    
    def __init__(
        self,
        name: str,
        description: str,
        item_type: ItemType,
        rarity: ItemRarity = ItemRarity.COMMON,
        required_level: int = 0,
        sell_price: int = 0,
        buy_price: int = 0,
        weight: float = 0.0,
        stackable: bool = False,
        max_stack: int = 1
    ):
        self.name = name
        self.description = description
        self.item_type = item_type
        self.rarity = rarity
        self.required_level = required_level
        self.sell_price = sell_price
        self.buy_price = buy_price
        self.weight = weight
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = 1
        self.durability = 100.0
        self.max_durability = 100.0
        
        # Уникальный идентификатор
        self.item_id = f"{item_type.value}_{name.lower().replace(' ', '_')}_{id(self)}"
        
        # Флаги
        self.is_equipped = False
        self.is_bound = False
        self.is_soulbound = False
        
        logger.debug(f"Создан предмет: {name} ({item_type.value})")
    
    def get_rarity_color(self) -> Tuple[int, int, int]:
        """Возвращает цвет редкости предмета"""
        rarity_colors = {
            ItemRarity.COMMON: (200, 200, 200),      # Серый
            ItemRarity.UNCOMMON: (0, 255, 0),        # Зеленый
            ItemRarity.RARE: (0, 100, 255),          # Синий
            ItemRarity.EPIC: (200, 0, 255),          # Фиолетовый
            ItemRarity.LEGENDARY: (255, 165, 0),     # Оранжевый
            ItemRarity.MYTHIC: (255, 0, 0)           # Красный
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))
    
    def can_equip(self, character_level: int) -> bool:
        """Проверяет, можно ли экипировать предмет"""
        if character_level < self.required_level:
            return False
        return True
    
    def use(self, user: Any) -> Dict[str, Any]:
        """Использует предмет"""
        return {"success": False, "message": "Этот предмет нельзя использовать"}
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает информацию о предмете"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.item_type.value,
            "rarity": self.rarity.value,
            "required_level": self.required_level,
            "durability": f"{self.durability:.1f}/{self.max_durability:.1f}",
            "sell_price": self.sell_price,
            "weight": self.weight
        }

class Weapon(BaseItem):
    """Класс оружия с поддержкой спецэффектов"""
    
    def __init__(
        self,
        name: str,
        description: str,
        damage: float,
        attack_speed: float,
        damage_type: DamageType,
        slot: ItemSlot,
        special_effects: Optional[List[SpecialEffect]] = None,
        **kwargs
    ):
        super().__init__(name, description, ItemType.WEAPON, **kwargs)
        
        self.damage = damage
        self.attack_speed = attack_speed
        self.damage_type = damage_type
        self.slot = slot
        self.special_effects = special_effects or []
        
        # Дополнительные параметры оружия
        self.range = 1.0
        self.accuracy = 0.95
        self.break_chance = 0.01
        
        logger.debug(f"Создано оружие: {name} (урон: {damage}, скорость: {attack_speed})")
    
    def apply_special_effects(self, source: Any, target: Any, trigger_type: str = "on_hit"):
        """Применяет специальные эффекты оружия при срабатывании триггера"""
        for special_effect in self.special_effects:
            if special_effect.can_trigger(source, target, trigger_type):
                special_effect.trigger(source, target)
                logger.debug(f"Сработал спецэффект {special_effect.effect.name} для {self.name}")
    
    def get_attack_damage(self, user_stats: Optional[Dict[str, float]] = None) -> float:
        """Рассчитывает урон атаки с учетом статов пользователя"""
        total_damage = self.damage
        
        if user_stats:
            # Применяем бонусы от статов
            if "strength" in user_stats:
                total_damage += user_stats["strength"] * 0.5
            if "agility" in user_stats:
                total_damage += user_stats["agility"] * 0.3
        
        return total_damage
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает расширенную информацию об оружии"""
        info = super().get_info()
        info.update({
            "damage": self.damage,
            "attack_speed": self.attack_speed,
            "damage_type": self.damage_type.value,
            "slot": self.slot.value,
            "range": self.range,
            "accuracy": self.accuracy,
            "special_effects_count": len(self.special_effects)
        })
        return info

class Armor(BaseItem):
    """Класс брони"""
    
    def __init__(
        self,
        name: str,
        description: str,
        slot: ItemSlot,
        armor_value: float,
        magic_resistance: float = 0.0,
        stats: Optional[ItemStats] = None,
        special_effects: Optional[List[SpecialEffect]] = None,
        **kwargs
    ):
        super().__init__(name, description, ItemType.ARMOR, **kwargs)
        
        self.slot = slot
        self.armor_value = armor_value
        self.magic_resistance = magic_resistance
        self.stats = stats or ItemStats()
        self.special_effects = special_effects or []
        
        logger.debug(f"Создана броня: {name} (броня: {armor_value}, сопротивление: {magic_resistance})")
    
    def get_protection(self) -> Dict[str, float]:
        """Возвращает защитные характеристики брони"""
        return {
            "armor": self.armor_value,
            "magic_resistance": self.magic_resistance
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает расширенную информацию о броне"""
        info = super().get_info()
        info.update({
            "slot": self.slot.value,
            "armor": self.armor_value,
            "magic_resistance": self.magic_resistance,
            "special_effects_count": len(self.special_effects)
        })
        return info

class Accessory(BaseItem):
    """Класс аксессуаров с поддержкой спецэффектов"""
    
    def __init__(
        self,
        name: str,
        description: str,
        slot: ItemSlot,
        stats: Optional[ItemStats] = None,
        special_effects: Optional[List[SpecialEffect]] = None,
        **kwargs
    ):
        super().__init__(name, description, ItemType.ACCESSORY, **kwargs)
        
        self.slot = slot
        self.stats = stats or ItemStats()
        self.special_effects = special_effects or []
        
        logger.debug(f"Создан аксессуар: {name} (слот: {slot.value})")
    
    def apply_special_effects(self, source: Any, target: Any, trigger_type: str):
        """Применяет специальные эффекты аксессуара"""
        for special_effect in self.special_effects:
            if special_effect.can_trigger(source, target, trigger_type):
                special_effect.trigger(source, target)
                logger.debug(f"Сработал спецэффект {special_effect.effect.name} для {self.name}")
    
    def get_stats_bonus(self) -> Dict[str, float]:
        """Возвращает бонусы к статам от аксессуара"""
        stats_dict = {}
        for stat_name, stat_value in self.stats.__dict__.items():
            if stat_value != 0:
                stats_dict[stat_name] = stat_value
        return stats_dict
    
    def get_info(self) -> Dict[str, Any]:
        """Возвращает расширенную информацию об аксессуаре"""
        info = super().get_info()
        info.update({
            "slot": self.slot.value,
            "stats_bonus": self.get_stats_bonus(),
            "special_effects_count": len(self.special_effects)
        })
        return info

class Consumable(BaseItem):
    """Класс расходуемых предметов"""
    
    def __init__(
        self,
        name: str,
        description: str,
        effects: List[Effect],
        cooldown: float = 0.0,
        **kwargs
    ):
        super().__init__(name, description, ItemType.CONSUMABLE, stackable=True, **kwargs)
        
        self.effects = effects
        self.cooldown = cooldown
        self.last_use_time = 0.0
        
        logger.debug(f"Создан расходуемый предмет: {name} (эффектов: {len(effects)})")
    
    def can_use(self, user: Any) -> bool:
        """Проверяет, можно ли использовать предмет"""
        import time
        current_time = time.time()
        
        if self.cooldown > 0 and (current_time - self.last_use_time) < self.cooldown:
            return False
        
        return True
    
    def use(self, user: Any) -> Dict[str, Any]:
        """Использует расходуемый предмет"""
        if not self.can_use(user):
            return {"success": False, "message": "Предмет на кулдауне"}
        
        try:
            # Применяем все эффекты
            for effect in self.effects:
                if effect.category == EffectCategory.INSTANT:
                    effect.apply_instant(self, user)
                else:
                    if hasattr(user, 'add_effect'):
                        user.add_effect(effect, self)
            
            # Уменьшаем количество
            self.quantity -= 1
            if self.quantity <= 0:
                # Предмет полностью израсходован
                pass
            
            # Обновляем время использования
            import time
            self.last_use_time = time.time()
            
            logger.debug(f"Использован предмет: {self.name}")
            return {"success": True, "message": f"Использован {self.name}"}
            
        except Exception as e:
            logger.error(f"Ошибка использования предмета {self.name}: {e}")
            return {"success": False, "message": f"Ошибка использования: {e}"}

class ItemFactory:
    """Фабрика для создания предметов"""
    
    @staticmethod
    def create_fire_sword() -> Weapon:
        """Создает огненный меч с улучшенными спецэффектами"""
        from ..effects.effect_system import Effect, SpecialEffect, DamageType, EffectCategory, TargetType
        
        # Эффект поджига
        burn_effect = Effect(
            name="Ожог",
            category=EffectCategory.DOT,
            value=8,
            damage_types=[DamageType.FIRE],
            duration=5,
            period=1,
            scaling={"intelligence": 0.2},
            target_type=TargetType.ENEMY
        )
        
        # Эффект взрыва
        explosion_effect = Effect(
            name="Огненный взрыв",
            category=EffectCategory.INSTANT,
            value=15,
            damage_types=[DamageType.FIRE],
            scaling={"intelligence": 0.3},
            target_type=TargetType.AREA,
            area={"shape": "circle", "radius": 2},
            ignore_resistance=0.2
        )
        
        # Специальные эффекты оружия
        special_effects = [
            SpecialEffect(
                chance=0.25,
                effect=burn_effect,
                trigger_condition="on_hit",
                cooldown=0,
                max_procs=0
            ),
            SpecialEffect(
                chance=0.1,
                effect=explosion_effect,
                trigger_condition="on_crit",
                cooldown=5,
                max_procs=1
            )
        ]
        
        return Weapon(
            name="Пылающий клинок",
            description="Меч, наполненный мощью огненного элементаля",
            damage=35,
            attack_speed=1.1,
            damage_type=DamageType.FIRE,
            slot=ItemSlot.MAIN_HAND,
            rarity=ItemRarity.EPIC,
            special_effects=special_effects,
            required_level=15
        )
    
    @staticmethod
    def create_lightning_ring() -> Accessory:
        """Создает кольцо молний со спецэффектами"""
        from ..effects.effect_system import Effect, SpecialEffect, DamageType, EffectCategory, TargetType
        
        # Эффект цепи молний
        chain_effect = Effect(
            name="Цепь молний",
            category=EffectCategory.INSTANT,
            value=20,
            damage_types=[DamageType.LIGHTNING],
            scaling={"intelligence": 0.5},
            target_type=TargetType.ENEMY,
            projectile_speed=10
        )
        
        # Эффект проводимости
        conductivity_effect = Effect(
            name="Проводимость",
            category=EffectCategory.DEBUFF,
            value={"lightning_resistance": -0.2},
            duration=4,
            target_type=TargetType.ENEMY
        )
        
        # Специальные эффекты аксессуара
        special_effects = [
            SpecialEffect(
                chance=0.15,
                effect=chain_effect,
                trigger_condition="on_spell_cast",
                cooldown=3,
                max_procs=0
            ),
            SpecialEffect(
                chance=0.3,
                effect=conductivity_effect,
                trigger_condition="on_lightning_damage",
                cooldown=0,
                max_procs=0
            )
        ]
        
        stats = ItemStats(intelligence=15)
        
        return Accessory(
            name="Кольцо грозы",
            description="Увеличивает мощь заклинаний молнии",
            slot=ItemSlot.RING_1,
            stats=stats,
            rarity=ItemRarity.RARE,
            special_effects=special_effects,
            required_level=10
        )
    
    @staticmethod
    def create_health_potion() -> Consumable:
        """Создает зелье здоровья"""
        from ..effects.effect_system import Effect, EffectCategory, TargetType
        
        heal_effect = Effect(
            name="Восстановление здоровья",
            category=EffectCategory.INSTANT,
            value=50,
            target_type=TargetType.SELF
        )
        
        return Consumable(
            name="Зелье здоровья",
            description="Восстанавливает 50 очков здоровья",
            effects=[heal_effect],
            cooldown=0,
            rarity=ItemRarity.COMMON,
            sell_price=10,
            buy_price=25
        )

class EnhancedItemSystem:
    """Улучшенная система управления предметами"""
    
    def __init__(self):
        self.items: Dict[str, BaseItem] = {}
        self.equipped_items: Dict[ItemSlot, BaseItem] = {}
        self.item_templates: Dict[str, BaseItem] = {}
        
        logger.info("Улучшенная система предметов инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы предметов"""
        try:
            self._setup_item_templates()
            
            logger.info("Улучшенная система предметов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации улучшенной системы предметов: {e}")
            return False
    
    def _setup_item_templates(self):
        """Настройка шаблонов предметов"""
        # Создаем базовые предметы
        self.item_templates["fire_sword"] = ItemFactory.create_fire_sword()
        self.item_templates["lightning_ring"] = ItemFactory.create_lightning_ring()
        self.item_templates["health_potion"] = ItemFactory.create_health_potion()
        
        logger.debug(f"Создано {len(self.item_templates)} шаблонов предметов")
    
    def create_item(self, template_name: str) -> Optional[BaseItem]:
        """Создает предмет по шаблону"""
        if template_name not in self.item_templates:
            logger.warning(f"Шаблон предмета {template_name} не найден")
            return None
        
        template = self.item_templates[template_name]
        
        # Создаем копию предмета
        if isinstance(template, Weapon):
            return Weapon(
                name=template.name,
                description=template.description,
                damage=template.damage,
                attack_speed=template.attack_speed,
                damage_type=template.damage_type,
                slot=template.slot,
                special_effects=template.special_effects.copy() if template.special_effects else [],
                rarity=template.rarity,
                required_level=template.required_level,
                sell_price=template.sell_price,
                buy_price=template.buy_price
            )
        elif isinstance(template, Accessory):
            return Accessory(
                name=template.name,
                description=template.description,
                slot=template.slot,
                stats=template.stats,
                special_effects=template.special_effects.copy() if template.special_effects else [],
                rarity=template.rarity,
                required_level=template.required_level,
                sell_price=template.sell_price,
                buy_price=template.buy_price
            )
        elif isinstance(template, Consumable):
            return Consumable(
                name=template.name,
                description=template.description,
                effects=template.effects.copy() if template.effects else [],
                cooldown=template.cooldown,
                rarity=template.rarity,
                required_level=template.required_level,
                sell_price=template.sell_price,
                buy_price=template.buy_price
            )
        
        return None
    
    def equip_item(self, item: BaseItem, character: Any) -> bool:
        """Экипирует предмет на персонажа"""
        if not hasattr(item, 'slot'):
            logger.warning(f"Предмет {item.name} не имеет слота для экипировки")
            return False
        
        # Проверяем уровень персонажа
        if hasattr(character, 'level') and not item.can_equip(character.level):
            logger.warning(f"Недостаточный уровень для экипировки {item.name}")
            return False
        
        # Снимаем предыдущий предмет в этом слоте
        if item.slot in self.equipped_items:
            self.unequip_item(item.slot, character)
        
        # Экипируем новый предмет
        self.equipped_items[item.slot] = item
        item.is_equipped = True
        
        # Применяем эффекты предмета к персонажу
        self._apply_item_effects(item, character, True)
        
        logger.info(f"Предмет {item.name} экипирован в слот {item.slot.value}")
        return True
    
    def unequip_item(self, slot: ItemSlot, character: Any) -> Optional[BaseItem]:
        """Снимает предмет с персонажа"""
        if slot not in self.equipped_items:
            return None
        
        item = self.equipped_items[slot]
        item.is_equipped = False
        
        # Убираем эффекты предмета с персонажа
        self._apply_item_effects(item, character, False)
        
        del self.equipped_items[slot]
        
        logger.info(f"Предмет {item.name} снят со слота {slot.value}")
        return item
    
    def _apply_item_effects(self, item: BaseItem, character: Any, is_equipping: bool):
        """Применяет или убирает эффекты предмета"""
        multiplier = 1 if is_equipping else -1
        
        if hasattr(item, 'stats') and hasattr(character, 'modify_stats'):
            # Применяем бонусы к статам
            for stat_name, stat_value in item.stats.__dict__.items():
                if stat_value != 0:
                    character.modify_stats(stat_name, stat_value * multiplier)
        
        if hasattr(item, 'special_effects'):
            # Регистрируем или убираем спецэффекты
            for special_effect in item.special_effects:
                if is_equipping:
                    # Регистрируем триггер
                    pass  # Будет реализовано через систему триггеров
                else:
                    # Убираем триггер
                    pass
    
    def get_equipped_item(self, slot: ItemSlot) -> Optional[BaseItem]:
        """Возвращает экипированный предмет в указанном слоте"""
        return self.equipped_items.get(slot)
    
    def get_all_equipped_items(self) -> Dict[ItemSlot, BaseItem]:
        """Возвращает все экипированные предметы"""
        return self.equipped_items.copy()
    
    def cleanup(self):
        """Очистка системы предметов"""
        logger.info("Очистка улучшенной системы предметов...")
        self.items.clear()
        self.equipped_items.clear()
        self.item_templates.clear()
