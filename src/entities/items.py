#!/usr/bin/env python3
"""
Базовые классы предметов для игры
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ..core.constants import ItemType, ItemRarity, ItemCategory, DamageType, StatType, ItemSlot

logger = logging.getLogger(__name__)

@dataclass
class ItemEffect:
    """Эффект предмета"""
    effect_id: str
    effect_type: str
    magnitude: float
    duration: float = 0.0
    chance: float = 1.0
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ItemRequirement:
    """Требования для использования предмета"""
    level: int = 1
    stats: Dict[StatType, int] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)

class Item:
    """Базовый класс для всех предметов в игре"""
    
    def __init__(self, 
                 item_id: str,
                 name: str,
                 description: str,
                 item_type: ItemType,
                 rarity: ItemRarity = ItemRarity.COMMON,
                 stack_size: int = 1,
                 weight: float = 0.0,
                 value: int = 0):
        
        self.item_id = item_id
        self.name = name
        self.description = description
        self.item_type = item_type
        self.rarity = rarity
        self.stack_size = stack_size
        self.weight = weight
        self.value = value
        
        # Базовые свойства
        self.quantity = 1
        self.durability = 1.0
        self.quality = 1.0
        self.level = 1
        
        # Эффекты и требования
        self.effects: List[ItemEffect] = []
        self.requirements = ItemRequirement()
        
        # Визуальные свойства
        self.icon = ""
        self.model = ""
        self.texture = ""
        self.visual_effects = []
        
        # Звуковые эффекты
        self.use_sound = ""
        self.equip_sound = ""
        self.unequip_sound = ""
        
        # Флаги
        self.is_consumable = False
        self.is_equippable = False
        self.is_tradeable = True
        self.is_droppable = True
        self.is_unique = False
        
        # Метаданные
        self.created_time = time.time()
        self.last_used = 0.0
        self.usage_count = 0
        
        logger.debug(f"Создан предмет: {name} ({item_id})")
    
    def can_use(self, user: Dict[str, Any]) -> bool:
        """Проверка возможности использования предмета"""
        try:
            # Проверка требований
            if not self._check_requirements(user):
                return False
            
            # Проверка количества
            if self.quantity <= 0:
                return False
            
            # Проверка прочности
            if self.durability <= 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности использования предмета {self.item_id}: {e}")
            return False
    
    def use(self, user: Dict[str, Any], target: Optional[Dict[str, Any]] = None) -> bool:
        """Использование предмета"""
        try:
            if not self.can_use(user):
                return False
            
            # Применение эффектов
            success = self._apply_effects(user, target)
            
            if success:
                # Обновление статистики использования
                self.last_used = time.time()
                self.usage_count += 1
                
                # Уменьшение количества для расходников
                if self.is_consumable:
                    self.quantity -= 1
                
                # Уменьшение прочности
                self._reduce_durability()
                
                logger.debug(f"Предмет {self.name} использован игроком {user.get('name', 'unknown')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка использования предмета {self.item_id}: {e}")
            return False
    
    def can_equip(self, user: Dict[str, Any], slot: ItemSlot) -> bool:
        """Проверка возможности экипировки"""
        try:
            if not self.is_equippable:
                return False
            
            if not self._check_requirements(user):
                return False
            
            # Проверка совместимости слота
            if not self._check_slot_compatibility(slot):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки экипировки предмета {self.item_id}: {e}")
            return False
    
    def equip(self, user: Dict[str, Any], slot: ItemSlot) -> bool:
        """Экипировка предмета"""
        try:
            if not self.can_equip(user, slot):
                return False
            
            # Применение эффектов экипировки
            success = self._apply_equip_effects(user)
            
            if success:
                logger.debug(f"Предмет {self.name} экипирован в слот {slot.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка экипировки предмета {self.item_id}: {e}")
            return False
    
    def unequip(self, user: Dict[str, Any]) -> bool:
        """Снятие предмета"""
        try:
            # Удаление эффектов экипировки
            success = self._remove_equip_effects(user)
            
            if success:
                logger.debug(f"Предмет {self.name} снят")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка снятия предмета {self.item_id}: {e}")
            return False
    
    def _check_requirements(self, user: Dict[str, Any]) -> bool:
        """Проверка требований для использования"""
        try:
            # Проверка уровня
            user_level = user.get('level', 0)
            if user_level < self.requirements.level:
                return False
            
            # Проверка характеристик
            for stat, required_value in self.requirements.stats.items():
                user_stat = user.get(stat.value, 0)
                if user_stat < required_value:
                    return False
            
            # Проверка навыков
            user_skills = user.get('skills', [])
            for skill in self.requirements.skills:
                if skill not in user_skills:
                    return False
            
            # Проверка предметов
            user_items = user.get('items', [])
            for item in self.requirements.items:
                if item not in user_items:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований предмета {self.item_id}: {e}")
            return False
    
    def _apply_effects(self, user: Dict[str, Any], target: Optional[Dict[str, Any]] = None) -> bool:
        """Применение эффектов предмета"""
        try:
            target = target or user
            
            for effect in self.effects:
                # Проверка шанса срабатывания
                if effect.chance < 1.0:
                    import random
                    if random.random() > effect.chance:
                        continue
                
                # Применение эффекта
                self._apply_single_effect(effect, target, user)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов предмета {self.item_id}: {e}")
            return False
    
    def _apply_single_effect(self, effect: ItemEffect, target: Dict[str, Any], source: Dict[str, Any]):
        """Применение одного эффекта"""
        try:
            if effect.effect_type == "stat_modifier":
                stat_name = effect.conditions.get('stat_name')
                if stat_name and stat_name in target:
                    target[stat_name] += effect.magnitude
            
            elif effect.effect_type == "heal":
                current_health = target.get('health', 0)
                max_health = target.get('max_health', 0)
                target['health'] = min(max_health, current_health + effect.magnitude)
            
            elif effect.effect_type == "damage":
                current_health = target.get('health', 0)
                target['health'] = max(0, current_health - effect.magnitude)
            
            elif effect.effect_type == "buff":
                # Добавление временного баффа
                buffs = target.get('buffs', [])
                buffs.append({
                    'effect_id': effect.effect_id,
                    'magnitude': effect.magnitude,
                    'duration': effect.duration,
                    'start_time': time.time()
                })
                target['buffs'] = buffs
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта {effect.effect_id}: {e}")
    
    def _apply_equip_effects(self, user: Dict[str, Any]) -> bool:
        """Применение эффектов экипировки"""
        try:
            # Применяем эффекты экипировки
            for effect in self.effects:
                if effect.effect_type == "equip_bonus":
                    self._apply_single_effect(effect, user, user)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов экипировки {self.item_id}: {e}")
            return False
    
    def _remove_equip_effects(self, user: Dict[str, Any]) -> bool:
        """Удаление эффектов экипировки"""
        try:
            # Удаляем эффекты экипировки
            for effect in self.effects:
                if effect.effect_type == "equip_bonus":
                    # Обратный эффект
                    reverse_effect = ItemEffect(
                        effect_id=f"reverse_{effect.effect_id}",
                        effect_type="equip_bonus",
                        magnitude=-effect.magnitude
                    )
                    self._apply_single_effect(reverse_effect, user, user)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффектов экипировки {self.item_id}: {e}")
            return False
    
    def _check_slot_compatibility(self, slot: ItemSlot) -> bool:
        """Проверка совместимости со слотом"""
        # Базовая проверка - можно переопределить в наследниках
        if self.item_type == ItemType.WEAPON and slot == ItemSlot.WEAPON:
            return True
        elif self.item_type == ItemType.ARMOR:
            armor_slots = [ItemSlot.ARMOR_HEAD, ItemSlot.ARMOR_CHEST, ItemSlot.ARMOR_LEGS, ItemSlot.ARMOR_FEET]
            return slot in armor_slots
        elif self.item_type == ItemType.ACCESSORY:
            accessory_slots = [ItemSlot.ACCESSORY_1, ItemSlot.ACCESSORY_2, ItemSlot.ACCESSORY_3]
            return slot in accessory_slots
        
        return False
    
    def _reduce_durability(self):
        """Уменьшение прочности предмета"""
        if self.durability > 0:
            # Уменьшаем прочность на 1% за использование
            self.durability = max(0, self.durability - 0.01)
    
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о предмете"""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type.value,
            'rarity': self.rarity.value,
            'stack_size': self.stack_size,
            'quantity': self.quantity,
            'weight': self.weight,
            'value': self.value,
            'durability': self.durability,
            'quality': self.quality,
            'level': self.level,
            'is_consumable': self.is_consumable,
            'is_equippable': self.is_equippable,
            'usage_count': self.usage_count
        }

