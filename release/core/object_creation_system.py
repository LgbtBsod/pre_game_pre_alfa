#!/usr/bin/env python3
"""
Система создания объектов для игры.
Позволяет создавать ловушки, врагов, сундуки с предметами и другие игровые объекты.
"""

import random
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ObjectType(Enum):
    """Типы создаваемых объектов"""
    TRAP = "trap"
    ENEMY = "enemy"
    CHEST = "chest"
    ITEM = "item"
    OBSTACLE = "obstacle"
    BEACON = "beacon"
    DECORATION = "decoration"
    INTERACTIVE = "interactive"


class TrapType(Enum):
    """Типы ловушек"""
    SPIKE = "spike"
    EXPLOSIVE = "explosive"
    POISON = "poison"
    ICE = "ice"
    ELECTRIC = "electric"
    TELEPORT = "teleport"
    SLOW = "slow"
    CONFUSION = "confusion"


class ChestType(Enum):
    """Типы сундуков"""
    WOODEN = "wooden"
    IRON = "iron"
    GOLDEN = "golden"
    MAGICAL = "magical"
    RARE = "rare"
    LEGENDARY = "legendary"


@dataclass
class ObjectTemplate:
    """Шаблон для создания объектов"""
    template_id: str
    object_type: ObjectType
    name: str
    description: str
    base_stats: Dict[str, float]
    appearance: Dict[str, Any]
    behavior: Dict[str, Any]
    requirements: Dict[str, Any]
    cost: Dict[str, int] = field(default_factory=dict)
    rarity: str = "common"


@dataclass
class CreatedObject:
    """Созданный игровой объект"""
    object_id: str
    template_id: str
    object_type: ObjectType
    name: str
    position: Tuple[float, float, float]
    rotation: float = 0.0
    scale: float = 1.0
    stats: Dict[str, float] = field(default_factory=dict)
    appearance: Dict[str, Any] = field(default_factory=dict)
    behavior: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    is_visible: bool = True
    is_interactable: bool = False
    created_at: float = 0.0
    creator_id: str = ""
    durability: float = 100.0
    max_durability: float = 100.0


@dataclass
class ObjectCreationRequest:
    """Запрос на создание объекта"""
    template_id: str
    position: Tuple[float, float, float]
    rotation: float = 0.0
    scale: float = 1.0
    custom_stats: Dict[str, float] = field(default_factory=dict)
    custom_appearance: Dict[str, Any] = field(default_factory=dict)
    creator_id: str = ""


