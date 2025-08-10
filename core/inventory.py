"""Компонент для управления инвентарем и экипировкой."""

from typing import Dict, Any, Optional, List, Tuple
from .component import Component


class InventoryComponent(Component):
    """Компонент для управления инвентарем."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.inventory: List[Dict[str, Any]] = []
        self.max_inventory_size = 20
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "helmet": None,
            "gloves": None,
            "boots": None,
            "accessory1": None,
            "accessory2": None
        }
    
    def add_item(self, item: Dict[str, Any]) -> bool:
        """Добавить предмет в инвентарь."""
        if len(self.inventory) >= self.max_inventory_size:
            return False
        
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Dict[str, Any]) -> bool:
        """Убрать предмет из инвентаря."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def remove_item_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Убрать предмет по индексу."""
        if 0 <= index < len(self.inventory):
            return self.inventory.pop(index)
        return None
    
    def get_item_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Получить предмет по индексу."""
        if 0 <= index < len(self.inventory):
            return self.inventory[index]
        return None
    
    def has_item(self, item_id: str) -> bool:
        """Проверить наличие предмета по ID."""
        return any(item.get('id') == item_id for item in self.inventory)
    
    def get_item_count(self, item_id: str) -> int:
        """Получить количество предметов по ID."""
        return sum(1 for item in self.inventory if item.get('id') == item_id)
    
    def find_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Найти предметы по типу."""
        return [item for item in self.inventory if item.get('type') == item_type]
    
    def find_consumables(self) -> List[Dict[str, Any]]:
        """Найти все расходуемые предметы."""
        return self.find_items_by_type("consumable")
    
    def find_healing_items(self) -> List[Dict[str, Any]]:
        """Найти предметы для лечения."""
        healing_items = []
        for item in self.inventory:
            if item.get('type') == 'consumable' and 'heal' in item.get('effects', {}):
                healing_items.append(item)
        return healing_items
    
    def use_consumable(self, item: Dict[str, Any]) -> bool:
        """Использовать расходуемый предмет."""
        if item.get('type') == 'consumable' and item in self.inventory:
            # Применяем эффекты предмета
            effects = item.get('effects', {})
            if self._apply_item_effects(effects):
                # Убираем предмет из инвентаря
                self.remove_item(item)
                return True
        return False
    
    def _apply_item_effects(self, effects: Dict[str, Any]) -> bool:
        """Применить эффекты предмета."""
        try:
            # Получаем компонент боевых характеристик
            combat_stats = self.entity.get_component('CombatStatsComponent')
            if not combat_stats:
                return False
            
            # Применяем эффекты
            if 'heal' in effects:
                heal_amount = effects['heal']
                combat_stats.heal(heal_amount)
            
            if 'restore_mana' in effects:
                mana_amount = effects['restore_mana']
                combat_stats.restore_mana(mana_amount)
            
            if 'restore_stamina' in effects:
                stamina_amount = effects['restore_stamina']
                combat_stats.restore_stamina(stamina_amount)
            
            return True
        except Exception:
            return False
    
    def equip_item(self, item: Dict[str, Any], slot: str) -> bool:
        """Экипировать предмет."""
        if slot not in self.equipment:
            return False
        
        # Проверяем, что предмет подходит для слота
        if not self._can_equip_to_slot(item, slot):
            return False
        
        # Снимаем текущий предмет из слота
        if self.equipment[slot]:
            self.unequip_item(slot)
        
        # Экипируем новый предмет
        self.equipment[slot] = item
        
        # Применяем эффекты экипировки
        self._apply_equipment_effects(item, True)
        
        return True
    
    def unequip_item(self, slot: str) -> Optional[Dict[str, Any]]:
        """Снять предмет из слота."""
        if slot not in self.equipment or not self.equipment[slot]:
            return None
        
        item = self.equipment[slot]
        self.equipment[slot] = None
        
        # Убираем эффекты экипировки
        self._apply_equipment_effects(item, False)
        
        return item
    
    def _can_equip_to_slot(self, item: Dict[str, Any], slot: str) -> bool:
        """Проверить, можно ли экипировать предмет в слот."""
        item_type = item.get('type')
        slot_type = slot
        
        # Простая проверка совместимости
        if slot_type == 'weapon' and item_type in ['sword', 'bow', 'staff', 'dagger']:
            return True
        elif slot_type == 'armor' and item_type == 'armor':
            return True
        elif slot_type == 'shield' and item_type == 'shield':
            return True
        elif slot_type in ['helmet', 'gloves', 'boots'] and item_type == 'armor':
            return True
        elif slot_type.startswith('accessory') and item_type == 'accessory':
            return True
        
        return False
    
    def _apply_equipment_effects(self, item: Dict[str, Any], equipping: bool) -> None:
        """Применить или убрать эффекты экипировки."""
        try:
            # Получаем компоненты
            combat_stats = self.entity.get_component('CombatStatsComponent')
            attributes = self.entity.get_component('AttributesComponent')
            
            if not combat_stats or not attributes:
                return
            
            effects = item.get('equipment_effects', {})
            multiplier = 1 if equipping else -1
            
            # Применяем эффекты к боевым характеристикам
            for stat, value in effects.get('combat_stats', {}).items():
                if hasattr(combat_stats.stats, stat):
                    current_value = getattr(combat_stats.stats, stat)
                    setattr(combat_stats.stats, stat, current_value + (value * multiplier))
            
            # Применяем эффекты к атрибутам
            for attr, value in effects.get('attributes', {}).items():
                attributes.add_attribute_bonus(attr, f"equipment_{item.get('id', 'unknown')}", value * multiplier)
        
        except Exception:
            pass
    
    def get_equipped_item(self, slot: str) -> Optional[Dict[str, Any]]:
        """Получить экипированный предмет из слота."""
        return self.equipment.get(slot)
    
    def is_slot_occupied(self, slot: str) -> bool:
        """Занят ли слот."""
        return slot in self.equipment and self.equipment[slot] is not None
    
    def get_inventory_size(self) -> int:
        """Получить текущий размер инвентаря."""
        return len(self.inventory)
    
    def get_free_slots(self) -> int:
        """Получить количество свободных слотов."""
        return self.max_inventory_size - len(self.inventory)
    
    def is_inventory_full(self) -> bool:
        """Полон ли инвентарь."""
        return len(self.inventory) >= self.max_inventory_size
    
    def _on_initialize(self) -> None:
        """Инициализация компонента."""
        pass
    
    def _on_update(self, delta_time: float) -> None:
        """Обновление компонента."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        data = super().to_dict()
        data.update({
            'inventory': self.inventory.copy(),
            'max_inventory_size': self.max_inventory_size,
            'equipment': {
                slot: item.copy() if item else None
                for slot, item in self.equipment.items()
            }
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация из словаря."""
        super().from_dict(data)
        
        self.inventory = data.get('inventory', []).copy()
        self.max_inventory_size = data.get('max_inventory_size', 20)
        
        equipment_data = data.get('equipment', {})
        for slot, item in equipment_data.items():
            if slot in self.equipment:
                self.equipment[slot] = item.copy() if item else None
