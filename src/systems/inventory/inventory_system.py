#!/usr/bin/env python3
"""
Система инвентаря - управление предметами сущностей
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem, Priority
from ...core.constants import (
    ItemType, ItemRarity, ItemCategory, StatType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class InventorySlot:
    """Слот инвентаря"""
    slot_id: int
    item_id: Optional[str] = None
    item_count: int = 0
    is_locked: bool = False
    lock_reason: str = ""
    last_updated: float = field(default_factory=time.time)

@dataclass
class Inventory:
    """Инвентарь сущности"""
    entity_id: str
    slots: List[InventorySlot] = field(default_factory=list)
    max_slots: int = SYSTEM_LIMITS["max_inventory_slots"]
    max_weight: float = SYSTEM_LIMITS["max_inventory_weight"]
    current_weight: float = 0.0
    is_expandable: bool = True
    expansion_cost: int = 100
    last_update: float = field(default_factory=time.time)
    inventory_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ItemStack:
    """Стек предметов"""
    item_id: str
    count: int
    max_stack_size: int = SYSTEM_LIMITS["max_item_stack_size"]
    quality: float = 1.0
    durability: float = 1.0
    created_time: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

class InventorySystem(BaseGameSystem):
    """Система управления инвентарями"""
    
    def __init__(self):
        super().__init__("inventory", Priority.NORMAL)
        
        # Инвентари сущностей
        self.inventories: Dict[str, Inventory] = {}
        
        # Предметы в инвентарях
        self.item_stacks: Dict[str, ItemStack] = {}
        
        # История операций с инвентарем
        self.inventory_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'default_slots': SYSTEM_LIMITS["default_inventory_slots"],
            'max_slots': SYSTEM_LIMITS["max_inventory_slots"],
            'max_weight': SYSTEM_LIMITS["max_inventory_weight"],
            'max_stack_size': SYSTEM_LIMITS["max_item_stack_size"],
            'weight_check_enabled': True,
            'stacking_enabled': True,
            'auto_sort_enabled': False
        }
        
        # Статистика системы
        self.system_stats = {
            'total_inventories': 0,
            'total_items': 0,
            'total_weight': 0.0,
            'items_added': 0,
            'items_removed': 0,
            'inventories_expanded': 0,
            'update_time': 0.0
        }
        
        logger.info("Система инвентаря инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы инвентаря"""
        try:
            if not super().initialize():
                return False
                
            logger.info("Инициализация системы инвентаря...")
            
            # Настраиваем систему
            self._setup_inventory_system()
            
            # Создаем базовые шаблоны инвентарей
            self._create_base_inventory_templates()
            
            # Регистрация состояний и репозиториев
            self._register_states()
            self._register_repositories()
            
            logger.info("Система инвентаря успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы инвентаря: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск системы"""
        try:
            if not super().start():
                return False
            
            # Восстановление данных из репозиториев
            self._restore_from_repositories()
            
            logger.info("Система инвентаря запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы инвентаря: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы"""
        try:
            # Сохранение данных в репозитории
            self._save_to_repositories()
            
            if not super().stop():
                return False
            
            logger.info("Система инвентаря остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки системы инвентаря: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы"""
        try:
            # Сохранение данных в репозитории
            self._save_to_repositories()
            
            if not super().destroy():
                return False
            
            logger.info("Система инвентаря уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы инвентаря: {e}")
            return False
    
    def update(self, delta_time: float) -> None:
        """Обновление системы инвентаря"""
        try:
            super().update(delta_time)
            
            start_time = time.time()
            
            # Обновляем инвентари
            self._update_inventories(delta_time)
            
            # Проверяем предметы на истечение срока
            self._check_expired_items(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            # Обновление состояний
            self._update_states()
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы инвентаря: {e}")
    
    def _register_states(self):
        """Регистрация состояний в StateManager"""
        if not self.state_manager:
            return
            
        try:
            # Настройки системы инвентаря
            self.state_manager.register_state(
                "inventory_system_settings",
                self.system_settings
            )
            
            # Статистика системы инвентаря
            self.state_manager.register_state(
                "inventory_system_stats",
                self.system_stats
            )
            
            # Активные инвентари
            self.state_manager.register_state(
                "active_inventories",
                {entity_id: {
                    "max_slots": inv.max_slots,
                    "current_weight": inv.current_weight,
                    "max_weight": inv.max_weight,
                    "is_expandable": inv.is_expandable,
                    "slot_count": len(inv.slots)
                } for entity_id, inv in self.inventories.items()}
            )
            
            logger.debug("Состояния системы инвентаря зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации состояний системы инвентаря: {e}")
    
    def _register_repositories(self):
        """Регистрация репозиториев в RepositoryManager"""
        if not self.repository_manager:
            return
            
        try:
            # Инвентари
            self.repository_manager.register_repository(
                "inventories",
                "inventories",
                "memory"
            )
            
            # Стеки предметов
            self.repository_manager.register_repository(
                "item_stacks",
                "item_stacks",
                "memory"
            )
            
            # История инвентаря
            self.repository_manager.register_repository(
                "inventory_history",
                "inventory_history",
                "memory"
            )
            
            logger.debug("Репозитории системы инвентаря зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации репозиториев системы инвентаря: {e}")
    
    def _restore_from_repositories(self):
        """Восстановление данных из репозиториев"""
        if not self.repository_manager:
            return
            
        try:
            # Восстанавливаем инвентари
            inventories_data = self.repository_manager.get_repository("inventories").get_all()
            if inventories_data:
                for inv_data in inventories_data:
                    if inv_data.get("entity_id"):
                        self.inventories[inv_data["entity_id"]] = Inventory(**inv_data)
                        self.system_stats['total_inventories'] += 1
            
            # Восстанавливаем стеки предметов
            item_stacks_data = self.repository_manager.get_repository("item_stacks").get_all()
            if item_stacks_data:
                for stack_data in item_stacks_data:
                    if stack_data.get("item_id"):
                        self.item_stacks[stack_data["item_id"]] = ItemStack(**stack_data)
                        self.system_stats['total_items'] += stack_data.get("count", 1)
            
            # Восстанавливаем историю
            history_data = self.repository_manager.get_repository("inventory_history").get_all()
            if history_data:
                for hist_data in history_data:
                    if hist_data.get("timestamp"):
                        self.inventory_history.append(hist_data)
            
            logger.debug("Данные системы инвентаря восстановлены из репозиториев")
            
        except Exception as e:
            logger.warning(f"Ошибка восстановления данных системы инвентаря: {e}")
    
    def _save_to_repositories(self):
        """Сохранение данных в репозитории"""
        if not self.repository_manager:
            return
            
        try:
            # Сохраняем инвентари
            inventories_repo = self.repository_manager.get_repository("inventories")
            inventories_repo.clear()
            for entity_id, inventory in self.inventories.items():
                inventories_repo.create({
                    "entity_id": inventory.entity_id,
                    "max_slots": inventory.max_slots,
                    "max_weight": inventory.max_weight,
                    "current_weight": inventory.current_weight,
                    "is_expandable": inventory.is_expandable,
                    "expansion_cost": inventory.expansion_cost,
                    "last_update": inventory.last_update
                })
            
            # Сохраняем стеки предметов
            item_stacks_repo = self.repository_manager.get_repository("item_stacks")
            item_stacks_repo.clear()
            for item_id, stack in self.item_stacks.items():
                item_stacks_repo.create({
                    "item_id": stack.item_id,
                    "count": stack.count,
                    "max_stack_size": stack.max_stack_size,
                    "quality": stack.quality,
                    "durability": stack.durability,
                    "created_time": stack.created_time,
                    "last_used": stack.last_used
                })
            
            # Сохраняем историю
            history_repo = self.repository_manager.get_repository("inventory_history")
            history_repo.clear()
            for hist_entry in self.inventory_history:
                history_repo.create(hist_entry)
            
            logger.debug("Данные системы инвентаря сохранены в репозитории")
            
        except Exception as e:
            logger.warning(f"Ошибка сохранения данных системы инвентаря: {e}")
    
    def _update_states(self):
        """Обновление состояний в StateManager"""
        if not self.state_manager:
            return
            
        try:
            # Обновляем статистику
            self.state_manager.set_state_value("inventory_system_stats", self.system_stats)
            
            # Обновляем активные инвентари
            self.state_manager.set_state_value("active_inventories", {
                entity_id: {
                    "max_slots": inv.max_slots,
                    "current_weight": inv.current_weight,
                    "max_weight": inv.max_weight,
                    "is_expandable": inv.is_expandable,
                    "slot_count": len(inv.slots)
                } for entity_id, inv in self.inventories.items()
            })
            
        except Exception as e:
            logger.warning(f"Ошибка обновления состояний системы инвентаря: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return self.system_stats.copy()
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        self.system_stats = {
            'total_inventories': 0,
            'total_items': 0,
            'total_weight': 0.0,
            'items_added': 0,
            'items_removed': 0,
            'inventories_expanded': 0,
            'update_time': 0.0
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "item_created":
                return self._handle_item_created(event_data)
            elif event_type == "item_destroyed":
                return self._handle_item_destroyed(event_data)
            elif event_type == "combat_ended":
                return self._handle_combat_ended(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'total_inventories': len(self.inventories),
            'total_items': self.system_stats['total_items'],
            'total_weight': self.system_stats['total_weight'],
            'stats': self.system_stats
        }
    
    def _setup_inventory_system(self) -> None:
        """Настройка системы инвентаря"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система инвентаря настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему инвентаря: {e}")
    
    def _create_base_inventory_templates(self) -> None:
        """Создание базовых шаблонов инвентарей"""
        try:
            # Здесь можно создать базовые шаблоны для разных типов сущностей
            logger.debug("Базовые шаблоны инвентарей созданы")
        except Exception as e:
            logger.warning(f"Не удалось создать базовые шаблоны инвентарей: {e}")
    
    def _update_inventories(self, delta_time: float) -> None:
        """Обновление инвентарей"""
        try:
            current_time = time.time()
            
            for entity_id, inventory in self.inventories.items():
                # Обновляем время последнего обновления
                inventory.last_update = current_time
                
                # Пересчитываем вес
                self._recalculate_inventory_weight(inventory)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления инвентарей: {e}")
    
    def _check_expired_items(self, delta_time: float) -> None:
        """Проверка предметов на истечение срока"""
        try:
            current_time = time.time()
            expired_items = []
            
            for item_id, item_stack in self.item_stacks.items():
                # Проверяем срок годности (если есть)
                if hasattr(item_stack, 'expiry_time') and item_stack.expiry_time > 0:
                    if current_time > item_stack.expiry_time:
                        expired_items.append(item_id)
                
                # Проверяем прочность
                if item_stack.durability <= 0:
                    expired_items.append(item_id)
            
            # Удаляем истекшие предметы
            for item_id in expired_items:
                self._remove_expired_item(item_id)
                
        except Exception as e:
            logger.warning(f"Ошибка проверки истекших предметов: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['total_inventories'] = len(self.inventories)
            self.system_stats['total_items'] = len(self.item_stacks)
            self.system_stats['total_weight'] = sum(inv.current_weight for inv in self.inventories.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            inventory_config = event_data.get('inventory_config', {})
            
            if entity_id:
                return self.create_inventory(entity_id, inventory_config)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_inventory(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_item_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания предмета"""
        try:
            item_id = event_data.get('item_id')
            item_data = event_data.get('item_data', {})
            
            if item_id and item_data:
                # Здесь можно добавить логику для новых предметов
                logger.debug(f"Обработано событие создания предмета {item_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания предмета: {e}")
            return False
    
    def _handle_item_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения предмета"""
        try:
            item_id = event_data.get('item_id')
            
            if item_id:
                # Удаляем предмет из всех инвентарей
                self._remove_item_from_all_inventories(item_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения предмета: {e}")
            return False
    
    def _handle_combat_ended(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события окончания боя"""
        try:
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            loot = event_data.get('loot', {})
            
            if combat_id and participants and loot:
                # Распределяем добычу между участниками
                self._distribute_combat_loot(participants, loot)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события окончания боя: {e}")
            return False
    
    def create_inventory(self, entity_id: str, config: Dict[str, Any] = None) -> bool:
        """Создание инвентаря для сущности"""
        try:
            if entity_id in self.inventories:
                logger.warning(f"Инвентарь для {entity_id} уже существует")
                return False
            
            # Настройки по умолчанию
            default_config = {
                'max_slots': self.system_settings['default_slots'],
                'max_weight': self.system_settings['max_weight'],
                'is_expandable': True,
                'expansion_cost': 100
            }
            
            if config:
                default_config.update(config)
            
            # Создаем слоты
            slots = []
            for i in range(default_config['max_slots']):
                slot = InventorySlot(slot_id=i)
                slots.append(slot)
            
            # Создаем инвентарь
            inventory = Inventory(
                entity_id=entity_id,
                slots=slots,
                max_slots=default_config['max_slots'],
                max_weight=default_config['max_weight'],
                is_expandable=default_config['is_expandable'],
                expansion_cost=default_config['expansion_cost']
            )
            
            # Добавляем в систему
            self.inventories[entity_id] = inventory
            
            # Записываем в историю
            current_time = time.time()
            self.inventory_history.append({
                'timestamp': current_time,
                'action': 'inventory_created',
                'entity_id': entity_id,
                'max_slots': inventory.max_slots,
                'max_weight': inventory.max_weight
            })
            
            logger.info(f"Создан инвентарь для {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания инвентаря для {entity_id}: {e}")
            return False
    
    def destroy_inventory(self, entity_id: str) -> bool:
        """Уничтожение инвентаря сущности"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            
            # Удаляем все предметы
            for slot in inventory.slots:
                if slot.item_id:
                    self._remove_item_from_slot(entity_id, slot.slot_id)
            
            # Удаляем инвентарь
            del self.inventories[entity_id]
            
            # Записываем в историю
            current_time = time.time()
            self.inventory_history.append({
                'timestamp': current_time,
                'action': 'inventory_destroyed',
                'entity_id': entity_id
            })
            
            logger.info(f"Инвентарь {entity_id} уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения инвентаря {entity_id}: {e}")
            return False
    
    def add_item_to_inventory(self, entity_id: str, item_id: str, count: int = 1, 
                             slot_id: Optional[int] = None, quality: float = 1.0) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            if entity_id not in self.inventories:
                logger.warning(f"Инвентарь для {entity_id} не найден")
                return False
            
            inventory = self.inventories[entity_id]
            
            # Проверяем вес
            if self.system_settings['weight_check_enabled']:
                item_weight = self._get_item_weight(item_id)
                if inventory.current_weight + item_weight * count > inventory.max_weight:
                    logger.warning(f"Недостаточно места по весу в инвентаре {entity_id}")
                    return False
            
            # Ищем подходящий слот
            target_slot = None
            if slot_id is not None:
                if 0 <= slot_id < len(inventory.slots):
                    target_slot = inventory.slots[slot_id]
                else:
                    logger.warning(f"Неверный ID слота {slot_id}")
                    return False
            else:
                # Ищем свободный слот или слот с тем же предметом
                target_slot = self._find_suitable_slot(inventory, item_id, count)
            
            if not target_slot:
                logger.warning(f"Нет свободного места в инвентаре {entity_id}")
                return False
            
            # Добавляем предмет
            if target_slot.item_id == item_id:
                # Добавляем к существующему стеку
                target_slot.item_count += count
                target_slot.last_updated = time.time()
                
                # Обновляем стек предметов
                stack_key = f"{entity_id}_{target_slot.slot_id}"
                if stack_key in self.item_stacks:
                    self.item_stacks[stack_key].count += count
                    self.item_stacks[stack_key].last_used = time.time()
                else:
                    self.item_stacks[stack_key] = ItemStack(
                        item_id=item_id,
                        count=target_slot.item_count,
                        quality=quality
                    )
            else:
                # Создаем новый стек
                target_slot.item_id = item_id
                target_slot.item_count = count
                target_slot.last_updated = time.time()
                
                # Создаем стек предметов
                stack_key = f"{entity_id}_{target_slot.slot_id}"
                self.item_stacks[stack_key] = ItemStack(
                    item_id=item_id,
                    count=count,
                    quality=quality
                )
            
            # Обновляем вес
            self._recalculate_inventory_weight(inventory)
            
            # Записываем в историю
            current_time = time.time()
            self.inventory_history.append({
                'timestamp': current_time,
                'action': 'item_added',
                'entity_id': entity_id,
                'item_id': item_id,
                'count': count,
                'slot_id': target_slot.slot_id
            })
            
            inventory.inventory_history.append({
                'timestamp': current_time,
                'action': 'item_added',
                'item_id': item_id,
                'count': count,
                'slot_id': target_slot.slot_id
            })
            
            self.system_stats['items_added'] += 1
            logger.debug(f"Добавлен предмет {item_id} в инвентарь {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета {item_id} в инвентарь {entity_id}: {e}")
            return False
    
    def remove_item_from_inventory(self, entity_id: str, item_id: str, count: int = 1, 
                                  slot_id: Optional[int] = None) -> bool:
        """Удаление предмета из инвентаря"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            
            # Ищем слот с предметом
            target_slot = None
            if slot_id is not None:
                if 0 <= slot_id < len(inventory.slots):
                    target_slot = inventory.slots[slot_id]
                else:
                    return False
            else:
                # Ищем любой слот с нужным предметом
                for slot in inventory.slots:
                    if slot.item_id == item_id and slot.item_count > 0:
                        target_slot = slot
                        break
            
            if not target_slot or target_slot.item_id != item_id:
                return False
            
            # Удаляем предметы
            if target_slot.item_count <= count:
                # Удаляем весь стек
                removed_count = target_slot.item_count
                target_slot.item_id = None
                target_slot.item_count = 0
                
                # Удаляем стек предметов
                stack_key = f"{entity_id}_{target_slot.slot_id}"
                if stack_key in self.item_stacks:
                    del self.item_stacks[stack_key]
            else:
                # Уменьшаем количество
                target_slot.item_count -= count
                removed_count = count
                
                # Обновляем стек предметов
                stack_key = f"{entity_id}_{target_slot.slot_id}"
                if stack_key in self.item_stacks:
                    self.item_stacks[stack_key].count -= count
            
            target_slot.last_updated = time.time()
            
            # Обновляем вес
            self._recalculate_inventory_weight(inventory)
            
            # Записываем в историю
            current_time = time.time()
            self.inventory_history.append({
                'timestamp': current_time,
                'action': 'item_removed',
                'entity_id': entity_id,
                'item_id': item_id,
                'count': removed_count,
                'slot_id': target_slot.slot_id
            })
            
            inventory.inventory_history.append({
                'timestamp': current_time,
                'action': 'item_removed',
                'item_id': item_id,
                'count': removed_count,
                'slot_id': target_slot.slot_id
            })
            
            self.system_stats['items_removed'] += 1
            logger.debug(f"Удален предмет {item_id} из инвентаря {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления предмета {item_id} из инвентаря {entity_id}: {e}")
            return False
    
    def _find_suitable_slot(self, inventory: Inventory, item_id: str, count: int) -> Optional[InventorySlot]:
        """Поиск подходящего слота для предмета"""
        try:
            # Сначала ищем слот с тем же предметом
            for slot in inventory.slots:
                if slot.item_id == item_id and not slot.is_locked:
                    # Проверяем, поместится ли еще
                    current_stack = self.item_stacks.get(f"{inventory.entity_id}_{slot.slot_id}")
                    if current_stack and current_stack.count + count <= current_stack.max_stack_size:
                        return slot
            
            # Ищем свободный слот
            for slot in inventory.slots:
                if slot.item_id is None and not slot.is_locked:
                    return slot
            
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка поиска подходящего слота: {e}")
            return None
    
    def _remove_item_from_slot(self, entity_id: str, slot_id: int) -> bool:
        """Удаление предмета из конкретного слота"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            if slot_id >= len(inventory.slots):
                return False
            
            slot = inventory.slots[slot_id]
            if not slot.item_id:
                return False
            
            # Удаляем предмет
            item_id = slot.item_id
            count = slot.item_count
            
            slot.item_id = None
            slot.item_count = 0
            slot.last_updated = time.time()
            
            # Удаляем стек предметов
            stack_key = f"{entity_id}_{slot_id}"
            if stack_key in self.item_stacks:
                del self.item_stacks[stack_key]
            
            # Обновляем вес
            self._recalculate_inventory_weight(inventory)
            
            logger.debug(f"Удален предмет {item_id} из слота {slot_id} инвентаря {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления предмета из слота {slot_id} инвентаря {entity_id}: {e}")
            return False
    
    def _remove_item_from_all_inventories(self, item_id: str) -> None:
        """Удаление предмета из всех инвентарей"""
        try:
            for entity_id, inventory in self.inventories.items():
                for slot in inventory.slots:
                    if slot.item_id == item_id:
                        self._remove_item_from_slot(entity_id, slot.slot_id)
                        
        except Exception as e:
            logger.error(f"Ошибка удаления предмета {item_id} из всех инвентарей: {e}")
    
    def _remove_expired_item(self, item_id: str) -> None:
        """Удаление истекшего предмета"""
        try:
            # Удаляем из всех инвентарей
            self._remove_item_from_all_inventories(item_id)
            
            # Удаляем из стеков предметов
            expired_stacks = [key for key, stack in self.item_stacks.items() if stack.item_id == item_id]
            for key in expired_stacks:
                del self.item_stacks[key]
            
            logger.debug(f"Удален истекший предмет {item_id}")
            
        except Exception as e:
            logger.error(f"Ошибка удаления истекшего предмета {item_id}: {e}")
    
    def _distribute_combat_loot(self, participants: List[str], loot: Dict[str, Any]) -> None:
        """Распределение добычи после боя"""
        try:
            if not participants or not loot:
                return
            
            # Простое распределение - каждому участнику по предмету
            for i, participant_id in enumerate(participants):
                if participant_id in self.inventories:
                    # Получаем предмет из добычи
                    item_id = list(loot.keys())[i % len(loot)]
                    item_data = loot[item_id]
                    
                    # Добавляем в инвентарь
                    self.add_item_to_inventory(
                        participant_id, 
                        item_id, 
                        count=item_data.get('count', 1),
                        quality=item_data.get('quality', 1.0)
                    )
                    
        except Exception as e:
            logger.error(f"Ошибка распределения добычи: {e}")
    
    def _recalculate_inventory_weight(self, inventory: Inventory) -> None:
        """Пересчет веса инвентаря"""
        try:
            total_weight = 0.0
            
            for slot in inventory.slots:
                if slot.item_id:
                    item_weight = self._get_item_weight(slot.item_id)
                    total_weight += item_weight * slot.item_count
            
            inventory.current_weight = total_weight
            
        except Exception as e:
            logger.warning(f"Ошибка пересчета веса инвентаря: {e}")
    
    def _get_item_weight(self, item_id: str) -> float:
        """Получение веса предмета"""
        try:
            # Здесь должна быть логика получения веса предмета
            # Пока возвращаем базовый вес
            return 1.0
            
        except Exception as e:
            logger.warning(f"Ошибка получения веса предмета {item_id}: {e}")
            return 1.0
    
    def get_inventory_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об инвентаре"""
        try:
            if entity_id not in self.inventories:
                return None
            
            inventory = self.inventories[entity_id]
            
            return {
                'entity_id': inventory.entity_id,
                'max_slots': inventory.max_slots,
                'used_slots': sum(1 for slot in inventory.slots if slot.item_id),
                'max_weight': inventory.max_weight,
                'current_weight': inventory.current_weight,
                'is_expandable': inventory.is_expandable,
                'expansion_cost': inventory.expansion_cost,
                'last_update': inventory.last_update,
                'slots': [
                    {
                        'slot_id': slot.slot_id,
                        'item_id': slot.item_id,
                        'item_count': slot.item_count,
                        'is_locked': slot.is_locked,
                        'lock_reason': slot.lock_reason,
                        'last_updated': slot.last_updated
                    }
                    for slot in inventory.slots
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об инвентаре {entity_id}: {e}")
            return None
    
    def expand_inventory(self, entity_id: str, additional_slots: int = 1) -> bool:
        """Расширение инвентаря"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            
            if not inventory.is_expandable:
                logger.warning(f"Инвентарь {entity_id} не может быть расширен")
                return False
            
            if inventory.max_slots + additional_slots > self.system_settings['max_slots']:
                logger.warning(f"Достигнут максимальный размер инвентаря")
                return False
            
            # Добавляем новые слоты
            for i in range(additional_slots):
                new_slot_id = inventory.max_slots + i
                new_slot = InventorySlot(slot_id=new_slot_id)
                inventory.slots.append(new_slot)
            
            inventory.max_slots += additional_slots
            
            # Записываем в историю
            current_time = time.time()
            self.inventory_history.append({
                'timestamp': current_time,
                'action': 'inventory_expanded',
                'entity_id': entity_id,
                'additional_slots': additional_slots,
                'new_max_slots': inventory.max_slots
            })
            
            self.system_stats['inventories_expanded'] += 1
            logger.info(f"Инвентарь {entity_id} расширен на {additional_slots} слотов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка расширения инвентаря {entity_id}: {e}")
            return False
    
    def lock_slot(self, entity_id: str, slot_id: int, reason: str = "") -> bool:
        """Блокировка слота инвентаря"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            if slot_id >= len(inventory.slots):
                return False
            
            slot = inventory.slots[slot_id]
            slot.is_locked = True
            slot.lock_reason = reason
            slot.last_updated = time.time()
            
            logger.debug(f"Заблокирован слот {slot_id} инвентаря {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка блокировки слота {slot_id} инвентаря {entity_id}: {e}")
            return False
    
    def unlock_slot(self, entity_id: str, slot_id: int) -> bool:
        """Разблокировка слота инвентаря"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            if slot_id >= len(inventory.slots):
                return False
            
            slot = inventory.slots[slot_id]
            slot.is_locked = False
            slot.lock_reason = ""
            slot.last_updated = time.time()
            
            logger.debug(f"Разблокирован слот {slot_id} инвентаря {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка разблокировки слота {slot_id} инвентаря {entity_id}: {e}")
            return False
    
    def get_inventory_history(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории инвентаря"""
        try:
            if entity_id not in self.inventories:
                return []
            
            inventory = self.inventories[entity_id]
            
            # Возвращаем последние записи
            return inventory.inventory_history[-limit:]
            
        except Exception as e:
            logger.error(f"Ошибка получения истории инвентаря для {entity_id}: {e}")
            return []
    
    def clear_inventory(self, entity_id: str) -> bool:
        """Очистка всего инвентаря"""
        try:
            if entity_id not in self.inventories:
                return False
            
            inventory = self.inventories[entity_id]
            
            # Удаляем все предметы
            for slot in inventory.slots:
                if slot.item_id:
                    self._remove_item_from_slot(entity_id, slot.slot_id)
            
            logger.info(f"Инвентарь {entity_id} очищен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки инвентаря {entity_id}: {e}")
            return False
    
    def transfer_item(self, from_entity_id: str, to_entity_id: str, item_id: str, 
                     count: int = 1, from_slot_id: Optional[int] = None) -> bool:
        """Передача предмета между инвентарями"""
        try:
            # Удаляем из исходного инвентаря
            if not self.remove_item_from_inventory(from_entity_id, item_id, count, from_slot_id):
                return False
            
            # Добавляем в целевой инвентарь
            if not self.add_item_to_inventory(to_entity_id, item_id, count):
                # Если не удалось добавить, возвращаем обратно
                self.add_item_to_inventory(from_entity_id, item_id, count, from_slot_id)
                return False
            
            logger.debug(f"Предмет {item_id} передан от {from_entity_id} к {to_entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка передачи предмета {item_id}: {e}")
            return False