class Weapon(Item):
    """Класс оружия"""
    
    def __init__(self, 
                 item_id: str,
                 name: str,
                 description: str,
                 damage: int,
                 damage_type: DamageType = DamageType.PHYSICAL,
                 attack_speed: float = 1.0,
                 range: float = 1.0,
                 **kwargs):
        
        super().__init__(item_id, name, description, ItemType.WEAPON, **kwargs)
        
        self.damage = damage
        self.damage_type = damage_type
        self.attack_speed = attack_speed
        self.range = range
        
        self.is_equippable = True
        
        # Специальные свойства оружия
        self.critical_chance = 0.05
        self.critical_multiplier = 2.0
        self.accuracy = 0.95
        self.durability_loss_per_use = 0.01

class Armor(Item):
    """Класс брони"""
    
    def __init__(self,
                 item_id: str,
                 name: str,
                 description: str,
                 armor_value: int,
                 armor_type: str = "physical",
                 slot: ItemSlot = ItemSlot.ARMOR_CHEST,
                 **kwargs):
        
        super().__init__(item_id, name, description, ItemType.ARMOR, **kwargs)
        
        self.armor_value = armor_value
        self.armor_type = armor_type
        self.slot = slot
        
        self.is_equippable = True
        
        # Специальные свойства брони
        self.resistance_bonuses = {}
        self.movement_penalty = 0.0
        self.durability_loss_per_hit = 0.005

class Consumable(Item):
    """Класс расходника"""
    
    def __init__(self,
                 item_id: str,
                 name: str,
                 description: str,
                 effect_type: str,
                 effect_magnitude: float,
                 **kwargs):
        
        super().__init__(item_id, name, description, ItemType.CONSUMABLE, **kwargs)
        
        self.effect_type = effect_type
        self.effect_magnitude = effect_magnitude
        
        self.is_consumable = True
        
        # Добавляем эффект
        effect = ItemEffect(
            effect_id=f"{item_id}_effect",
            effect_type=effect_type,
            magnitude=effect_magnitude
        )
        self.effects.append(effect)

class Accessory(Item):
    """Класс аксессуара"""
    
    def __init__(self,
                 item_id: str,
                 name: str,
                 description: str,
                 **kwargs):
        
        super().__init__(item_id, name, description, ItemType.ACCESSORY, **kwargs)
        
        self.is_equippable = True
        
        # Специальные свойства аксессуаров
        self.special_abilities = []
        self.set_bonus = None