class ObjectCreationSystem:
    """Система создания объектов"""
    
    def __init__(self):
        self.templates: Dict[str, ObjectTemplate] = {}
        self.created_objects: Dict[str, CreatedObject] = {}
        self.object_counter = 0
        
        # Ограничения
        self.max_objects_per_type = {
            ObjectType.TRAP: 50,
            ObjectType.ENEMY: 100,
            ObjectType.CHEST: 30,
            ObjectType.ITEM: 200,
            ObjectType.OBSTACLE: 100,
            ObjectType.BEACON: 20,
            ObjectType.DECORATION: 150,
            ObjectType.INTERACTIVE: 50
        }
        
        # Статистика
        self.creation_stats = {
            "total_created": 0,
            "by_type": {obj_type.value: 0 for obj_type in ObjectType},
            "by_creator": {},
            "failed_creations": 0
        }
        
        # Инициализация шаблонов
        self._initialize_templates()
        
        logger.info("Система создания объектов инициализирована")
    
    def _initialize_templates(self):
        """Инициализирует базовые шаблоны объектов"""
        try:
            # Шаблоны ловушек
            self._add_trap_templates()
            
            # Шаблоны врагов
            self._add_enemy_templates()
            
            # Шаблоны сундуков
            self._add_chest_templates()
            
            # Шаблоны предметов
            self._add_item_templates()
            
            # Шаблоны препятствий
            self._add_obstacle_templates()
            
            logger.info(f"Загружено {len(self.templates)} шаблонов объектов")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации шаблонов: {e}")
    
    def _add_trap_templates(self):
        """Добавляет шаблоны ловушек"""
        trap_templates = [
            ObjectTemplate(
                template_id="trap_spike",
                object_type=ObjectType.TRAP,
                name="Шипованная ловушка",
                description="Острые шипы, наносящие физический урон",
                base_stats={
                    "damage": 25.0,
                    "trigger_radius": 2.0,
                    "cooldown": 5.0,
                    "durability": 50.0
                },
                appearance={
                    "color": (128, 64, 64),
                    "size": 8.0,
                    "shape": "spike"
                },
                behavior={
                    "trigger_type": "proximity",
                    "effect_type": "damage",
                    "is_reusable": True
                },
                requirements={
                    "materials": {"iron": 2, "wood": 1},
                    "skill_level": 1
                },
                cost={"gold": 10}
            ),
            ObjectTemplate(
                template_id="trap_explosive",
                object_type=ObjectType.TRAP,
                name="Взрывная ловушка",
                description="Взрывается при срабатывании",
                base_stats={
                    "damage": 50.0,
                    "trigger_radius": 3.0,
                    "explosion_radius": 5.0,
                    "cooldown": 10.0,
                    "durability": 30.0
                },
                appearance={
                    "color": (255, 128, 0),
                    "size": 10.0,
                    "shape": "explosive"
                },
                behavior={
                    "trigger_type": "proximity",
                    "effect_type": "explosion",
                    "is_reusable": False
                },
                requirements={
                    "materials": {"gunpowder": 3, "iron": 1},
                    "skill_level": 3
                },
                cost={"gold": 25}
            ),
            ObjectTemplate(
                template_id="trap_poison",
                object_type=ObjectType.TRAP,
                name="Ядовитая ловушка",
                description="Наносит урон ядом и замедляет",
                base_stats={
                    "damage": 15.0,
                    "poison_damage": 5.0,
                    "poison_duration": 10.0,
                    "slow_duration": 5.0,
                    "trigger_radius": 2.5,
                    "cooldown": 8.0,
                    "durability": 40.0
                },
                appearance={
                    "color": (0, 128, 0),
                    "size": 9.0,
                    "shape": "poison"
                },
                behavior={
                    "trigger_type": "proximity",
                    "effect_type": "poison",
                    "is_reusable": True
                },
                requirements={
                    "materials": {"poison": 2, "wood": 2},
                    "skill_level": 2
                },
                cost={"gold": 15}
            )
        ]
        
        for template in trap_templates:
            self.templates[template.template_id] = template
    
    def _add_enemy_templates(self):
        """Добавляет шаблоны врагов"""
        enemy_templates = [
            ObjectTemplate(
                template_id="enemy_goblin",
                object_type=ObjectType.ENEMY,
                name="Гоблин",
                description="Небольшой агрессивный гоблин",
                base_stats={
                    "health": 30.0,
                    "max_health": 30.0,
                    "damage": 8.0,
                    "speed": 1.5,
                    "aggro_range": 8.0,
                    "attack_range": 1.5,
                    "experience": 15
                },
                appearance={
                    "color": (0, 128, 0),
                    "size": 12.0,
                    "shape": "humanoid"
                },
                behavior={
                    "ai_type": "aggressive",
                    "patrol_radius": 5.0,
                    "flee_health": 0.3
                },
                requirements={
                    "materials": {},
                    "skill_level": 0
                },
                cost={"gold": 5}
            ),
            ObjectTemplate(
                template_id="enemy_orc",
                object_type=ObjectType.ENEMY,
                name="Орк",
                description="Сильный орк-воин",
                base_stats={
                    "health": 80.0,
                    "max_health": 80.0,
                    "damage": 20.0,
                    "speed": 1.2,
                    "aggro_range": 12.0,
                    "attack_range": 2.0,
                    "experience": 40
                },
                appearance={
                    "color": (128, 64, 0),
                    "size": 16.0,
                    "shape": "humanoid"
                },
                behavior={
                    "ai_type": "aggressive",
                    "patrol_radius": 8.0,
                    "flee_health": 0.2
                },
                requirements={
                    "materials": {},
                    "skill_level": 0
                },
                cost={"gold": 15}
            ),
            ObjectTemplate(
                template_id="enemy_skeleton",
                object_type=ObjectType.ENEMY,
                name="Скелет",
                description="Нежить, устойчивая к физическому урону",
                base_stats={
                    "health": 50.0,
                    "max_health": 50.0,
                    "damage": 12.0,
                    "speed": 1.0,
                    "aggro_range": 10.0,
                    "attack_range": 1.8,
                    "experience": 25,
                    "physical_resistance": 0.5
                },
                appearance={
                    "color": (192, 192, 192),
                    "size": 14.0,
                    "shape": "skeleton"
                },
                behavior={
                    "ai_type": "aggressive",
                    "patrol_radius": 6.0,
                    "flee_health": 0.4
                },
                requirements={
                    "materials": {},
                    "skill_level": 0
                },
                cost={"gold": 10}
            )
        ]
        
        for template in enemy_templates:
            self.templates[template.template_id] = template
    
    def _add_chest_templates(self):
        """Добавляет шаблоны сундуков"""
        chest_templates = [
            ObjectTemplate(
                template_id="chest_wooden",
                object_type=ObjectType.CHEST,
                name="Деревянный сундук",
                description="Простой деревянный сундук",
                base_stats={
                    "capacity": 5,
                    "lock_difficulty": 1,
                    "durability": 30.0,
                    "rarity_bonus": 0.0
                },
                appearance={
                    "color": (139, 69, 19),
                    "size": 24.0,
                    "shape": "chest"
                },
                behavior={
                    "lock_type": "simple",
                    "trap_chance": 0.1,
                    "respawn_time": 300.0
                },
                requirements={
                    "materials": {"wood": 3},
                    "skill_level": 0
                },
                cost={"gold": 5}
            ),
            ObjectTemplate(
                template_id="chest_iron",
                object_type=ObjectType.CHEST,
                name="Железный сундук",
                description="Прочный железный сундук",
                base_stats={
                    "capacity": 8,
                    "lock_difficulty": 3,
                    "durability": 80.0,
                    "rarity_bonus": 0.2
                },
                appearance={
                    "color": (105, 105, 105),
                    "size": 26.0,
                    "shape": "chest"
                },
                behavior={
                    "lock_type": "complex",
                    "trap_chance": 0.3,
                    "respawn_time": 600.0
                },
                requirements={
                    "materials": {"iron": 4, "wood": 1},
                    "skill_level": 2
                },
                cost={"gold": 20}
            ),
            ObjectTemplate(
                template_id="chest_magical",
                object_type=ObjectType.CHEST,
                name="Магический сундук",
                description="Сундук с магической защитой",
                base_stats={
                    "capacity": 12,
                    "lock_difficulty": 5,
                    "durability": 120.0,
                    "rarity_bonus": 0.5
                },
                appearance={
                    "color": (138, 43, 226),
                    "size": 28.0,
                    "shape": "chest"
                },
                behavior={
                    "lock_type": "magical",
                    "trap_chance": 0.5,
                    "respawn_time": 1200.0
                },
                requirements={
                    "materials": {"magic_crystal": 2, "iron": 2},
                    "skill_level": 5
                },
                cost={"gold": 50}
            )
        ]
        
        for template in chest_templates:
            self.templates[template.template_id] = template
    
    def _add_item_templates(self):
        """Добавляет шаблоны предметов"""
        item_templates = [
            ObjectTemplate(
                template_id="item_health_potion",
                object_type=ObjectType.ITEM,
                name="Зелье здоровья",
                description="Восстанавливает здоровье",
                base_stats={
                    "heal_amount": 25.0,
                    "weight": 0.5,
                    "value": 10
                },
                appearance={
                    "color": (255, 0, 0),
                    "size": 6.0,
                    "shape": "potion"
                },
                behavior={
                    "use_type": "consumable",
                    "stackable": True,
                    "max_stack": 10
                },
                requirements={
                    "materials": {"herbs": 2, "water": 1},
                    "skill_level": 1
                },
                cost={"gold": 8}
            ),
            ObjectTemplate(
                template_id="item_mana_potion",
                object_type=ObjectType.ITEM,
                name="Зелье маны",
                description="Восстанавливает ману",
                base_stats={
                    "mana_amount": 30.0,
                    "weight": 0.5,
                    "value": 12
                },
                appearance={
                    "color": (0, 0, 255),
                    "size": 6.0,
                    "shape": "potion"
                },
                behavior={
                    "use_type": "consumable",
                    "stackable": True,
                    "max_stack": 10
                },
                requirements={
                    "materials": {"magic_herbs": 2, "water": 1},
                    "skill_level": 2
                },
                cost={"gold": 10}
            )
        ]
        
        for template in item_templates:
            self.templates[template.template_id] = template
    
    def _add_obstacle_templates(self):
        """Добавляет шаблоны препятствий"""
        obstacle_templates = [
            ObjectTemplate(
                template_id="obstacle_rock",
                object_type=ObjectType.OBSTACLE,
                name="Камень",
                description="Большой камень, блокирующий путь",
                base_stats={
                    "health": 100.0,
                    "blocking": True,
                    "durability": 200.0
                },
                appearance={
                    "color": (128, 128, 128),
                    "size": 20.0,
                    "shape": "rock"
                },
                behavior={
                    "movable": False,
                    "destructible": True
                },
                requirements={
                    "materials": {},
                    "skill_level": 0
                },
                cost={"gold": 0}
            ),
            ObjectTemplate(
                template_id="obstacle_tree",
                object_type=ObjectType.OBSTACLE,
                name="Дерево",
                description="Высокое дерево",
                base_stats={
                    "health": 80.0,
                    "blocking": True,
                    "durability": 150.0
                },
                appearance={
                    "color": (34, 139, 34),
                    "size": 25.0,
                    "shape": "tree"
                },
                behavior={
                    "movable": False,
                    "destructible": True
                },
                requirements={
                    "materials": {},
                    "skill_level": 0
                },
                cost={"gold": 0}
            )
        ]
        
        for template in obstacle_templates:
            self.templates[template.template_id] = template
    
    def create_object(self, request: ObjectCreationRequest, current_time: float) -> Optional[CreatedObject]:
        """Создает объект по запросу"""
        try:
            # Проверяем существование шаблона
            if request.template_id not in self.templates:
                logger.error(f"Шаблон {request.template_id} не найден")
                self.creation_stats["failed_creations"] += 1
                return None
            
            template = self.templates[request.template_id]
            
            # Проверяем лимиты
            if not self._check_creation_limits(template.object_type):
                logger.warning(f"Достигнут лимит объектов типа {template.object_type.value}")
                self.creation_stats["failed_creations"] += 1
                return None
            
            # Создаем объект
            object_id = f"{template.object_type.value}_{self.object_counter:06d}"
            self.object_counter += 1
            
            # Объединяем базовые и кастомные характеристики
            stats = template.base_stats.copy()
            stats.update(request.custom_stats)
            
            appearance = template.appearance.copy()
            appearance.update(request.custom_appearance)
            
            behavior = template.behavior.copy()
            
            created_object = CreatedObject(
                object_id=object_id,
                template_id=request.template_id,
                object_type=template.object_type,
                name=template.name,
                position=request.position,
                rotation=request.rotation,
                scale=request.scale,
                stats=stats,
                appearance=appearance,
                behavior=behavior,
                created_at=current_time,
                creator_id=request.creator_id,
                durability=stats.get("durability", 100.0),
                max_durability=stats.get("durability", 100.0)
            )
            
            # Добавляем в список созданных объектов
            self.created_objects[object_id] = created_object
            
            # Обновляем статистику
            self.creation_stats["total_created"] += 1
            self.creation_stats["by_type"][template.object_type.value] += 1
            
            if request.creator_id:
                if request.creator_id not in self.creation_stats["by_creator"]:
                    self.creation_stats["by_creator"][request.creator_id] = 0
                self.creation_stats["by_creator"][request.creator_id] += 1
            
            logger.info(f"Создан объект {object_id} типа {template.object_type.value}")
            return created_object
            
        except Exception as e:
            logger.error(f"Ошибка создания объекта: {e}")
            self.creation_stats["failed_creations"] += 1
            return None
    
    def _check_creation_limits(self, object_type: ObjectType) -> bool:
        """Проверяет лимиты создания объектов"""
        try:
            current_count = self.creation_stats["by_type"].get(object_type.value, 0)
            max_count = self.max_objects_per_type.get(object_type, 100)
            
            return current_count < max_count
            
        except Exception as e:
            logger.error(f"Ошибка проверки лимитов создания: {e}")
            return False
    
    def destroy_object(self, object_id: str) -> bool:
        """Уничтожает объект"""
        try:
            if object_id not in self.created_objects:
                logger.warning(f"Объект {object_id} не найден")
                return False
            
            object_type = self.created_objects[object_id].object_type
            del self.created_objects[object_id]
            
            # Обновляем статистику
            self.creation_stats["by_type"][object_type.value] = max(0, self.creation_stats["by_type"][object_type.value] - 1)
            
            logger.info(f"Объект {object_id} уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения объекта: {e}")
            return False
    
    def get_objects_by_type(self, object_type: ObjectType) -> List[CreatedObject]:
        """Возвращает все объекты указанного типа"""
        try:
            return [
                obj for obj in self.created_objects.values()
                if obj.object_type == object_type and obj.is_active
            ]
        except Exception as e:
            logger.error(f"Ошибка получения объектов по типу: {e}")
            return []
    
    def get_objects_in_area(self, center: Tuple[float, float, float], radius: float) -> List[CreatedObject]:
        """Возвращает объекты в указанной области"""
        try:
            objects_in_area = []
            
            for obj in self.created_objects.values():
                if not obj.is_active:
                    continue
                
                distance = ((obj.position[0] - center[0])**2 + 
                           (obj.position[1] - center[1])**2 + 
                           (obj.position[2] - center[2])**2)**0.5
                
                if distance <= radius:
                    objects_in_area.append(obj)
            
            return objects_in_area
            
        except Exception as e:
            logger.error(f"Ошибка получения объектов в области: {e}")
            return []
    
    def get_available_templates(self, object_type: Optional[ObjectType] = None) -> List[ObjectTemplate]:
        """Возвращает доступные шаблоны"""
        try:
            if object_type:
                return [
                    template for template in self.templates.values()
                    if template.object_type == object_type
                ]
            else:
                return list(self.templates.values())
                
        except Exception as e:
            logger.error(f"Ошибка получения доступных шаблонов: {e}")
            return []
    
    def get_creation_stats(self) -> Dict[str, Any]:
        """Возвращает статистику создания объектов"""
        try:
            return {
                "total_created": self.creation_stats["total_created"],
                "by_type": self.creation_stats["by_type"].copy(),
                "by_creator": self.creation_stats["by_creator"].copy(),
                "failed_creations": self.creation_stats["failed_creations"],
                "active_objects": len([obj for obj in self.created_objects.values() if obj.is_active]),
                "total_templates": len(self.templates)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики создания: {e}")
            return {}
    
    def save_objects_data(self, filepath: str) -> bool:
        """Сохраняет данные объектов в файл"""
        try:
            objects_data = {
                "created_objects": {
                    obj_id: {
                        "template_id": obj.template_id,
                        "object_type": obj.object_type.value,
                        "name": obj.name,
                        "position": obj.position,
                        "rotation": obj.rotation,
                        "scale": obj.scale,
                        "stats": obj.stats,
                        "appearance": obj.appearance,
                        "behavior": obj.behavior,
                        "is_active": obj.is_active,
                        "is_visible": obj.is_visible,
                        "is_interactable": obj.is_interactable,
                        "created_at": obj.created_at,
                        "creator_id": obj.creator_id,
                        "durability": obj.durability,
                        "max_durability": obj.max_durability
                    }
                    for obj_id, obj in self.created_objects.items()
                },
                "creation_stats": self.creation_stats,
                "object_counter": self.object_counter
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(objects_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Данные объектов сохранены в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных объектов: {e}")
            return False
    
    def load_objects_data(self, filepath: str) -> bool:
        """Загружает данные объектов из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                objects_data = json.load(f)
            
            # Загружаем созданные объекты
            self.created_objects.clear()
            for obj_id, obj_data in objects_data.get("created_objects", {}).items():
                created_object = CreatedObject(
                    object_id=obj_id,
                    template_id=obj_data["template_id"],
                    object_type=ObjectType(obj_data["object_type"]),
                    name=obj_data["name"],
                    position=tuple(obj_data["position"]),
                    rotation=obj_data["rotation"],
                    scale=obj_data["scale"],
                    stats=obj_data["stats"],
                    appearance=obj_data["appearance"],
                    behavior=obj_data["behavior"],
                    is_active=obj_data["is_active"],
                    is_visible=obj_data["is_visible"],
                    is_interactable=obj_data["is_interactable"],
                    created_at=obj_data["created_at"],
                    creator_id=obj_data["creator_id"],
                    durability=obj_data["durability"],
                    max_durability=obj_data["max_durability"]
                )
                self.created_objects[obj_id] = created_object
            
            # Загружаем статистику
            self.creation_stats.update(objects_data.get("creation_stats", {}))
            self.object_counter = objects_data.get("object_counter", 0)
            
            logger.info(f"Данные объектов загружены из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных объектов: {e}")
            return False
