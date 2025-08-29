"""
Система инвентаря - консолидированная система для управления предметами и экипировкой
"""

import time
import random
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"          # Оружие
    ARMOR = "armor"            # Броня
    CONSUMABLE = "consumable"  # Расходники
    MATERIAL = "material"      # Материалы
    QUEST = "quest"            # Квестовые предметы
    CURRENCY = "currency"      # Валюта
    TOOL = "tool"              # Инструменты
    GENE = "gene"              # Гены


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"          # Обычный
    UNCOMMON = "uncommon"      # Необычный
    RARE = "rare"              # Редкий
    EPIC = "epic"              # Эпический
    LEGENDARY = "legendary"    # Легендарный
    MYTHIC = "mythic"          # Мифический


class EquipmentSlot(Enum):
    """Слоты экипировки"""
    HEAD = "head"              # Голова
    NECK = "neck"              # Шея
    SHOULDERS = "shoulders"    # Плечи
    CHEST = "chest"            # Грудь
    BACK = "back"              # Спина
    WRISTS = "wrists"          # Запястья
    HANDS = "hands"            # Руки
    WAIST = "waist"            # Пояс
    LEGS = "legs"              # Ноги
    FEET = "feet"              # Ступни
    MAIN_HAND = "main_hand"    # Основная рука
    OFF_HAND = "off_hand"      # Вторая рука
    RING_1 = "ring_1"          # Кольцо 1
    RING_2 = "ring_2"          # Кольцо 2
    TRINKET_1 = "trinket_1"    # Аксессуар 1
    TRINKET_2 = "trinket_2"    # Аксессуар 2


@dataclass
class ItemStats:
    """Характеристики предмета"""
    damage: float = 0.0
    armor: float = 0.0
    health: float = 0.0
    mana: float = 0.0
    strength: float = 0.0
    agility: float = 0.0
    intelligence: float = 0.0
    resistance: Dict[str, float] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)


@dataclass
class Item:
    """Базовый класс предмета"""
    id: str
    name: str
    item_type: ItemType
    rarity: ItemRarity
    level_requirement: int = 1
    stack_size: int = 1
    max_stack: int = 1
    description: str = ""
    icon: str = ""
    model: str = ""
    stats: ItemStats = field(default_factory=ItemStats)
    effects: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def can_stack_with(self, other: 'Item') -> bool:
        """Проверить, можно ли сложить с другим предметом"""
        return (self.id == other.id and 
                self.stack_size < self.max_stack and 
                other.stack_size < other.max_stack)
    
    def get_total_stats(self) -> ItemStats:
        """Получить общие характеристики с учетом количества"""
        total_stats = ItemStats()
        
        # Умножаем характеристики на количество
        for attr in ['damage', 'armor', 'health', 'mana', 'strength', 'agility', 'intelligence']:
            value = getattr(self.stats, attr, 0.0)
            setattr(total_stats, attr, value * self.stack_size)
        
        # Копируем сопротивления и эффекты
        total_stats.resistance = self.stats.resistance.copy()
        total_stats.special_effects = self.stats.special_effects.copy()
        
        return total_stats


@dataclass
class InventorySlot:
    """Слот инвентаря"""
    item: Optional[Item] = None
    quantity: int = 0
    locked: bool = False
    position: Tuple[int, int] = (0, 0)
    
    def is_empty(self) -> bool:
        """Проверить, пуст ли слот"""
        return self.item is None or self.quantity <= 0
    
    def can_accept_item(self, item: Item, quantity: int = 1) -> bool:
        """Проверить, можно ли поместить предмет в слот"""
        if self.locked:
            return False
    
        if self.is_empty():
            return True
            
        if self.item.id == item.id:
            return self.quantity + quantity <= self.item.max_stack
        
                return False
            

@dataclass
class EquipmentSet:
    """Комплект экипировки"""
    name: str
    pieces: List[str] = field(default_factory=list)  # ID предметов
    bonus_effects: List[str] = field(default_factory=list)
    set_bonus_levels: Dict[int, List[str]] = field(default_factory=dict)


