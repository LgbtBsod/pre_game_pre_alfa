"""Базовый класс для всех врагов."""

import random
import json
import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .entity import Entity
from .effect import Effect
from ai.advanced_ai import AdvancedAIController

logger = logging.getLogger(__name__)


class BaseEnemy(Entity):
    """Базовый класс для всех врагов."""
    
    # Общие пути к данным
    GENETIC_PROFILES_PATH = "data/genetic_profiles.json"
    EFFECTS_PATH = "data/effects.json"
    ABILITIES_PATH = "data/abilities.json"
    
    def __init__(self, entity_id: str, enemy_type: str, level: int, position: Tuple[float, float]):
        super().__init__(entity_id, position)
        
        self.enemy_type = enemy_type
        self.level = level
        self.is_player = False
        
        # Загрузка данных
        self.genetic_profiles = self._load_data(self.GENETIC_PROFILES_PATH)
        self.effects_db = self._load_data(self.EFFECTS_PATH)
        self.abilities_db = self._load_data(self.ABILITIES_PATH)
        
        # Инициализация ИИ контроллера
        self.ai_controller = AdvancedAIController(self)
        
        # Инициализация характеристик
        self._init_attributes()
        
        # Загрузка генетического профиля
        self._load_genetic_profile()
        
        # Загрузка способностей
        self._load_abilities()
        
        # Применение начальных эффектов
        self._apply_initial_effects()
    
    def _load_data(self, file_path: str) -> dict:
        """Загрузка данных из JSON-файла"""
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки {file_path}: {str(e)}")
            return {}
    
    def _init_attributes(self):
        """Инициализация атрибутов. Должна быть переопределена в подклассах."""
        raise NotImplementedError("Метод _init_attributes должен быть переопределен")
    
    def _load_genetic_profile(self):
        """Загрузка генетического профиля. Должна быть переопределена в подклассах."""
        raise NotImplementedError("Метод _load_genetic_profile должен быть переопределен")
    
    def _load_abilities(self):
        """Загрузка способностей. Должна быть переопределена в подклассах."""
        raise NotImplementedError("Метод _load_abilities должен быть переопределен")
    
    def _apply_initial_effects(self):
        """Применение начальных эффектов. Должна быть переопределена в подклассах."""
        raise NotImplementedError("Метод _apply_initial_effects должен быть переопределен")
    
    def update(self, delta_time: float):
        """Обновление врага"""
        super().update(delta_time)
        
        # Обновление ИИ
        if self.ai_controller:
            self.ai_controller.update(delta_time)
        
        # Использование способностей
        self._use_abilities(delta_time)
        
        # Обновление эффектов
        self.update_effects(delta_time)
    
    def _use_abilities(self, delta_time: float):
        """Использование способностей. Должна быть переопределена в подклассах."""
        pass
    
    def take_damage(self, damage_report: dict):
        """Получение урона"""
        super().take_damage(damage_report)
        
        # Дополнительная логика для врагов (например, агрессия)
        if hasattr(self, 'ai_controller') and self.ai_controller:
            self.ai_controller.on_damage_taken(damage_report)
    
    def die(self):
        """Смерть врага"""
        super().die()
        
        # Генерация лута
        self._generate_loot()
    
    def _generate_loot(self):
        """Генерация лута. Должна быть переопределена в подклассах."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация врага"""
        data = super().to_dict()
        data.update({
            'enemy_type': self.enemy_type,
            'level': self.level,
            'is_player': self.is_player
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация врага"""
        super().from_dict(data)
        self.enemy_type = data.get('enemy_type', 'unknown')
        self.level = data.get('level', 1)
        self.is_player = data.get('is_player', False)
