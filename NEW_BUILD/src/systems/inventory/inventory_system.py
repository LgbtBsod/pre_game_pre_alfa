#!/usr/bin/env python3
"""
Inventory System - Система инвентаря
Отвечает только за управление предметами и инвентарем сущностей
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ItemCategory(Enum):
    """Категории предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    TOOL = "tool"
    QUEST = "quest"
    SPECIAL = "special"

class InventorySlot:
    """Слот инвентаря"""
    
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.item_id = None
        self.quantity = 0
        self.durability = 100.0
        self.enchantments = []
        self.locked = False
    
    def is_empty(self) -> bool:
        """Проверка, пуст ли слот"""
        return self.item_id is None or self.quantity <= 0
    
    def can_stack_with(self, item_id: str, quantity: int) -> bool:
        """Проверка возможности стака с предметом"""
        if self.is_empty():
            return True
        
        if self.item_id != item_id:
            return False
        
        # Проверяем максимальный размер стака
        # Упрощенная реализация
        return self.quantity + quantity <= 100
    
    def add_item(self, item_id: str, quantity: int = 1) -> int:
        """Добавление предмета в слот"""
        if self.locked:
            return 0
        
        if self.is_empty():
            self.item_id = item_id
            self.quantity = quantity
            return quantity
        
        if self.item_id == item_id:
            # Добавляем к существующему стаку
            added = min(quantity, 100 - self.quantity)
            self.quantity += added
            return added
        
        return 0
    
    def remove_item(self, quantity: int = 1) -> int:
        """Удаление предмета из слота"""
        if self.is_empty() or self.locked:
            return 0
        
        removed = min(quantity, self.quantity)
        self.quantity -= removed
        
        if self.quantity <= 0:
            self.clear()
        
        return removed
    
    def clear(self):
        """Очистка слота"""
        self.item_id = None
        self.quantity = 0
        self.durability = 100.0
        self.enchantments.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о слоте"""
        return {
            "slot_id": self.slot_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "durability": self.durability,
            "enchantments": self.enchantments.copy(),
            "locked": self.locked,
            "empty": self.is_empty()
        }

class Inventory:
    """Инвентарь сущности"""
    
    def __init__(self, owner_id: str, max_slots: int = 20):
        self.owner_id = owner_id
        self.max_slots = max_slots
        self.slots: List[InventorySlot] = []
        self.equipped_items: Dict[str, str] = {}  # slot_type -> item_id
        self.gold = 0
        self.weight_limit = 100.0
        self.current_weight = 0.0
        
        # Инициализация слотов
        for i in range(max_slots):
            self.slots.append(InventorySlot(i))
        
        logger.info(f"Инвентарь создан для {owner_id} с {max_slots} слотами")
    
    def add_item(self, item_id: str, quantity: int = 1) -> Tuple[bool, int]:
        """Добавление предмета в инвентарь"""
        if quantity <= 0:
            return False, 0
        
        remaining_quantity = quantity
        added_total = 0
        
        # Сначала пытаемся добавить к существующим стакам
        for slot in self.slots:
            if slot.can_stack_with(item_id, remaining_quantity):
                added = slot.add_item(item_id, remaining_quantity)
                remaining_quantity -= added
                added_total += added
                
                if remaining_quantity <= 0:
                    break
        
        # Затем ищем пустые слоты
        if remaining_quantity > 0:
            for slot in self.slots:
                if slot.is_empty():
                    added = slot.add_item(item_id, remaining_quantity)
                    remaining_quantity -= added
                    added_total += added
                    
                    if remaining_quantity <= 0:
                        break
        
        if added_total > 0:
            logger.debug(f"Добавлено {added_total}x {item_id} в инвентарь {self.owner_id}")
        
        return remaining_quantity == 0, added_total
    
    def remove_item(self, item_id: str, quantity: int = 1) -> Tuple[bool, int]:
        """Удаление предмета из инвентаря"""
        if quantity <= 0:
            return False, 0
        
        remaining_quantity = quantity
        removed_total = 0
        
        # Удаляем из слотов (сначала из последних)
        for slot in reversed(self.slots):
            if slot.item_id == item_id and not slot.is_empty():
                removed = slot.remove_item(remaining_quantity)
                remaining_quantity -= removed
                removed_total += removed
                
                if remaining_quantity <= 0:
                    break
        
        if removed_total > 0:
            logger.debug(f"Удалено {removed_total}x {item_id} из инвентаря {self.owner_id}")
        
        return remaining_quantity == 0, removed_total
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Проверка наличия предмета в инвентаре"""
        total_quantity = 0
        
        for slot in self.slots:
            if slot.item_id == item_id:
                total_quantity += slot.quantity
        
        return total_quantity >= quantity
    
    def get_item_count(self, item_id: str) -> int:
        """Получение количества предмета в инвентаре"""
        total_quantity = 0
        
        for slot in self.slots:
            if slot.item_id == item_id:
                total_quantity += slot.quantity
        
        return total_quantity
    
    def find_item_slots(self, item_id: str) -> List[int]:
        """Поиск слотов с указанным предметом"""
        slots = []
        
        for slot in self.slots:
            if slot.item_id == item_id:
                slots.append(slot.slot_id)
        
        return slots
    
    def get_slot_info(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о слоте"""
        if 0 <= slot_id < len(self.slots):
            return self.slots[slot_id].get_info()
        return None
    
    def move_item(self, from_slot: int, to_slot: int, quantity: int = 1) -> bool:
        """Перемещение предмета между слотами"""
        if (0 <= from_slot < len(self.slots) and 
            0 <= to_slot < len(self.slots) and
            from_slot != to_slot):
            
            from_slot_obj = self.slots[from_slot]
            to_slot_obj = self.slots[to_slot]
            
            if from_slot_obj.is_empty() or from_slot_obj.locked or to_slot_obj.locked:
                return False
            
            # Проверяем возможность перемещения
            if to_slot_obj.is_empty():
                # Перемещаем весь стак
                to_slot_obj.item_id = from_slot_obj.item_id
                to_slot_obj.quantity = from_slot_obj.quantity
                to_slot_obj.durability = from_slot_obj.durability
                to_slot_obj.enchantments = from_slot_obj.enchantments.copy()
                from_slot_obj.clear()
                return True
            
            elif to_slot_obj.item_id == from_slot_obj.item_id:
                # Объединяем стаки
                max_stack = 100  # Упрощенная реализация
                space_available = max_stack - to_slot_obj.quantity
                
                if space_available > 0:
                    move_quantity = min(quantity, from_slot_obj.quantity, space_available)
                    
                    to_slot_obj.quantity += move_quantity
                    from_slot_obj.quantity -= move_quantity
                    
                    if from_slot_obj.quantity <= 0:
                        from_slot_obj.clear()
                    
                    return True
            
            else:
                # Меняем местами
                temp_item_id = to_slot_obj.item_id
                temp_quantity = to_slot_obj.quantity
                temp_durability = to_slot_obj.durability
                temp_enchantments = to_slot_obj.enchantments.copy()
                
                to_slot_obj.item_id = from_slot_obj.item_id
                to_slot_obj.quantity = from_slot_obj.quantity
                to_slot_obj.durability = from_slot_obj.durability
                to_slot_obj.enchantments = from_slot_obj.enchantments.copy()
                
                from_slot_obj.item_id = temp_item_id
                from_slot_obj.quantity = temp_quantity
                from_slot_obj.durability = temp_durability
                from_slot_obj.enchantments = temp_enchantments
                
                return True
        
        return False
    
    def equip_item(self, slot_id: int, equipment_slot: str) -> bool:
        """Экипировка предмета"""
        if 0 <= slot_id < len(self.slots):
            slot = self.slots[slot_id]
            
            if slot.is_empty():
                return False
            
            # Проверяем, можно ли экипировать этот предмет
            if self._can_equip_item(slot.item_id, equipment_slot):
                # Снимаем предыдущий предмет
                if equipment_slot in self.equipped_items:
                    old_item_id = self.equipped_items[equipment_slot]
                    # Возвращаем в инвентарь (упрощенная реализация)
                
                # Экипируем новый предмет
                self.equipped_items[equipment_slot] = slot.item_id
                slot.clear()
                
                logger.debug(f"Предмет {slot.item_id} экипирован в слот {equipment_slot}")
                return True
        
        return False
    
    def unequip_item(self, equipment_slot: str) -> bool:
        """Снятие предмета"""
        if equipment_slot in self.equipped_items:
            item_id = self.equipped_items[equipment_slot]
            
            # Находим свободный слот
            for slot in self.slots:
                if slot.is_empty():
                    slot.item_id = item_id
                    slot.quantity = 1
                    del self.equipped_items[equipment_slot]
                    
                    logger.debug(f"Предмет {item_id} снят из слота {equipment_slot}")
                    return True
        
        return False
    
    def _can_equip_item(self, item_id: str, equipment_slot: str) -> bool:
        """Проверка возможности экипировки предмета"""
        # Упрощенная реализация
        equipment_slot_types = {
            "weapon": ["weapon"],
            "armor": ["armor"],
            "tool": ["tool"]
        }
        
        if equipment_slot in equipment_slot_types:
            # Проверяем тип предмета (упрощенно)
            return True
        
        return False
    
    def get_inventory_info(self) -> Dict[str, Any]:
        """Получение информации об инвентаре"""
        slots_info = []
        for slot in self.slots:
            slots_info.append(slot.get_info())
        
        return {
            "owner_id": self.owner_id,
            "max_slots": self.max_slots,
            "used_slots": len([s for s in self.slots if not s.is_empty()]),
            "slots": slots_info,
            "equipped_items": self.equipped_items.copy(),
            "gold": self.gold,
            "weight_limit": self.weight_limit,
            "current_weight": self.current_weight
        }
    
    def add_gold(self, amount: int) -> bool:
        """Добавление золота"""
        if amount > 0:
            self.gold += amount
            logger.debug(f"Добавлено {amount} золота в инвентарь {self.owner_id}")
            return True
        return False
    
    def remove_gold(self, amount: int) -> bool:
        """Удаление золота"""
        if amount > 0 and self.gold >= amount:
            self.gold -= amount
            logger.debug(f"Удалено {amount} золота из инвентаря {self.owner_id}")
            return True
        return False
    
    def has_gold(self, amount: int) -> bool:
        """Проверка наличия золота"""
        return self.gold >= amount
    
    def lock_slot(self, slot_id: int) -> bool:
        """Блокировка слота"""
        if 0 <= slot_id < len(self.slots):
            self.slots[slot_id].locked = True
            return True
        return False
    
    def unlock_slot(self, slot_id: int) -> bool:
        """Разблокировка слота"""
        if 0 <= slot_id < len(self.slots):
            self.slots[slot_id].locked = False
            return True
        return False
    
    def clear_inventory(self):
        """Очистка всего инвентаря"""
        for slot in self.slots:
            slot.clear()
        
        self.equipped_items.clear()
        self.gold = 0
        self.current_weight = 0.0
        
        logger.info(f"Инвентарь {self.owner_id} очищен")

class InventorySystem:
    """Система управления инвентарями"""
    
    def __init__(self):
        self.inventories: Dict[str, Inventory] = {}
        self.item_database: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Система инвентаря инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы инвентаря"""
        try:
            self._setup_item_database()
            logger.info("Система инвентаря успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы инвентаря: {e}")
            return False
    
    def _setup_item_database(self):
        """Настройка базы данных предметов"""
        self.item_database = {
            "wooden_sword": {
                "name": "Деревянный меч",
                "category": ItemCategory.WEAPON,
                "weight": 1.0,
                "value": 10,
                "stackable": False,
                "max_stack": 1,
                "effects": {"attack": 5}
            },
            "iron_sword": {
                "name": "Железный меч",
                "category": ItemCategory.WEAPON,
                "weight": 2.0,
                "value": 25,
                "stackable": False,
                "max_stack": 1,
                "effects": {"attack": 12}
            },
            "leather_armor": {
                "name": "Кожаная броня",
                "category": ItemCategory.ARMOR,
                "weight": 3.0,
                "value": 15,
                "stackable": False,
                "max_stack": 1,
                "effects": {"defense": 3}
            },
            "health_potion": {
                "name": "Зелье здоровья",
                "category": ItemCategory.CONSUMABLE,
                "weight": 0.2,
                "value": 5,
                "stackable": True,
                "max_stack": 10,
                "effects": {"heal": 25}
            },
            "wood": {
                "name": "Дерево",
                "category": ItemCategory.MATERIAL,
                "weight": 0.1,
                "value": 1,
                "stackable": True,
                "max_stack": 100,
                "effects": {}
            },
            "stone": {
                "name": "Камень",
                "category": ItemCategory.MATERIAL,
                "weight": 0.5,
                "value": 2,
                "stackable": True,
                "max_stack": 100,
                "effects": {}
            }
        }
    
    def create_inventory(self, owner_id: str, max_slots: int = 20) -> bool:
        """Создание нового инвентаря"""
        if owner_id in self.inventories:
            logger.warning(f"Инвентарь для {owner_id} уже существует")
            return False
        
        inventory = Inventory(owner_id, max_slots)
        self.inventories[owner_id] = inventory
        
        logger.info(f"Создан инвентарь для {owner_id}")
        return True
    
    def remove_inventory(self, owner_id: str):
        """Удаление инвентаря"""
        if owner_id in self.inventories:
            del self.inventories[owner_id]
            logger.info(f"Инвентарь {owner_id} удален")
    
    def get_inventory(self, owner_id: str) -> Optional[Inventory]:
        """Получение инвентаря по ID владельца"""
        return self.inventories.get(owner_id)
    
    def add_item_to_inventory(self, owner_id: str, item_id: str, quantity: int = 1) -> Tuple[bool, int]:
        """Добавление предмета в инвентарь"""
        inventory = self.get_inventory(owner_id)
        if not inventory:
            logger.error(f"Инвентарь для {owner_id} не найден")
            return False, 0
        
        return inventory.add_item(item_id, quantity)
    
    def remove_item_from_inventory(self, owner_id: str, item_id: str, quantity: int = 1) -> Tuple[bool, int]:
        """Удаление предмета из инвентаря"""
        inventory = self.get_inventory(owner_id)
        if not inventory:
            logger.error(f"Инвентарь для {owner_id} не найден")
            return False, 0
        
        return inventory.remove_item(item_id, quantity)
    
    def has_item_in_inventory(self, owner_id: str, item_id: str, quantity: int = 1) -> bool:
        """Проверка наличия предмета в инвентаре"""
        inventory = self.get_inventory(owner_id)
        if not inventory:
            return False
        
        return inventory.has_item(item_id, quantity)
    
    def get_item_info(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о предмете"""
        return self.item_database.get(item_id)
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Получение списка всех предметов"""
        items = []
        for item_id, item_data in self.item_database.items():
            item_info = item_data.copy()
            item_info["id"] = item_id
            items.append(item_info)
        
        return items
    
    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """Поиск предметов по запросу"""
        results = []
        query_lower = query.lower()
        
        for item_id, item_data in self.item_database.items():
            if (query_lower in item_data["name"].lower() or 
                query_lower in item_data["description"].lower()):
                
                item_info = item_data.copy()
                item_info["id"] = item_id
                results.append(item_info)
        
        return results
    
    def get_items_by_category(self, category: ItemCategory) -> List[Dict[str, Any]]:
        """Получение предметов по категории"""
        results = []
        
        for item_id, item_data in self.item_database.items():
            if item_data["category"] == category:
                item_info = item_data.copy()
                item_info["id"] = item_id
                results.append(item_info)
        
        return results
    
    def cleanup(self):
        """Очистка системы инвентаря"""
        logger.info("Очистка системы инвентаря...")
        self.inventories.clear()
        self.item_database.clear()