class InventorySystem(BaseComponent):
    """
    Консолидированная система инвентаря
    Управляет предметами, экипировкой и интеграцией с другими системами
    """
    
    def __init__(self):
        super().__init__(
            name="InventorySystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Инвентари сущностей
        self.inventories: Dict[str, 'Inventory'] = {}
        
        # Регистры предметов
        self.item_templates: Dict[str, Item] = {}
        self.item_effects: Dict[str, Callable] = {}
        
        # Система экипировки
        self.equipment_sets: Dict[str, EquipmentSet] = {}
        self.equipment_bonuses: Dict[str, Dict[str, float]] = {}
        
        # Система крафтинга
        self.crafting_recipes: Dict[str, Dict[str, Any]] = {}
        self.crafting_stations: Dict[str, List[str]] = {}
        
        # Настройки
        self.max_inventory_size = 50
        self.max_equipment_slots = len(EquipmentSlot)
        
    def _on_initialize(self) -> bool:
        """Инициализация системы инвентаря"""
        try:
            # Регистрация базовых предметов
            self._register_base_items()
            
            # Регистрация эффектов предметов
            self._register_item_effects()
            
            # Регистрация комплектов экипировки
            self._register_equipment_sets()
            
            # Регистрация рецептов крафтинга
            self._register_crafting_recipes()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации InventorySystem: {e}")
            return False
    
    def _register_base_items(self):
        """Регистрация базовых предметов"""
        # Базовое оружие
        basic_sword = Item(
            id="basic_sword",
            name="Базовая сабля",
            item_type=ItemType.WEAPON,
            rarity=ItemRarity.COMMON,
            level_requirement=1,
            description="Простая сабля для начинающих",
            stats=ItemStats(damage=10.0, strength=2.0),
            effects=["basic_attack"],
            tags=["weapon", "sword", "melee"]
        )
        self.item_templates["basic_sword"] = basic_sword
        
        # Базовая броня
        basic_armor = Item(
            id="basic_armor",
            name="Базовая броня",
            item_type=ItemType.ARMOR,
            rarity=ItemRarity.COMMON,
            level_requirement=1,
            description="Простая кожаная броня",
            stats=ItemStats(armor=5.0, health=20.0),
            effects=["basic_defense"],
            tags=["armor", "leather", "defense"]
        )
        self.item_templates["basic_armor"] = basic_armor
        
        # Лечебное зелье
        health_potion = Item(
            id="health_potion",
            name="Лечебное зелье",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            stack_size=1,
            max_stack=10,
            description="Восстанавливает здоровье",
            effects=["restore_health"],
            tags=["consumable", "healing", "potion"]
        )
        self.item_templates["health_potion"] = health_potion
    
    def _register_item_effects(self):
        """Регистрация эффектов предметов"""
        self.item_effects["basic_attack"] = self._basic_attack_effect
        self.item_effects["basic_defense"] = self._basic_defense_effect
        self.item_effects["restore_health"] = self._restore_health_effect
    
    def _register_equipment_sets(self):
        """Регистрация комплектов экипировки"""
        # Комплект новичка
        beginner_set = EquipmentSet(
            name="Комплект новичка",
            pieces=["basic_sword", "basic_armor"],
            bonus_effects=["beginner_bonus"],
            set_bonus_levels={
                2: ["+10% к опыту", "+5% к здоровью"]
            }
        )
        self.equipment_sets["beginner_set"] = beginner_set
    
    def _register_crafting_recipes(self):
        """Регистрация рецептов крафтинга"""
        # Рецепт улучшенной сабли
        improved_sword_recipe = {
            "id": "improved_sword",
            "name": "Улучшенная сабля",
            "materials": {
                "basic_sword": 1,
                "iron_ingot": 3,
                "leather_strap": 1
            },
            "result": {
                "item_id": "improved_sword",
                "quantity": 1
            },
            "skill_required": "blacksmithing",
            "skill_level": 2,
            "crafting_time": 30.0
        }
        self.crafting_recipes["improved_sword"] = improved_sword_recipe
    
    # Создание инвентаря
    def create_inventory(self, entity_id: str, size: Optional[int] = None) -> 'Inventory':
        """Создать инвентарь для сущности"""
        if entity_id in self.inventories:
            return self.inventories[entity_id]
        
        inventory_size = size or self.max_inventory_size
        inventory = Inventory(entity_id, inventory_size, self)
        self.inventories[entity_id] = inventory
        
        return inventory
    
    def get_inventory(self, entity_id: str) -> Optional['Inventory']:
        """Получить инвентарь сущности"""
        return self.inventories.get(entity_id)
    
    # Управление предметами
    def create_item(self, template_id: str, quantity: int = 1) -> Optional[Item]:
        """Создать предмет по шаблону"""
        if template_id not in self.item_templates:
            self.logger.warning(f"Шаблон предмета не найден: {template_id}")
            return None
        
        template = self.item_templates[template_id]
        item = Item(
            id=f"{template_id}_{int(time.time() * 1000)}",
            name=template.name,
            item_type=template.item_type,
            rarity=template.rarity,
            level_requirement=template.level_requirement,
            stack_size=quantity,
            max_stack=template.max_stack,
            description=template.description,
            icon=template.icon,
            model=template.model,
            stats=template.stats,
            effects=template.effects,
            requirements=template.requirements,
            tags=template.tags
        )
        
        return item
    
    def add_item_to_inventory(self, entity_id: str, item: Item) -> bool:
        """Добавить предмет в инвентарь"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            inventory = self.create_inventory(entity_id)
        
        return inventory.add_item(item)
    
    def remove_item_from_inventory(self, entity_id: str, item_id: str, quantity: int = 1) -> bool:
        """Убрать предмет из инвентаря"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return False
        
        return inventory.remove_item(item_id, quantity)
    
    # Система экипировки
    def equip_item(self, entity_id: str, item: Item, slot: EquipmentSlot) -> bool:
        """Экипировать предмет"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return False
        
        return inventory.equip_item(item, slot)
    
    def unequip_item(self, entity_id: str, slot: EquipmentSlot) -> Optional[Item]:
        """Снять предмет с экипировки"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return None
        
        return inventory.unequip_item(slot)
    
    def get_equipment_bonuses(self, entity_id: str) -> Dict[str, float]:
        """Получить бонусы от экипировки"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return {}
        
        return inventory.get_equipment_bonuses()
    
    # Система крафтинга
    def can_craft_item(self, entity_id: str, recipe_id: str) -> bool:
        """Проверить, можно ли скрафтить предмет"""
        if recipe_id not in self.crafting_recipes:
            return False
            
        recipe = self.crafting_recipes[recipe_id]
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return False
    
        # Проверяем наличие материалов
        for material_id, required_quantity in recipe["materials"].items():
            if not inventory.has_item(material_id, required_quantity):
            return False
            
        # TODO: Проверка навыков крафтинга
                return True
    
    def craft_item(self, entity_id: str, recipe_id: str) -> Optional[Item]:
        """Скрафтить предмет"""
        if not self.can_craft_item(entity_id, recipe_id):
            return None
        
        recipe = self.crafting_recipes[recipe_id]
        inventory = self.get_inventory(entity_id)
        
        # Убираем материалы
        for material_id, required_quantity in recipe["materials"].items():
            inventory.remove_item(material_id, required_quantity)
        
        # Создаем результат
        result_item = self.create_item(recipe["result"]["item_id"], recipe["result"]["quantity"])
        if result_item:
            inventory.add_item(result_item)
        
        return result_item
    
    # Эффекты предметов
    def _basic_attack_effect(self, entity_id: str, context: Dict[str, Any]):
        """Эффект базовой атаки"""
        # TODO: Интеграция с боевой системой
        pass
    
    def _basic_defense_effect(self, entity_id: str, context: Dict[str, Any]):
        """Эффект базовой защиты"""
        # TODO: Интеграция с системой защиты
        pass
    
    def _restore_health_effect(self, entity_id: str, context: Dict[str, Any]):
        """Эффект восстановления здоровья"""
        # TODO: Интеграция с системой здоровья
        pass
    
    # Публичные методы
    def get_item_template(self, template_id: str) -> Optional[Item]:
        """Получить шаблон предмета"""
        return self.item_templates.get(template_id)
    
    def register_item_template(self, template: Item):
        """Зарегистрировать шаблон предмета"""
        self.item_templates[template.id] = template
    
    def get_crafting_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Получить рецепт крафтинга"""
        return self.crafting_recipes.get(recipe_id)
    
    def register_crafting_recipe(self, recipe: Dict[str, Any]):
        """Зарегистрировать рецепт крафтинга"""
        self.crafting_recipes[recipe["id"]] = recipe
    
    def get_entity_items(self, entity_id: str) -> List[Item]:
        """Получить все предметы сущности"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return []
        
        return inventory.get_all_items()
    
    def get_entity_equipment(self, entity_id: str) -> Dict[EquipmentSlot, Item]:
        """Получить экипировку сущности"""
        inventory = self.get_inventory(entity_id)
        if not inventory:
            return {}
        
        return inventory.get_equipment()


class Inventory:
    """Инвентарь сущности"""
    
    def __init__(self, entity_id: str, size: int, system: InventorySystem):
        self.entity_id = entity_id
        self.size = size
        self.system = system
        
        # Слоты инвентаря
        self.slots: List[InventorySlot] = []
        for i in range(size):
            row = i // 10
            col = i % 10
            self.slots.append(InventorySlot(position=(row, col)))
        
        # Экипировка
        self.equipment: Dict[EquipmentSlot, Item] = {}
        
        # Настройки
        self.auto_stack = True
        self.auto_sort = False
    
    def add_item(self, item: Item) -> bool:
        """Добавить предмет в инвентарь"""
        # Ищем слот для предмета
        slot = self._find_slot_for_item(item)
        if not slot:
                return False
            
            # Добавляем предмет
        if slot.is_empty():
            slot.item = item
            slot.quantity = item.stack_size
                else:
            # Складываем с существующим предметом
            max_add = min(item.stack_size, slot.item.max_stack - slot.quantity)
            slot.quantity += max_add
            
            # Если остался излишек, создаем новый слот
            if max_add < item.stack_size:
                remaining_item = Item(
                    id=item.id,
                    name=item.name,
                    item_type=item.item_type,
                    rarity=item.rarity,
                    level_requirement=item.level_requirement,
                    stack_size=item.stack_size - max_add,
                    max_stack=item.max_stack,
                    description=item.description,
                    icon=item.icon,
                    model=item.model,
                    stats=item.stats,
                    effects=item.effects,
                    requirements=item.requirements,
                    tags=item.tags
                )
                return self.add_item(remaining_item)
        
            return True
            
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Убрать предмет из инвентаря"""
            # Ищем слот с предметом
        slot = self._find_slot_by_item_id(item_id)
        if not slot:
                    return False
        
        # Убираем предмет
        if slot.quantity <= quantity:
            slot.item = None
            slot.quantity = 0
            else:
            slot.quantity -= quantity
        
            return True
            
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Проверить наличие предмета"""
        total_quantity = 0
        for slot in self.slots:
            if slot.item and slot.item.id == item_id:
                total_quantity += slot.quantity
                if total_quantity >= quantity:
                    return True
            return False
    
    def equip_item(self, item: Item, slot: EquipmentSlot) -> bool:
        """Экипировать предмет"""
        # Проверяем требования
        if not self._check_equipment_requirements(item):
                return False
            
        # Снимаем предыдущий предмет
        if slot in self.equipment:
            self.unequip_item(slot)
        
        # Экипируем новый предмет
        self.equipment[slot] = item
        
        # Применяем эффекты
        self._apply_equipment_effects(item, True)
        
            return True
            
    def unequip_item(self, slot: EquipmentSlot) -> Optional[Item]:
        """Снять предмет с экипировки"""
        if slot not in self.equipment:
            return None
        
        item = self.equipment[slot]
        
        # Убираем эффекты
        self._apply_equipment_effects(item, False)
        
        # Убираем из экипировки
        del self.equipment[slot]
        
        return item
    
    def get_equipment_bonuses(self) -> Dict[str, float]:
        """Получить бонусы от экипировки"""
        bonuses = {}
        
        for item in self.equipment.values():
            stats = item.get_total_stats()
            
            # Складываем характеристики
            for attr in ['damage', 'armor', 'health', 'mana', 'strength', 'agility', 'intelligence']:
                value = getattr(stats, attr, 0.0)
                if value > 0:
                    bonuses[attr] = bonuses.get(attr, 0.0) + value
            
            # Складываем сопротивления
            for resistance_type, resistance_value in stats.resistance.items():
                bonuses[f"resistance_{resistance_type}"] = bonuses.get(f"resistance_{resistance_type}", 0.0) + resistance_value
        
        return bonuses
    
    def get_all_items(self) -> List[Item]:
        """Получить все предметы в инвентаре"""
        items = []
        for slot in self.slots:
            if not slot.is_empty():
                items.append(slot.item)
        return items
    
    def get_equipment(self) -> Dict[EquipmentSlot, Item]:
        """Получить экипировку"""
        return self.equipment.copy()
    
    # Приватные методы
    def _find_slot_for_item(self, item: Item) -> Optional[InventorySlot]:
        """Найти слот для предмета"""
        # Сначала ищем слот с таким же предметом для складывания
        if self.auto_stack:
            for slot in self.slots:
                if slot.item and slot.item.id == item.id and slot.quantity < slot.item.max_stack:
                    return slot
        
        # Ищем пустой слот
        for slot in self.slots:
            if slot.is_empty():
                return slot
        
                return None
            
    def _find_slot_by_item_id(self, item_id: str) -> Optional[InventorySlot]:
        """Найти слот по ID предмета"""
        for slot in self.slots:
            if slot.item and slot.item.id == item_id:
                return slot
            return None
    
    def _check_equipment_requirements(self, item: Item) -> bool:
        """Проверить требования для экипировки"""
        # TODO: Проверка уровня, характеристик и других требований
            return True
            
    def _apply_equipment_effects(self, item: Item, equipping: bool):
        """Применить эффекты экипировки"""
        for effect_name in item.effects:
            if effect_name in self.system.item_effects:
                effect_func = self.system.item_effects[effect_name]
                try:
                    effect_func(self.entity_id, {"equipping": equipping, "item": item})
        except Exception as e:
                    self.system.logger.error(f"Ошибка применения эффекта {effect_name}: {e}")
