#!/usr/bin/env python3
"""
Base Entity - Базовая сущность для всех игровых объектов
Объединяет системы: характеристики, инвентарь, эмоции, гены, память, навыки
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.constants import constants_manager, (
    StatType, DamageType, AIState, ItemType, EmotionType, 
    GeneType, EntityType, ItemSlot, BASE_STATS, PROBABILITY_CONSTANTS
)

logger = logging.getLogger(__name__)

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
    equipped_items: Dict[ItemSlot, Any] = field(default_factory=dict)
    max_slots: int = 20
    max_weight: float = 100.0
    current_weight: float = 0.0

@dataclass
class EntityEmotions:
    """Эмоциональное состояние сущности"""
    entity_id: str
    emotions: List[Dict[str, Any]] = field(default_factory=list)
    mood: float = 0.0  # -1.0 до 1.0
    stress_level: float = 0.0  # 0.0 до 1.0
    emotional_stability: float = 0.5
    last_emotion_update: float = field(default_factory=time.time)

@dataclass
class EntityGenes:
    """Генетическая информация сущности"""
    entity_id: str
    genes: List[Dict[str, Any]] = field(default_factory=list)
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    generation: int = 1
    last_gene_update: float = field(default_factory=time.time)

@dataclass
class EntitySkills:
    """Навыки сущности"""
    entity_id: str
    skills: List[str] = field(default_factory=list)
    skill_levels: Dict[str, int] = field(default_factory=dict)
    skill_experience: Dict[str, int] = field(default_factory=dict)
    active_skills: List[str] = field(default_factory=list)

@dataclass
class EntityEffects:
    """Эффекты сущности"""
    entity_id: str
    active_effects: List[Dict[str, Any]] = field(default_factory=list)
    permanent_effects: List[Dict[str, Any]] = field(default_factory=list)
    effect_history: List[Dict[str, Any]] = field(default_factory=list)

class BaseEntity:
    """Базовая сущность для всех игровых объектов"""
    
    def __init__(self, entity_id: str, entity_type: EntityType, name: str = ""):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name or f"{entity_type.value}_{entity_id}"
        
        # Основные системы
        self.stats = EntityStats()
        self.memory = EntityMemory(entity_id=entity_id)
        self.inventory = EntityInventory(entity_id=entity_id)
        self.emotions = EntityEmotions(entity_id=entity_id)
        self.genes = EntityGenes(entity_id=entity_id)
        self.skills = EntitySkills(entity_id=entity_id)
        self.effects = EntityEffects(entity_id=entity_id)
        
        # Позиция и состояние
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0)
        self.current_state = AIState.IDLE
        
        # Временные метки
        self.created_time = time.time()
        self.last_update = time.time()
        self.last_save = time.time()
        
        # Флаги состояния
        self.is_alive = True
        self.is_in_combat = False
        self.is_moving = False
        self.is_casting = False
        self.is_busy = False
        
        # Цели и взаимодействия
        self.current_target: Optional[str] = None
        self.interaction_target: Optional[str] = None
        
        logger.info(f"Создана базовая сущность: {self.name} ({entity_type.value})")
    
    def update(self, delta_time: float):
        """Обновление состояния сущности"""
        try:
            current_time = time.time()
            
            # Обновление характеристик
            self._update_stats(delta_time)
            
            # Обновление эффектов
            self._update_effects(delta_time)
            
            # Обновление эмоций
            self._update_emotions(delta_time)
            
            # Обновление памяти
            self._update_memory(delta_time)
            
            # Обновление состояния
            self._update_state(delta_time)
            
            self.last_update = current_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления сущности {self.entity_id}: {e}")
    
    def _update_stats(self, delta_time: float):
        """Обновление характеристик"""
        # Регенерация здоровья
        if self.stats.health < self.stats.max_health:
            regen_amount = 1.0 * delta_time  # Базовая регенерация
            self.stats.health = min(self.stats.health + regen_amount, self.stats.max_health)
        
        # Регенерация маны
        if self.stats.mana < self.stats.max_mana:
            regen_amount = 0.5 * delta_time  # Базовая регенерация маны
            self.stats.mana = min(self.stats.mana + regen_amount, self.stats.max_mana)
        
        # Регенерация выносливости
        if self.stats.stamina < self.stats.max_stamina:
            regen_amount = 2.0 * delta_time  # Быстрая регенерация выносливости
            self.stats.stamina = min(self.stats.stamina + regen_amount, self.stats.max_stamina)
    
    def _update_effects(self, delta_time: float):
        """Обновление эффектов"""
        current_time = time.time()
        
        # Обновляем активные эффекты
        effects_to_remove = []
        for effect in self.effects.active_effects:
            if 'duration' in effect and effect['duration'] > 0:
                effect['duration'] -= delta_time
                if effect['duration'] <= 0:
                    effects_to_remove.append(effect)
        
        # Удаляем истекшие эффекты
        for effect in effects_to_remove:
            self.effects.active_effects.remove(effect)
            self._remove_effect(effect)
    
    def _update_emotions(self, delta_time: float):
        """Обновление эмоций"""
        current_time = time.time()
        
        # Затухание эмоций
        emotions_to_remove = []
        for emotion in self.emotions.emotions:
            if 'duration' in emotion and emotion['duration'] > 0:
                emotion['duration'] -= delta_time
                if emotion['duration'] <= 0:
                    emotions_to_remove.append(emotion)
        
        # Удаляем истекшие эмоции
        for emotion in emotions_to_remove:
            self.emotions.emotions.remove(emotion)
        
        # Обновляем общее настроение
        self._calculate_mood()
    
    def _update_memory(self, delta_time: float):
        """Обновление памяти"""
        current_time = time.time()
        
        # Ограничиваем размер памяти
        if len(self.memory.memories) > self.memory.max_memories:
            # Удаляем старые записи
            self.memory.memories = self.memory.memories[-self.memory.max_memories:]
    
    def _update_state(self, delta_time: float):
        """Обновление состояния"""
        # Проверяем, жива ли сущность
        if self.stats.health <= 0 and self.is_alive:
            self.die()
    
    def _calculate_mood(self):
        """Расчет общего настроения"""
        if not self.emotions.emotions:
            self.emotions.mood = 0.0
            return
        
        total_mood = 0.0
        total_weight = 0.0
        
        for emotion in self.emotions.emotions:
            intensity = emotion.get('intensity', 0.5)
            value = emotion.get('value', 0.0)
            weight = intensity * abs(value)
            
            total_mood += value * weight
            total_weight += weight
        
        if total_weight > 0:
            self.emotions.mood = total_mood / total_weight
        else:
            self.emotions.mood = 0.0
    
    def take_damage(self, damage: int, damage_type: DamageType = DamageType.PHYSICAL, 
                   source: Optional[str] = None) -> bool:
        """Получение урона"""
        try:
            if not self.is_alive:
                return False
            
            # Применяем защиту
            actual_damage = max(1, damage - self.stats.defense)
            
            # Применяем сопротивление к типу урона
            resistance = self.stats.resistances.get(damage_type, 0.0)
            actual_damage = int(actual_damage * (1.0 - resistance))
            
            self.stats.health = max(0, self.stats.health - actual_damage)
            
            # Добавляем память о получении урона
            self.add_memory('combat', {
                'action': 'damage_received',
                'damage': actual_damage,
                'damage_type': damage_type.value,
                'source': source
            }, 'damage_received', {
                'damage_dealt': actual_damage,
                'health_remaining': self.stats.health
            }, True)
            
            # Добавляем эмоцию страха/боли
            self.add_emotion(EmotionType.FEAR, 0.3, 5.0, source)
            
            logger.debug(f"Сущность {self.entity_id} получила {actual_damage} урона")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка получения урона: {e}")
            return False
    
    def heal(self, amount: int, source: Optional[str] = None) -> bool:
        """Восстановление здоровья"""
        try:
            if not self.is_alive:
                return False
            
            old_health = self.stats.health
            self.stats.health = min(self.stats.max_health, self.stats.health + amount)
            actual_heal = self.stats.health - old_health
            
            if actual_heal > 0:
                # Добавляем память о лечении
                self.add_memory('combat', {
                    'action': 'healing',
                    'amount': actual_heal,
                    'source': source
                }, 'healing', {
                    'health_gained': actual_heal,
                    'health_remaining': self.stats.health
                }, True)
                
                # Добавляем эмоцию радости
                self.add_emotion(EmotionType.JOY, 0.2, 3.0, source)
                
                logger.debug(f"Сущность {self.entity_id} восстановила {actual_heal} здоровья")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка лечения: {e}")
            return False
    
    def gain_experience(self, amount: int, source: Optional[str] = None) -> bool:
        """Получение опыта"""
        try:
            self.stats.experience += amount
            
            # Проверяем повышение уровня
            if self.stats.experience >= self.stats.experience_to_next:
                self._level_up()
            
            # Добавляем память о получении опыта
            self.add_memory('progression', {
                'action': 'experience_gained',
                'amount': amount,
                'source': source
            }, 'experience_gained', {
                'experience_gained': amount,
                'total_experience': self.stats.experience
            }, True)
            
            logger.debug(f"Сущность {self.entity_id} получила {amount} опыта")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка получения опыта: {e}")
            return False
    
    def _level_up(self):
        """Повышение уровня"""
        try:
            self.stats.level += 1
            self.stats.experience -= self.stats.experience_to_next
            
            # Увеличиваем требования к следующему уровню
            self.stats.experience_to_next = int(self.stats.experience_to_next * 1.5)
            
            # Увеличиваем характеристики
            self.stats.max_health += 10
            self.stats.health = self.stats.max_health
            self.stats.max_mana += 5
            self.stats.mana = self.stats.max_mana
            self.stats.attack += 2
            self.stats.defense += 1
            
            # Добавляем память о повышении уровня
            self.add_memory('progression', {
                'action': 'level_up',
                'new_level': self.stats.level
            }, 'level_up', {
                'new_level': self.stats.level,
                'new_stats': {
                    'max_health': self.stats.max_health,
                    'max_mana': self.stats.max_mana,
                    'attack': self.stats.attack,
                    'defense': self.stats.defense
                }
            }, True)
            
            # Добавляем эмоцию радости
            self.add_emotion(EmotionType.JOY, 0.5, 10.0, 'system')
            
            logger.info(f"Сущность {self.entity_id} повысила уровень до {self.stats.level}")
            
        except Exception as e:
            logger.error(f"Ошибка повышения уровня: {e}")
    
    def add_item(self, item: Any) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            if len(self.inventory.items) >= self.inventory.max_slots:
                logger.warning(f"Инвентарь сущности {self.entity_id} переполнен")
                return False
            
            # Проверяем вес
            if self.inventory.current_weight + item.weight > self.inventory.max_weight:
                logger.warning(f"Превышен лимит веса инвентаря сущности {self.entity_id}")
                return False
            
            self.inventory.items.append(item)
            self.inventory.current_weight += item.weight
            
            # Добавляем память о получении предмета
            self.add_memory('inventory', {
                'action': 'item_added',
                'item_id': item.item_id,
                'item_name': item.name
            }, 'item_added', {
                'item_id': item.item_id,
                'inventory_count': len(self.inventory.items)
            }, True)
            
            logger.debug(f"Предмет {item.name} добавлен в инвентарь сущности {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False
    
    def remove_item(self, item_id: str) -> Optional[Any]:
        """Удаление предмета из инвентаря"""
        try:
            for i, item in enumerate(self.inventory.items):
                if item.item_id == item_id:
                    removed_item = self.inventory.items.pop(i)
                    self.inventory.current_weight -= removed_item.weight
                    
                    # Добавляем память об удалении предмета
                    self.add_memory('inventory', {
                        'action': 'item_removed',
                        'item_id': item_id,
                        'item_name': removed_item.name
                    }, 'item_removed', {
                        'item_id': item_id,
                        'inventory_count': len(self.inventory.items)
                    }, True)
                    
                    logger.debug(f"Предмет {removed_item.name} удален из инвентаря сущности {self.entity_id}")
                    return removed_item
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка удаления предмета: {e}")
            return None
    
    def equip_item(self, item: Any, slot: ItemSlot) -> bool:
        """Экипировка предмета"""
        try:
            if not item.can_equip({'entity_id': self.entity_id}, slot):
                logger.warning(f"Предмет {item.name} нельзя экипировать в слот {slot.value}")
                return False
            
            # Снимаем предыдущий предмет
            if slot in self.inventory.equipped_items:
                self.unequip_item(slot)
            
            # Экипируем новый предмет
            self.inventory.equipped_items[slot] = item
            
            # Применяем эффекты предмета
            if item.effects:
                for effect in item.effects:
                    self._apply_effect(effect)
            
            # Добавляем память об экипировке
            self.add_memory('inventory', {
                'action': 'item_equipped',
                'item_id': item.item_id,
                'slot': slot.value
            }, 'item_equipped', {
                'item_id': item.item_id,
                'slot': slot.value
            }, True)
            
            logger.debug(f"Предмет {item.name} экипирован в слот {slot.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экипировки предмета: {e}")
            return False
    
    def unequip_item(self, slot: ItemSlot) -> Optional[Any]:
        """Снятие предмета"""
        try:
            if slot not in self.inventory.equipped_items:
                return None
            
            item = self.inventory.equipped_items.pop(slot)
            
            # Убираем эффекты предмета
            if item.effects:
                for effect in item.effects:
                    self._remove_effect(effect)
            
            # Добавляем память о снятии предмета
            self.add_memory('inventory', {
                'action': 'item_unequipped',
                'item_id': item.item_id,
                'slot': slot.value
            }, 'item_unequipped', {
                'item_id': item.item_id,
                'slot': slot.value
            }, True)
            
            logger.debug(f"Предмет {item.name} снят со слота {slot.value}")
            return item
            
        except Exception as e:
            logger.error(f"Ошибка снятия предмета: {e}")
            return None
    
    def use_item(self, item: Any, target: Optional[str] = None) -> bool:
        """Использование предмета"""
        try:
            if not item.can_use({'entity_id': self.entity_id}):
                logger.warning(f"Предмет {item.name} нельзя использовать")
                return False
            
            # Используем предмет
            success = item.use({'entity_id': self.entity_id}, {'entity_id': target} if target else None)
            
            if success:
                # Удаляем предмет если он расходуемый
                if item.is_consumable:
                    self.remove_item(item.item_id)
                
                # Добавляем память об использовании
                self.add_memory('inventory', {
                    'action': 'item_used',
                    'item_id': item.item_id,
                    'target': target
                }, 'item_used', {
                    'item_id': item.item_id,
                    'success': True
                }, True)
                
                logger.debug(f"Предмет {item.name} использован")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка использования предмета: {e}")
            return False
    
    def add_emotion(self, emotion_type: EmotionType, intensity: float, 
                   duration: float = 0.0, source: str = "system") -> bool:
        """Добавление эмоции"""
        try:
            emotion = {
                'emotion_id': f"{emotion_type.value}_{int(time.time() * 1000)}",
                'emotion_type': emotion_type.value,
                'intensity': intensity,
                'value': 0.5 if emotion_type in [EmotionType.JOY, EmotionType.LOVE] else -0.5,
                'duration': duration,
                'start_time': time.time(),
                'source': source
            }
            
            self.emotions.emotions.append(emotion)
            
            # Ограничиваем количество эмоций
            if len(self.emotions.emotions) > 10:
                self.emotions.emotions = self.emotions.emotions[-10:]
            
            # Обновляем настроение
            self._calculate_mood()
            
            logger.debug(f"Добавлена эмоция {emotion_type.value} к сущности {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления эмоции: {e}")
            return False
    
    def add_memory(self, memory_type: str, context: Dict[str, Any], 
                  action: str, outcome: Dict[str, Any], success: bool) -> bool:
        """Добавление записи в память"""
        try:
            memory = {
                'memory_type': memory_type,
                'timestamp': time.time(),
                'context': context,
                'action': action,
                'outcome': outcome,
                'success': success,
                'learning_value': 0.5 if success else 0.3
            }
            
            self.memory.memories.append(memory)
            
            # Ограничиваем размер памяти
            if len(self.memory.memories) > self.memory.max_memories:
                self.memory.memories = self.memory.memories[-self.memory.max_memories:]
            
            logger.debug(f"Добавлена память типа {memory_type} для сущности {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления памяти: {e}")
            return False
    
    def add_skill(self, skill_id: str, level: int = 1) -> bool:
        """Добавление навыка"""
        try:
            if skill_id not in self.skills.skills:
                self.skills.skills.append(skill_id)
                self.skills.skill_levels[skill_id] = level
                self.skills.skill_experience[skill_id] = 0
                
                # Добавляем память о получении навыка
                self.add_memory('skills', {
                    'action': 'skill_learned',
                    'skill_id': skill_id,
                    'level': level
                }, 'skill_learned', {
                    'skill_id': skill_id,
                    'level': level
                }, True)
                
                logger.debug(f"Навык {skill_id} добавлен сущности {self.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка добавления навыка: {e}")
            return False
    
    def _apply_effect(self, effect: Dict[str, Any]) -> bool:
        """Применение эффекта"""
        try:
            effect['start_time'] = time.time()
            self.effects.active_effects.append(effect)
            
            # Применяем эффект к характеристикам
            if 'stat_modifier' in effect:
                stat_type = effect['stat_modifier'].get('stat_type')
                value = effect['stat_modifier'].get('value', 0)
                
                if stat_type == 'health':
                    self.stats.health = min(self.stats.max_health, self.stats.health + value)
                elif stat_type == 'mana':
                    self.stats.mana = min(self.stats.max_mana, self.stats.mana + value)
                elif stat_type == 'stamina':
                    self.stats.stamina = min(self.stats.max_stamina, self.stats.stamina + value)
            
            logger.debug(f"Эффект применен к сущности {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта: {e}")
            return False
    
    def _remove_effect(self, effect: Dict[str, Any]) -> bool:
        """Удаление эффекта"""
        try:
            if effect in self.effects.active_effects:
                self.effects.active_effects.remove(effect)
                
                # Убираем эффект с характеристик
                if 'stat_modifier' in effect:
                    stat_type = effect['stat_modifier'].get('stat_type')
                    value = effect['stat_modifier'].get('value', 0)
                    
                    if stat_type == 'health':
                        self.stats.health = max(0, self.stats.health - value)
                    elif stat_type == 'mana':
                        self.stats.mana = max(0, self.stats.mana - value)
                    elif stat_type == 'stamina':
                        self.stats.stamina = max(0, self.stats.stamina - value)
                
                logger.debug(f"Эффект удален с сущности {self.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта: {e}")
            return False
    
    def die(self):
        """Смерть сущности"""
        try:
            if not self.is_alive:
                return
            
            self.is_alive = False
            self.current_state = AIState.DEAD
            
            # Добавляем память о смерти
            self.add_memory('combat', {
                'action': 'death',
                'cause': 'health_zero'
            }, 'death', {
                'cause': 'health_zero',
                'level': self.stats.level,
                'experience': self.stats.experience
            }, False)
            
            # Добавляем эмоцию страха
            self.add_emotion(EmotionType.FEAR, 1.0, 10.0, 'system')
            
            logger.info(f"Сущность {self.entity_id} умерла")
            
        except Exception as e:
            logger.error(f"Ошибка смерти сущности: {e}")
    
    def respawn(self, position: Optional[Tuple[float, float, float]] = None):
        """Возрождение сущности"""
        try:
            if self.is_alive:
                return
            
            self.is_alive = True
            self.current_state = AIState.IDLE
            
            # Восстанавливаем здоровье
            self.stats.health = self.stats.max_health
            self.stats.mana = self.stats.max_mana
            self.stats.stamina = self.stats.max_stamina
            
            # Устанавливаем позицию
            if position:
                self.position = position
            
            # Очищаем эффекты
            self.effects.active_effects.clear()
            
            # Добавляем память о возрождении
            self.add_memory('combat', {
                'action': 'respawn',
                'position': self.position
            }, 'respawn', {
                'position': self.position,
                'health': self.stats.health
            }, True)
            
            logger.info(f"Сущность {self.entity_id} возродилась")
            
        except Exception as e:
            logger.error(f"Ошибка возрождения сущности: {e}")
    
    def get_entity_data(self) -> Dict[str, Any]:
        """Получение данных сущности"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'name': self.name,
            'position': self.position,
            'rotation': self.rotation,
            'current_state': self.current_state.value,
            'is_alive': self.is_alive,
            'is_in_combat': self.is_in_combat,
            'stats': {
                'health': self.stats.health,
                'max_health': self.stats.max_health,
                'mana': self.stats.mana,
                'max_mana': self.stats.max_mana,
                'stamina': self.stats.stamina,
                'max_stamina': self.stats.max_stamina,
                'level': self.stats.level,
                'experience': self.stats.experience,
                'experience_to_next': self.stats.experience_to_next
            },
            'inventory': {
                'items_count': len(self.inventory.items),
                'equipped_count': len(self.inventory.equipped_items),
                'current_weight': self.inventory.current_weight,
                'max_weight': self.inventory.max_weight
            },
            'emotions': {
                'mood': self.emotions.mood,
                'stress_level': self.emotions.stress_level,
                'emotions_count': len(self.emotions.emotions)
            },
            'skills': {
                'skills_count': len(self.skills.skills),
                'active_skills_count': len(self.skills.active_skills)
            },
            'effects': {
                'active_effects_count': len(self.effects.active_effects),
                'permanent_effects_count': len(self.effects.permanent_effects)
            },
            'memory': {
                'memories_count': len(self.memory.memories),
                'learning_rate': self.memory.learning_rate
            },
            'genes': {
                'genes_count': len(self.genes.genes),
                'mutations_count': len(self.genes.mutations),
                'generation': self.genes.generation
            }
        }
    
    def get_info(self) -> str:
        """Получение информации о сущности"""
        return (f"Сущность: {self.name} ({self.entity_type.value})\n"
                f"Уровень: {self.stats.level} | Опыт: {self.stats.experience}/{self.stats.experience_to_next}\n"
                f"Здоровье: {self.stats.health}/{self.stats.max_health} | "
                f"Мана: {self.stats.mana}/{self.stats.max_mana} | "
                f"Выносливость: {self.stats.stamina}/{self.stats.max_stamina}\n"
                f"Атака: {self.stats.attack} | Защита: {self.stats.defense} | "
                f"Скорость: {self.stats.speed}\n"
                f"Настроение: {self.emotions.mood:.2f} | Стресс: {self.emotions.stress_level:.2f}\n"
                f"Инвентарь: {len(self.inventory.items)}/{self.inventory.max_slots} | "
                f"Навыки: {len(self.skills.skills)} | Эффекты: {len(self.effects.active_effects)}")
