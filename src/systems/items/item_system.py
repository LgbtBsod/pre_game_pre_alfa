#!/usr/bin/env python3
"""
Система предметов - управление игровыми предметами и их свойствами
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ...core.system_interfaces import BaseGameSystem, Priority
from ...core.constants import constants_manager, ItemType, ItemRarity, ItemCategory, DamageType, StatType, BASE_STATS, PROBABILITY_CONSTANTS, SYSTEM_LIMITS_RO, TIME_CONSTANTS_RO, get_float

logger = logging.getLogger(__name__)

class ItemQuality(Enum):
    """Качество предмета"""
    BROKEN = 0
    POOR = 1
    COMMON = 2
    GOOD = 3
    EXCELLENT = 4
    MASTERWORK = 5
    LEGENDARY = 6

class EffectTrigger(Enum):
    """Триггеры эффектов"""
    ON_EQUIP = "on_equip"
    ON_USE = "on_use"
    ON_HIT = "on_hit"
    ON_TAKE_DAMAGE = "on_take_damage"
    ON_KILL = "on_kill"
    ON_LEVEL_UP = "on_level_up"
    PASSIVE = "passive"

class EffectCategory(Enum):
    """Категории эффектов"""
    BUFF = "buff"
    DEBUFF = "debuff"
    DAMAGE = "damage"
    HEALING = "healing"
    UTILITY = "utility"
    COSMETIC = "cosmetic"

@dataclass
class ItemRequirement:
    """Требование для использования предмета"""
    requirement_type: str  # "level", "stat", "skill", "reputation", "quest"
    requirement_value: Any
    comparison: str = ">="  # ">=", "==", "<=", ">", "<"
    description: str = ""

@dataclass
class ItemVisual:
    """Визуальные свойства предмета"""
    model_path: str = ""
    texture_path: str = ""
    icon_path: str = ""
    particle_effect: str = ""
    glow_effect: str = ""
    animation_path: str = ""
    scale: float = 1.0
    rotation: float = 0.0
    color_tint: str = "#FFFFFF"

@dataclass
class ItemAudio:
    """Аудио свойства предмета"""
    use_sound: str = ""
    equip_sound: str = ""
    unequip_sound: str = ""
    hit_sound: str = ""
    break_sound: str = ""
    ambient_sound: str = ""
    volume: float = 1.0
    pitch: float = 1.0

@dataclass
class ItemDurability:
    """Система прочности предмета"""
    current: int = 100
    maximum: int = 100
    decay_rate: float = 0.1  # Скорость износа
    repair_cost_multiplier: float = 1.0
    break_chance_on_low: float = 0.1
    quality_affects_durability: bool = True

@dataclass
class SpecialEffect:
    """Расширенный специальный эффект предмета"""
    effect_id: str
    name: str
    effect_type: str
    category: EffectCategory = EffectCategory.UTILITY
    trigger: EffectTrigger = EffectTrigger.ON_USE
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    chance: float = 1.0
    stack_limit: int = 1
    priority: int = 0
    visual_effect: str = ""
    sound_effect: str = ""
    particle_effect: str = ""
    icon_effect: str = ""

@dataclass
class Item:
    """Расширенный игровой предмет"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    category: ItemCategory
    rarity: ItemRarity
    quality: ItemQuality = ItemQuality.COMMON
    level: int = 1
    stack_size: int = 1
    max_stack: int = 1
    weight: float = 0.0
    value: int = 0
    
    # Расширенная система прочности
    durability: ItemDurability = field(default_factory=lambda: ItemDurability())
    
    # Расширенные требования
    requirements: List[ItemRequirement] = field(default_factory=list)
    
    # Характеристики
    stats: Dict[StatType, int] = field(default_factory=dict)
    damage: int = 0
    damage_type: Optional[DamageType] = None
    armor: int = 0
    
    # Расширенные эффекты
    special_effects: List[SpecialEffect] = field(default_factory=list)
    
    # Визуальные свойства
    visual: ItemVisual = field(default_factory=lambda: ItemVisual())
    
    # Аудио свойства
    audio: ItemAudio = field(default_factory=lambda: ItemAudio())
    
    # Дополнительные свойства
    is_tradeable: bool = True
    is_droppable: bool = True
    is_destroyable: bool = True
    bind_on_pickup: bool = False
    bind_on_equip: bool = False
    bind_on_use: bool = False
    
    # Система улучшений
    upgrade_level: int = 0
    max_upgrade_level: int = 10
    upgrade_cost_multiplier: float = 1.5
    
    # Система гнезд
    socket_count: int = 0
    socketed_gems: List[str] = field(default_factory=list)
    
    # Система набора
    set_name: str = ""
    set_bonus: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    created_by: str = ""
    created_date: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    version: str = "1.0"
    
    # Обратная совместимость
    @property
    def icon(self) -> str:
        return self.visual.icon_path
    
    @property
    def model(self) -> str:
        return self.visual.model_path
    
    @property
    def sound(self) -> str:
        return self.audio.use_sound

