"""
Менеджер предметов.
Управляет созданием, модификацией и использованием предметов в игре.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from core.data_manager import data_manager, ItemData

logger = logging.getLogger(__name__)


class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    ACCESSORY = "accessory"
    MATERIAL = "material"
    QUEST = "quest"


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ItemInstance:
    """Экземпляр предмета с текущими характеристиками"""
    item_id: str
    name: str
    description: str
    item_type: str
    slot: Optional[str]
    rarity: str
    level_requirement: int
    base_damage: float
    attack_speed: float
    damage_type: Optional[str]
    element: Optional[str]
    element_damage: float
    defense: float
    weight: float
    durability: int
    max_durability: int
    cost: int
    effects: List[str]
    modifiers: Dict[str, Any]
    tags: List[str]
    resist_mod: Dict[str, float]
    weakness_mod: Dict[str, float]
    
    # Динамические характеристики
    current_durability: int
    enchantments: List[str]
    socketed_gems: List[str]
    quality: float  # 0.0 - 1.0
    
    def __post_init__(self):
        if self.current_durability == 0:
            self.current_durability = self.max_durability
        if self.quality == 0.0:
            self.quality = 1.0
    
    @property
    def is_broken(self) -> bool:
        """Проверяет, сломан ли предмет"""
        return self.current_durability <= 0
    
    @property
    def durability_percentage(self) -> float:
        """Возвращает процент прочности"""
        return self.current_durability / self.max_durability
    
    def take_damage(self, damage: int) -> bool:
        """Наносит урон предмету"""
        self.current_durability = max(0, self.current_durability - damage)
        return self.is_broken
    
    def repair(self, amount: int = None) -> bool:
        """Ремонтирует предмет"""
        if amount is None:
            self.current_durability = self.max_durability
        else:
            self.current_durability = min(self.max_durability, self.current_durability + amount)
        return True
    
    def get_effective_damage(self) -> float:
        """Возвращает эффективный урон с учетом качества и прочности"""
        durability_multiplier = self.durability_percentage
        return self.base_damage * self.quality * durability_multiplier
    
    def get_effective_defense(self) -> float:
        """Возвращает эффективную защиту с учетом качества и прочности"""
        durability_multiplier = self.durability_percentage
        return self.defense * self.quality * durability_multiplier
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует предмет в словарь"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "slot": self.slot,
            "rarity": self.rarity,
            "level_requirement": self.level_requirement,
            "base_damage": self.base_damage,
            "attack_speed": self.attack_speed,
            "damage_type": self.damage_type,
            "element": self.element,
            "element_damage": self.element_damage,
            "defense": self.defense,
            "weight": self.weight,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "cost": self.cost,
            "effects": self.effects,
            "modifiers": self.modifiers,
            "tags": self.tags,
            "resist_mod": self.resist_mod,
            "weakness_mod": self.weakness_mod,
            "current_durability": self.current_durability,
            "enchantments": self.enchantments,
            "socketed_gems": self.socketed_gems,
            "quality": self.quality
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemInstance':
        """Создает предмет из словаря"""
        return cls(**data)


class ItemManager:
    """Менеджер предметов"""
    
    def __init__(self):
        self._item_cache: Dict[str, ItemInstance] = {}
    
    def create_item(self, item_id: str, quality: float = 1.0) -> Optional[ItemInstance]:
        """Создает экземпляр предмета"""
        try:
            # Получаем данные предмета
            item_data = data_manager.get_item(item_id)
            if not item_data:
                logger.warning(f"Предмет {item_id} не найден")
                return None
            
            # Создаем экземпляр предмета
            item_instance = ItemInstance(
                item_id=item_data.id,
                name=item_data.name,
                description=item_data.description,
                item_type=item_data.type,
                slot=item_data.slot,
                rarity=item_data.rarity,
                level_requirement=item_data.level_requirement,
                base_damage=item_data.base_damage,
                attack_speed=item_data.attack_speed,
                damage_type=item_data.damage_type,
                element=item_data.element,
                element_damage=item_data.element_damage,
                defense=item_data.defense,
                weight=item_data.weight,
                durability=item_data.durability,
                max_durability=item_data.max_durability,
                cost=item_data.cost,
                effects=item_data.effects.copy(),
                modifiers=item_data.modifiers.copy(),
                tags=item_data.tags.copy(),
                resist_mod=item_data.resist_mod.copy(),
                weakness_mod=item_data.weakness_mod.copy(),
                current_durability=item_data.durability,
                enchantments=[],
                socketed_gems=[],
                quality=quality
            )
            
            # Применяем качество к характеристикам
            self._apply_quality_modifiers(item_instance, quality)
            
            logger.debug(f"Создан предмет: {item_id} с качеством {quality}")
            return item_instance
            
        except Exception as e:
            logger.error(f"Ошибка создания предмета {item_id}: {e}")
            return None
    
    def create_random_item(self, item_type: str = None, rarity: str = None, 
                          level_range: Tuple[int, int] = (1, 10)) -> Optional[ItemInstance]:
        """Создает случайный предмет"""
        try:
            # Получаем список предметов по фильтрам
            items = data_manager.get_all_items()
            
            if item_type:
                items = [item for item in items if item.type == item_type]
            
            if rarity:
                items = [item for item in items if item.rarity == rarity]
            
            if level_range:
                items = [item for item in items if level_range[0] <= item.level_requirement <= level_range[1]]
            
            if not items:
                logger.warning("Не найдено предметов по заданным критериям")
                return None
            
            # Выбираем случайный предмет
            import random
            selected_item = random.choice(items)
            
            # Генерируем случайное качество
            quality = random.uniform(0.8, 1.0)
            
            return self.create_item(selected_item.id, quality)
            
        except Exception as e:
            logger.error(f"Ошибка создания случайного предмета: {e}")
            return None
    
    def create_loot_table(self, enemy_level: int, enemy_type: str = None) -> List[ItemInstance]:
        """Создает таблицу добычи для врага"""
        try:
            loot_items = []
            
            # Определяем количество предметов в добыче
            import random
            item_count = random.randint(1, 3)
            
            # Определяем редкость на основе уровня врага
            rarity_weights = self._get_rarity_weights(enemy_level)
            
            for _ in range(item_count):
                # Выбираем редкость
                rarity = random.choices(
                    list(rarity_weights.keys()),
                    weights=list(rarity_weights.values())
                )[0]
                
                # Создаем предмет
                item = self.create_random_item(
                    rarity=rarity,
                    level_range=(max(1, enemy_level - 2), enemy_level + 2)
                )
                
                if item:
                    loot_items.append(item)
            
            return loot_items
            
        except Exception as e:
            logger.error(f"Ошибка создания таблицы добычи: {e}")
            return []
    
    def enchant_item(self, item: ItemInstance, enchantment_id: str) -> bool:
        """Зачаровывает предмет"""
        try:
            # Проверяем, можно ли зачаровать предмет
            if not self._can_enchant_item(item, enchantment_id):
                return False
            
            # Добавляем зачарование
            if enchantment_id not in item.enchantments:
                item.enchantments.append(enchantment_id)
                
                # Применяем эффекты зачарования
                self._apply_enchantment_effects(item, enchantment_id)
                
                logger.debug(f"Предмет {item.item_id} зачарован: {enchantment_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка зачарования предмета: {e}")
            return False
    
    def socket_gem(self, item: ItemInstance, gem_id: str) -> bool:
        """Вставляет камень в предмет"""
        try:
            # Проверяем, можно ли вставить камень
            if not self._can_socket_gem(item, gem_id):
                return False
            
            # Добавляем камень
            if gem_id not in item.socketed_gems:
                item.socketed_gems.append(gem_id)
                
                # Применяем эффекты камня
                self._apply_gem_effects(item, gem_id)
                
                logger.debug(f"В предмет {item.item_id} вставлен камень: {gem_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка вставки камня: {e}")
            return False
    
    def _apply_quality_modifiers(self, item: ItemInstance, quality: float):
        """Применяет модификаторы качества к предмету"""
        # Качество влияет на базовые характеристики
        quality_multiplier = 0.5 + (quality * 0.5)  # 0.5 - 1.0
        
        item.base_damage *= quality_multiplier
        item.defense *= quality_multiplier
        item.cost = int(item.cost * quality)
    
    def _get_rarity_weights(self, enemy_level: int) -> Dict[str, float]:
        """Возвращает веса редкости на основе уровня врага"""
        if enemy_level <= 5:
            return {
                "common": 0.7,
                "uncommon": 0.25,
                "rare": 0.05,
                "epic": 0.0,
                "legendary": 0.0
            }
        elif enemy_level <= 15:
            return {
                "common": 0.5,
                "uncommon": 0.3,
                "rare": 0.15,
                "epic": 0.05,
                "legendary": 0.0
            }
        else:
            return {
                "common": 0.3,
                "uncommon": 0.4,
                "rare": 0.2,
                "epic": 0.08,
                "legendary": 0.02
            }
    
    def _can_enchant_item(self, item: ItemInstance, enchantment_id: str) -> bool:
        """Проверяет, можно ли зачаровать предмет"""
        # Проверяем тип предмета
        if item.item_type not in ["weapon", "armor", "accessory"]:
            return False
        
        # Проверяем количество зачарований
        max_enchantments = 3
        if len(item.enchantments) >= max_enchantments:
            return False
        
        # Проверяем совместимость зачарования
        # Здесь можно добавить логику проверки совместимости
        return True
    
    def _can_socket_gem(self, item: ItemInstance, gem_id: str) -> bool:
        """Проверяет, можно ли вставить камень"""
        # Проверяем тип предмета
        if item.item_type not in ["weapon", "armor"]:
            return False
        
        # Проверяем количество слотов
        max_sockets = 3
        if len(item.socketed_gems) >= max_sockets:
            return False
        
        # Проверяем совместимость камня
        # Здесь можно добавить логику проверки совместимости
        return True
    
    def _apply_enchantment_effects(self, item: ItemInstance, enchantment_id: str):
        """Применяет эффекты зачарования"""
        # Здесь можно добавить логику применения эффектов зачарования
        pass
    
    def _apply_gem_effects(self, item: ItemInstance, gem_id: str):
        """Применяет эффекты камня"""
        # Здесь можно добавить логику применения эффектов камней
        pass


# Глобальный экземпляр менеджера предметов
item_manager = ItemManager()
