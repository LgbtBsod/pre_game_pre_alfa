"""Класс босса, наследующий от BaseEnemy."""

import random
from typing import Tuple, Dict, Any
from .base_enemy import BaseEnemy
from .effect import Effect


class Boss(BaseEnemy):
    """Класс босса."""
    
    BOSS_TYPES = ["dragon", "demon_lord", "lich_king", "titan", "behemoth", "leviathan"]
    
    def __init__(self, boss_type: str = None, level: int = 10, position: Tuple[float, float] = (0, 0)):
        # Определяем тип босса
        if not boss_type:
            boss_type = random.choice(self.BOSS_TYPES)
        
        # Создаем ID для босса
        entity_id = f"{boss_type}_{random.randint(1000,9999)}"
        
        # Сохраняем тип босса как атрибут
        self.boss_type = boss_type
        
        # Вызываем конструктор базового класса
        super().__init__(entity_id, boss_type, level, position)
        
        # Специфичные для босса свойства
        self.is_boss = True
        self.title = f"Великий {boss_type.capitalize()}"
        self.phase = 1
        self.phase_transition_health = [0.7, 0.4, 0.2]  # Пороги здоровья для смены фаз
        self.special_attack_cooldown = 0.0
        self.last_phase_transition = 0
        
        # Скорость обучения для боссов (очень медленная)
        self.learning_rate = 0.005
        
        # Устанавливаем приоритет для ИИ (боссы имеют высший приоритет)
        self.priority = 1
        
        # Установка фазовых эффектов
        self.apply_phase_effects()
    
    def _init_attributes(self):
        """Инициализация атрибутов босса"""
        # Базовые характеристики для боссов
        base_stats = {
            "strength": 20,
            "dexterity": 15,
            "intelligence": 18,
            "vitality": 25,
            "endurance": 20,
            "faith": 15
        }
        
        # Модификаторы по типам боссов
        type_modifiers = {
            "dragon": {
                "strength": 1.5,
                "vitality": 1.4,
                "intelligence": 1.3
            },
            "demon_lord": {
                "strength": 1.4,
                "intelligence": 1.5,
                "faith": 1.3
            },
            "lich_king": {
                "intelligence": 1.6,
                "faith": 1.4,
                "vitality": 1.2
            },
            "titan": {
                "strength": 1.8,
                "vitality": 1.6,
                "endurance": 1.4
            },
            "behemoth": {
                "strength": 1.7,
                "vitality": 1.8,
                "endurance": 1.5
            },
            "leviathan": {
                "intelligence": 1.5,
                "faith": 1.6,
                "dexterity": 1.3
            }
        }
        
        # Применяем модификаторы типа
        modifiers = type_modifiers.get(self.boss_type, {})
        for attr, value in base_stats.items():
            modifier = modifiers.get(attr, 1.0)
            # Боссы получают больший бонус за уровень
            final_value = int(value * modifier * (1 + (self.level - 1) * 0.2))
            self.set_attribute_base(attr, final_value)
    
    def _load_genetic_profile(self):
        """Загрузка генетического профиля босса"""
        if not self.genetic_profiles:
            return
        
        # Поиск профиля по типу босса
        profile = self.genetic_profiles.get(self.boss_type, {})
        if not profile:
            return
        
        # Применение генетических модификаторов
        for attr, modifier in profile.get("attribute_modifiers", {}).items():
            if self.has_attribute(attr):
                current_value = self.get_attribute(attr)
                new_value = int(current_value * modifier)
                self.set_attribute_base(attr, new_value)
    
    def _load_abilities(self):
        """Загрузка способностей босса"""
        if not self.abilities_db:
            return
        
        # Поиск способностей по типу босса
        abilities = self.abilities_db.get(self.boss_type, [])
        for ability_id in abilities:
            # Здесь можно добавить логику загрузки способностей
            pass
    
    def _apply_initial_effects(self):
        """Применение начальных эффектов босса"""
        if not self.effects_db:
            return
        
        # Поиск эффектов по типу босса
        effects = self.effects_db.get(self.boss_type, [])
        for effect_data in effects:
            effect = Effect.from_dict(effect_data)
            if effect:
                self.add_effect(effect)
    
    def apply_phase_effects(self):
        """Применение эффектов текущей фазы"""
        # Удаляем старые фазовые эффекты
        self.active_effects = {k: v for k, v in self.active_effects.items() 
                              if not hasattr(v, 'is_phase_effect')}
        
        # Применяем новые фазовые эффекты
        phase_effects = {
            1: {
                "id": "phase_1", 
                "tags": ["phase", "buff"], 
                "modifiers": [
                    {"attribute": "damage_output", "value": 1.0, "mode": "multiply"}
                ]
            },
            2: {
                "id": "phase_2", 
                "tags": ["phase", "buff"], 
                "modifiers": [
                    {"attribute": "damage_output", "value": 1.3, "mode": "multiply"},
                    {"attribute": "attack_speed", "value": 1.2, "mode": "multiply"}
                ]
            },
            3: {
                "id": "phase_3", 
                "tags": ["phase", "buff"], 
                "modifiers": [
                    {"attribute": "damage_output", "value": 1.6, "mode": "multiply"},
                    {"attribute": "attack_speed", "value": 1.4, "mode": "multiply"},
                    {"attribute": "movement_speed", "value": 1.3, "mode": "multiply"}
                ]
            }
        }
        
        if self.phase in phase_effects:
            effect_data = phase_effects[self.phase]
            effect = Effect.from_dict(effect_data)
            if effect:
                effect.is_phase_effect = True
                # Используем effect.id как effect_id и effect_data как effect_data
                self.add_effect(effect.id, effect_data)
    
    def update(self, delta_time: float):
        """Обновление босса"""
        super().update(delta_time)
        
        # Проверка смены фазы
        self.check_phase_transition()
        
        # Обновление специальных атак
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= delta_time
    
    def check_phase_transition(self):
        """Проверка необходимости смены фазы"""
        health_percentage = self.get_health() / self.get_max_health()
        
        for i, threshold in enumerate(self.phase_transition_health, 1):
            if health_percentage <= threshold and self.phase == i:
                self.set_phase(i + 1)
                break
    
    def set_phase(self, new_phase: int):
        """Установка новой фазы"""
        if new_phase != self.phase and new_phase <= len(self.phase_transition_health) + 1:
            self.phase = new_phase
            self.last_phase_transition = 0
            
            # Применяем эффекты новой фазы
            self.apply_phase_effects()
            
            # Специальные действия при смене фазы
            if new_phase == 2:
                # Фаза 2: увеличение агрессивности
                self.special_attack_cooldown = 0  # Сброс перезарядки
            elif new_phase == 3:
                # Фаза 3: максимальная агрессивность
                self.special_attack_cooldown = 0
                # Можно добавить специальные способности
    
    def _use_abilities(self, delta_time: float):
        """Использование способностей босса"""
        # Проверяем возможность использования специальной атаки
        if self.special_attack_cooldown <= 0:
            # Используем специальную атаку
            self._use_special_attack()
            self.special_attack_cooldown = 10.0  # 10 секунд перезарядки
    
    def _use_special_attack(self):
        """Использование специальной атаки босса"""
        # Здесь можно добавить логику специальных атак
        pass
    
    def use_skill(self, ability_id: str):
        """Использование способности по ID"""
        # Проверяем наличие способности
        if not self.abilities_db or self.boss_type not in self.abilities_db:
            return False
        
        abilities = self.abilities_db[self.boss_type]
        if ability_id not in abilities:
            return False
        
        # Используем способность
        ability_data = abilities[ability_id]
        # Здесь можно добавить логику применения способности
        
        return True
    
    def take_damage(self, damage_report: dict):
        """Получение урона боссом"""
        super().take_damage(damage_report)
        
        # Дополнительная логика для боссов
        if hasattr(self, 'ai_controller') and self.ai_controller:
            self.ai_controller.on_damage_taken(damage_report)
    
    def die(self):
        """Смерть босса"""
        super().die()
        
        # Генерация награды
        self._generate_reward()
    
    def _generate_reward(self):
        """Генерация награды при смерти босса"""
        # Боссы всегда дают награду
        reward = {
            "gold": self.calculate_gold_amount(100),
            "experience": self.level * 100,
            "items": []
        }
        
        # Шанс выпадения редких предметов
        if random.random() < 0.8:  # 80% шанс
            reward["items"].append({
                "type": "rare_weapon",
                "quality": self.calculate_loot_quality(1.5),
                "value": self.level * 200
            })
        
        # Шанс выпадения эпических предметов
        if random.random() < 0.3:  # 30% шанс
            reward["items"].append({
                "type": "epic_armor",
                "quality": self.calculate_loot_quality(2.0),
                "value": self.level * 500
            })
        
        return reward
    
    def calculate_gold_amount(self, base_gold: int) -> int:
        """Расчет количества золота"""
        return int(base_gold * self.level * (1 + random.random() * 0.5))
    
    def calculate_loot_quality(self, base_quality: float) -> float:
        """Расчет качества лута"""
        return base_quality * (1 + (self.level - 1) * 0.1)
    
    def player_died(self):
        """Реакция на смерть игрока"""
        # Босс может восстановить здоровье или получить бафф
        if self.phase > 1:
            # В поздних фазах босс становится сильнее
            self.set_phase(self.phase - 1)
        
        # Восстанавливаем часть здоровья
        current_health = self.get_health()
        max_health = self.get_max_health()
        restore_amount = max_health * 0.3
        
        self.heal(restore_amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация босса"""
        data = super().to_dict()
        data.update({
            'is_boss': self.is_boss,
            'title': self.title,
            'phase': self.phase,
            'phase_transition_health': self.phase_transition_health,
            'special_attack_cooldown': self.special_attack_cooldown,
            'last_phase_transition': self.last_phase_transition
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация босса"""
        super().from_dict(data)
        self.is_boss = data.get('is_boss', True)
        self.title = data.get('title', 'Великий Босс')
        self.phase = data.get('phase', 1)
        self.phase_transition_health = data.get('phase_transition_health', [0.7, 0.4, 0.2])
        self.special_attack_cooldown = data.get('special_attack_cooldown', 0.0)
        self.last_phase_transition = data.get('last_phase_transition', 0)


class BossGenerator:
    """Генератор боссов."""
    
    @staticmethod
    def generate_boss(level: int = 10, position: Tuple[float, float] = None):
        """Генерация босса"""
        if position is None:
            position = (random.randint(0, 100), random.randint(0, 100))
        
        return Boss(level=level, position=position)
    
    @staticmethod
    def generate_area_boss(area_level: int, area_type: str):
        """Генерация босса для определенной области"""
        # Определяем тип босса по типу области
        area_boss_mapping = {
            "forest": "dragon",
            "dungeon": "demon_lord",
            "crypt": "lich_king",
            "mountain": "titan",
            "swamp": "behemoth",
            "ocean": "leviathan"
        }
        
        boss_type = area_boss_mapping.get(area_type, "dragon")
        level = max(area_level, 10)
        
        return Boss(boss_type=boss_type, level=level)