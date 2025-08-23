#!/usr/bin/env python3
"""
Система компьютерного зрения для обучения ИИ.
Позволяет ИИ анализировать визуальную информацию и принимать решения на её основе.
"""

import numpy as np
import random
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VisionObjectType(Enum):
    """Типы объектов, которые может видеть ИИ"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    ITEM = "item"
    CHEST = "chest"
    TRAP = "trap"
    OBSTACLE = "obstacle"
    BEACON = "beacon"
    WEAPON = "weapon"
    PROJECTILE = "projectile"
    EFFECT = "effect"
    UNKNOWN = "unknown"


class VisionAction(Enum):
    """Действия, основанные на визуальной информации"""
    APPROACH = "approach"
    AVOID = "avoid"
    ATTACK = "attack"
    DEFEND = "defend"
    COLLECT = "collect"
    INTERACT = "interact"
    FLEE = "flee"
    INVESTIGATE = "investigate"
    IGNORE = "ignore"


@dataclass
class VisualObject:
    """Визуальный объект, обнаруженный ИИ"""
    object_id: str
    object_type: VisionObjectType
    position: Tuple[float, float, float]
    distance: float
    direction: Tuple[float, float]
    size: float
    color: Tuple[int, int, int]
    movement_speed: float = 0.0
    health_percentage: float = 1.0
    threat_level: float = 0.0
    is_hostile: bool = False
    is_interactable: bool = False
    confidence: float = 1.0  # Уверенность в определении объекта


@dataclass
class VisualField:
    """Поле зрения ИИ"""
    center: Tuple[float, float, float]
    radius: float
    angle: float  # Угол обзора в радианах
    detected_objects: List[VisualObject] = field(default_factory=list)
    last_update: float = 0.0


@dataclass
class VisualMemory:
    """Визуальная память ИИ"""
    object_id: str
    object_type: VisionObjectType
    last_seen_position: Tuple[float, float, float]
    last_seen_time: float
    memory_duration: float = 30.0  # Время хранения памяти в секундах
    importance: float = 1.0  # Важность объекта для памяти


@dataclass
class VisualPattern:
    """Визуальный паттерн для обучения"""
    pattern_id: str
    object_combination: List[VisionObjectType]
    spatial_relationship: Dict[str, Any]
    temporal_sequence: List[float]
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: float = 0.0


class ComputerVisionSystem:
    """Система компьютерного зрения для ИИ"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        
        # Параметры зрения
        self.vision_radius = 50.0
        self.vision_angle = np.pi * 2  # 360 градусов
        self.max_detection_distance = 100.0
        
        # Поле зрения
        self.visual_field = VisualField(
            center=(0, 0, 0),
            radius=self.vision_radius,
            angle=self.vision_angle
        )
        
        # Визуальная память
        self.visual_memory: Dict[str, VisualMemory] = {}
        self.memory_decay_rate = 0.1
        
        # Обнаруженные паттерны
        self.visual_patterns: Dict[str, VisualPattern] = {}
        self.pattern_recognition_threshold = 0.7
        
        # История визуальных наблюдений
        self.visual_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Q-learning для визуальных решений
        self.visual_q_table: Dict[str, Dict[VisionAction, float]] = {}
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        # Статистика
        self.vision_stats = {
            "objects_detected": 0,
            "patterns_recognized": 0,
            "successful_decisions": 0,
            "total_decisions": 0,
            "memory_hits": 0,
            "memory_misses": 0
        }
        
        logger.info(f"Система компьютерного зрения инициализирована для {entity_id}")
    
    def update_visual_field(self, entity_position: Tuple[float, float, float], 
                           world_objects: List[Any], current_time: float):
        """Обновляет поле зрения ИИ"""
        try:
            # Обновляем центр поля зрения
            self.visual_field.center = entity_position
            self.visual_field.last_update = current_time
            
            # Очищаем предыдущие обнаружения
            self.visual_field.detected_objects.clear()
            
            # Анализируем объекты в мире
            for obj in world_objects:
                if self._is_object_visible(obj, entity_position):
                    visual_obj = self._create_visual_object(obj, entity_position)
                    if visual_obj:
                        self.visual_field.detected_objects.append(visual_obj)
                        self._update_visual_memory(visual_obj, current_time)
            
            # Анализируем паттерны
            self._analyze_visual_patterns(current_time)
            
            # Обновляем статистику
            self.vision_stats["objects_detected"] += len(self.visual_field.detected_objects)
            
        except Exception as e:
            logger.error(f"Ошибка обновления поля зрения: {e}")
    
    def _is_object_visible(self, obj: Any, observer_position: Tuple[float, float, float]) -> bool:
        """Проверяет, видим ли объект"""
        try:
            # Получаем позицию объекта
            if hasattr(obj, 'position'):
                obj_pos = (obj.position.x, obj.position.y, obj.position.z)
            elif isinstance(obj, dict) and 'position' in obj:
                obj_pos = obj['position']
            else:
                return False
            
            # Вычисляем расстояние
            distance = np.sqrt(
                (obj_pos[0] - observer_position[0])**2 +
                (obj_pos[1] - observer_position[1])**2 +
                (obj_pos[2] - observer_position[2])**2
            )
            
            # Проверяем, в пределах ли радиуса зрения
            return distance <= self.max_detection_distance
            
        except Exception as e:
            logger.error(f"Ошибка проверки видимости объекта: {e}")
            return False
    
    def _create_visual_object(self, obj: Any, observer_position: Tuple[float, float, float]) -> Optional[VisualObject]:
        """Создает визуальный объект из игрового объекта"""
        try:
            # Определяем тип объекта
            obj_type = self._determine_object_type(obj)
            
            # Получаем позицию
            if hasattr(obj, 'position'):
                obj_pos = (obj.position.x, obj.position.y, obj.position.z)
            elif isinstance(obj, dict) and 'position' in obj:
                obj_pos = obj['position']
            else:
                return None
            
            # Вычисляем расстояние и направление
            distance = np.sqrt(
                (obj_pos[0] - observer_position[0])**2 +
                (obj_pos[1] - observer_position[1])**2 +
                (obj_pos[2] - observer_position[2])**2
            )
            
            direction = (
                (obj_pos[0] - observer_position[0]) / distance if distance > 0 else 0,
                (obj_pos[1] - observer_position[1]) / distance if distance > 0 else 0
            )
            
            # Определяем размер и цвет
            size = self._determine_object_size(obj, obj_type)
            color = self._determine_object_color(obj, obj_type)
            
            # Определяем уровень угрозы
            threat_level = self._calculate_threat_level(obj, obj_type, distance)
            
            # Определяем враждебность
            is_hostile = self._is_object_hostile(obj, obj_type)
            
            # Определяем возможность взаимодействия
            is_interactable = self._is_object_interactable(obj, obj_type)
            
            return VisualObject(
                object_id=getattr(obj, 'id', str(id(obj))),
                object_type=obj_type,
                position=obj_pos,
                distance=distance,
                direction=direction,
                size=size,
                color=color,
                threat_level=threat_level,
                is_hostile=is_hostile,
                is_interactable=is_interactable
            )
            
        except Exception as e:
            logger.error(f"Ошибка создания визуального объекта: {e}")
            return None
    
    def _determine_object_type(self, obj: Any) -> VisionObjectType:
        """Определяет тип объекта"""
        try:
            if hasattr(obj, 'type'):
                obj_type = obj.type
            elif isinstance(obj, dict) and 'type' in obj:
                obj_type = obj['type']
            else:
                return VisionObjectType.UNKNOWN
            
            # Маппинг типов
            type_mapping = {
                'player': VisionObjectType.PLAYER,
                'enemy': VisionObjectType.ENEMY,
                'npc': VisionObjectType.NPC,
                'item': VisionObjectType.ITEM,
                'chest': VisionObjectType.CHEST,
                'trap': VisionObjectType.TRAP,
                'obstacle': VisionObjectType.OBSTACLE,
                'beacon': VisionObjectType.BEACON,
                'weapon': VisionObjectType.WEAPON,
                'projectile': VisionObjectType.PROJECTILE,
                'effect': VisionObjectType.EFFECT
            }
            
            return type_mapping.get(obj_type, VisionObjectType.UNKNOWN)
            
        except Exception as e:
            logger.error(f"Ошибка определения типа объекта: {e}")
            return VisionObjectType.UNKNOWN
    
    def _determine_object_size(self, obj: Any, obj_type: VisionObjectType) -> float:
        """Определяет размер объекта"""
        try:
            # Базовые размеры по типам
            base_sizes = {
                VisionObjectType.PLAYER: 16.0,
                VisionObjectType.ENEMY: 12.0,
                VisionObjectType.NPC: 14.0,
                VisionObjectType.ITEM: 6.0,
                VisionObjectType.CHEST: 24.0,
                VisionObjectType.TRAP: 8.0,
                VisionObjectType.OBSTACLE: 20.0,
                VisionObjectType.BEACON: 10.0,
                VisionObjectType.WEAPON: 8.0,
                VisionObjectType.PROJECTILE: 4.0,
                VisionObjectType.EFFECT: 12.0,
                VisionObjectType.UNKNOWN: 10.0
            }
            
            base_size = base_sizes.get(obj_type, 10.0)
            
            # Модификаторы размера
            if hasattr(obj, 'scale'):
                base_size *= obj.scale
            elif isinstance(obj, dict) and 'scale' in obj:
                base_size *= obj['scale']
            
            return base_size
            
        except Exception as e:
            logger.error(f"Ошибка определения размера объекта: {e}")
            return 10.0
    
    def _determine_object_color(self, obj: Any, obj_type: VisionObjectType) -> Tuple[int, int, int]:
        """Определяет цвет объекта"""
        try:
            # Базовые цвета по типам
            base_colors = {
                VisionObjectType.PLAYER: (0, 255, 0),    # Зеленый
                VisionObjectType.ENEMY: (255, 0, 0),     # Красный
                VisionObjectType.NPC: (0, 0, 255),       # Синий
                VisionObjectType.ITEM: (0, 255, 255),    # Голубой
                VisionObjectType.CHEST: (255, 255, 0),   # Желтый
                VisionObjectType.TRAP: (255, 128, 0),    # Оранжевый
                VisionObjectType.OBSTACLE: (128, 128, 128), # Серый
                VisionObjectType.BEACON: (255, 0, 255),  # Пурпурный
                VisionObjectType.WEAPON: (192, 192, 192), # Серебряный
                VisionObjectType.PROJECTILE: (255, 255, 255), # Белый
                VisionObjectType.EFFECT: (128, 0, 255),  # Фиолетовый
                VisionObjectType.UNKNOWN: (64, 64, 64)   # Темно-серый
            }
            
            return base_colors.get(obj_type, (64, 64, 64))
            
        except Exception as e:
            logger.error(f"Ошибка определения цвета объекта: {e}")
            return (64, 64, 64)
    
    def _calculate_threat_level(self, obj: Any, obj_type: VisionObjectType, distance: float) -> float:
        """Вычисляет уровень угрозы объекта"""
        try:
            base_threat = 0.0
            
            # Базовые уровни угрозы по типам
            if obj_type == VisionObjectType.ENEMY:
                base_threat = 0.8
            elif obj_type == VisionObjectType.TRAP:
                base_threat = 0.6
            elif obj_type == VisionObjectType.PROJECTILE:
                base_threat = 0.7
            elif obj_type == VisionObjectType.PLAYER:
                base_threat = 0.3  # Игрок может быть угрозой в PvP
            else:
                base_threat = 0.1
            
            # Модификаторы угрозы
            if hasattr(obj, 'stats') and hasattr(obj.stats, 'health'):
                health_ratio = obj.stats.health / obj.stats.max_health if obj.stats.max_health > 0 else 1.0
                base_threat *= (1.0 + (1.0 - health_ratio))  # Больше угрозы от здоровых врагов
            
            # Расстояние влияет на угрозу
            distance_factor = max(0.1, 1.0 - (distance / self.max_detection_distance))
            base_threat *= distance_factor
            
            return min(1.0, base_threat)
            
        except Exception as e:
            logger.error(f"Ошибка вычисления уровня угрозы: {e}")
            return 0.5
    
    def _is_object_hostile(self, obj: Any, obj_type: VisionObjectType) -> bool:
        """Определяет, является ли объект враждебным"""
        try:
            if obj_type == VisionObjectType.ENEMY:
                return True
            elif obj_type == VisionObjectType.TRAP:
                return True
            elif obj_type == VisionObjectType.PROJECTILE:
                return True
            elif hasattr(obj, 'is_hostile'):
                return obj.is_hostile
            elif isinstance(obj, dict) and 'is_hostile' in obj:
                return obj['is_hostile']
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка определения враждебности объекта: {e}")
            return False
    
    def _is_object_interactable(self, obj: Any, obj_type: VisionObjectType) -> bool:
        """Определяет, можно ли взаимодействовать с объектом"""
        try:
            if obj_type in [VisionObjectType.ITEM, VisionObjectType.CHEST, VisionObjectType.NPC]:
                return True
            elif hasattr(obj, 'is_interactable'):
                return obj.is_interactable
            elif isinstance(obj, dict) and 'is_interactable' in obj:
                return obj['is_interactable']
            else:
                return False
                
        except Exception as e:
            logger.error(f"Ошибка определения возможности взаимодействия: {e}")
            return False
    
    def _update_visual_memory(self, visual_obj: VisualObject, current_time: float):
        """Обновляет визуальную память"""
        try:
            memory_key = f"{visual_obj.object_type.value}_{visual_obj.object_id}"
            
            if memory_key in self.visual_memory:
                # Обновляем существующую память
                memory = self.visual_memory[memory_key]
                memory.last_seen_position = visual_obj.position
                memory.last_seen_time = current_time
                memory.importance = max(memory.importance, visual_obj.threat_level)
            else:
                # Создаем новую память
                self.visual_memory[memory_key] = VisualMemory(
                    object_id=visual_obj.object_id,
                    object_type=visual_obj.object_type,
                    last_seen_position=visual_obj.position,
                    last_seen_time=current_time,
                    importance=visual_obj.threat_level
                )
            
        except Exception as e:
            logger.error(f"Ошибка обновления визуальной памяти: {e}")
    
    def _analyze_visual_patterns(self, current_time: float):
        """Анализирует визуальные паттерны"""
        try:
            if len(self.visual_field.detected_objects) < 2:
                return
            
            # Создаем комбинацию объектов
            object_types = [obj.object_type for obj in self.visual_field.detected_objects]
            object_types.sort(key=lambda x: x.value)  # Сортируем для консистентности
            
            # Создаем ключ паттерна
            pattern_key = "_".join([t.value for t in object_types])
            
            if pattern_key not in self.visual_patterns:
                # Создаем новый паттерн
                self.visual_patterns[pattern_key] = VisualPattern(
                    pattern_id=pattern_key,
                    object_combination=object_types,
                    spatial_relationship={},
                    temporal_sequence=[current_time]
                )
            else:
                # Обновляем существующий паттерн
                pattern = self.visual_patterns[pattern_key]
                pattern.usage_count += 1
                pattern.last_used = current_time
                pattern.temporal_sequence.append(current_time)
                
                # Ограничиваем размер последовательности
                if len(pattern.temporal_sequence) > 10:
                    pattern.temporal_sequence = pattern.temporal_sequence[-10:]
            
        except Exception as e:
            logger.error(f"Ошибка анализа визуальных паттернов: {e}")
    
    def make_visual_decision(self, current_time: float) -> VisionAction:
        """Принимает решение на основе визуальной информации"""
        try:
            if not self.visual_field.detected_objects:
                return VisionAction.IGNORE
            
            # Создаем ключ состояния
            state_key = self._create_state_key()
            
            # Инициализируем Q-таблицу для состояния
            if state_key not in self.visual_q_table:
                self.visual_q_table[state_key] = {action: 0.0 for action in VisionAction}
            
            # Выбираем действие
            if random.random() < self.exploration_rate:
                # Исследование: случайное действие
                action = random.choice(list(VisionAction))
            else:
                # Эксплуатация: лучшее действие
                q_values = self.visual_q_table[state_key]
                best_actions = [a for a, q in q_values.items() if q == max(q_values.values())]
                action = random.choice(best_actions)
            
            # Обновляем статистику
            self.vision_stats["total_decisions"] += 1
            
            return action
            
        except Exception as e:
            logger.error(f"Ошибка принятия визуального решения: {e}")
            return VisionAction.IGNORE
    
    def _create_state_key(self) -> str:
        """Создает ключ состояния для Q-learning"""
        try:
            if not self.visual_field.detected_objects:
                return "empty_field"
            
            # Создаем упрощенное описание состояния
            object_types = [obj.object_type.value for obj in self.visual_field.detected_objects]
            object_types.sort()
            
            # Добавляем информацию об угрозах
            threats = [obj.threat_level for obj in self.visual_field.detected_objects if obj.threat_level > 0.5]
            threat_level = "high" if threats and max(threats) > 0.8 else "medium" if threats else "low"
            
            return f"{'_'.join(object_types)}_{threat_level}"
            
        except Exception as e:
            logger.error(f"Ошибка создания ключа состояния: {e}")
            return "unknown_state"
    
    def learn_from_visual_decision(self, action: VisionAction, success: bool, reward: float):
        """Учится на результате визуального решения"""
        try:
            state_key = self._create_state_key()
            
            if state_key not in self.visual_q_table:
                return
            
            # Обновляем Q-значение
            current_q = self.visual_q_table[state_key].get(action, 0.0)
            new_q = current_q + self.learning_rate * (reward - current_q)
            self.visual_q_table[state_key][action] = new_q
            
            # Обновляем статистику
            if success:
                self.vision_stats["successful_decisions"] += 1
            
        except Exception as e:
            logger.error(f"Ошибка обучения на визуальном решении: {e}")
    
    def get_visual_analysis(self) -> Dict[str, Any]:
        """Возвращает анализ визуальной информации"""
        try:
            return {
                "detected_objects": len(self.visual_field.detected_objects),
                "memory_objects": len(self.visual_memory),
                "recognized_patterns": len(self.visual_patterns),
                "threat_level": self._calculate_overall_threat_level(),
                "nearest_object": self._get_nearest_object_info(),
                "most_threatening_object": self._get_most_threatening_object_info(),
                "vision_stats": self.vision_stats.copy()
            }
        except Exception as e:
            logger.error(f"Ошибка получения визуального анализа: {e}")
            return {}
    
    def _calculate_overall_threat_level(self) -> float:
        """Вычисляет общий уровень угрозы"""
        try:
            if not self.visual_field.detected_objects:
                return 0.0
            
            threat_levels = [obj.threat_level for obj in self.visual_field.detected_objects]
            return max(threat_levels) if threat_levels else 0.0
            
        except Exception as e:
            logger.error(f"Ошибка вычисления общего уровня угрозы: {e}")
            return 0.0
    
    def _get_nearest_object_info(self) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о ближайшем объекте"""
        try:
            if not self.visual_field.detected_objects:
                return None
            
            nearest_obj = min(self.visual_field.detected_objects, key=lambda x: x.distance)
            
            return {
                "type": nearest_obj.object_type.value,
                "distance": nearest_obj.distance,
                "threat_level": nearest_obj.threat_level,
                "is_hostile": nearest_obj.is_hostile
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о ближайшем объекте: {e}")
            return None
    
    def _get_most_threatening_object_info(self) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о самом угрожающем объекте"""
        try:
            if not self.visual_field.detected_objects:
                return None
            
            most_threatening = max(self.visual_field.detected_objects, key=lambda x: x.threat_level)
            
            return {
                "type": most_threatening.object_type.value,
                "distance": most_threatening.distance,
                "threat_level": most_threatening.threat_level,
                "is_hostile": most_threatening.is_hostile
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о самом угрожающем объекте: {e}")
            return None
    
    def cleanup_old_memory(self, current_time: float):
        """Очищает старую память"""
        try:
            memory_keys_to_remove = []
            
            for key, memory in self.visual_memory.items():
                if current_time - memory.last_seen_time > memory.memory_duration:
                    memory_keys_to_remove.append(key)
            
            for key in memory_keys_to_remove:
                del self.visual_memory[key]
                
        except Exception as e:
            logger.error(f"Ошибка очистки старой памяти: {e}")
    
    def save_vision_data(self, filepath: str) -> bool:
        """Сохраняет данные зрения в файл"""
        try:
            vision_data = {
                "entity_id": self.entity_id,
                "visual_patterns": {
                    pattern_id: {
                        "object_combination": [t.value for t in pattern.object_combination],
                        "usage_count": pattern.usage_count,
                        "success_rate": pattern.success_rate,
                        "last_used": pattern.last_used
                    }
                    for pattern_id, pattern in self.visual_patterns.items()
                },
                "visual_q_table": self.visual_q_table,
                "vision_stats": self.vision_stats
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(vision_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Данные зрения сохранены в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных зрения: {e}")
            return False
    
    def load_vision_data(self, filepath: str) -> bool:
        """Загружает данные зрения из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                vision_data = json.load(f)
            
            # Загружаем паттерны
            self.visual_patterns.clear()
            for pattern_id, pattern_data in vision_data.get("visual_patterns", {}).items():
                self.visual_patterns[pattern_id] = VisualPattern(
                    pattern_id=pattern_id,
                    object_combination=[VisionObjectType(t) for t in pattern_data["object_combination"]],
                    spatial_relationship={},
                    temporal_sequence=[],
                    success_rate=pattern_data.get("success_rate", 0.0),
                    usage_count=pattern_data.get("usage_count", 0),
                    last_used=pattern_data.get("last_used", 0.0)
                )
            
            # Загружаем Q-таблицу
            self.visual_q_table = vision_data.get("visual_q_table", {})
            
            # Загружаем статистику
            self.vision_stats.update(vision_data.get("vision_stats", {}))
            
            logger.info(f"Данные зрения загружены из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных зрения: {e}")
            return False
