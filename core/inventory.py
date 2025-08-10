"""
Система инвентаря и экипировки.
Управляет предметами, экипировкой и их эффектами.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EquipmentSlot:
    """Слот экипировки"""

    name: str
    item: Optional[Any] = None
    item_type: str = ""

    def is_empty(self) -> bool:
        """Проверяет, пуст ли слот"""
        return self.item is None

    def equip_item(self, item: Any) -> Optional[Any]:
        """Экипирует предмет, возвращает предыдущий предмет"""
        previous_item = self.item
        self.item = item
        self.item_type = item.item_type if hasattr(item, "item_type") else ""
        return previous_item

    def unequip_item(self) -> Optional[Any]:
        """Снимает предмет из слота"""
        item = self.item
        self.item = None
        self.item_type = ""
        return item


class Inventory:
    """Инвентарь сущности"""

    def __init__(self, max_size: int = 20):
        # Получаем настройки инвентаря
        from config.unified_settings import UnifiedSettings

        self.items: List[Any] = []
        self.max_size = max_size if max_size > 0 else 20
        self.weight_limit = 100.0
        self.current_weight = 0.0

    def add_item(self, item: Any) -> bool:
        """Добавляет предмет в инвентарь"""
        if len(self.items) >= self.max_size:
            return False

        item_weight = getattr(item, "weight", 0.0)
        if self.current_weight + item_weight > self.weight_limit:
            return False

        self.items.append(item)
        self.current_weight += item_weight
        return True

    def remove_item(self, item: Any) -> bool:
        """Удаляет предмет из инвентаря"""
        if item in self.items:
            self.items.remove(item)
            item_weight = getattr(item, "weight", 0.0)
            self.current_weight -= item_weight
            return True
        return False

    def get_item_by_id(self, item_id: str) -> Optional[Any]:
        """Получает предмет по ID"""
        for item in self.items:
            if hasattr(item, "item_id") and item.item_id == item_id:
                return item
        return None

    def get_items_by_type(self, item_type: str) -> List[Any]:
        """Получает предметы по типу"""
        return [
            item
            for item in self.items
            if hasattr(item, "item_type") and item.item_type == item_type
        ]

    def get_consumables(self) -> List[Any]:
        """Получает расходники"""
        return self.get_items_by_type("consumable")

    def get_weapons(self) -> List[Any]:
        """Получает оружие"""
        return self.get_items_by_type("weapon")

    def get_armor(self) -> List[Any]:
        """Получает броню"""
        return self.get_items_by_type("armor")

    def is_full(self) -> bool:
        """Проверяет, полон ли инвентарь"""
        return len(self.items) >= self.max_size

    def get_free_space(self) -> int:
        """Возвращает количество свободных слотов"""
        return self.max_size - len(self.items)

    def get_weight_percentage(self) -> float:
        """Возвращает процент заполнения по весу"""
        return self.current_weight / self.weight_limit if self.weight_limit > 0 else 0.0

    def is_overweight(self) -> bool:
        """Проверяет, перегружен ли инвентарь"""
        return self.current_weight > self.weight_limit


class Equipment:
    """Экипировка сущности"""

    def __init__(self):
        self.slots: Dict[str, EquipmentSlot] = {
            "weapon": EquipmentSlot("weapon"),
            "shield": EquipmentSlot("shield"),
            "armor": EquipmentSlot("armor"),
            "helmet": EquipmentSlot("helmet"),
            "gloves": EquipmentSlot("gloves"),
            "boots": EquipmentSlot("boots"),
            "accessory1": EquipmentSlot("accessory1"),
            "accessory2": EquipmentSlot("accessory2"),
        }

    def equip_item(self, item: Any, slot_name: str) -> Optional[Any]:
        """Экипирует предмет в указанный слот"""
        if slot_name in self.slots:
            return self.slots[slot_name].equip_item(item)
        return None

    def unequip_item(self, slot_name: str) -> Optional[Any]:
        """Снимает предмет из указанного слота"""
        if slot_name in self.slots:
            return self.slots[slot_name].unequip_item()
        return None

    def get_equipped_item(self, slot_name: str) -> Optional[Any]:
        """Получает экипированный предмет из слота"""
        if slot_name in self.slots:
            return self.slots[slot_name].item
        return None

    def get_equipped_items(self) -> Dict[str, Any]:
        """Получает все экипированные предметы"""
        return {
            slot_name: slot.item
            for slot_name, slot in self.slots.items()
            if not slot.is_empty()
        }

    def get_equipment_bonuses(self) -> Dict[str, float]:
        """Получает бонусы от экипировки"""
        bonuses = {}

        for slot in self.slots.values():
            if not slot.is_empty() and hasattr(slot.item, "modifiers"):
                for stat, value in slot.item.modifiers.items():
                    if stat in bonuses:
                        bonuses[stat] += value
                    else:
                        bonuses[stat] = value

        return bonuses

    def get_equipment_resistances(self) -> Dict[str, float]:
        """Получает сопротивления от экипировки"""
        resistances = {}

        for slot in self.slots.values():
            if not slot.is_empty():
                # Проверяем resist_mod
                if hasattr(slot.item, "resist_mod"):
                    for element, value in slot.item.resist_mod.items():
                        if element in resistances:
                            resistances[element] += value
                        else:
                            resistances[element] = value

                # Проверяем weakness_mod
                if hasattr(slot.item, "weakness_mod"):
                    for element, value in slot.item.weakness_mod.items():
                        if element in resistances:
                            resistances[element] -= value
                        else:
                            resistances[element] = -value

        return resistances


class InventoryManager:
    """Менеджер инвентаря и экипировки"""

    def __init__(self, max_inventory_size: int = 20):
        # Получаем настройки инвентаря
        from config.unified_settings import UnifiedSettings

        self.max_inventory_size = max_inventory_size if max_inventory_size > 0 else 20
        self.inventory = Inventory(max_inventory_size)
        self.equipment = Equipment()

    def add_item_to_inventory(self, item: Any) -> bool:
        """Добавляет предмет в инвентарь"""
        return self.inventory.add_item(item)

    def remove_item_from_inventory(self, item: Any) -> bool:
        """Удаляет предмет из инвентаря"""
        return self.inventory.remove_item(item)

    def equip_item(self, item: Any, slot_name: str) -> bool:
        """Экипирует предмет"""
        # Удаляем предмет из инвентаря
        if self.inventory.remove_item(item):
            # Экипируем предмет
            previous_item = self.equipment.equip_item(item, slot_name)

            # Если был предыдущий предмет, возвращаем его в инвентарь
            if previous_item:
                self.inventory.add_item(previous_item)

            return True
        return False

    def unequip_item(self, slot_name: str) -> bool:
        """Снимает предмет из экипировки"""
        item = self.equipment.unequip_item(slot_name)
        if item:
            return self.inventory.add_item(item)
        return False

    def get_inventory_items(self) -> List[Any]:
        """Получает предметы из инвентаря"""
        return self.inventory.items.copy()

    def get_equipped_items(self) -> Dict[str, Any]:
        """Получает экипированные предметы"""
        return self.equipment.get_equipped_items()

    def get_equipment_bonuses(self) -> Dict[str, float]:
        """Получает бонусы от экипировки"""
        return self.equipment.get_equipment_bonuses()

    def get_equipment_resistances(self) -> Dict[str, float]:
        """Получает сопротивления от экипировки"""
        return self.equipment.get_equipment_resistances()

    def is_inventory_full(self) -> bool:
        """Проверяет, полон ли инвентарь"""
        return self.inventory.is_full()

    def get_free_inventory_space(self) -> int:
        """Возвращает количество свободных слотов в инвентаре"""
        return self.inventory.get_free_space()

    def get_inventory_weight_percentage(self) -> float:
        """Возвращает процент заполнения инвентаря по весу"""
        return self.inventory.get_weight_percentage()

    def is_inventory_overweight(self) -> bool:
        """Проверяет, перегружен ли инвентарь"""
        return self.inventory.is_overweight()
