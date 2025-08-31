from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import os
import re
import sys
import time

#!/usr/bin/env python3
"""Base Entity - Базовая сущность для всех игровых объектов
Объединяет системы: характеристики, инвентарь, эмоции, гены, память, навыки"""

logger = logging.getLogger(__name__)

# = ОСНОВНЫЕ ТИПЫ И ПЕРЕЧИСЛЕНИЯ

class EntityType(Enum):
    """Типы сущностей"""
    PLAYER = "player"
    NPC = "npc"
    ENEMY = "enemy"
    BOSS = "boss"
    MUTANT = "mutant"
    ANIMAL = "animal"
    CREATURE = "creature"
    OBJECT = "object"

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    PSYCHIC = "psychic"
    TRUE = "true"

class EmotionType(Enum):
    """Типы эмоций"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONFUSED = "confused"
    SUSPICIOUS = "suspicious"

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    TOOL = "tool"
    CURRENCY = "currency"
    QUEST = "quest"
    SPECIAL = "special"

class ItemSlot(Enum):
    """Слоты экипировки"""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    WAIST = "waist"
    NECK = "neck"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    TRINKET_1 = "trinket_1"
    TRINKET_2 = "trinket_2"

# = БАЗОВЫЕ КОНСТАНТЫ

BASE_STATS = {
    "health": 100,
    "mana": 50,
    "stamina": 100,
    "attack": 10,
    "defense": 5,
    "speed": 1.0,
    "range": 1.0,
    "strength": 10,
    "agility": 10,
    "intelligence": 10,
    "constitution": 10,
    "wisdom": 10,
    "charisma": 10
}

PROBABILITY_CONSTANTS = {
    "base_luck": 0.05,
    "base_critical_chance": 0.05,
    "base_dodge_chance": 0.05,
    "base_block_chance": 0.05
}

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class EntityStats:
    """Базовые характеристики сущности"""
    # Основные характеристики
    health: int = BASE_STATS["health"]
    max_health: int = BASE_STATS["health"]
    mana: int = BASE_STATS["mana"]
    max_mana: int = BASE_STATS["mana"]
    stamina: int = BASE_STATS["stamina"]
    max_stamina: int = BASE_STATS["stamina"]
    
    # Боевые характеристики
    attack: int = BASE_STATS["attack"]
    defense: int = BASE_STATS["defense"]
    speed: float = BASE_STATS["speed"]
    attack_speed: float = 1.0
    range: float = BASE_STATS["range"]
    
    # Атрибуты
    strength: int = BASE_STATS["strength"]
    agility: int = BASE_STATS["agility"]
    intelligence: int = BASE_STATS["intelligence"]
    constitution: int = BASE_STATS["constitution"]
    wisdom: int = BASE_STATS["wisdom"]
    charisma: int = BASE_STATS["charisma"]
    luck: float = PROBABILITY_CONSTANTS["base_luck"]
    
    # Сопротивления
    resistances: Dict[DamageType, float] = field(default_factory=dict)
    
    # Опыт и уровень
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100

@dataclass
class EntityMemory:
    """Память сущности"""
    entity_id: str
    memories: List[Dict[str, Any]] = field(default_factory=list)
    max_memories: int = 100
    learning_rate: float = 0.5
    last_memory_update: float = field(default_factory=time.time)

@dataclass
class EntityInventory:
    """Инвентарь сущности"""
    entity_id: str
    items: List[Any] = field(default_factory=list)
    max_items: int = 50
    max_weight: float = 100.0
    current_weight: float = 0.0
    equipped_items: Dict[ItemSlot, str] = field(default_factory=dict)

@dataclass
class EntityEmotion:
    """Эмоциональное состояние сущности"""
    entity_id: str
    current_emotion: EmotionType = EmotionType.NEUTRAL
    emotion_intensity: float = 0.5  # 0.0 - 1.0
    mood: float = 0.0  # -1.0 до 1.0
    stress_level: float = 0.0  # 0.0 - 1.0
    emotional_stability: float = 0.5  # 0.0 - 1.0
    emotion_history: List[Dict[str, Any]] = field(default_factory=list)
    emotion_triggers: Dict[str, float] = field(default_factory=dict)

@dataclass
class EntitySkills:
    """Навыки сущности"""
    entity_id: str
    skills: Dict[str, int] = field(default_factory=dict)  # skill_id: level
    skill_points: int = 0
    max_skill_level: int = 100
    skill_experience: Dict[str, int] = field(default_factory=dict)
    skill_cooldowns: Dict[str, float] = field(default_factory=dict)

@dataclass
class EntityEffects:
    """Эффекты сущности"""
    entity_id: str
    active_effects: List[Dict[str, Any]] = field(default_factory=list)
    passive_effects: List[Dict[str, Any]] = field(default_factory=list)
    temporary_effects: List[Dict[str, Any]] = field(default_factory=list)
    effect_duration: Dict[str, float] = field(default_factory=dict)

class BaseEntity:
    """Базовая сущность для всех игровых объектов"""
    
    def __init__(self, entity_id: str, entity_type: EntityType, name: str = ""):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name or f"{entity_type.value}_{entity_id}"
        
        # Основные компоненты
        self.stats = EntityStats()
        self.memory = EntityMemory(entity_id=entity_id)
        self.inventory = EntityInventory(entity_id=entity_id)
        self.emotion = EntityEmotion(entity_id=entity_id)
        self.skills = EntitySkills(entity_id=entity_id)
        self.effects = EntityEffects(entity_id=entity_id)
        
        # Позиция и состояние
        self.position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.is_active: bool = True
        self.is_alive: bool = True
        self.is_visible: bool = True
        
        # Время создания
        self.created_at: float = time.time()
        self.last_update: float = time.time()
        
        # События
        self.on_damage: Optional[Callable] = None
        self.on_heal: Optional[Callable] = None
        self.on_death: Optional[Callable] = None
        self.on_level_up: Optional[Callable] = None
        
        logger.info(f"Создана сущность {self.name} (ID: {entity_id})")
    
    def take_damage(self, damage: int, damage_type: DamageType = DamageType.PHYSICAL, 
                   source: Optional[str] = None) -> int:
        """Получение урона"""
        try:
            # Применение сопротивлений
            resistance = self.stats.resistances.get(damage_type, 0.0)
            actual_damage = int(damage * (1.0 - resistance))
            
            # Применение урона
            old_health = self.stats.health
            self.stats.health = max(0, self.stats.health - actual_damage)
            
            # Проверка смерти
            if self.stats.health <= 0 and self.is_alive:
                self.die()
            
            # Вызов callback
            if self.on_damage:
                self.on_damage(self, actual_damage, damage_type, source)
            
            logger.debug(f"{self.name} получил {actual_damage} урона (тип: {damage_type.value})")
            return actual_damage
            
        except Exception as e:
            logger.error(f"Ошибка применения урона к {self.name}: {e}")
            return 0
    
    def heal(self, amount: int, source: Optional[str] = None) -> int:
        """Восстановление здоровья"""
        try:
            old_health = self.stats.health
            self.stats.health = min(self.stats.max_health, self.stats.health + amount)
            actual_heal = self.stats.health - old_health
            
            # Вызов callback
            if self.on_heal:
                self.on_heal(self, actual_heal, source)
            
            logger.debug(f"{self.name} восстановил {actual_heal} здоровья")
            return actual_heal
            
        except Exception as e:
            logger.error(f"Ошибка восстановления здоровья {self.name}: {e}")
            return 0
    
    def die(self):
        """Смерть сущности"""
        try:
            if not self.is_alive:
                return
            
            self.is_alive = False
            self.is_active = False
            
            # Вызов callback
            if self.on_death:
                self.on_death(self)
            
            logger.info(f"{self.name} умер")
            
        except Exception as e:
            logger.error(f"Ошибка обработки смерти {self.name}: {e}")
    
    def gain_experience(self, amount: int) -> bool:
        """Получение опыта"""
        try:
            self.stats.experience += amount
            
            # Проверка повышения уровня
            while self.stats.experience >= self.stats.experience_to_next:
                self.level_up()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка получения опыта {self.name}: {e}")
            return False
    
    def level_up(self):
        """Повышение уровня"""
        try:
            self.stats.level += 1
            self.stats.experience -= self.stats.experience_to_next
            self.stats.experience_to_next = int(self.stats.experience_to_next * 1.5)
            
            # Увеличение характеристик
            self.stats.max_health += 10
            self.stats.max_mana += 5
            self.stats.max_stamina += 10
            self.stats.attack += 2
            self.stats.defense += 1
            
            # Восстановление здоровья и маны
            self.stats.health = self.stats.max_health
            self.stats.mana = self.stats.max_mana
            self.stats.stamina = self.stats.max_stamina
            
            # Вызов callback
            if self.on_level_up:
                self.on_level_up(self)
            
            logger.info(f"{self.name} достиг уровня {self.stats.level}")
            
        except Exception as e:
            logger.error(f"Ошибка повышения уровня {self.name}: {e}")
    
    def add_memory(self, memory_data: Dict[str, Any]):
        """Добавление памяти"""
        try:
            memory = {
                "timestamp": time.time(),
                "data": memory_data
            }
            
            self.memory.memories.append(memory)
            
            # Ограничение количества воспоминаний
            if len(self.memory.memories) > self.memory.max_memories:
                self.memory.memories.pop(0)
            
            self.memory.last_memory_update = time.time()
            
        except Exception as e:
            logger.error(f"Ошибка добавления памяти {self.name}: {e}")
    
    def add_item(self, item: Any) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            if len(self.inventory.items) >= self.inventory.max_items:
                logger.warning(f"Инвентарь {self.name} переполнен")
                return False
            
            self.inventory.items.append(item)
            # Здесь должна быть логика расчета веса
            logger.debug(f"Предмет добавлен в инвентарь {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета {self.name}: {e}")
            return False
    
    def remove_item(self, item_id: str) -> Optional[Any]:
        """Удаление предмета из инвентаря"""
        try:
            for i, item in enumerate(self.inventory.items):
                if hasattr(item, 'item_id') and item.item_id == item_id:
                    return self.inventory.items.pop(i)
            return None
            
        except Exception as e:
            logger.error(f"Ошибка удаления предмета {self.name}: {e}")
            return None
    
    def equip_item(self, item_id: str, slot: ItemSlot) -> bool:
        """Экипировка предмета"""
        try:
            item = self.remove_item(item_id)
            if item is None:
                return False
            
            # Снимаем предыдущий предмет
            if slot in self.inventory.equipped_items:
                old_item_id = self.inventory.equipped_items[slot]
                # Здесь должна быть логика возврата предмета в инвентарь
            
            self.inventory.equipped_items[slot] = item_id
            logger.debug(f"Предмет {item_id} экипирован в слот {slot.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экипировки предмета {self.name}: {e}")
            return False
    
    def unequip_item(self, slot: ItemSlot) -> Optional[str]:
        """Снятие предмета"""
        try:
            if slot not in self.inventory.equipped_items:
                return None
            
            item_id = self.inventory.equipped_items.pop(slot)
            logger.debug(f"Предмет {item_id} снят со слота {slot.value}")
            return item_id
            
        except Exception as e:
            logger.error(f"Ошибка снятия предмета {self.name}: {e}")
            return None
    
    def set_emotion(self, emotion: EmotionType, intensity: float = 0.5):
        """Установка эмоции"""
        try:
            self.emotion.current_emotion = emotion
            self.emotion.emotion_intensity = max(0.0, min(1.0, intensity))
            
            # Запись в историю
            emotion_record = {
                "emotion": emotion.value,
                "intensity": intensity,
                "timestamp": time.time()
            }
            self.emotion.emotion_history.append(emotion_record)
            
            logger.debug(f"{self.name} испытывает эмоцию {emotion.value} (интенсивность: {intensity})")
            
        except Exception as e:
            logger.error(f"Ошибка установки эмоции {self.name}: {e}")
    
    def learn_skill(self, skill_id: str, level: int = 1) -> bool:
        """Изучение навыка"""
        try:
            if skill_id in self.skills.skills:
                # Повышение уровня существующего навыка
                self.skills.skills[skill_id] = min(self.skills.max_skill_level, 
                                                 self.skills.skills[skill_id] + level)
            else:
                # Изучение нового навыка
                self.skills.skills[skill_id] = level
            
            logger.debug(f"{self.name} изучил навык {skill_id} (уровень: {self.skills.skills[skill_id]})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изучения навыка {self.name}: {e}")
            return False
    
    def add_effect(self, effect_data: Dict[str, Any], duration: float = -1.0):
        """Добавление эффекта"""
        try:
            effect = {
                "data": effect_data,
                "start_time": time.time(),
                "duration": duration
            }
            
            if duration > 0:
                self.effects.temporary_effects.append(effect)
                self.effects.effect_duration[effect_data.get("effect_id", "unknown")] = duration
            else:
                self.effects.passive_effects.append(effect)
            
            logger.debug(f"Эффект добавлен к {self.name}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления эффекта {self.name}: {e}")
    
    def remove_effect(self, effect_id: str) -> bool:
        """Удаление эффекта"""
        try:
            # Удаление из временных эффектов
            for i, effect in enumerate(self.effects.temporary_effects):
                if effect["data"].get("effect_id") == effect_id:
                    self.effects.temporary_effects.pop(i)
                    return True
            
            # Удаление из пассивных эффектов
            for i, effect in enumerate(self.effects.passive_effects):
                if effect["data"].get("effect_id") == effect_id:
                    self.effects.passive_effects.pop(i)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта {self.name}: {e}")
            return False
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        try:
            current_time = time.time()
            
            # Обновление эффектов
            self._update_effects(delta_time)
            
            # Обновление эмоций
            self._update_emotions(delta_time)
            
            # Обновление времени
            self.last_update = current_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления {self.name}: {e}")
    
    def _update_effects(self, delta_time: float):
        """Обновление эффектов"""
        try:
            current_time = time.time()
            
            # Обновление временных эффектов
            expired_effects = []
            for i, effect in enumerate(self.effects.temporary_effects):
                if effect["duration"] > 0:
                    elapsed = current_time - effect["start_time"]
                    if elapsed >= effect["duration"]:
                        expired_effects.append(i)
            
            # Удаление истекших эффектов
            for i in reversed(expired_effects):
                self.effects.temporary_effects.pop(i)
            
        except Exception as e:
            logger.error(f"Ошибка обновления эффектов {self.name}: {e}")
    
    def _update_emotions(self, delta_time: float):
        """Обновление эмоций"""
        try:
            # Постепенное возвращение к нейтральному состоянию
            if self.emotion.emotion_intensity > 0.1:
                self.emotion.emotion_intensity *= 0.95
            else:
                self.emotion.current_emotion = EmotionType.NEUTRAL
                self.emotion.emotion_intensity = 0.0
            
        except Exception as e:
            logger.error(f"Ошибка обновления эмоций {self.name}: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о сущности"""
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "type": self.entity_type.value,
            "level": self.stats.level,
            "health": f"{self.stats.health}/{self.stats.max_health}",
            "mana": f"{self.stats.mana}/{self.stats.max_mana}",
            "experience": f"{self.stats.experience}/{self.stats.experience_to_next}",
            "position": self.position,
            "is_alive": self.is_alive,
            "is_active": self.is_active
        }
    
    def cleanup(self):
        """Очистка сущности"""
        try:
            self.is_active = False
            self.is_alive = False
            
            # Очистка данных
            self.memory.memories.clear()
            self.inventory.items.clear()
            self.inventory.equipped_items.clear()
            self.emotion.emotion_history.clear()
            self.skills.skills.clear()
            self.effects.active_effects.clear()
            self.effects.passive_effects.clear()
            self.effects.temporary_effects.clear()
            
            logger.info(f"Сущность {self.name} очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки {self.name}: {e}")
