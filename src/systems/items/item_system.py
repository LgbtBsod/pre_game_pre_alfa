#!/usr/bin/env python3
"""
Система предметов - управление игровыми предметами и их свойствами
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem, Priority
from ...core.constants import (
    ItemType, ItemRarity, ItemCategory, DamageType, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class SpecialEffect:
    """Специальный эффект предмета"""
    effect_id: str
    name: str
    effect_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    chance: float = 1.0

@dataclass
class Item:
    """Игровой предмет"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    category: ItemCategory
    rarity: ItemRarity
    level: int = 1
    stack_size: int = 1
    max_stack: int = 1
    weight: float = 0.0
    value: int = 0
    durability: int = 100
    max_durability: int = 100
    requirements: Dict[str, Any] = field(default_factory=dict)
    stats: Dict[StatType, int] = field(default_factory=dict)
    damage: int = 0
    damage_type: Optional[DamageType] = None
    armor: int = 0
    special_effects: List[SpecialEffect] = field(default_factory=list)
    icon: str = ""
    model: str = ""
    sound: str = ""

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
            'max_items_per_entity': SYSTEM_LIMITS["max_items_per_entity"],
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
            if self._system_state != SystemState.READY:
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
                    if item.durability < item.max_durability:
                        # Простой износ со временем
                        decay_rate = 0.1  # 0.1 единицы в секунду
                        item.durability = max(0, item.durability - decay_rate * delta_time)
                        
                        # Если предмет полностью изношен
                        if item.durability <= 0:
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
            
            # Создаем копию предмета
            new_item = Item(
                item_id=f"{item_id}_{int(time.time() * 1000)}",
                name=base_item.name,
                description=base_item.description,
                item_type=base_item.item_type,
                category=base_item.category,
                rarity=base_item.rarity,
                level=base_item.level,
                stack_size=base_item.stack_size,
                max_stack=base_item.max_stack,
                weight=base_item.weight,
                value=base_item.value,
                durability=base_item.durability,
                max_durability=base_item.max_durability,
                requirements=base_item.requirements.copy(),
                stats=base_item.stats.copy(),
                damage=base_item.damage,
                damage_type=base_item.damage_type,
                armor=base_item.armor,
                special_effects=base_item.special_effects.copy(),
                icon=base_item.icon,
                model=base_item.model,
                sound=base_item.sound
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
                'item_level': new_item.level
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
                return True
            else:
                # Предмет полностью израсходован
                return self.destroy_item_from_entity(entity_id, item.item_id)
                
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
                    'max_durability': item.max_durability,
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
                'max_durability': item.max_durability,
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
            
            if item_to_repair.durability >= item_to_repair.max_durability:
                logger.debug(f"Предмет {item_id} не нуждается в ремонте")
                return True
            
            # Восстанавливаем прочность
            item_to_repair.durability = item_to_repair.max_durability
            
            logger.info(f"Предмет {item_id} отремонтирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка ремонта предмета {item_id} у сущности {entity_id}: {e}")
            return False
    
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
                level=base_item.level + 1,
                stack_size=1,
                max_stack=1,
                weight=base_item.weight,
                value=int(base_item.value * 1.5),
                durability=base_item.max_durability,
                max_durability=base_item.max_durability,
                requirements=base_item.requirements.copy(),
                stats={stat: int(value * 1.2) for stat, value in base_item.stats.items()},
                damage=int(base_item.damage * 1.2) if base_item.damage > 0 else 0,
                damage_type=base_item.damage_type,
                armor=int(base_item.armor * 1.2) if base_item.armor > 0 else 0,
                special_effects=base_item.special_effects.copy(),
                icon=base_item.icon,
                model=base_item.model,
                sound=base_item.sound
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
            level=5,
            stack_size=1,
            max_stack=1,
            weight=3.0,
            value=500,
            durability=100,
            max_durability=100,
            requirements={"strength": 15, "level": 5},
            stats={StatType.STRENGTH: 8, StatType.AGILITY: 3},
            damage=25,
            damage_type=DamageType.FIRE,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="fire_burn",
                    name="Огненное Пламя",
                    effect_type="damage_over_time",
                    parameters={"damage": 5, "duration": 3.0},
                    duration=3.0,
                    chance=0.3
                )
            ],
            icon="fire_sword_icon",
            model="fire_sword_model",
            sound="fire_sword_sound"
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
            level=3,
            stack_size=1,
            max_stack=1,
            weight=0.1,
            value=300,
            durability=100,
            max_durability=100,
            requirements={"intelligence": 12, "level": 3},
            stats={StatType.INTELLIGENCE: 5, StatType.WISDOM: 3},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="lightning_boost",
                    name="Усиление Молний",
                    effect_type="damage_boost",
                    parameters={"damage_multiplier": 1.5, "damage_type": "lightning"},
                    duration=0.0,
                    chance=1.0
                )
            ],
            icon="lightning_ring_icon",
            model="lightning_ring_model",
            sound="lightning_ring_sound"
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
            level=1,
            stack_size=1,
            max_stack=10,
            weight=0.5,
            value=50,
            durability=100,
            max_durability=100,
            requirements={},
            stats={},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="heal",
                    name="Исцеление",
                    effect_type="heal",
                    parameters={"heal_amount": 50},
                    duration=0.0,
                    chance=1.0
                )
            ],
            icon="health_potion_icon",
            model="health_potion_model",
            sound="health_potion_sound"
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
            level=1,
            stack_size=1,
            max_stack=10,
            weight=0.5,
            value=50,
            durability=100,
            max_durability=100,
            requirements={},
            stats={},
            damage=0,
            damage_type=None,
            armor=0,
            special_effects=[
                SpecialEffect(
                    effect_id="mana_restore",
                    name="Восстановление Маны",
                    effect_type="mana_restore",
                    parameters={"mana_amount": 50},
                    duration=0.0,
                    chance=1.0
                )
            ],
            icon="mana_potion_icon",
            model="mana_potion_model",
            sound="mana_potion_sound"
        )
