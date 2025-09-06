#!/usr/bin/env python3
"""Система инвентаря - управление предметами и экипировкой
Обеспечивает полную систему инвентаря с предметами, экипировкой и торговлей"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    MISC = "misc"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class ItemSlot(Enum):
    """Слоты экипировки"""
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    WEAPON = "weapon"
    SHIELD = "shield"
    RING = "ring"
    NECKLACE = "necklace"

@dataclass
class ItemEffect:
    """Эффект предмета"""
    effect_type: str
    value: float
    duration: float = 0.0  # 0 = постоянный эффект
    stackable: bool = False

@dataclass
class ItemModifier:
    """Модификатор предмета"""
    attribute: str
    value: float
    is_percentage: bool = False

@dataclass
class ItemRequirement:
    """Требования для использования предмета"""
    level: int = 1
    attributes: Dict[str, float] = None
    skills: Dict[str, int] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.skills is None:
            self.skills = {}

@dataclass
class Item:
    """Предмет"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    value: int
    weight: float
    stack_size: int = 1
    effects: List[ItemEffect] = None
    modifiers: List[ItemModifier] = None
    requirements: ItemRequirement = None
    equipment_slot: Optional[ItemSlot] = None
    durability: int = 100
    max_durability: int = 100
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []
        if self.modifiers is None:
            self.modifiers = []
        if self.requirements is None:
            self.requirements = ItemRequirement()

@dataclass
class InventorySlot:
    """Слот инвентаря"""
    item_id: str
    quantity: int
    durability: int = 100

@dataclass
class Equipment:
    """Экипировка персонажа"""
    head: Optional[str] = None
    chest: Optional[str] = None
    legs: Optional[str] = None
    feet: Optional[str] = None
    hands: Optional[str] = None
    weapon: Optional[str] = None
    shield: Optional[str] = None
    ring: Optional[str] = None
    necklace: Optional[str] = None

@dataclass
class Inventory:
    """Инвентарь персонажа"""
    entity_id: str
    slots: List[InventorySlot]
    equipment: Equipment
    gold: int = 0
    max_slots: int = 50

