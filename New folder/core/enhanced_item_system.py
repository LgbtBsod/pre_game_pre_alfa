#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УЛУЧШЕННАЯ СИСТЕМА ПРЕДМЕТОВ
Интеграция с генератором контента и системой скиллов
Поддержка уникальных скиллов атаки для каждого оружия
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST_ITEM = "quest_item"
    KEY = "key"
    MAP = "map"
    TOOL = "tool"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class SkillType(Enum):
    """Типы скиллов"""
    ACTIVE = "active"
    PASSIVE = "passive"
    TRIGGER = "trigger"
    BASIC_ATTACK = "basic_attack"

@dataclass
class ItemSkill:
    """Скилл предмета"""
    skill_id: str
    name: str
    skill_type: SkillType
    description: str
    effects: Dict[str, Any] = field(default_factory=dict)
    cooldown: float = 0.0
    mana_cost: int = 0
    requirements: Dict[str, int] = field(default_factory=dict)
    is_weapon_basic_attack: bool = False

@dataclass
class ItemModifier:
    """Модификатор предмета"""
    modifier_type: str
    value: float
    duration: float = 0.0
    condition: str = ""

@dataclass
class ItemRequirement:
    """Требования для предмета"""
    level: int = 1
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0
    wisdom: int = 0
    charisma: int = 0
    luck: int = 0
    endurance: int = 0

@dataclass
class Item:
    """Предмет"""
    item_id: str
    name: str
    item_type: ItemType
    rarity: ItemRarity
    description: str
    base_stats: Dict[str, float] = field(default_factory=dict)
    modifiers: List[ItemModifier] = field(default_factory=list)
    skills: List[ItemSkill] = field(default_factory=list)
    basic_attack_skill: Optional[ItemSkill] = None
    requirements: ItemRequirement = field(default_factory=ItemRequirement)
    value: int = 0
    weight: float = 0.0
    durability: int = 100
    max_durability: int = 100
    stack_size: int = 1
    created_at: float = field(default_factory=time.time)

class EquipmentSlot(Enum):
    """Слоты экипировки"""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    NECK = "neck"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    CONSUMABLE = "consumable"

@dataclass
class Equipment:
    """Экипировка сущности"""
    entity_id: str
    slots: Dict[EquipmentSlot, Optional[Item]] = field(default_factory=dict)
    total_modifiers: List[ItemModifier] = field(default_factory=list)
    active_skills: List[ItemSkill] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

@dataclass
class InventorySlot:
    """Слот инвентаря"""
    item: Optional[Item] = None
    quantity: int = 0
    max_quantity: int = 1

