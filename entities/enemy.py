from .entity import Entity
from .effect import Effect
from ai.advanced_ai import AdvancedAIController
import random
from typing import List, Tuple, Optional, Dict, Any
import json
import os
import math
import time

class Enemy(Entity):
    # Общая память между всеми врагами
    shared_knowledge = {}
    GENETIC_PROFILES_PATH = "data/genetic_profiles.json"
    EFFECTS_PATH = "data/effects.json"
    ABILITIES_PATH = "data/abilities.json"
    
    # Типы врагов для разнообразия (хотя формально это одна сущность)
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
            
        super().__init__(f"{enemy_type}_{random.randint(1000,9999)}", position)
        
        self.enemy_type = enemy_type
        self.level = level
        self.learning_rate = 0.05
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
            print(f"Ошибка загрузки {file_path}: {str(e)}")
            return {}
    
    def _init_attributes(self):
        """Инициализация характеристик в зависимости от типа врага"""
        # Базовые значения
        base_stats = {
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "faith": 10,
            "vitality": 10,
            "endurance": 10,
            "luck": 5
        }
        
        # Модификаторы для разных типов врагов
        type_modifiers = {
            "warrior": {
                "strength": 1.5,
                "vitality": 1.4,
                "endurance": 1.3,
                "luck": 0.8
            },
            "archer": {
                "dexterity": 1.8,
                "intelligence": 1.2,
                "luck": 1.2
            },
            "mage": {
                "intelligence": 2.0,
                "faith": 1.5,
                "vitality": 0.8,
                "luck": 1.0
            },
            "assassin": {
                "dexterity": 1.7,
                "strength": 1.2,
                "luck": 1.5
            },
            "berserker": {
                "strength": 2.0,
                "endurance": 1.5,
                "vitality": 0.7,
                "luck": 0.7
            },
            "shaman": {
                "faith": 1.8,
                "intelligence": 1.5,
                "vitality": 1.1,
                "luck": 1.3
            },
            "tank": {
                "vitality": 2.0,
                "endurance": 1.8,
                "strength": 1.1,
                "luck": 0.5
            },
            "summoner": {
                "intelligence": 1.7,
                "faith": 1.3,
                "luck": 1.1
            }
        }
        
        # Применяем модификаторы уровня
        level_bonus = (self.level - 1) * 2
        
        for attr in self.attributes:
            # Базовое значение + бонус уровня
            value = base_stats[attr] + level_bonus
            
            # Применяем модификатор типа
            if self.enemy_type in type_modifiers and attr in type_modifiers[self.enemy_type]:
                value *= type_modifiers[self.enemy_type][attr]
            
            self.attributes[attr] = int(value)
        
        # Обновляем производные характеристики
        self.update_derived_stats()
        
        # Устанавливаем текущие ресурсы
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.mana = self.max_mana
        
        # Уникальные боевые характеристики по типам
        if self.enemy_type == "archer":
            self.combat_stats["attack_range"] *= 1.5
            self.combat_stats["critical_chance"] += 0.1
        elif self.enemy_type == "mage":
            self.combat_stats["elemental_penetration"] = 0.2
        elif self.enemy_type == "assassin":
            self.combat_stats["critical_damage"] = 2.0
            self.combat_stats["movement_speed"] *= 1.3
        elif self.enemy_type == "berserker":
            self.combat_stats["physical_damage_mod"] = 1.3
            self.combat_stats["life_steal"] = 0.1
        elif self.enemy_type == "tank":
            self.combat_stats["physical_resist"] = 0.3
            self.combat_stats["block_chance"] = 0.2
    
    def _load_genetic_profile(self):
        """Загрузка генетического профиля для типа врага"""
        if self.enemy_type in self.genetic_profiles:
            self.genetic_profile = self.genetic_profiles[self.enemy_type]
        else:
            # Дефолтный профиль
            self.genetic_profile = {
                "AGGRESSIVE_GENE": {
                    "immediate_effects": {"damage_boost": 10},
                    "effects": {"damage_multiplier": 1.2},
                    "emotion_modifier": {"emotion": "RAGE", "multiplier": 1.3}
                }
            }
    
    def _load_abilities(self):
        """Загрузка способностей для типа врага"""
        if self.enemy_type in self.abilities_db:
            # Загружаем способности для этого типа
            self.skills = self.abilities_db[self.enemy_type]
        else:
            # Дефолтные способности
            self.skills = {
                "basic_attack": {
                    "name": "Базовая атака",
                    "description": "Обычная атака",
                    "damage": 10,
                    "cooldown": 1.0,
                    "stamina_cost": 5,
                    "tags": ["attack"]
                }
            }
        
        # Добавляем способности из генетического профиля
        for gene_id, gene_data in self.genetic_profile.items():
            if "abilities" in gene_data:
                for ability_id, ability_data in gene_data["abilities"].items():
                    self.skills[ability_id] = ability_data
    
    def _apply_initial_effects(self):
        """Применение начальных эффектов в зависимости от типа"""
        initial_effects = {
            "warrior": ["combat_training"],
            "archer": ["eagle_eye"],
            "mage": ["arcane_aura"],
            "assassin": ["stealth"],
            "berserker": ["bloodlust"],
            "shaman": ["spirit_guard"],
            "tank": ["iron_skin"],
            "summoner": ["summoners_blessing"]
        }
        
        if self.enemy_type in initial_effects:
            for effect_id in initial_effects[self.enemy_type]:
                if effect_id in self.effects_db:
                    self.add_effect(effect_id, self.effects_db[effect_id])
    
    def update(self, delta_time: float):
        """Обновление состояния врага"""
        if not self.alive:
            return
        
        # Обновление эффектов
        self.update_effects(delta_time)
        
        # Обновление ИИ контроллера
        self.ai_controller.update(delta_time)
        
        # Обновление таймеров
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Автоматическое применение способностей
        self._use_abilities(delta_time)
        
        # Обновление расстояния до игрока (для оптимизации ИИ)
        if hasattr(self, 'player_ref') and self.player_ref:
            self.distance_to_player = self.distance_to(self.player_ref)
        else:
            self.distance_to_player = float('inf')
    
    def _use_abilities(self, delta_time: float):
        """Автоматическое использование способностей"""
        # Проверяем возможность использовать способность
        current_time = time.time()
        can_use_ability = True
        
        # Проверяем глобальную перезарядку способностей
        if hasattr(self, 'last_ability_time') and current_time - self.last_ability_time < 2.0:
            can_use_ability = False
        
        # Шанс использования способности
        use_chance = 0.2 * delta_time
        
        # Увеличиваем шанс в зависимости от интеллекта
        use_chance *= (0.5 + self.attributes["intelligence"] * 0.02)
        
        if can_use_ability and random.random() < use_chance:
            self._select_and_use_ability()
    
    def _select_and_use_ability(self):
        """Выбор и использование наиболее подходящей способности"""
        # Если здоровье низкое - попытка лечения
        if self.health < self.max_health * 0.3:
            healing_skills = [skill_id for skill_id, skill_data in self.skills.items() 
                             if "heal" in skill_data.get('tags', [])]
            if healing_skills:
                self.use_skill(random.choice(healing_skills))
                return
        
        # Если угроза высокая - защитные способности
        if self.ai_controller.threat_level > 15:
            defense_skills = [skill_id for skill_id, skill_data in self.skills.items() 
                             if "defense" in skill_data.get('tags', [])]
            if defense_skills:
                self.use_skill(random.choice(defense_skills))
                return
        
        # Если противник слаб - атакующие способности
        if self.ai_controller.threat_level < 5 and self.health > self.max_health * 0.7:
            buff_skills = [skill_id for skill_id, skill_data in self.skills.items() 
                          if "buff" in skill_data.get('tags', [])]
            if buff_skills:
                self.use_skill(random.choice(buff_skills))
                return
        
        # Стандартные атакующие способности
        attack_skills = [skill_id for skill_id, skill_data in self.skills.items() 
                        if "attack" in skill_data.get('tags', [])]
        if attack_skills:
            self.use_skill(random.choice(attack_skills))
    
    def take_damage(self, damage_report: dict):
        """Переопределение метода получения урона"""
        super().take_damage(damage_report)
        
        # Обновление эмоционального состояния при получении урона
        if self.health < self.max_health * 0.5:
            self.emotion = "AGGRESSIVE"
        if self.health < self.max_health * 0.3:
            self.emotion = "DESPERATE"
    
    def die(self):
        """Переопределение метода смерти"""
        super().die()
        
        # Генерация лута при смерти
        self._generate_loot()
    
    def _generate_loot(self):
        """Генерация лута при смерти врага"""
        # Базовые предметы
        loot = []
        
        # Всегда золото
        base_gold = random.randint(5, 20) * self.level
        gold_amount = self.calculate_gold_amount(base_gold)
        loot.append({"type": "currency", "amount": gold_amount})
        
        # Шанс выпадения предмета
        item_chance = 0.3 + self.attributes["luck"] * 0.01
        
        # Типы предметов в зависимости от типа врага
        item_types = {
            "warrior": ["weapon", "armor"],
            "archer": ["weapon", "ammo"],
            "mage": ["weapon", "scroll", "potion"],
            "assassin": ["weapon", "poison"],
            "berserker": ["weapon", "material"],
            "shaman": ["reagent", "totem"],
            "tank": ["armor", "shield"],
            "summoner": ["scroll", "reagent"]
        }
        
        if random.random() < item_chance:
            # Выбор типа предмета
            possible_types = item_types.get(self.enemy_type, ["weapon", "material"])
            item_type = random.choice(possible_types)
            
            # Создание предмета
            item = {
                "type": item_type,
                "quality": self.calculate_loot_quality(1.0),
                "value": random.randint(5, 50) * self.level
            }
            
            # Редкие предметы
            if random.random() < 0.1 * self.attributes["luck"] * 0.01:
                item["rarity"] = "RARE"
                item["value"] *= 3
            else:
                item["rarity"] = "COMMON"
            
            loot.append(item)
        
        return loot
    
    def to_dict(self):
        """Сериализация врага в словарь"""
        return {
            "id": self.id,
            "type": self.enemy_type,
            "level": self.level,
            "position": self.position,
            "health": self.health,
            "max_health": self.max_health,
            "attributes": self.attributes,
            "combat_stats": self.combat_stats,
            "effects": [effect.id for effect in self.active_effects.values()]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание врага из словаря"""
        enemy = cls(data["type"], data["level"], data["position"])
        enemy.id = data["id"]
        enemy.health = data["health"]
        enemy.max_health = data["max_health"]
        enemy.attributes = data["attributes"]
        enemy.combat_stats = data["combat_stats"]
        
        # Восстановление эффектов
        for effect_id in data.get("effects", []):
            if effect_id in enemy.effects_db:
                enemy.add_effect(effect_id, enemy.effects_db[effect_id])
        
        return enemy

# Генератор врагов для удобного создания
class EnemyGenerator:
    @staticmethod
    def generate_enemy(level: int, position: Tuple[float, float] = None):
        """Генерация случайного врага"""
        if not position:
            position = (random.randint(0, 1000), random.randint(0, 1000))
        
        enemy_type = random.choice(Enemy.ENEMY_TYPES)
        return Enemy(enemy_type, level, position)
    
    @staticmethod
    def generate_boss(level: int, position: Tuple[float, float] = None):
        """Генерация босса (формально враг, но с улучшенными характеристиками)"""
        if not position:
            position = (random.randint(0, 1000), random.randint(0, 1000))
        
        # Босс всегда уникального типа
        boss_types = ["dragon", "demon_lord", "lich_king", "titan"]
        boss_type = random.choice(boss_types)
        
        boss = Enemy(boss_type, level, position)
        
        # Улучшенные характеристики для босса
        for attr in boss.attributes:
            boss.attributes[attr] = int(boss.attributes[attr] * 1.5)
        
        boss.max_health *= 5
        boss.health = boss.max_health
        boss.combat_level = level * 2
        boss.damage_output *= 3
        boss.is_boss = True
        
        # Особые способности босса
        boss.skills.update({
            "boss_ability": {
                "name": "Гнев босса",
                "description": "Мощная атака босса",
                "damage": 50 + level * 10,
                "cooldown": 10.0,
                "mana_cost": 30,
                "tags": ["attack", "aoe", "boss"]
            }
        })
        
        # Особые эффекты босса
        boss.add_effect("boss_aura", {
            "tags": ["aura", "boss"],
            "modifiers": [
                {
                    "attribute": "physical_resist",
                    "value": 0.2,
                    "mode": "add"
                },
                {
                    "attribute": "all_damage_mod",
                    "value": 1.2,
                    "mode": "multiply"
                }
            ]
        })
        
        return boss