class InventorySystem:
    """Система инвентаря"""
    
    def __init__(self, db_path: str = "data/inventory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger("inventory_system")
        
        # Кэш предметов
        self.items_cache: Dict[str, Item] = {}
        
        # Инициализация базы данных
        self._init_database()
        self._load_items()
        
    def _init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица предметов
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        item_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        item_type TEXT NOT NULL,
                        rarity TEXT NOT NULL,
                        value INTEGER NOT NULL,
                        weight REAL NOT NULL,
                        stack_size INTEGER DEFAULT 1,
                        effects TEXT,
                        modifiers TEXT,
                        requirements TEXT,
                        equipment_slot TEXT,
                        durability INTEGER DEFAULT 100,
                        max_durability INTEGER DEFAULT 100
                    )
                """)
                
                # Таблица инвентарей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventories (
                        entity_id TEXT PRIMARY KEY,
                        slots TEXT NOT NULL,
                        equipment TEXT NOT NULL,
                        gold INTEGER DEFAULT 0,
                        max_slots INTEGER DEFAULT 50
                    )
                """)
                
                conn.commit()
                self.logger.info("База данных инвентаря инициализирована")
                
        except Exception as e:
            self.logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def _load_items(self):
        """Загрузка предметов из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM items")
                
                for row in cursor.fetchall():
                    item = Item(
                        item_id=row[0],
                        name=row[1],
                        description=row[2],
                        item_type=ItemType(row[3]),
                        rarity=ItemRarity(row[4]),
                        value=row[5],
                        weight=row[6],
                        stack_size=row[7],
                        effects=self._deserialize_effects(row[8]) if row[8] else [],
                        modifiers=self._deserialize_modifiers(row[9]) if row[9] else [],
                        requirements=self._deserialize_requirements(row[10]) if row[10] else ItemRequirement(),
                        equipment_slot=ItemSlot(row[11]) if row[11] else None,
                        durability=row[12],
                        max_durability=row[13]
                    )
                    self.items_cache[item.item_id] = item
                    
            self.logger.info(f"Загружено {len(self.items_cache)} предметов")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки предметов: {e}")
    
    def _deserialize_effects(self, effects_json: str) -> List[ItemEffect]:
        """Десериализация эффектов"""
        try:
            effects_data = json.loads(effects_json)
            return [ItemEffect(**effect) for effect in effects_data]
        except:
            return []
    
    def _deserialize_modifiers(self, modifiers_json: str) -> List[ItemModifier]:
        """Десериализация модификаторов"""
        try:
            modifiers_data = json.loads(modifiers_json)
            return [ItemModifier(**modifier) for modifier in modifiers_data]
        except:
            return []
    
    def _deserialize_requirements(self, requirements_json: str) -> ItemRequirement:
        """Десериализация требований"""
        try:
            requirements_data = json.loads(requirements_json)
            return ItemRequirement(**requirements_data)
        except:
            return ItemRequirement()
    
    def _serialize_effects(self, effects: List[ItemEffect]) -> str:
        """Сериализация эффектов"""
        return json.dumps([asdict(effect) for effect in effects])
    
    def _serialize_modifiers(self, modifiers: List[ItemModifier]) -> str:
        """Сериализация модификаторов"""
        return json.dumps([asdict(modifier) for modifier in modifiers])
    
    def _serialize_requirements(self, requirements: ItemRequirement) -> str:
        """Сериализация требований"""
        return json.dumps(asdict(requirements))
    
    def create_item(self, item: Item) -> bool:
        """Создание предмета"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.item_id,
                    item.name,
                    item.description,
                    item.item_type.value,
                    item.rarity.value,
                    item.value,
                    item.weight,
                    item.stack_size,
                    self._serialize_effects(item.effects),
                    self._serialize_modifiers(item.modifiers),
                    self._serialize_requirements(item.requirements),
                    item.equipment_slot.value if item.equipment_slot else None,
                    item.durability,
                    item.max_durability
                ))
                conn.commit()
                
            self.items_cache[item.item_id] = item
            self.logger.info(f"Создан предмет: {item.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания предмета: {e}")
            return False
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Получение предмета по ID"""
        return self.items_cache.get(item_id)
    
    def initialize_entity_inventory(self, entity_id: str) -> bool:
        """Инициализация инвентаря сущности"""
        try:
            inventory = Inventory(
                entity_id=entity_id,
                slots=[],
                equipment=Equipment(),
                gold=100,  # Начальное золото
                max_slots=50
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO inventories VALUES (?, ?, ?, ?, ?)
                """, (
                    entity_id,
                    json.dumps([asdict(slot) for slot in inventory.slots]),
                    json.dumps(asdict(inventory.equipment)),
                    inventory.gold,
                    inventory.max_slots
                ))
                conn.commit()
                
            self.logger.info(f"Инициализирован инвентарь для сущности: {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации инвентаря: {e}")
            return False
    
    def get_inventory_contents(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение содержимого инвентаря"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slots FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if row:
                    slots_data = json.loads(row[0])
                    contents = []
                    
                    for slot_data in slots_data:
                        item = self.get_item(slot_data['item_id'])
                        if item:
                            contents.append({
                                'item': asdict(item),
                                'quantity': slot_data['quantity'],
                                'durability': slot_data['durability']
                            })
                    
                    return contents
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения содержимого инвентаря: {e}")
            
        return []
    
    def add_item_to_inventory(self, entity_id: str, item_id: str, quantity: int = 1) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            item = self.get_item(item_id)
            if not item:
                self.logger.warning(f"Предмет {item_id} не найден")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slots, max_slots FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if not row:
                    self.logger.warning(f"Инвентарь для сущности {entity_id} не найден")
                    return False
                
                slots_data = json.loads(row[0])
                max_slots = row[1]
                
                # Ищем существующий слот с этим предметом
                for slot_data in slots_data:
                    if slot_data['item_id'] == item_id and slot_data['quantity'] < item.stack_size:
                        slot_data['quantity'] += quantity
                        break
                else:
                    # Создаем новый слот
                    if len(slots_data) >= max_slots:
                        self.logger.warning(f"Инвентарь сущности {entity_id} переполнен")
                        return False
                    
                    slots_data.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'durability': item.durability
                    })
                
                # Сохраняем обновленный инвентарь
                cursor.execute("""
                    UPDATE inventories SET slots = ? WHERE entity_id = ?
                """, (json.dumps(slots_data), entity_id))
                conn.commit()
                
            self.logger.info(f"Добавлен предмет {item_id} x{quantity} в инвентарь {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления предмета в инвентарь: {e}")
            return False
    
    def remove_item_from_inventory(self, entity_id: str, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета из инвентаря"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slots FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                slots_data = json.loads(row[0])
                
                # Ищем слот с предметом
                for i, slot_data in enumerate(slots_data):
                    if slot_data['item_id'] == item_id:
                        if slot_data['quantity'] >= quantity:
                            slot_data['quantity'] -= quantity
                            if slot_data['quantity'] <= 0:
                                slots_data.pop(i)
                            break
                        else:
                            self.logger.warning(f"Недостаточно предметов {item_id} в инвентаре")
                            return False
                else:
                    self.logger.warning(f"Предмет {item_id} не найден в инвентаре")
                    return False
                
                # Сохраняем обновленный инвентарь
                cursor.execute("""
                    UPDATE inventories SET slots = ? WHERE entity_id = ?
                """, (json.dumps(slots_data), entity_id))
                conn.commit()
                
            self.logger.info(f"Удален предмет {item_id} x{quantity} из инвентаря {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления предмета из инвентаря: {e}")
            return False
    
    def equip_item(self, entity_id: str, item_id: str) -> bool:
        """Экипировка предмета"""
        try:
            item = self.get_item(item_id)
            if not item or not item.equipment_slot:
                self.logger.warning(f"Предмет {item_id} нельзя экипировать")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slots, equipment FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                slots_data = json.loads(row[0])
                equipment_data = json.loads(row[1])
                
                # Проверяем наличие предмета в инвентаре
                item_found = False
                for slot_data in slots_data:
                    if slot_data['item_id'] == item_id and slot_data['quantity'] > 0:
                        item_found = True
                        slot_data['quantity'] -= 1
                        if slot_data['quantity'] <= 0:
                            slots_data.remove(slot_data)
                        break
                
                if not item_found:
                    self.logger.warning(f"Предмет {item_id} не найден в инвентаре")
                    return False
                
                # Экипируем предмет
                equipment_data[item.equipment_slot.value] = item_id
                
                # Сохраняем обновленный инвентарь
                cursor.execute("""
                    UPDATE inventories SET slots = ?, equipment = ? WHERE entity_id = ?
                """, (json.dumps(slots_data), json.dumps(equipment_data), entity_id))
                conn.commit()
                
            self.logger.info(f"Экипирован предмет {item_id} в слот {item.equipment_slot.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экипировки предмета: {e}")
            return False
    
    def use_item(self, entity_id: str, item_id: str) -> bool:
        """Использование предмета"""
        try:
            item = self.get_item(item_id)
            if not item:
                return False
            
            if item.item_type == ItemType.CONSUMABLE:
                # Используем расходный предмет
                if self.remove_item_from_inventory(entity_id, item_id, 1):
                    self.logger.info(f"Использован предмет {item_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка использования предмета: {e}")
            return False
    
    def get_equipment(self, entity_id: str) -> Dict[str, Optional[str]]:
        """Получение экипировки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT equipment FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if row:
                    equipment_data = json.loads(row[0])
                    return equipment_data
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения экипировки: {e}")
            
        return {}
    
    def get_inventory_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистики инвентаря"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slots, gold, max_slots FROM inventories WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                
                if row:
                    slots_data = json.loads(row[0])
                    used_slots = len([slot for slot in slots_data if slot['quantity'] > 0])
                    
                    return {
                        'used_slots': used_slots,
                        'total_slots': row[2],
                        'gold': row[1],
                        'free_slots': row[2] - used_slots
                    }
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики инвентаря: {e}")
            
        return {
            'used_slots': 0,
            'total_slots': 50,
            'gold': 0,
            'free_slots': 50
        }
    
    def create_default_items(self):
        """Создание предметов по умолчанию"""
        default_items = [
            Item(
                item_id="health_potion",
                name="Health Potion",
                description="Восстанавливает 50 HP",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.COMMON,
                value=10,
                weight=0.1,
                stack_size=10,
                effects=[ItemEffect("heal", 50.0)]
            ),
            Item(
                item_id="iron_sword",
                name="Iron Sword",
                description="Простой железный меч",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.COMMON,
                value=50,
                weight=2.0,
                equipment_slot=ItemSlot.WEAPON,
                modifiers=[ItemModifier("physical_damage", 15.0)]
            ),
            Item(
                item_id="leather_armor",
                name="Leather Armor",
                description="Кожаная броня",
                item_type=ItemType.ARMOR,
                rarity=ItemRarity.COMMON,
                value=30,
                weight=3.0,
                equipment_slot=ItemSlot.CHEST,
                modifiers=[ItemModifier("armor", 5.0)]
            )
        ]
        
        for item in default_items:
            self.create_item(item)
        
        self.logger.info("Созданы предметы по умолчанию")
