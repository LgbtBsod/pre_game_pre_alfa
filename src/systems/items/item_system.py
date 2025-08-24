#!/usr/bin/env python3
"""
Система предметов - управление предметами и их специальными эффектами
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

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
    defense: int = 0
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
        self.special_effects: List[Any] = []  # Упрощено для совместимости
        self.required_level: int = 1
        self.stack_size: int = 1
        self.max_stack: int = 1
        self.icon: Optional[str] = None
        self.model: Optional[str] = None
        
    def add_special_effect(self, effect: Any):
        """Добавляет специальный эффект к предмету"""
        self.special_effects.append(effect)
    
    def get_effects_for_trigger(self, trigger_type) -> List[Any]:
        """Возвращает эффекты для определенного триггера"""
        return [effect for effect in self.special_effects if hasattr(effect, 'trigger_condition') and effect.trigger_condition == trigger_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация предмета"""
        return {
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "rarity": self.rarity.value,
            "special_effects": [effect.to_dict() if hasattr(effect, 'to_dict') else str(effect) for effect in self.special_effects],
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
                 damage_type: str, slot: str, rarity: ItemRarity = ItemRarity.COMMON):
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
            "damage_type": self.damage_type,
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
            damage_type=data["damage_type"],
            slot=data["slot"],
            rarity=ItemRarity(data["rarity"])
        )
        
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
        
        # Восстанавливаем остальные свойства
        accessory.required_level = data.get("required_level", 1)
        
        return accessory