class ItemSystem(BaseGameSystem):
    """Система управления предметами (интегрирована с BaseGameSystem)"""
    
    def __init__(self):
        super().__init__("items", Priority.HIGH)
        
        # Зарегистрированные предметы
        self.registered_items: Dict[str, Item] = {}
        
        # Предметы сущностей
        self.entity_items: Dict[str, List[Item]] = {}
        
        # Шаблоны предметов
        self.item_templates: Dict[str, Dict[str, Any]] = {}
        
        # История предметов
        self.item_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_items_per_entity': SYSTEM_LIMITS_RO["max_items_per_entity"],
            'max_item_level': 100,
            'durability_decay_enabled': True,
            'item_combining_enabled': True,
            'auto_item_upgrade': False
        }
        
        # Статистика системы
        self.system_stats = {
            'registered_items_count': 0,
            'total_entity_items': 0,
            'items_created_today': 0,
            'items_destroyed_today': 0,
            'items_upgraded_today': 0,
            'update_time': 0.0
        }
        
        logger.info("Система предметов инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы предметов"""
        try:
            if not super().initialize():
                return False
            logger.info("Инициализация системы предметов...")
            
            # Регистрируем базовые предметы
            self._register_base_items()
            
            # Загружаем шаблоны предметов
            self._load_item_templates()
            
            logger.info("Система предметов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы предметов: {e}")
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы предметов"""
        try:
            # Используем базовую проверку состояния из BaseGameSystem
            if not super().update(delta_time):
                return False

            start_time = time.time()

            # Обновляем износ предметов
            if self.system_settings['durability_decay_enabled']:
                self._update_item_durability(delta_time)

            # Обновляем статистику системы
            self._update_system_stats()

            self.system_stats['update_time'] = time.time() - start_time

            return True

        except Exception as e:
            logger.error(f"Ошибка обновления системы предметов: {e}")
            return False
    
    # Пауза/резюмирование покрываются базовым компонентом при необходимости
    
    def destroy(self) -> bool:
        """Очистка/уничтожение системы предметов"""
        try:
            logger.info("Очистка системы предметов...")
            self.registered_items.clear()
            self.entity_items.clear()
            self.item_templates.clear()
            self.item_history.clear()
            self.reset_stats()
            return super().destroy()
        except Exception as e:
            logger.error(f"Ошибка очистки системы предметов: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'registered_items': len(self.registered_items),
            'item_templates': len(self.item_templates),
            'entities_with_items': len(self.entity_items),
            'total_entity_items': self.system_stats['total_entity_items'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "item_created":
                return self._handle_item_created(event_data)
            elif event_type == "item_destroyed":
                return self._handle_item_destroyed(event_data)
            elif event_type == "item_used":
                return self._handle_item_used(event_data)
            elif event_type == "item_upgraded":
                return self._handle_item_upgraded(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _register_base_items(self) -> None:
        """Регистрация базовых предметов"""
        try:
            # Оружие
            weapons = [
                Item(
                    item_id="iron_sword",
                    name="Железный меч",
                    description="Надежный железный меч",
                    item_type=ItemType.WEAPON,
                    category=ItemCategory.MELEE,
                    rarity=ItemRarity.COMMON,
                    level=5,
                    damage=35,
                    damage_type=DamageType.PHYSICAL,
                    stats={StatType.STRENGTH: 5},
                    weight=2.5,
                    value=150,
                    icon="iron_sword"
                ),
                Item(
                    item_id="fire_staff",
                    name="Огненный посох",
                    description="Посох, излучающий огонь",
                    item_type=ItemType.WEAPON,
                    category=ItemCategory.MAGIC,
                    rarity=ItemRarity.UNCOMMON,
                    level=8,
                    damage=45,
                    damage_type=DamageType.FIRE,
                    stats={StatType.INTELLIGENCE: 8},
                    weight=1.8,
                    value=300,
                    icon="fire_staff"
                )
            ]
            
            # Броня
            armor = [
                Item(
                    item_id="leather_armor",
                    name="Кожаная броня",
                    description="Легкая кожаная броня",
                    item_type=ItemType.ARMOR,
                    category=ItemCategory.LIGHT,
                    rarity=ItemRarity.COMMON,
                    level=3,
                    armor=15,
                    stats={StatType.AGILITY: 3},
                    weight=3.0,
                    value=100,
                    icon="leather_armor"
                ),
                Item(
                    item_id="steel_plate",
                    name="Стальная пластина",
                    description="Тяжелая стальная броня",
                    item_type=ItemType.ARMOR,
                    category=ItemCategory.HEAVY,
                    rarity=ItemRarity.UNCOMMON,
                    level=10,
                    armor=35,
                    stats={StatType.STRENGTH: 6, StatType.DEFENSE: 8},
                    weight=8.5,
                    value=450,
                    icon="steel_plate"
                )
            ]
            
            # Зелья
            potions = [
                Item(
                    item_id="health_potion",
                    name="Зелье здоровья",
                    description="Восстанавливает здоровье",
                    item_type=ItemType.CONSUMABLE,
                    category=ItemCategory.POTION,
                    rarity=ItemRarity.COMMON,
                    level=1,
                    stack_size=1,
                    max_stack=10,
                    weight=0.2,
                    value=25,
                    icon="health_potion"
                ),
                Item(
                    item_id="mana_potion",
                    name="Зелье маны",
                    description="Восстанавливает ману",
                    item_type=ItemType.CONSUMABLE,
                    category=ItemCategory.POTION,
                    rarity=ItemRarity.COMMON,
                    level=1,
                    stack_size=1,
                    max_stack=10,
                    weight=0.2,
                    value=30,
                    icon="mana_potion"
                )
            ]
            
            # Материалы
            materials = [
                Item(
                    item_id="iron_ore",
                    name="Железная руда",
                    description="Сырая железная руда",
                    item_type=ItemType.MATERIAL,
                    category=ItemCategory.ORE,
                    rarity=ItemRarity.COMMON,
                    level=1,
                    stack_size=1,
                    max_stack=100,
                    weight=0.5,
                    value=5,
                    icon="iron_ore"
                ),
                Item(
                    item_id="herb",
                    name="Трава",
                    description="Полезная трава",
                    item_type=ItemType.MATERIAL,
                    category=ItemCategory.HERB,
                    rarity=ItemRarity.COMMON,
                    level=1,
                    stack_size=1,
                    max_stack=50,
                    weight=0.1,
                    value=2,
                    icon="herb"
                )
            ]
            
            # Регистрируем все предметы
            all_items = weapons + armor + potions + materials
            
            for item in all_items:
                self.registered_items[item.item_id] = item
            
            logger.info(f"Зарегистрировано {len(all_items)} базовых предметов")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации базовых предметов: {e}")
    
    def _load_item_templates(self) -> None:
        """Загрузка шаблонов предметов"""
        try:
            # Шаблоны для генерации предметов
            self.item_templates = {
                'weapon': {
                    'base_stats': {StatType.STRENGTH: 2, StatType.AGILITY: 1},
                    'damage_multiplier': 1.5,
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.6,
                        ItemRarity.UNCOMMON: 0.25,
                        ItemRarity.RARE: 0.1,
                        ItemRarity.EPIC: 0.04,
                        ItemRarity.LEGENDARY: 0.01
                    }
                },
                'armor': {
                    'base_stats': {StatType.DEFENSE: 3, StatType.VITALITY: 2},
                    'armor_multiplier': 1.3,
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.7,
                        ItemRarity.UNCOMMON: 0.2,
                        ItemRarity.RARE: 0.08,
                        ItemRarity.EPIC: 0.015,
                        ItemRarity.LEGENDARY: 0.005
                    }
                },
                'consumable': {
                    'base_stats': {},
                    'effect_multiplier': 1.2,
                    'rarity_weights': {
                        ItemRarity.COMMON: 0.8,
                        ItemRarity.UNCOMMON: 0.15,
                        ItemRarity.RARE: 0.04,
                        ItemRarity.EPIC: 0.01,
                        ItemRarity.LEGENDARY: 0.0
                    }
                }
            }
            
            logger.info(f"Загружено {len(self.item_templates)} шаблонов предметов")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов предметов: {e}")
    
    def _update_item_durability(self, delta_time: float) -> None:
        """Обновление износа предметов"""
        try:
            current_time = time.time()
            
            for entity_id, items in self.entity_items.items():
                for item in items:
                    if item.durability.current < item.durability.maximum:
                        # Используем индивидуальную скорость износа предмета
                        decay_rate = item.durability.decay_rate
                        item.durability.current = max(0, item.durability.current - decay_rate * delta_time)
                        
                        # Если предмет полностью изношен
                        if item.durability.current <= 0:
                            logger.debug(f"Предмет {item.item_id} полностью изношен у {entity_id}")
                            # Здесь можно добавить логику уничтожения изношенных предметов
                
        except Exception as e:
            logger.warning(f"Ошибка обновления износа предметов: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['registered_items_count'] = len(self.registered_items)
            self.system_stats['total_entity_items'] = sum(len(items) for items in self.entity_items.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_item_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания предмета"""
        try:
            item_id = event_data.get('item_id')
            entity_id = event_data.get('entity_id')
            item_data = event_data.get('item_data', {})
            
            if item_id and entity_id:
                return self.create_item_for_entity(item_id, entity_id, item_data)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания предмета: {e}")
            return False
    
    def _handle_item_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения предмета"""
        try:
            item_id = event_data.get('item_id')
            entity_id = event_data.get('entity_id')
            
            if item_id and entity_id:
                return self.destroy_item_from_entity(entity_id, item_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения предмета: {e}")
            return False
    
    def _handle_item_used(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события использования предмета"""
        try:
            item_id = event_data.get('item_id')
            entity_id = event_data.get('entity_id')
            target_id = event_data.get('target_id')
            
            if item_id and entity_id:
                return self.use_item(entity_id, item_id, target_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события использования предмета: {e}")
            return False
    
    def _handle_item_upgraded(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события улучшения предмета"""
        try:
            item_id = event_data.get('item_id')
            entity_id = event_data.get('entity_id')
            new_level = event_data.get('new_level')
            
            if item_id and entity_id and new_level:
                return self.upgrade_item(entity_id, item_id, new_level)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события улучшения предмета: {e}")
            return False
    
    def create_item_for_entity(self, item_id: str, entity_id: str, item_data: Dict[str, Any] = None) -> bool:
        """Создание предмета для сущности"""
        try:
            if item_id not in self.registered_items:
                logger.warning(f"Предмет {item_id} не найден")
                return False
            
            base_item = self.registered_items[item_id]
            
            # Создаем копию предмета с новыми свойствами
            new_item = Item(
                item_id=f"{item_id}_{int(time.time() * 1000)}",
                name=base_item.name,
                description=base_item.description,
                item_type=base_item.item_type,
                category=base_item.category,
                rarity=base_item.rarity,
                quality=base_item.quality,
                level=base_item.level,
                stack_size=base_item.stack_size,
                max_stack=base_item.max_stack,
                weight=base_item.weight,
                value=base_item.value,
                durability=ItemDurability(
                    current=base_item.durability.current,
                    maximum=base_item.durability.maximum,
                    decay_rate=base_item.durability.decay_rate,
                    repair_cost_multiplier=base_item.durability.repair_cost_multiplier,
                    break_chance_on_low=base_item.durability.break_chance_on_low,
                    quality_affects_durability=base_item.durability.quality_affects_durability
                ),
                requirements=base_item.requirements.copy(),
                stats=base_item.stats.copy(),
                damage=base_item.damage,
                damage_type=base_item.damage_type,
                armor=base_item.armor,
                special_effects=base_item.special_effects.copy(),
                visual=ItemVisual(
                    model_path=base_item.visual.model_path,
                    texture_path=base_item.visual.texture_path,
                    icon_path=base_item.visual.icon_path,
                    particle_effect=base_item.visual.particle_effect,
                    glow_effect=base_item.visual.glow_effect,
                    animation_path=base_item.visual.animation_path,
                    scale=base_item.visual.scale,
                    rotation=base_item.visual.rotation,
                    color_tint=base_item.visual.color_tint
                ),
                audio=ItemAudio(
                    use_sound=base_item.audio.use_sound,
                    equip_sound=base_item.audio.equip_sound,
                    unequip_sound=base_item.audio.unequip_sound,
                    hit_sound=base_item.audio.hit_sound,
                    break_sound=base_item.audio.break_sound,
                    ambient_sound=base_item.audio.ambient_sound,
                    volume=base_item.audio.volume,
                    pitch=base_item.audio.pitch
                ),
                is_tradeable=base_item.is_tradeable,
                is_droppable=base_item.is_droppable,
                is_destroyable=base_item.is_destroyable,
                bind_on_pickup=base_item.bind_on_pickup,
                bind_on_equip=base_item.bind_on_equip,
                bind_on_use=base_item.bind_on_use,
                upgrade_level=base_item.upgrade_level,
                max_upgrade_level=base_item.max_upgrade_level,
                upgrade_cost_multiplier=base_item.upgrade_cost_multiplier,
                socket_count=base_item.socket_count,
                socketed_gems=base_item.socketed_gems.copy(),
                set_name=base_item.set_name,
                set_bonus=base_item.set_bonus.copy(),
                created_by=base_item.created_by,
                created_date=base_item.created_date,
                last_modified=time.time(),
                version=base_item.version
            )
            
            # Применяем дополнительные данные
            if item_data:
                for key, value in item_data.items():
                    if hasattr(new_item, key):
                        setattr(new_item, key, value)
            
            # Инициализируем предметы сущности, если нужно
            if entity_id not in self.entity_items:
                self.entity_items[entity_id] = []
            
            # Проверяем лимит предметов
            if len(self.entity_items[entity_id]) >= self.system_settings['max_items_per_entity']:
                logger.warning(f"Достигнут лимит предметов для сущности {entity_id}")
                return False
            
            # Добавляем предмет
            self.entity_items[entity_id].append(new_item)
            
            # Записываем в историю
            current_time = time.time()
            self.item_history.append({
                'timestamp': current_time,
                'action': 'created',
                'item_id': new_item.item_id,
                'base_item_id': item_id,
                'entity_id': entity_id,
                'item_level': new_item.level,
                'item_quality': new_item.quality.value
            })
            
            self.system_stats['items_created_today'] += 1
            logger.info(f"Предмет {item_id} создан для сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания предмета {item_id} для сущности {entity_id}: {e}")
            return False
    
    def destroy_item_from_entity(self, entity_id: str, item_id: str) -> bool:
        """Уничтожение предмета у сущности"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            items = self.entity_items[entity_id]
            item_to_remove = None
            
            for item in items:
                if item.item_id == item_id:
                    item_to_remove = item
                    break
            
            if not item_to_remove:
                return False
            
            # Удаляем предмет
            items.remove(item_to_remove)
            
            # Удаляем пустые записи
            if not items:
                del self.entity_items[entity_id]
            
            # Записываем в историю
            current_time = time.time()
            self.item_history.append({
                'timestamp': current_time,
                'action': 'destroyed',
                'item_id': item_id,
                'entity_id': entity_id,
                'item_level': item_to_remove.level
            })
            
            self.system_stats['items_destroyed_today'] += 1
            logger.info(f"Предмет {item_id} уничтожен у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения предмета {item_id} у сущности {entity_id}: {e}")
            return False
    
    def use_item(self, entity_id: str, item_id: str, target_id: Optional[str] = None) -> bool:
        """Использование предмета"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            item_to_use = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_use = item
                    break
            
            if not item_to_use:
                logger.warning(f"Предмет {item_id} не найден у сущности {entity_id}")
                return False
            
            # Проверяем тип предмета
            if item_to_use.item_type == ItemType.CONSUMABLE:
                return self._use_consumable_item(entity_id, item_to_use, target_id)
            elif item_to_use.item_type == ItemType.WEAPON:
                return self._use_weapon_item(entity_id, item_to_use, target_id)
            elif item_to_use.item_type == ItemType.ARMOR:
                return self._use_armor_item(entity_id, item_to_use, target_id)
            else:
                logger.debug(f"Предмет {item_id} не может быть использован")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка использования предмета {item_id} сущностью {entity_id}: {e}")
            return False
    
    def _use_consumable_item(self, entity_id: str, item: Item, target_id: Optional[str]) -> bool:
        """Использование расходуемого предмета"""
        try:
            # Уменьшаем количество
            if item.stack_size > 1:
                item.stack_size -= 1
                logger.debug(f"Использован расходуемый предмет {item.item_id} у {entity_id}")
                # Эмитим событие для применения эффектов расходника
                try:
                    if self.event_bus and item.special_effects:
                        for se in item.special_effects:
                            effect_id = getattr(se, 'effect_id', None)
                            if effect_id:
                                self.event_bus.emit("apply_effect", {
                                    'target_id': target_id or entity_id,
                                    'effect_id': effect_id,
                                    'applied_by': entity_id
                                })
                except Exception:
                    pass
                return True
            else:
                # Предмет полностью израсходован
                used = self.destroy_item_from_entity(entity_id, item.item_id)
                try:
                    if used and self.event_bus and item.special_effects:
                        for se in item.special_effects:
                            effect_id = getattr(se, 'effect_id', None)
                            if effect_id:
                                self.event_bus.emit("apply_effect", {
                                    'target_id': target_id or entity_id,
                                    'effect_id': effect_id,
                                    'applied_by': entity_id
                                })
                except Exception:
                    pass
                return used
                
        except Exception as e:
            logger.error(f"Ошибка использования расходуемого предмета {item.item_id}: {e}")
            return False
    
    def _use_weapon_item(self, entity_id: str, item: Item, target_id: Optional[str]) -> bool:
        """Использование оружия"""
        try:
            # Оружие используется в бою, здесь просто логируем
            logger.debug(f"Оружие {item.item_id} готово к использованию у {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования оружия {item.item_id}: {e}")
            return False
    
    def _use_armor_item(self, entity_id: str, item: Item, target_id: Optional[str]) -> bool:
        """Использование брони"""
        try:
            # Броня надевается, здесь просто логируем
            logger.debug(f"Броня {item.item_id} готова к использованию у {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования брони {item.item_id}: {e}")
            return False
    
    def upgrade_item(self, entity_id: str, item_id: str, new_level: int) -> bool:
        """Улучшение предмета"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            item_to_upgrade = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_upgrade = item
                    break
            
            if not item_to_upgrade:
                logger.warning(f"Предмет {item_id} не найден у сущности {entity_id}")
                return False
            
            if new_level <= item_to_upgrade.level:
                logger.warning(f"Новый уровень {new_level} должен быть больше текущего {item_to_upgrade.level}")
                return False
            
            if new_level > self.system_settings['max_item_level']:
                logger.warning(f"Новый уровень {new_level} превышает максимальный {self.system_settings['max_item_level']}")
                return False
            
            # Улучшаем предмет
            old_level = item_to_upgrade.level
            item_to_upgrade.level = new_level
            
            # Улучшаем характеристики предмета
            self._upgrade_item_stats(item_to_upgrade, old_level, new_level)
            
            # Записываем в историю
            current_time = time.time()
            self.item_history.append({
                'timestamp': current_time,
                'action': 'upgraded',
                'item_id': item_id,
                'entity_id': entity_id,
                'old_level': old_level,
                'new_level': new_level
            })
            
            self.system_stats['items_upgraded_today'] += 1
            logger.info(f"Предмет {item_id} сущности {entity_id} улучшен до уровня {new_level}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка улучшения предмета {item_id} сущности {entity_id}: {e}")
            return False
    
    def _upgrade_item_stats(self, item: Item, old_level: int, new_level: int) -> None:
        """Улучшение характеристик предмета"""
        try:
            level_multiplier = 1 + (new_level - old_level) * 0.15  # 15% за уровень
            
            # Улучшаем характеристики
            for stat_type, value in item.stats.items():
                item.stats[stat_type] = int(value * level_multiplier)
            
            # Улучшаем урон
            if item.damage > 0:
                item.damage = int(item.damage * level_multiplier)
            
            # Улучшаем броню
            if item.armor > 0:
                item.armor = int(item.armor * level_multiplier)
            
            # Улучшаем стоимость
            item.value = int(item.value * level_multiplier)
            
        except Exception as e:
            logger.error(f"Ошибка улучшения характеристик предмета {item.item_id}: {e}")
    
    def get_entity_items(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение предметов сущности"""
        try:
            if entity_id not in self.entity_items:
                return []
            
            items_info = []
            
            for item in self.entity_items[entity_id]:
                items_info.append({
                    'item_id': item.item_id,
                    'name': item.name,
                    'description': item.description,
                    'item_type': item.item_type.value,
                    'category': item.category.value,
                    'rarity': item.rarity.value,
                    'level': item.level,
                    'stack_size': item.stack_size,
                    'max_stack': item.max_stack,
                    'weight': item.weight,
                    'value': item.value,
                    'durability': item.durability,
                    'max_durability': item.durability.maximum,
                    'damage': item.damage,
                    'damage_type': item.damage_type.value if item.damage_type else None,
                    'armor': item.armor,
                    'icon': item.icon
                })
            
            return items_info
            
        except Exception as e:
            logger.error(f"Ошибка получения предметов сущности {entity_id}: {e}")
            return []
    
    def get_item_info(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о предмете"""
        try:
            if item_id not in self.registered_items:
                return None
            
            item = self.registered_items[item_id]
            
            return {
                'item_id': item.item_id,
                'name': item.name,
                'description': item.description,
                'item_type': item.item_type.value,
                'category': item.category.value,
                'rarity': item.rarity.value,
                'level': item.level,
                'stack_size': item.stack_size,
                'max_stack': item.max_stack,
                'weight': item.weight,
                'value': item.value,
                'durability': item.durability,
                'max_durability': item.durability.maximum,
                'requirements': item.requirements,
                'stats': {stat.value: value for stat, value in item.stats.items()},
                'damage': item.damage,
                'damage_type': item.damage_type.value if item.damage_type else None,
                'armor': item.armor,
                'icon': item.icon,
                'model': item.model,
                'sound': item.sound
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о предмете {item_id}: {e}")
            return None
    
    def register_custom_item(self, item: Item) -> bool:
        """Регистрация пользовательского предмета"""
        try:
            if item.item_id in self.registered_items:
                logger.warning(f"Предмет {item.item_id} уже зарегистрирован")
                return False
            
            self.registered_items[item.item_id] = item
            logger.info(f"Зарегистрирован пользовательский предмет {item.item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользовательского предмета {item.item_id}: {e}")
            return False
    
    def get_items_by_category(self, category: ItemCategory) -> List[Dict[str, Any]]:
        """Получение предметов по категории"""
        try:
            items = []
            
            for item in self.registered_items.values():
                if item.category == category:
                    items.append({
                        'item_id': item.item_id,
                        'name': item.name,
                        'description': item.description,
                        'item_type': item.item_type.value,
                        'rarity': item.rarity.value,
                        'level': item.level,
                        'icon': item.icon
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Ошибка получения предметов по категории {category.value}: {e}")
            return []
    
    def get_items_by_rarity(self, rarity: ItemRarity) -> List[Dict[str, Any]]:
        """Получение предметов по редкости"""
        try:
            items = []
            
            for item in self.registered_items.values():
                if item.rarity == rarity:
                    items.append({
                        'item_id': item.item_id,
                        'name': item.name,
                        'description': item.description,
                        'item_type': item.item_type.value,
                        'category': item.category.value,
                        'level': item.level,
                        'icon': item.icon
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Ошибка получения предметов по редкости {rarity.value}: {e}")
            return []
    
    def repair_item(self, entity_id: str, item_id: str) -> bool:
        """Ремонт предмета"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            item_to_repair = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_repair = item
                    break
            
            if not item_to_repair:
                return False
            
            if item_to_repair.durability.current >= item_to_repair.durability.maximum:
                logger.debug(f"Предмет {item_id} не нуждается в ремонте")
                return True
            
            # Восстанавливаем прочность
            item_to_repair.durability.current = item_to_repair.durability.maximum
            
            logger.info(f"Предмет {item_id} отремонтирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка ремонта предмета {item_id} у сущности {entity_id}: {e}")
            return False
    
    def upgrade_item_quality(self, entity_id: str, item_id: str, new_quality: ItemQuality) -> bool:
        """Улучшение качества предмета"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            item_to_upgrade = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_upgrade = item
                    break
            
            if not item_to_upgrade:
                return False
            
            if new_quality.value <= item_to_upgrade.quality.value:
                logger.warning(f"Новое качество {new_quality.value} должно быть больше текущего {item_to_upgrade.quality.value}")
                return False
            
            # Улучшаем качество
            old_quality = item_to_upgrade.quality
            item_to_upgrade.quality = new_quality
            
            # Применяем бонусы качества
            self._apply_quality_bonuses(item_to_upgrade, old_quality, new_quality)
            
            # Обновляем метаданные
            item_to_upgrade.last_modified = time.time()
            
            logger.info(f"Качество предмета {item_id} улучшено с {old_quality.name} до {new_quality.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка улучшения качества предмета {item_id}: {e}")
            return False
    
    def _apply_quality_bonuses(self, item: Item, old_quality: ItemQuality, new_quality: ItemQuality) -> None:
        """Применение бонусов качества к предмету"""
        try:
            quality_multiplier = 1.0 + (new_quality.value - old_quality.value) * 0.1
            
            # Улучшаем характеристики
            for stat_type, value in item.stats.items():
                item.stats[stat_type] = int(value * quality_multiplier)
            
            # Улучшаем урон
            if item.damage > 0:
                item.damage = int(item.damage * quality_multiplier)
            
            # Улучшаем броню
            if item.armor > 0:
                item.armor = int(item.armor * quality_multiplier)
            
            # Улучшаем стоимость
            item.value = int(item.value * quality_multiplier)
            
            # Улучшаем прочность
            if item.durability.quality_affects_durability:
                item.durability.maximum = int(item.durability.maximum * quality_multiplier)
                item.durability.current = item.durability.maximum
            
        except Exception as e:
            logger.error(f"Ошибка применения бонусов качества к предмету {item.item_id}: {e}")
    
    def socket_gem(self, entity_id: str, item_id: str, gem_id: str) -> bool:
        """Вставка камня в гнездо предмета"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            item_to_socket = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_socket = item
                    break
            
            if not item_to_socket:
                return False
            
            if item_to_socket.socket_count <= len(item_to_socket.socketed_gems):
                logger.warning(f"У предмета {item_id} нет свободных гнезд")
                return False
            
            # Добавляем камень
            item_to_socket.socketed_gems.append(gem_id)
            
            # Применяем эффекты камня
            self._apply_gem_effects(item_to_socket, gem_id)
            
            # Обновляем метаданные
            item_to_socket.last_modified = time.time()
            
            logger.info(f"Камень {gem_id} вставлен в предмет {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка вставки камня {gem_id} в предмет {item_id}: {e}")
            return False
    
    def _apply_gem_effects(self, item: Item, gem_id: str) -> None:
        """Применение эффектов камня к предмету"""
        try:
            # Здесь должна быть логика применения эффектов камня
            # Пока просто логируем
            logger.debug(f"Применяются эффекты камня {gem_id} к предмету {item.item_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов камня {gem_id}: {e}")
    
    def remove_gem(self, entity_id: str, item_id: str, gem_index: int) -> Optional[str]:
        """Удаление камня из гнезда"""
        try:
            if entity_id not in self.entity_items:
                return None
            
            item_to_unsocket = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_unsocket = item
                    break
            
            if not item_to_unsocket:
                return None
            
            if gem_index >= len(item_to_unsocket.socketed_gems):
                logger.warning(f"Индекс камня {gem_index} превышает количество вставленных камней")
                return None
            
            # Удаляем камень
            removed_gem = item_to_unsocket.socketed_gems.pop(gem_index)
            
            # Убираем эффекты камня
            self._remove_gem_effects(item_to_unsocket, removed_gem)
            
            # Обновляем метаданные
            item_to_unsocket.last_modified = time.time()
            
            logger.info(f"Камень {removed_gem} удален из предмета {item_id}")
            return removed_gem
            
        except Exception as e:
            logger.error(f"Ошибка удаления камня из предмета {item_id}: {e}")
            return None
    
    def _remove_gem_effects(self, item: Item, gem_id: str) -> None:
        """Удаление эффектов камня с предмета"""
        try:
            # Здесь должна быть логика удаления эффектов камня
            # Пока просто логируем
            logger.debug(f"Удаляются эффекты камня {gem_id} с предмета {item.item_id}")
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффектов камня {gem_id}: {e}")
    
    def get_set_bonus(self, entity_id: str, set_name: str) -> Dict[str, Any]:
        """Получение бонуса набора предметов"""
        try:
            if entity_id not in self.entity_items:
                return {}
            
            set_items = []
            for item in self.entity_items[entity_id]:
                if item.set_name == set_name:
                    set_items.append(item)
            
            if not set_items:
                return {}
            
            # Подсчитываем количество предметов набора
            set_count = len(set_items)
            
            # Получаем бонусы набора
            set_bonuses = {}
            for item in set_items:
                for bonus_name, bonus_value in item.set_bonus.items():
                    if bonus_name not in set_bonuses:
                        set_bonuses[bonus_name] = 0
                    set_bonuses[bonus_name] += bonus_value
            
            # Применяем множители за количество предметов
            if set_count >= 2:
                for bonus_name in set_bonuses:
                    set_bonuses[bonus_name] = int(set_bonuses[bonus_name] * (1 + (set_count - 1) * 0.2))
            
            return {
                'set_name': set_name,
                'items_count': set_count,
                'bonuses': set_bonuses
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения бонуса набора {set_name}: {e}")
            return {}
    
    def check_item_requirements(self, entity_id: str, item_id: str, entity_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка требований предмета"""
        try:
            if entity_id not in self.entity_items:
                return {'can_use': False, 'missing_requirements': []}
            
            item_to_check = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_check = item
                    break
            
            if not item_to_check:
                return {'can_use': False, 'missing_requirements': ['item_not_found']}
            
            missing_requirements = []
            
            for requirement in item_to_check.requirements:
                if not self._check_single_requirement(requirement, entity_stats):
                    missing_requirements.append({
                        'type': requirement.requirement_type,
                        'value': requirement.requirement_value,
                        'comparison': requirement.comparison,
                        'description': requirement.description
                    })
            
            can_use = len(missing_requirements) == 0
            
            return {
                'can_use': can_use,
                'missing_requirements': missing_requirements,
                'item_level': item_to_check.level,
                'item_quality': item_to_check.quality.value
            }
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований предмета {item_id}: {e}")
            return {'can_use': False, 'missing_requirements': ['error']}
    
    def _check_single_requirement(self, requirement: ItemRequirement, entity_stats: Dict[str, Any]) -> bool:
        """Проверка одного требования"""
        try:
            if requirement.requirement_type not in entity_stats:
                return False
            
            entity_value = entity_stats[requirement.requirement_type]
            required_value = requirement.requirement_value
            
            if requirement.comparison == ">=":
                return entity_value >= required_value
            elif requirement.comparison == "==":
                return entity_value == required_value
            elif requirement.comparison == "<=":
                return entity_value <= required_value
            elif requirement.comparison == ">":
                return entity_value > required_value
            elif requirement.comparison == "<":
                return entity_value < required_value
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка проверки требования {requirement.requirement_type}: {e}")
            return False
    
    def get_item_effects_summary(self, entity_id: str, item_id: str) -> Dict[str, Any]:
        """Получение сводки эффектов предмета"""
        try:
            if entity_id not in self.entity_items:
                return {}
            
            item_to_analyze = None
            for item in self.entity_items[entity_id]:
                if item.item_id == item_id:
                    item_to_analyze = item
                    break
            
            if not item_to_analyze:
                return {}
            
            effects_summary = {
                'passive_effects': [],
                'triggered_effects': [],
                'visual_effects': [],
                'audio_effects': [],
                'set_bonuses': {},
                'socket_effects': []
            }
            
            # Анализируем специальные эффекты
            for effect in item_to_analyze.special_effects:
                if effect.trigger == EffectTrigger.PASSIVE:
                    effects_summary['passive_effects'].append({
                        'name': effect.name,
                        'category': effect.category.value,
                        'parameters': effect.parameters
                    })
                else:
                    effects_summary['triggered_effects'].append({
                        'name': effect.name,
                        'trigger': effect.trigger.value,
                        'chance': effect.chance,
                        'duration': effect.duration
                    })
                
                # Визуальные эффекты
                if effect.visual_effect:
                    effects_summary['visual_effects'].append(effect.visual_effect)
                if effect.particle_effect:
                    effects_summary['visual_effects'].append(effect.particle_effect)
                
                # Аудио эффекты
                if effect.sound_effect:
                    effects_summary['audio_effects'].append(effect.sound_effect)
            
            # Бонусы набора
            if item_to_analyze.set_name:
                set_bonus = self.get_set_bonus(entity_id, item_to_analyze.set_name)
                if set_bonus:
                    effects_summary['set_bonuses'] = set_bonus
            
            # Эффекты камней
            for gem_id in item_to_analyze.socketed_gems:
                effects_summary['socket_effects'].append({
                    'gem_id': gem_id,
                    'effect_type': 'socket_bonus'
                })
            
            return effects_summary
            
        except Exception as e:
            logger.error(f"Ошибка получения сводки эффектов предмета {item_id}: {e}")
            return {}
    
    def combine_items(self, entity_id: str, item_ids: List[str]) -> Optional[Item]:
        """Объединение предметов"""
        try:
            if not self.system_settings['item_combining_enabled']:
                logger.warning("Объединение предметов отключено")
                return None
            
            if len(item_ids) < 2:
                logger.warning("Для объединения нужно минимум 2 предмета")
                return None
            
            if entity_id not in self.entity_items:
                return None
            
            # Проверяем, что все предметы принадлежат сущности
            items_to_combine = []
            for item_id in item_ids:
                item_found = False
                for item in self.entity_items[entity_id]:
                    if item.item_id == item_id:
                        items_to_combine.append(item)
                        item_found = True
                        break
                
                if not item_found:
                    logger.warning(f"Предмет {item_id} не найден у сущности {entity_id}")
                    return None
            
            # Простая логика объединения - создаем улучшенный предмет
            base_item = items_to_combine[0]
            
            # Создаем новый предмет с улучшенными характеристиками
            combined_item = Item(
                item_id=f"combined_{int(time.time() * 1000)}",
                name=f"Улучшенный {base_item.name}",
                description=f"Улучшенная версия {base_item.name}",
                item_type=base_item.item_type,
                category=base_item.category,
                rarity=base_item.rarity,
                quality=ItemQuality(min(base_item.quality.value + 1, ItemQuality.LEGENDARY.value)),
                level=base_item.level + 1,
                stack_size=1,
                max_stack=1,
                weight=base_item.weight,
                value=int(base_item.value * 1.5),
                durability=ItemDurability(
                    current=base_item.durability.maximum,
                    maximum=base_item.durability.maximum,
                    decay_rate=base_item.durability.decay_rate * 0.8
                ),
                requirements=base_item.requirements.copy(),
                stats={stat: int(value * 1.2) for stat, value in base_item.stats.items()},
                damage=int(base_item.damage * 1.2) if base_item.damage > 0 else 0,
                damage_type=base_item.damage_type,
                armor=int(base_item.armor * 1.2) if base_item.armor > 0 else 0,
                special_effects=base_item.special_effects.copy(),
                visual=ItemVisual(
                    model_path=base_item.visual.model_path,
                    texture_path=base_item.visual.texture_path,
                    icon_path=base_item.visual.icon_path,
                    particle_effect=base_item.visual.particle_effect,
                    glow_effect=base_item.visual.glow_effect,
                    animation_path=base_item.visual.animation_path,
                    scale=base_item.visual.scale,
                    rotation=base_item.visual.rotation,
                    color_tint=base_item.visual.color_tint
                ),
                audio=ItemAudio(
                    use_sound=base_item.audio.use_sound,
                    equip_sound=base_item.audio.equip_sound,
                    unequip_sound=base_item.audio.unequip_sound,
                    hit_sound=base_item.audio.hit_sound,
                    break_sound=base_item.audio.break_sound,
                    ambient_sound=base_item.audio.ambient_sound,
                    volume=base_item.audio.volume,
                    pitch=base_item.audio.pitch
                ),
                is_tradeable=base_item.is_tradeable,
                is_droppable=base_item.is_droppable,
                is_destroyable=base_item.is_destroyable,
                bind_on_pickup=base_item.bind_on_pickup,
                bind_on_equip=base_item.bind_on_equip,
                bind_on_use=base_item.bind_on_use,
                upgrade_level=base_item.upgrade_level,
                max_upgrade_level=base_item.max_upgrade_level,
                upgrade_cost_multiplier=base_item.upgrade_cost_multiplier,
                socket_count=base_item.socket_count + 1,
                socketed_gems=base_item.socketed_gems.copy(),
                set_name=base_item.set_name,
                set_bonus=base_item.set_bonus.copy(),
                created_by=base_item.created_by,
                created_date=time.time(),
                last_modified=time.time(),
                version="2.0"
            )
            
            # Удаляем исходные предметы
            for item in items_to_combine:
                self.destroy_item_from_entity(entity_id, item.item_id)
            
            # Добавляем объединенный предмет
            self.entity_items[entity_id].append(combined_item)
            
            logger.info(f"Предметы объединены в {combined_item.name} для сущности {entity_id}")
            return combined_item
            
        except Exception as e:
            logger.error(f"Ошибка объединения предметов для сущности {entity_id}: {e}")
            return None

class ItemFactory:
    """Фабрика для создания предметов"""
    
    @staticmethod
    def create_enhanced_fire_sword() -> Item:
        """Создание улучшенного огненного меча"""
        return Item(
            item_id="enhanced_fire_sword",
            name="Улучшенный Огненный Меч",
            description="Мощный меч, зачарованный огнем",
            item_type=ItemType.WEAPON,
            category=ItemCategory.MELEE,
            rarity=ItemRarity.RARE,
            quality=ItemQuality.EXCELLENT,
            level=5,
            stack_size=1,
            max_stack=1,
            weight=3.0,
            value=500,
            durability=ItemDurability(current=100, maximum=100, decay_rate=0.05),
            requirements=[
                ItemRequirement(requirement_type="strength", requirement_value=15, comparison=">=", description="Требуется сила 15"),
                ItemRequirement(requirement_type="level", requirement_value=5, comparison=">=", description="Требуется уровень 5")
            ],
            stats={StatType.STRENGTH: 8, StatType.AGILITY: 3},
            damage=25,
            damage_type=DamageType.FIRE,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="fire_burn",
                    name="Огненное Пламя",
                    effect_type="damage_over_time",
                    category=EffectCategory.DEBUFF,
                    trigger=EffectTrigger.ON_HIT,
                    parameters={"damage": 5, "duration": 3.0},
                    duration=3.0,
                    chance=0.3,
                    visual_effect="fire_particle",
                    sound_effect="fire_burn_sound",
                    particle_effect="fire_particle_effect"
                )
            ],
            visual=ItemVisual(
                icon_path="fire_sword_icon",
                model_path="fire_sword_model",
                glow_effect="fire_glow",
                particle_effect="fire_trail"
            ),
            audio=ItemAudio(
                use_sound="fire_sword_sound",
                hit_sound="fire_hit_sound",
                ambient_sound="fire_ambient"
            ),
            socket_count=2,
            set_name="Огненный Брон",
            set_bonus={"fire_damage_multiplier": 1.2},
            created_by="GameMaster",
            version="1.1"
        )
    
    @staticmethod
    def create_lightning_ring() -> Item:
        """Создание кольца молний"""
        return Item(
            item_id="lightning_ring",
            name="Кольцо Молний",
            description="Кольцо, усиливающее электрические атаки",
            item_type=ItemType.ACCESSORY,
            category=ItemCategory.RING,
            rarity=ItemRarity.EPIC,
            quality=ItemQuality.MASTERWORK,
            level=3,
            stack_size=1,
            max_stack=1,
            weight=0.1,
            value=300,
            durability=ItemDurability(current=100, maximum=100, decay_rate=0.02),
            requirements=[
                ItemRequirement(requirement_type="intelligence", requirement_value=12, comparison=">=", description="Требуется интеллект 12"),
                ItemRequirement(requirement_type="level", requirement_value=3, comparison=">=", description="Требуется уровень 3")
            ],
            stats={StatType.INTELLIGENCE: 5, StatType.WISDOM: 3},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="lightning_boost",
                    name="Усиление Молний",
                    effect_type="damage_boost",
                    category=EffectCategory.BUFF,
                    trigger=EffectTrigger.ON_HIT,
                    parameters={"damage_multiplier": 1.5, "damage_type": "lightning"},
                    duration=0.0,
                    chance=1.0,
                    visual_effect="lightning_particle",
                    sound_effect="lightning_boost_sound",
                    particle_effect="lightning_particle_effect"
                )
            ],
            visual=ItemVisual(
                icon_path="lightning_ring_icon",
                model_path="lightning_ring_model",
                glow_effect="lightning_glow",
                particle_effect="lightning_sparkle"
            ),
            audio=ItemAudio(
                use_sound="lightning_ring_sound",
                ambient_sound="lightning_ambient"
            ),
            socket_count=1,
            set_name="Электрический Брон",
            set_bonus={"lightning_damage_multiplier": 1.1},
            created_by="GameMaster",
            version="1.1"
        )
    
    @staticmethod
    def create_health_potion() -> Item:
        """Создание зелья здоровья"""
        return Item(
            item_id="health_potion",
            name="Зелье Здоровья",
            description="Восстанавливает здоровье",
            item_type=ItemType.CONSUMABLE,
            category=ItemCategory.POTION,
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.GOOD,
            level=1,
            stack_size=1,
            max_stack=10,
            weight=0.5,
            value=50,
            durability=ItemDurability(current=100, maximum=100, decay_rate=0.01),
            requirements=[],
            stats={},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="heal",
                    name="Исцеление",
                    effect_type="heal",
                    category=EffectCategory.HEALING,
                    trigger=EffectTrigger.ON_USE,
                    parameters={"heal_amount": 50},
                    duration=0.0,
                    chance=1.0,
                    visual_effect="heal_particle",
                    sound_effect="heal_sound",
                    particle_effect="heal_particle_effect"
                )
            ],
            visual=ItemVisual(
                icon_path="health_potion_icon",
                model_path="health_potion_model",
                glow_effect="health_glow"
            ),
            audio=ItemAudio(
                use_sound="health_potion_sound"
            ),
            set_name="Здоровье",
            set_bonus={"health_regeneration": 1.0},
            created_by="GameMaster",
            version="1.1"
        )
    
    @staticmethod
    def create_mana_potion() -> Item:
        """Создание зелья маны"""
        return Item(
            item_id="mana_potion",
            name="Зелье Маны",
            description="Восстанавливает ману",
            item_type=ItemType.CONSUMABLE,
            category=ItemCategory.POTION,
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.GOOD,
            level=1,
            stack_size=1,
            max_stack=10,
            weight=0.5,
            value=50,
            durability=ItemDurability(current=100, maximum=100, decay_rate=0.01),
            requirements=[],
            stats={},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="mana_restore",
                    name="Восстановление Маны",
                    effect_type="mana_restore",
                    category=EffectCategory.HEALING,
                    trigger=EffectTrigger.ON_USE,
                    parameters={"mana_amount": 50},
                    duration=0.0,
                    chance=1.0,
                    visual_effect="mana_particle",
                    sound_effect="mana_sound",
                    particle_effect="mana_particle_effect"
                )
            ],
            visual=ItemVisual(
                icon_path="mana_potion_icon",
                model_path="mana_potion_model",
                glow_effect="mana_glow"
            ),
            audio=ItemAudio(
                use_sound="mana_potion_sound"
            ),
            set_name="Мана",
            set_bonus={"mana_regeneration": 1.0},
            created_by="GameMaster",
            version="1.1"
        )
