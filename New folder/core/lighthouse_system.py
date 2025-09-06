#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА ПОИСКА МАЯКА
Основная игровая механика - поиск маяка как выхода с уровня
Интеграция с ИИ обучением и навигацией
"""

import time
import math
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class LighthouseState(Enum):
    """Состояния маяка"""
    HIDDEN = "hidden"           # Скрыт, не обнаружен
    DETECTED = "detected"       # Обнаружен, но не достигнут
    REACHED = "reached"         # Достигнут
    ACTIVATED = "activated"     # Активирован (выход открыт)

class DiscoveryMethod(Enum):
    """Способы обнаружения маяка"""
    VISUAL = "visual"           # Визуальное обнаружение
    RADAR = "radar"             # Радар/сканирование
    MAP = "map"                 # По карте
    AI_LEARNING = "ai_learning" # ИИ обучение
    RANDOM = "random"           # Случайное обнаружение

@dataclass
class LighthouseLocation:
    """Расположение маяка"""
    x: float
    y: float
    z: float
    world_id: str
    region_id: str
    difficulty_level: int
    discovery_radius: float = 100.0
    activation_radius: float = 5.0

@dataclass
class LighthouseDiscovery:
    """Обнаружение маяка"""
    entity_id: str
    discovery_time: float
    discovery_method: DiscoveryMethod
    distance: float
    confidence: float  # Уверенность в обнаружении (0.0 - 1.0)

@dataclass
class Lighthouse:
    """Маяк"""
    lighthouse_id: str
    name: str
    location: LighthouseLocation
    state: LighthouseState
    discoveries: List[LighthouseDiscovery] = field(default_factory=list)
    activation_requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class LighthouseSystem:
    """Система поиска маяка"""
    
    def __init__(self, world_size: Tuple[float, float] = (1000.0, 1000.0)):
        self.world_size = world_size
        self.logger = get_logger(__name__)
        
        # Кэш маяков
        self.lighthouses: Dict[str, Lighthouse] = {}
        self.active_lighthouse: Optional[Lighthouse] = None
        
        # Настройки обнаружения
        self.visual_detection_range = 200.0
        self.radar_detection_range = 500.0
        self.ai_learning_bonus = 0.1  # Бонус к обнаружению от ИИ обучения
        
        # Статистика
        self.total_discoveries = 0
        self.total_activations = 0
        
        log_system_event("lighthouse_system", "initialized")
    
    def generate_lighthouse_for_session(self, session_id: str, difficulty_level: int = 1) -> Lighthouse:
        """Генерация маяка для роглайк сессии"""
        try:
            # Генерируем случайное расположение
            x = random.uniform(-self.world_size[0]/2, self.world_size[0]/2)
            y = random.uniform(-self.world_size[1]/2, self.world_size[1]/2)
            z = 0.0  # Маяк на уровне земли
            
            # Создаем маяк
            lighthouse_id = f"lighthouse_{session_id}_{int(time.time())}"
            location = LighthouseLocation(
                x=x, y=y, z=z,
                world_id=f"world_{session_id}",
                region_id=f"region_{session_id}",
                difficulty_level=difficulty_level,
                discovery_radius=100.0 + (difficulty_level * 20.0),
                activation_radius=5.0
            )
            
            lighthouse = Lighthouse(
                lighthouse_id=lighthouse_id,
                name=f"Ancient Lighthouse {session_id[:8]}",
                location=location,
                state=LighthouseState.HIDDEN,
                activation_requirements={
                    "keys_required": random.randint(1, 3),
                    "items_required": random.randint(0, 2),
                    "ai_memory_level": difficulty_level * 10
                },
                rewards=[
                    "experience_bonus",
                    "rare_items",
                    "ai_memory_upgrade"
                ]
            )
            
            self.lighthouses[lighthouse_id] = lighthouse
            self.active_lighthouse = lighthouse
            
            self.logger.info(f"Generated lighthouse {lighthouse_id} at ({x:.1f}, {y:.1f}) for session {session_id}")
            return lighthouse
            
        except Exception as e:
            self.logger.error(f"Error generating lighthouse: {e}")
            return None
    
    def attempt_discovery(self, entity_id: str, entity_position: Tuple[float, float, float], 
                         entity_type: str, ai_memory_level: int = 0) -> Optional[LighthouseDiscovery]:
        """Попытка обнаружения маяка"""
        if not self.active_lighthouse:
            return None
        
        try:
            # Вычисляем расстояние до маяка
            distance = self._calculate_distance(entity_position, self.active_lighthouse.location)
            
            # Определяем метод обнаружения
            discovery_method = self._determine_discovery_method(entity_type, distance, ai_memory_level)
            
            # Вычисляем вероятность обнаружения
            discovery_chance = self._calculate_discovery_chance(
                distance, discovery_method, entity_type, ai_memory_level
            )
            
            # Проверяем успешность обнаружения
            if random.random() < discovery_chance:
                discovery = LighthouseDiscovery(
                    entity_id=entity_id,
                    discovery_time=time.time(),
                    discovery_method=discovery_method,
                    distance=distance,
                    confidence=discovery_chance
                )
                
                # Добавляем обнаружение к маяку
                self.active_lighthouse.discoveries.append(discovery)
                
                # Обновляем состояние маяка
                if self.active_lighthouse.state == LighthouseState.HIDDEN:
                    self.active_lighthouse.state = LighthouseState.DETECTED
                
                self.total_discoveries += 1
                
                self.logger.info(f"Lighthouse discovered by {entity_id} using {discovery_method.value} method")
                return discovery
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error attempting discovery: {e}")
            return None
    
    def attempt_activation(self, entity_id: str, entity_position: Tuple[float, float, float],
                          entity_inventory: List[str], ai_memory_level: int) -> bool:
        """Попытка активации маяка"""
        if not self.active_lighthouse:
            return False
        
        try:
            # Проверяем расстояние
            distance = self._calculate_distance(entity_position, self.active_lighthouse.location)
            if distance > self.active_lighthouse.location.activation_radius:
                return False
            
            # Проверяем требования активации
            if not self._check_activation_requirements(entity_inventory, ai_memory_level):
                return False
            
            # Активируем маяк
            self.active_lighthouse.state = LighthouseState.ACTIVATED
            self.total_activations += 1
            
            self.logger.info(f"Lighthouse activated by {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error attempting activation: {e}")
            return False
    
    def get_lighthouse_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о маяке для сущности"""
        if not self.active_lighthouse:
            return None
        
        # Проверяем, обнаружил ли сущность маяк
        has_discovered = any(
            discovery.entity_id == entity_id 
            for discovery in self.active_lighthouse.discoveries
        )
        
        if not has_discovered:
            return {
                "state": "hidden",
                "message": "Маяк не обнаружен"
            }
        
        # Получаем информацию об обнаружении
        discovery = next(
            discovery for discovery in self.active_lighthouse.discoveries
            if discovery.entity_id == entity_id
        )
        
        return {
            "lighthouse_id": self.active_lighthouse.lighthouse_id,
            "name": self.active_lighthouse.name,
            "state": self.active_lighthouse.state.value,
            "location": {
                "x": self.active_lighthouse.location.x,
                "y": self.active_lighthouse.location.y,
                "z": self.active_lighthouse.location.z
            },
            "distance": discovery.distance,
            "discovery_method": discovery.discovery_method.value,
            "confidence": discovery.confidence,
            "activation_requirements": self.active_lighthouse.activation_requirements,
            "rewards": self.active_lighthouse.rewards
        }
    
    def get_navigation_hints(self, entity_id: str, entity_position: Tuple[float, float, float]) -> List[str]:
        """Получение подсказок для навигации к маяку"""
        if not self.active_lighthouse:
            return []
        
        hints = []
        distance = self._calculate_distance(entity_position, self.active_lighthouse.location)
        
        # Общие подсказки
        if distance > 500:
            hints.append("Маяк находится очень далеко. Ищите высокие сооружения на горизонте.")
        elif distance > 200:
            hints.append("Маяк в пределах досягаемости. Продолжайте движение в том же направлении.")
        elif distance > 50:
            hints.append("Маяк близко! Вы должны его видеть.")
        else:
            hints.append("Вы почти у цели! Маяк должен быть прямо перед вами.")
        
        # Направление
        dx = self.active_lighthouse.location.x - entity_position[0]
        dy = self.active_lighthouse.location.y - entity_position[1]
        
        if abs(dx) > abs(dy):
            direction = "восток" if dx > 0 else "запад"
        else:
            direction = "север" if dy > 0 else "юг"
        
        hints.append(f"Маяк находится на {direction} от вашего текущего положения.")
        
        return hints
    
    def update_ai_learning(self, entity_id: str, learning_data: Dict[str, Any]):
        """Обновление ИИ обучения для улучшения поиска маяка"""
        if not self.active_lighthouse:
            return
        
        # Улучшаем способности обнаружения на основе обучения
        learning_bonus = learning_data.get("lighthouse_search_bonus", 0.0)
        
        # Обновляем бонус к обнаружению
        if learning_bonus > 0:
            self.ai_learning_bonus = min(0.5, self.ai_learning_bonus + learning_bonus)
            self.logger.info(f"AI learning bonus increased to {self.ai_learning_bonus} for {entity_id}")
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                           pos2: LighthouseLocation) -> float:
        """Вычисление расстояния между двумя точками"""
        dx = pos1[0] - pos2.x
        dy = pos1[1] - pos2.y
        dz = pos1[2] - pos2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _determine_discovery_method(self, entity_type: str, distance: float, 
                                   ai_memory_level: int) -> DiscoveryMethod:
        """Определение метода обнаружения"""
        # Только игрок может обнаруживать маяк
        if entity_type != "player":
            return DiscoveryMethod.RANDOM  # Враги не могут обнаруживать маяк
        
        if distance <= self.visual_detection_range:
            return DiscoveryMethod.VISUAL
        elif distance <= self.radar_detection_range:
            return DiscoveryMethod.RADAR
        elif ai_memory_level > 50:
            return DiscoveryMethod.AI_LEARNING
        else:
            return DiscoveryMethod.RANDOM
    
    def _calculate_discovery_chance(self, distance: float, method: DiscoveryMethod,
                                   entity_type: str, ai_memory_level: int) -> float:
        """Вычисление вероятности обнаружения"""
        # Только игрок может обнаруживать маяк
        if entity_type != "player":
            return 0.0  # Враги не могут обнаруживать маяк
        
        base_chance = 0.1
        
        # Модификаторы по расстоянию
        if distance <= 50:
            distance_modifier = 1.0
        elif distance <= 100:
            distance_modifier = 0.8
        elif distance <= 200:
            distance_modifier = 0.6
        elif distance <= 500:
            distance_modifier = 0.3
        else:
            distance_modifier = 0.1
        
        # Модификаторы по методу
        method_modifiers = {
            DiscoveryMethod.VISUAL: 0.9,
            DiscoveryMethod.RADAR: 0.7,
            DiscoveryMethod.AI_LEARNING: 0.5 + (ai_memory_level * 0.01),
            DiscoveryMethod.MAP: 0.8,
            DiscoveryMethod.RANDOM: 0.05
        }
        
        # Итоговая вероятность (только для игрока)
        final_chance = (base_chance * distance_modifier * 
                       method_modifiers.get(method, 0.1) + 
                       self.ai_learning_bonus)
        
        return min(1.0, max(0.0, final_chance))
    
    def _check_activation_requirements(self, entity_inventory: List[str], 
                                      ai_memory_level: int) -> bool:
        """Проверка требований для активации маяка"""
        if not self.active_lighthouse:
            return False
        
        requirements = self.active_lighthouse.activation_requirements
        
        # Проверяем уровень памяти ИИ
        if ai_memory_level < requirements.get("ai_memory_level", 0):
            return False
        
        # Проверяем наличие ключей
        keys_required = requirements.get("keys_required", 0)
        keys_found = sum(1 for item in entity_inventory if "key" in item.lower())
        
        if keys_found < keys_required:
            return False
        
        # Проверяем наличие предметов
        items_required = requirements.get("items_required", 0)
        if len(entity_inventory) < items_required:
            return False
        
        return True
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы маяков"""
        return {
            "total_lighthouses": len(self.lighthouses),
            "active_lighthouse": self.active_lighthouse.lighthouse_id if self.active_lighthouse else None,
            "total_discoveries": self.total_discoveries,
            "total_activations": self.total_activations,
            "ai_learning_bonus": self.ai_learning_bonus,
            "world_size": self.world_size
        }
    
    def save_lighthouse_data(self, save_id: str) -> bool:
        """Сохранение данных маяков"""
        try:
            lighthouse_data = {
                "lighthouses": {
                    lighthouse_id: {
                        "lighthouse_id": lighthouse.lighthouse_id,
                        "name": lighthouse.name,
                        "location": {
                            "x": lighthouse.location.x,
                            "y": lighthouse.location.y,
                            "z": lighthouse.location.z,
                            "world_id": lighthouse.location.world_id,
                            "region_id": lighthouse.location.region_id,
                            "difficulty_level": lighthouse.location.difficulty_level,
                            "discovery_radius": lighthouse.location.discovery_radius,
                            "activation_radius": lighthouse.location.activation_radius
                        },
                        "state": lighthouse.state.value,
                        "discoveries": [
                            {
                                "entity_id": discovery.entity_id,
                                "discovery_time": discovery.discovery_time,
                                "discovery_method": discovery.discovery_method.value,
                                "distance": discovery.distance,
                                "confidence": discovery.confidence
                            }
                            for discovery in lighthouse.discoveries
                        ],
                        "activation_requirements": lighthouse.activation_requirements,
                        "rewards": lighthouse.rewards,
                        "created_at": lighthouse.created_at
                    }
                    for lighthouse_id, lighthouse in self.lighthouses.items()
                },
                "active_lighthouse_id": self.active_lighthouse.lighthouse_id if self.active_lighthouse else None,
                "total_discoveries": self.total_discoveries,
                "total_activations": self.total_activations,
                "ai_learning_bonus": self.ai_learning_bonus
            }
            
            # Сохраняем в файл
            lighthouse_file = Path("data") / f"{save_id}_lighthouses.json"
            lighthouse_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(lighthouse_file, 'w', encoding='utf-8') as f:
                json.dump(lighthouse_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved lighthouse data to {lighthouse_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving lighthouse data: {e}")
            return False
