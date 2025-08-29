"""
Inventory System Package
Система инвентаря
"""

from systems.inventory.inventory_system import InventorySystem, Inventory, InventorySlot
from core.constants import ItemCategory

__all__ = ['InventorySystem', 'Inventory', 'InventorySlot', 'ItemCategory']
