"""Класс врага, наследующий от BaseEnemy."""

import random
from typing import List, Tuple, Optional, Dict, Any
from .base_enemy import BaseEnemy
from .effect import Effect


class Enemy(BaseEnemy):
    """Класс обычного врага."""
    
    # Типы врагов для разнообразия
    ENEMY_TYPES = [
        "warrior",      # Ближний бой, высокая защита
        "archer",       # Дальний бой, высокая точность
        "mage",         # Магический урон, контроль
        "assassin",     # Скорость, критический урон
        "berserker",    # Высокий урон, низкая защита
        "shaman",       # Поддержка, баффы/дебаффы
        "tank",         # Высокая защита, угроза
        "summoner"      # Призыв существ
    ]
    
    def __init__(self, enemy_type: str = None, level: int = 1, position: Tuple[float, float] = (0, 0)):
        # Определяем тип врага
        if not enemy_type:
            enemy_type = random.choice(self.ENEMY_TYPES)
        
        # Создаем ID для врага
        entity_id = f"{enemy_type}_{random.randint(1000,9999)}"
        
        # Вызываем конструктор базового класса
        super().__init__(entity_id, enemy_type, level, position)
        
        # Устанавливаем приоритет для ИИ
        self.priority = {
            "warrior": 4,
            "archer": 4,
            "mage": 4,
            "assassin": 3,
            "berserker": 3,
            "shaman": 3,
            "tank": 3,
            "summoner": 3
        }.get(enemy_type, 4)
        
        # Скорость обучения для обычных врагов
        self.learning_rate = 0.05
    
    def _init_attributes(self):
        """Инициализация атрибутов на основе типа и уровня"""
        # Базовые характеристики для всех врагов
        base_stats = {
            "strength": 8,
            "dexterity": 8,
            "intelligence": 8,
            "vitality": 8,
            "endurance": 8,
            "faith": 8
        }
        
        # Модификаторы по типам врагов
        type_modifiers = {
            "warrior": {
                "strength": 1.3,
                "vitality": 1.2,
                "endurance": 1.1
            },
            "archer": {
                "dexterity": 1.4,
                "endurance": 1.2,
                "strength": 0.9
            },
            "mage": {
                "intelligence": 1.5,
                "faith": 1.2,
                "vitality": 0.8
            },
            "assassin": {
                "dexterity": 1.6,
                "strength": 1.1,
                "endurance": 1.3
            },
            "berserker": {
                "strength": 1.8,
                "vitality": 1.1,
                "endurance": 1.2
            },
            "shaman": {
                "intelligence": 1.3,
                "faith": 1.4,
                "vitality": 1.0
            },
            "tank": {
                "vitality": 1.6,
                "endurance": 1.4,
                "strength": 1.1
            },
            "summoner": {
                "intelligence": 1.4,
                "faith": 1.3,
                "endurance": 1.1
            }
        }
        
        # Применяем модификаторы типа
        modifiers = type_modifiers.get(self.enemy_type, {})
        for attr, value in base_stats.items():
            modifier = modifiers.get(attr, 1.0)
            final_value = int(value * modifier * (1 + (self.level - 1) * 0.1))
            self.set_attribute_base(attr, final_value)
    
    def _load_genetic_profile(self):
        """Загрузка генетического профиля"""
        if not self.genetic_profiles:
            return
        
        # Поиск профиля по типу врага
        profile = self.genetic_profiles.get(self.enemy_type, {})
        if not profile:
            return
        
        # Применение генетических модификаторов
        for attr, modifier in profile.get("attribute_modifiers", {}).items():
            if self.has_attribute(attr):
                current_value = self.get_attribute(attr)
                new_value = int(current_value * modifier)
                self.set_attribute_base(attr, new_value)
    
    def _load_abilities(self):
        """Загрузка способностей"""
        if not self.abilities_db:
            return
        
        # Поиск способностей по типу врага
        abilities = self.abilities_db.get(self.enemy_type, [])
        for ability_id in abilities:
            # Здесь можно добавить логику загрузки способностей
            pass
    
    def _apply_initial_effects(self):
        """Применение начальных эффектов"""
        if not self.effects_db:
            return
        
        # Поиск эффектов по типу врага
        effects = self.effects_db.get(self.enemy_type, [])
        for effect_data in effects:
            effect = Effect.from_dict(effect_data)
            if effect:
                self.add_effect(effect)
    
    def _use_abilities(self, delta_time: float):
        """Использование способностей"""
        # Простая логика использования способностей
        if hasattr(self, 'ai_controller') and self.ai_controller:
            # ИИ контроллер решает, какую способность использовать
            pass
    
    def _generate_loot(self):
        """Генерация лута при смерти"""
        # Простая генерация лута
        loot_chance = 0.3  # 30% шанс выпадения лута
        
        if random.random() < loot_chance:
            # Здесь можно добавить логику генерации конкретных предметов
            pass


class EnemyGenerator:
    """Генератор врагов."""
    
    @staticmethod
    def generate_enemy(level: int, position: Tuple[float, float] = None):
        """Генерация обычного врага"""
        if position is None:
            position = (random.randint(0, 100), random.randint(0, 100))
        
        return Enemy(level=level, position=position)
    
    @staticmethod
    def generate_boss(level: int, position: Tuple[float, float] = None):
        """Генерация босса (перенаправляет на BossGenerator)"""
        from .boss import BossGenerator
        return BossGenerator.generate_boss(level, position)