class Consumable(BaseItem):
    """Класс расходуемых предметов"""
    
    def __init__(self, name: str, description: str, effects: List[Any], 
                 rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(name, description, ItemType.CONSUMABLE, rarity)
        self.effects = effects
        self.max_stack = 99  # Расходуемые предметы можно складывать
        
    def use(self, target: Any):
        """Использует расходуемый предмет"""
        for effect in self.effects:
            if hasattr(effect, 'apply_instant'):
                effect.apply_instant(self, target)
            elif hasattr(effect, 'apply'):
                effect.apply(self, target)
        
        # Уменьшаем количество предметов
        self.stack_size -= 1
        
        logger.info(f"Использован предмет: {self.name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация расходуемого предмета"""
        data = super().to_dict()
        data.update({
            "effects": [effect.to_dict() if hasattr(effect, 'to_dict') else str(effect) for effect in self.effects]
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Consumable':
        """Десериализация расходуемого предмета"""
        # Упрощенная загрузка эффектов
        effects = []
        
        consumable = cls(
            name=data["name"],
            description=data["description"],
            effects=effects,
            rarity=ItemRarity(data["rarity"])
        )
        
        # Восстанавливаем остальные свойства
        consumable.required_level = data.get("required_level", 1)
        consumable.stack_size = data.get("stack_size", 1)
        
        return consumable

class ItemSystem(ISystem):
    """Система управления предметами для всех сущностей"""
    
    def __init__(self):
        self._system_name = "item"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Предметы в системе
        self.items: Dict[str, BaseItem] = {}
        
        # Предметы сущностей
        self.entity_items: Dict[str, List[BaseItem]] = {}
        
        # Шаблоны предметов
        self.item_templates: Dict[str, Dict[str, Any]] = {}
        
        # Фабрика предметов
        self.item_factory = ItemFactory()
        
        # Статистика системы
        self.system_stats = {
            'items_count': 0,
            'entities_count': 0,
            'items_created': 0,
            'items_used': 0,
            'update_time': 0.0
        }
        
        logger.info("Система предметов инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы предметов"""
        try:
            logger.info("Инициализация системы предметов...")
            
            # Инициализируем шаблоны предметов
            self._initialize_item_templates()
            
            # Создаем базовые предметы
            self._create_base_items()
            
            self._system_state = SystemState.READY
            logger.info("Система предметов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы предметов: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы предметов"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем предметы (например, прочность, эффекты)
            self._update_items(delta_time)
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы предметов: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы предметов"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система предметов приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы предметов: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы предметов"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система предметов возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы предметов: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы предметов"""
        try:
            logger.info("Очистка системы предметов...")
            
            # Очищаем все данные
            self.items.clear()
            self.entity_items.clear()
            self.item_templates.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'items_count': 0,
                'entities_count': 0,
                'items_created': 0,
                'items_used': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система предметов очищена")
            return True
            
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
            'items_count': len(self.items),
            'entities_count': len(self.entity_items),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "item_created":
                return self._handle_item_created(event_data)
            elif event_type == "item_used":
                return self._handle_item_used(event_data)
            elif event_type == "item_equipped":
                return self._handle_item_equipped(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def create_item(self, item_template: str, **kwargs) -> Optional[BaseItem]:
        """Создает предмет по шаблону"""
        try:
            if item_template not in self.item_templates:
                logger.warning(f"Шаблон предмета {item_template} не найден")
                return None
            
            template = self.item_templates[item_template]
            
            # Создаем предмет на основе шаблона
            if template['type'] == 'weapon':
                item = Weapon(
                    name=template['name'],
                    description=template['description'],
                    damage=template['damage'],
                    attack_speed=template['attack_speed'],
                    damage_type=template['damage_type'],
                    slot=template['slot'],
                    rarity=ItemRarity(template['rarity'])
                )
            elif template['type'] == 'armor':
                item = Armor(
                    name=template['name'],
                    description=template['description'],
                    armor_value=template['armor_value'],
                    slot=template['slot'],
                    rarity=ItemRarity(template['rarity'])
                )
            elif template['type'] == 'accessory':
                item = Accessory(
                    name=template['name'],
                    description=template['description'],
                    slot=template['slot'],
                    stats=template['stats'],
                    rarity=ItemRarity(template['rarity'])
                )
            elif template['type'] == 'consumable':
                item = Consumable(
                    name=template['name'],
                    description=template['description'],
                    effects=[],
                    rarity=ItemRarity(template['rarity'])
                )
            else:
                item = BaseItem(
                    name=template['name'],
                    description=template['description'],
                    item_type=ItemType(template['type']),
                    rarity=ItemRarity(template['rarity'])
                )
            
            # Применяем дополнительные параметры
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            # Добавляем в систему
            item_id = f"{item.name}_{len(self.items)}"
            self.items[item_id] = item
            self.system_stats['items_count'] = len(self.items)
            self.system_stats['items_created'] += 1
            
            logger.info(f"Создан предмет: {item.name}")
            return item
            
        except Exception as e:
            logger.error(f"Ошибка создания предмета {item_template}: {e}")
            return None
    
    def add_item_to_entity(self, entity_id: str, item: BaseItem) -> bool:
        """Добавляет предмет сущности"""
        try:
            if entity_id not in self.entity_items:
                self.entity_items[entity_id] = []
                self.system_stats['entities_count'] = len(self.entity_items)
            
            self.entity_items[entity_id].append(item)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета к сущности {entity_id}: {e}")
            return False
    
    def get_entity_items(self, entity_id: str) -> List[BaseItem]:
        """Получает все предметы сущности"""
        return self.entity_items.get(entity_id, [])
    
    def use_item(self, entity_id: str, item_name: str, target: Any = None) -> bool:
        """Использует предмет сущности"""
        try:
            if entity_id not in self.entity_items:
                return False
            
            # Ищем предмет
            item = None
            for entity_item in self.entity_items[entity_id]:
                if entity_item.name == item_name:
                    item = entity_item
                    break
            
            if not item:
                return False
            
            # Используем предмет
            if hasattr(item, 'use'):
                item.use(target)
                self.system_stats['items_used'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка использования предмета {item_name} для {entity_id}: {e}")
            return False
    
    def _initialize_item_templates(self) -> None:
        """Инициализация шаблонов предметов"""
        try:
            # Шаблоны для разных типов предметов
            self.item_templates = {
                'basic_sword': {
                    'type': 'weapon',
                    'name': 'Базовый меч',
                    'description': 'Простой железный меч',
                    'damage': 15,
                    'attack_speed': 1.0,
                    'damage_type': 'physical',
                    'slot': 'main_hand',
                    'rarity': 'common'
                },
                'leather_armor': {
                    'type': 'armor',
                    'name': 'Кожаная броня',
                    'description': 'Легкая кожаная броня',
                    'armor_value': 8,
                    'slot': 'chest',
                    'rarity': 'common'
                },
                'health_potion': {
                    'type': 'consumable',
                    'name': 'Зелье здоровья',
                    'description': 'Восстанавливает здоровье',
                    'rarity': 'common'
                }
            }
            
            logger.debug("Шаблоны предметов инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать шаблоны предметов: {e}")
    
    def _create_base_items(self) -> None:
        """Создание базовых предметов"""
        try:
            # Создаем базовые предметы из шаблонов
            for template_id in self.item_templates:
                self.create_item(template_id)
            
            logger.info(f"Создано {len(self.items)} базовых предметов")
            
        except Exception as e:
            logger.warning(f"Не удалось создать базовые предметы: {e}")
    
    def _update_items(self, delta_time: float) -> None:
        """Обновление предметов"""
        try:
            # Обновляем все предметы (например, прочность, эффекты)
            for item in self.items.values():
                if hasattr(item, 'update'):
                    item.update(delta_time)
                    
        except Exception as e:
            logger.warning(f"Ошибка обновления предметов: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Инициализируем список предметов для новой сущности
                self.entity_items[entity_id] = []
                self.system_stats['entities_count'] = len(self.entity_items)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_item_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания предмета"""
        try:
            item_template = event_data.get('item_template')
            entity_id = event_data.get('entity_id')
            
            if item_template:
                item = self.create_item(item_template)
                if item and entity_id:
                    return self.add_item_to_entity(entity_id, item)
                return item is not None
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания предмета: {e}")
            return False
    
    def _handle_item_used(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события использования предмета"""
        try:
            entity_id = event_data.get('entity_id')
            item_name = event_data.get('item_name')
            target = event_data.get('target')
            
            if entity_id and item_name:
                return self.use_item(entity_id, item_name, target)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события использования предмета: {e}")
            return False
    
    def _handle_item_equipped(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события экипировки предмета"""
        try:
            entity_id = event_data.get('entity_id')
            item_name = event_data.get('item_name')
            slot = event_data.get('slot')
            
            if entity_id and item_name and slot:
                # Логика экипировки предмета
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события экипировки предмета: {e}")
            return False

class ItemFactory:
    """Фабрика для создания предметов"""
    
    @staticmethod
    def create_enhanced_fire_sword() -> Weapon:
        """Создает огненный меч с улучшенными спецэффектами"""
        weapon = Weapon(
            name="Пылающий клинок",
            description="Меч, наполненный мощью огненного элементаля",
            damage=35,
            attack_speed=1.1,
            damage_type="fire",
            slot="main_hand",
            rarity=ItemRarity.EPIC
        )
        
        weapon.required_level = 15
        
        return weapon
    
    @staticmethod
    def create_lightning_ring() -> Accessory:
        """Создает кольцо молний со спецэффектами"""
        accessory = Accessory(
            name="Кольцо грозы",
            description="Увеличивает мощь заклинаний молнии",
            slot="ring",
            stats={"intelligence": 15, "spell_power": 0.1},
            rarity=ItemRarity.RARE
        )
        
        accessory.required_level = 10
        
        return accessory