@dataclass
class Inventory:
    """Инвентарь сущности"""
    entity_id: str
    slots: List[InventorySlot] = field(default_factory=list)
    max_slots: int = 50
    total_weight: float = 0.0
    max_weight: float = 100.0
    last_update: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Инициализация слотов инвентаря"""
        if not self.slots:
            self.slots = [InventorySlot() for _ in range(self.max_slots)]

class EnhancedItemSystem:
    """Улучшенная система предметов"""
    
    def __init__(self, items_directory: str = "data/items"):
        self.items_directory = Path(items_directory)
        self.items_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger(__name__)
        
        # Кэш предметов
        self.items_cache: Dict[str, Item] = {}
        self.equipment_cache: Dict[str, Equipment] = {}
        self.inventory_cache: Dict[str, Inventory] = {}
        
        # Шаблоны скиллов
        self.skill_templates = self._load_skill_templates()
        
        log_system_event("enhanced_item_system", "initialized")
    
    def create_item_from_generated_data(self, generated_item_data: Any) -> Item:
        """Создание предмета из данных генератора контента"""
        try:
            # Создаем базовый предмет
            item = Item(
                item_id=generated_item_data.item_id,
                name=generated_item_data.name,
                item_type=ItemType(generated_item_data.item_type),
                rarity=ItemRarity(generated_item_data.rarity.value),
                description=generated_item_data.description,
                base_stats=generated_item_data.base_stats,
                value=self._calculate_item_value(generated_item_data),
                weight=self._calculate_item_weight(generated_item_data),
                durability=100,
                max_durability=100
            )
            
            # Создаем модификаторы из специальных эффектов
            for effect in generated_item_data.special_effects:
                modifier = ItemModifier(
                    modifier_type=effect["type"],
                    value=effect["value"],
                    duration=effect.get("duration", 0.0)
                )
                item.modifiers.append(modifier)
            
            # Создаем скиллы
            for skill_id in generated_item_data.active_skills:
                skill = self._create_skill_from_template(skill_id, SkillType.ACTIVE)
                if skill:
                    item.skills.append(skill)
            
            for skill_id in generated_item_data.trigger_skills:
                skill = self._create_skill_from_template(skill_id, SkillType.TRIGGER)
                if skill:
                    item.skills.append(skill)
            
            # Создаем базовый скилл атаки для оружия
            if generated_item_data.basic_attack_skill and item.item_type == ItemType.WEAPON:
                basic_attack = self._create_basic_attack_skill(
                    generated_item_data.basic_attack_skill,
                    item
                )
                item.basic_attack_skill = basic_attack
                item.skills.append(basic_attack)
            
            # Создаем требования
            item.requirements = self._create_requirements_from_data(generated_item_data.requirements)
            
            # Кэшируем предмет
            self.items_cache[item.item_id] = item
            
            self.logger.info(f"Created item from generated data: {item.name}")
            return item
            
        except Exception as e:
            self.logger.error(f"Error creating item from generated data: {e}")
            return None
    
    def equip_item(self, entity_id: str, item: Item, slot: EquipmentSlot) -> bool:
        """Экипировка предмета"""
        try:
            if not self._can_equip_item(entity_id, item, slot):
                return False
            
            # Получаем или создаем экипировку
            if entity_id not in self.equipment_cache:
                self.equipment_cache[entity_id] = Equipment(entity_id=entity_id)
            
            equipment = self.equipment_cache[entity_id]
            
            # Снимаем старый предмет если есть
            if slot in equipment.slots and equipment.slots[slot]:
                self._unequip_item(entity_id, slot)
            
            # Экипируем новый предмет
            equipment.slots[slot] = item
            
            # Обновляем модификаторы и скиллы
            self._update_equipment_stats(entity_id)
            
            self.logger.info(f"Equipped {item.name} to {entity_id} in slot {slot.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error equipping item: {e}")
            return False
    
    def unequip_item(self, entity_id: str, slot: EquipmentSlot) -> Optional[Item]:
        """Снятие предмета"""
        try:
            if entity_id not in self.equipment_cache:
                return None
            
            equipment = self.equipment_cache[entity_id]
            if slot not in equipment.slots or not equipment.slots[slot]:
                return None
            
            item = equipment.slots[slot]
            equipment.slots[slot] = None
            
            # Обновляем модификаторы и скиллы
            self._update_equipment_stats(entity_id)
            
            self.logger.info(f"Unequipped {item.name} from {entity_id}")
            return item
            
        except Exception as e:
            self.logger.error(f"Error unequipping item: {e}")
            return None
    
    def get_equipment_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистик экипировки"""
        if entity_id not in self.equipment_cache:
            return {}
        
        equipment = self.equipment_cache[entity_id]
        
        # Суммируем все модификаторы
        total_modifiers = {}
        for modifier in equipment.total_modifiers:
            if modifier.modifier_type not in total_modifiers:
                total_modifiers[modifier.modifier_type] = 0
            total_modifiers[modifier.modifier_type] += modifier.value
        
        return {
            "modifiers": total_modifiers,
            "active_skills": [skill.skill_id for skill in equipment.active_skills],
            "equipped_items": {
                slot.value: item.name if item else None
                for slot, item in equipment.slots.items()
            }
        }
    
    def get_weapon_basic_attack_skill(self, entity_id: str) -> Optional[ItemSkill]:
        """Получение базового скилла атаки оружия"""
        if entity_id not in self.equipment_cache:
            return None
        
        equipment = self.equipment_cache[entity_id]
        main_hand_item = equipment.slots.get(EquipmentSlot.MAIN_HAND)
        
        if main_hand_item and main_hand_item.basic_attack_skill:
            return main_hand_item.basic_attack_skill
        
        return None
    
    def use_item(self, entity_id: str, item: Item) -> bool:
        """Использование предмета"""
        try:
            if item.item_type == ItemType.CONSUMABLE:
                return self._use_consumable(entity_id, item)
            elif item.item_type == ItemType.WEAPON:
                return self._use_weapon_skill(entity_id, item)
            elif item.item_type == ItemType.QUEST_ITEM:
                return self._use_quest_item(entity_id, item)
            elif item.item_type == ItemType.KEY:
                return self._use_key(entity_id, item)
            elif item.item_type == ItemType.MAP:
                return self._use_map(entity_id, item)
            else:
                self.logger.warning(f"Cannot use item type: {item.item_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error using item: {e}")
            return False
    
    # === МЕТОДЫ ИНВЕНТАРЯ ===
    
    def create_inventory(self, entity_id: str, max_slots: int = 50, max_weight: float = 100.0) -> Inventory:
        """Создание инвентаря для сущности"""
        try:
            inventory = Inventory(
                entity_id=entity_id,
                max_slots=max_slots,
                max_weight=max_weight
            )
            
            self.inventory_cache[entity_id] = inventory
            self.logger.info(f"Created inventory for {entity_id} with {max_slots} slots")
            return inventory
            
        except Exception as e:
            self.logger.error(f"Error creating inventory: {e}")
            return None
    
    def add_item_to_inventory(self, entity_id: str, item: Item, quantity: int = 1) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            if entity_id not in self.inventory_cache:
                self.create_inventory(entity_id)
            
            inventory = self.inventory_cache[entity_id]
            
            # Проверяем вес
            total_weight = item.weight * quantity
            if inventory.total_weight + total_weight > inventory.max_weight:
                self.logger.warning(f"Inventory weight limit exceeded for {entity_id}")
                return False
            
            # Ищем существующий слот с таким же предметом (для стакающихся предметов)
            if item.stack_size > 1:
                for slot in inventory.slots:
                    if slot.item and slot.item.item_id == item.item_id and slot.quantity < slot.max_quantity:
                        can_add = min(quantity, slot.max_quantity - slot.quantity)
                        slot.quantity += can_add
                        quantity -= can_add
                        inventory.total_weight += item.weight * can_add
                        
                        if quantity <= 0:
                            inventory.last_update = time.time()
                            self.logger.info(f"Added {can_add} {item.name} to existing slot in {entity_id}'s inventory")
                            return True
            
            # Ищем пустой слот
            for slot in inventory.slots:
                if slot.item is None:
                    slot.item = item
                    slot.quantity = min(quantity, item.stack_size)
                    slot.max_quantity = item.stack_size
                    inventory.total_weight += item.weight * slot.quantity
                    quantity -= slot.quantity
                    
                    if quantity <= 0:
                        inventory.last_update = time.time()
                        self.logger.info(f"Added {slot.quantity} {item.name} to new slot in {entity_id}'s inventory")
                        return True
            
            if quantity > 0:
                self.logger.warning(f"No space in inventory for {quantity} {item.name}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding item to inventory: {e}")
            return False
    
    def remove_item_from_inventory(self, entity_id: str, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета из инвентаря"""
        try:
            if entity_id not in self.inventory_cache:
                return False
            
            inventory = self.inventory_cache[entity_id]
            
            for slot in inventory.slots:
                if slot.item and slot.item.item_id == item_id:
                    can_remove = min(quantity, slot.quantity)
                    slot.quantity -= can_remove
                    inventory.total_weight -= slot.item.weight * can_remove
                    quantity -= can_remove
                    
                    if slot.quantity <= 0:
                        slot.item = None
                        slot.quantity = 0
                        slot.max_quantity = 1
                    
                    if quantity <= 0:
                        inventory.last_update = time.time()
                        self.logger.info(f"Removed {can_remove} {item_id} from {entity_id}'s inventory")
                        return True
            
            if quantity > 0:
                self.logger.warning(f"Not enough {item_id} in inventory")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing item from inventory: {e}")
            return False
    
    def get_inventory_items(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение списка предметов в инвентаре"""
        if entity_id not in self.inventory_cache:
            return []
        
        inventory = self.inventory_cache[entity_id]
        items = []
        
        for i, slot in enumerate(inventory.slots):
            if slot.item:
                items.append({
                    "slot_index": i,
                    "item_id": slot.item.item_id,
                    "name": slot.item.name,
                    "item_type": slot.item.item_type.value,
                    "rarity": slot.item.rarity.value,
                    "quantity": slot.quantity,
                    "max_quantity": slot.max_quantity,
                    "weight": slot.item.weight,
                    "value": slot.item.value,
                    "description": slot.item.description
                })
        
        return items
    
    def get_inventory_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистик инвентаря"""
        if entity_id not in self.inventory_cache:
            return {}
        
        inventory = self.inventory_cache[entity_id]
        
        used_slots = sum(1 for slot in inventory.slots if slot.item is not None)
        total_items = sum(slot.quantity for slot in inventory.slots if slot.item is not None)
        
        return {
            "used_slots": used_slots,
            "max_slots": inventory.max_slots,
            "total_items": total_items,
            "total_weight": inventory.total_weight,
            "max_weight": inventory.max_weight,
            "weight_usage_percent": (inventory.total_weight / inventory.max_weight) * 100
        }
    
    def equip_item_from_inventory(self, entity_id: str, slot_index: int, equipment_slot: EquipmentSlot) -> bool:
        """Экипировка предмета из инвентаря"""
        try:
            if entity_id not in self.inventory_cache:
                return False
            
            inventory = self.inventory_cache[entity_id]
            
            if slot_index >= len(inventory.slots) or not inventory.slots[slot_index].item:
                return False
            
            item = inventory.slots[slot_index].item
            
            # Экипируем предмет
            if self.equip_item(entity_id, item, equipment_slot):
                # Удаляем из инвентаря
                self.remove_item_from_inventory(entity_id, item.item_id, 1)
                self.logger.info(f"Equipped {item.name} from inventory slot {slot_index}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error equipping item from inventory: {e}")
            return False
    
    def unequip_item_to_inventory(self, entity_id: str, equipment_slot: EquipmentSlot) -> bool:
        """Снятие предмета в инвентарь"""
        try:
            # Снимаем предмет
            item = self.unequip_item(entity_id, equipment_slot)
            if not item:
                return False
            
            # Добавляем в инвентарь
            if self.add_item_to_inventory(entity_id, item, 1):
                self.logger.info(f"Unequipped {item.name} to inventory")
                return True
            else:
                # Если не поместился в инвентарь, экипируем обратно
                self.equip_item(entity_id, item, equipment_slot)
                self.logger.warning(f"Could not add {item.name} to inventory, re-equipped")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unequipping item to inventory: {e}")
            return False
    
    def _can_equip_item(self, entity_id: str, item: Item, slot: EquipmentSlot) -> bool:
        """Проверка возможности экипировки предмета"""
        # Проверяем соответствие типа предмета и слота
        slot_type_map = {
            EquipmentSlot.MAIN_HAND: [ItemType.WEAPON],
            EquipmentSlot.OFF_HAND: [ItemType.WEAPON, ItemType.ACCESSORY],
            EquipmentSlot.HEAD: [ItemType.ARMOR],
            EquipmentSlot.CHEST: [ItemType.ARMOR],
            EquipmentSlot.LEGS: [ItemType.ARMOR],
            EquipmentSlot.FEET: [ItemType.ARMOR],
            EquipmentSlot.HANDS: [ItemType.ARMOR],
            EquipmentSlot.NECK: [ItemType.ACCESSORY],
            EquipmentSlot.RING_1: [ItemType.ACCESSORY],
            EquipmentSlot.RING_2: [ItemType.ACCESSORY],
            EquipmentSlot.CONSUMABLE: [ItemType.CONSUMABLE]
        }
        
        if item.item_type not in slot_type_map.get(slot, []):
            return False
        
        # Проверяем требования (здесь можно добавить проверку характеристик сущности)
        # Пока что просто возвращаем True
        return True
    
    def _update_equipment_stats(self, entity_id: str):
        """Обновление статистик экипировки"""
        if entity_id not in self.equipment_cache:
            return
        
        equipment = self.equipment_cache[entity_id]
        
        # Очищаем старые модификаторы и скиллы
        equipment.total_modifiers.clear()
        equipment.active_skills.clear()
        
        # Собираем модификаторы и скиллы со всех экипированных предметов
        for slot, item in equipment.slots.items():
            if item:
                # Добавляем модификаторы предмета
                equipment.total_modifiers.extend(item.modifiers)
                
                # Добавляем активные скиллы
                for skill in item.skills:
                    if skill.skill_type == SkillType.ACTIVE:
                        equipment.active_skills.append(skill)
        
        equipment.last_update = time.time()
    
    def _create_skill_from_template(self, skill_id: str, skill_type: SkillType) -> Optional[ItemSkill]:
        """Создание скилла из шаблона"""
        if skill_id not in self.skill_templates:
            return None
        
        template = self.skill_templates[skill_id]
        
        return ItemSkill(
            skill_id=skill_id,
            name=template["name"],
            skill_type=skill_type,
            description=template["description"],
            effects=template["effects"],
            cooldown=template.get("cooldown", 0.0),
            mana_cost=template.get("mana_cost", 0),
            requirements=template.get("requirements", {})
        )
    
    def _create_basic_attack_skill(self, skill_name: str, weapon: Item) -> ItemSkill:
        """Создание базового скилла атаки для оружия"""
        # Извлекаем тип оружия из названия скилла
        weapon_type = skill_name.replace("_basic_attack", "")
        
        # Создаем уникальный скилл для этого оружия
        skill_id = f"{weapon.item_id}_basic_attack"
        
        return ItemSkill(
            skill_id=skill_id,
            name=f"{weapon.name} Basic Attack",
            skill_type=SkillType.BASIC_ATTACK,
            description=f"Basic attack with {weapon.name}",
            effects={
                "damage": weapon.base_stats.get("damage", 10),
                "damage_type": "physical",
                "range": weapon.base_stats.get("range", 1.0),
                "weapon_type": weapon_type
            },
            cooldown=0.0,
            mana_cost=0,
            is_weapon_basic_attack=True
        )
    
    def _create_requirements_from_data(self, requirements_data: Dict[str, int]) -> ItemRequirement:
        """Создание требований из данных"""
        return ItemRequirement(
            level=requirements_data.get("level", 1),
            strength=requirements_data.get("strength", 0),
            agility=requirements_data.get("agility", 0),
            intelligence=requirements_data.get("intelligence", 0),
            vitality=requirements_data.get("vitality", 0),
            wisdom=requirements_data.get("wisdom", 0),
            charisma=requirements_data.get("charisma", 0),
            luck=requirements_data.get("luck", 0),
            endurance=requirements_data.get("endurance", 0)
        )
    
    def _calculate_item_value(self, generated_item: Any) -> int:
        """Расчет стоимости предмета"""
        base_value = {
            ItemRarity.COMMON: 10,
            ItemRarity.UNCOMMON: 25,
            ItemRarity.RARE: 50,
            ItemRarity.EPIC: 100,
            ItemRarity.LEGENDARY: 250
        }[generated_item.rarity]
        
        # Добавляем стоимость за скиллы
        skill_bonus = len(generated_item.active_skills) * 5 + len(generated_item.trigger_skills) * 3
        
        return base_value + skill_bonus
    
    def _calculate_item_weight(self, generated_item: Any) -> float:
        """Расчет веса предмета"""
        base_weight = {
            ItemType.WEAPON: 2.0,
            ItemType.ARMOR: 3.0,
            ItemType.ACCESSORY: 0.5,
            ItemType.CONSUMABLE: 0.1,
            ItemType.MATERIAL: 0.2,
            ItemType.QUEST_ITEM: 0.1,
            ItemType.KEY: 0.05,
            ItemType.MAP: 0.1,
            ItemType.TOOL: 1.0
        }[ItemType(generated_item.item_type)]
        
        return base_weight
    
    def _use_consumable(self, entity_id: str, item: Item) -> bool:
        """Использование расходника"""
        # Здесь можно добавить логику применения эффектов расходника
        self.logger.info(f"Used consumable {item.name} by {entity_id}")
        return True
    
    def _use_weapon_skill(self, entity_id: str, item: Item) -> bool:
        """Использование скилла оружия"""
        # Здесь можно добавить логику активации скилла оружия
        self.logger.info(f"Used weapon skill from {item.name} by {entity_id}")
        return True
    
    def _use_quest_item(self, entity_id: str, item: Item) -> bool:
        """Использование предмета задания"""
        # Здесь можно добавить логику активации предмета задания
        self.logger.info(f"Used quest item {item.name} by {entity_id}")
        return True
    
    def _use_key(self, entity_id: str, item: Item) -> bool:
        """Использование ключа"""
        # Здесь можно добавить логику использования ключа (открытие дверей, сундуков)
        self.logger.info(f"Used key {item.name} by {entity_id}")
        return True
    
    def _use_map(self, entity_id: str, item: Item) -> bool:
        """Использование карты"""
        # Здесь можно добавить логику отображения карты
        self.logger.info(f"Used map {item.name} by {entity_id}")
        return True
    
    def _load_skill_templates(self) -> Dict[str, Dict[str, Any]]:
        """Загрузка шаблонов скиллов"""
        # В реальной реализации здесь была бы загрузка из файла
        return {
            "weapon_skill_1": {
                "name": "Power Strike",
                "description": "A powerful strike that deals extra damage",
                "effects": {"damage_multiplier": 1.5, "damage_type": "physical"},
                "cooldown": 5.0,
                "mana_cost": 10
            },
            "weapon_skill_2": {
                "name": "Quick Slash",
                "description": "A fast attack that can hit multiple times",
                "effects": {"attack_count": 2, "damage_type": "physical"},
                "cooldown": 3.0,
                "mana_cost": 5
            },
            "trigger_skill_1": {
                "name": "Counter Attack",
                "description": "Automatically counter attacks when hit",
                "effects": {"trigger_chance": 0.2, "damage_type": "physical"},
                "cooldown": 0.0,
                "mana_cost": 0
            }
        }
    
    def save_item_data(self, save_id: str) -> bool:
        """Сохранение данных предметов"""
        try:
            item_data = {
                "items": {
                    item_id: {
                        "item_id": item.item_id,
                        "name": item.name,
                        "item_type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "description": item.description,
                        "base_stats": item.base_stats,
                        "modifiers": [
                            {
                                "modifier_type": mod.modifier_type,
                                "value": mod.value,
                                "duration": mod.duration,
                                "condition": mod.condition
                            }
                            for mod in item.modifiers
                        ],
                        "skills": [
                            {
                                "skill_id": skill.skill_id,
                                "name": skill.name,
                                "skill_type": skill.skill_type.value,
                                "description": skill.description,
                                "effects": skill.effects,
                                "cooldown": skill.cooldown,
                                "mana_cost": skill.mana_cost,
                                "requirements": skill.requirements,
                                "is_weapon_basic_attack": skill.is_weapon_basic_attack
                            }
                            for skill in item.skills
                        ],
                        "basic_attack_skill": {
                            "skill_id": item.basic_attack_skill.skill_id,
                            "name": item.basic_attack_skill.name,
                            "skill_type": item.basic_attack_skill.skill_type.value,
                            "description": item.basic_attack_skill.description,
                            "effects": item.basic_attack_skill.effects,
                            "cooldown": item.basic_attack_skill.cooldown,
                            "mana_cost": item.basic_attack_skill.mana_cost,
                            "is_weapon_basic_attack": item.basic_attack_skill.is_weapon_basic_attack
                        } if item.basic_attack_skill else None,
                        "requirements": {
                            "level": item.requirements.level,
                            "strength": item.requirements.strength,
                            "agility": item.requirements.agility,
                            "intelligence": item.requirements.intelligence,
                            "vitality": item.requirements.vitality,
                            "wisdom": item.requirements.wisdom,
                            "charisma": item.requirements.charisma,
                            "luck": item.requirements.luck,
                            "endurance": item.requirements.endurance
                        },
                        "value": item.value,
                        "weight": item.weight,
                        "durability": item.durability,
                        "max_durability": item.max_durability,
                        "stack_size": item.stack_size,
                        "created_at": item.created_at
                    }
                    for item_id, item in self.items_cache.items()
                },
                "equipment": {
                    entity_id: {
                        "entity_id": equipment.entity_id,
                        "slots": {
                            slot.value: item.item_id if item else None
                            for slot, item in equipment.slots.items()
                        },
                        "total_modifiers": [
                            {
                                "modifier_type": mod.modifier_type,
                                "value": mod.value,
                                "duration": mod.duration,
                                "condition": mod.condition
                            }
                            for mod in equipment.total_modifiers
                        ],
                        "active_skills": [
                            {
                                "skill_id": skill.skill_id,
                                "name": skill.name,
                                "skill_type": skill.skill_type.value,
                                "description": skill.description,
                                "effects": skill.effects,
                                "cooldown": skill.cooldown,
                                "mana_cost": skill.mana_cost
                            }
                            for skill in equipment.active_skills
                        ],
                                                 "last_update": equipment.last_update
                     }
                     for entity_id, equipment in self.equipment_cache.items()
                 },
                 "inventories": {
                     entity_id: {
                         "entity_id": inventory.entity_id,
                         "slots": [
                             {
                                 "item_id": slot.item.item_id if slot.item else None,
                                 "quantity": slot.quantity,
                                 "max_quantity": slot.max_quantity
                             }
                             for slot in inventory.slots
                         ],
                         "max_slots": inventory.max_slots,
                         "total_weight": inventory.total_weight,
                         "max_weight": inventory.max_weight,
                         "last_update": inventory.last_update
                     }
                     for entity_id, inventory in self.inventory_cache.items()
                 }
             }
            
            # Сохраняем в файл
            item_file = self.items_directory / f"{save_id}_items.json"
            with open(item_file, 'w', encoding='utf-8') as f:
                json.dump(item_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved item data to {item_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving item data: {e}")
            return False
