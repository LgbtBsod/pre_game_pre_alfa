import random
import json
import os
import time
from typing import Tuple
from .entity import Entity, Attribute
from .effect import Effect
from ai.advanced_ai import AdvancedAIController

class Boss(Entity):
    # Общая память боссов
    shared_knowledge = {}
    GENETIC_PROFILES_PATH = "data/genetic_profiles.json"
    EFFECTS_PATH = "data/effects.json"
    ABILITIES_PATH = "data/abilities.json"
    BOSS_TYPES = ["dragon", "demon_lord", "lich_king", "titan", "behemoth", "leviathan"]
    
    def __init__(self, boss_type: str = None, level: int = 10, position: Tuple[float, float] = (0, 0)):
        # Определяем тип босса
        if not boss_type:
            boss_type = random.choice(self.BOSS_TYPES)
            
        super().__init__(f"{boss_type}_{random.randint(1000,9999)}", position)
        
        self.boss_type = boss_type
        self.level = level
        self.learning_rate = 0.005
        self.priority = 1
        self.is_boss = True
        self.title = f"Великий {boss_type.capitalize()}"
        self.phase = 1
        self.phase_transition_health = [0.7, 0.4, 0.2]  # Пороги здоровья для смены фаз
        self.special_attack_cooldown = 0.0
        self.last_phase_transition = 0
        
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
        
        # Установка фазовых эффектов
        self.apply_phase_effects()
    
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
                "strength": 1.6,
                "vitality": 1.5,
                "endurance": 1.4
            },
            "behemoth": {
                "strength": 1.5,
                "vitality": 1.6,
                "endurance": 1.3
            },
            "leviathan": {
                "strength": 1.4,
                "vitality": 1.5,
                "intelligence": 1.3
            }
        }
        
        # Бонус за уровень
        level_bonus = (self.level - 1) * 3
        
        # Устанавливаем атрибуты с использованием нового формата Attribute
        for attr in base_stats:
            # Базовое значение + бонус уровня
            value = base_stats[attr] + level_bonus
            
            # Применяем модификатор типа
            if self.boss_type in type_modifiers and attr in type_modifiers[self.boss_type]:
                value *= type_modifiers[self.boss_type][attr]
            
            # Используем новый формат Attribute
            self.attributes[attr] = Attribute(int(value))
        
        # Обновляем производные характеристики
        self.update_derived_stats()
        
        # Устанавливаем текущие ресурсы
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.mana = self.max_mana
        
        # Уникальные боевые характеристики для боссов
        self.combat_level = self.level * 2
        self.damage_output = self.attributes["strength"].value * 8
        self.combat_stats["critical_multiplier"] = 2.0
        self.combat_stats["defense"] = self.combat_stats.get("defense", 5) + 10
    
    def _load_genetic_profile(self):
        """Загрузка генетического профиля для босса"""
        if self.boss_type in self.genetic_profiles:
            self.genetic_profile = self.genetic_profiles[self.boss_type]
        else:
            # Дефолтный профиль для босса
            self.genetic_profile = {
                "BOSS_GENE": {
                    "immediate_effects": {"heal": 200},
                    "effects": {"health_regen": "1%/1"},
                    "emotion_modifier": {"emotion": "RAGE", "multiplier": 1.5}
                }
            }
    
    def _load_abilities(self):
        """Загрузка способностей для босса"""
        # Базовые способности
        self.skills = {
            "boss_attack": {
                "name": "Атака босса",
                "description": "Мощная базовая атака",
                "damage": 30 + self.level * 5,
                "cooldown": 3.0,
                "stamina_cost": 20,
                "tags": ["attack", "boss"]
            }
        }
        
        # Способности из конфига
        if self.boss_type in self.abilities_db:
            self.skills.update(self.abilities_db[self.boss_type])
        
        # Фазовые способности
        self.phase_abilities = {
            1: ["phase1_ability"],
            2: ["phase2_ability1", "phase2_ability2"],
            3: ["phase3_ability", "ultimate_ability"]
        }
        
        # Добавляем фазовые способности
        for phase, abilities in self.phase_abilities.items():
            for ability_id in abilities:
                if ability_id in self.abilities_db:
                    self.skills[ability_id] = self.abilities_db[ability_id]
    
    def _apply_initial_effects(self):
        """Применение начальных эффектов для босса"""
        # Общие эффекты для всех боссов
        self.add_effect("boss_presence", self.effects_db.get("boss_presence", {
            "tags": ["aura", "boss"],
            "modifiers": [
                {
                    "attribute": "physical_resist",
                    "value": 0.1,
                    "mode": "add"
                },
                {
                    "attribute": "movement_speed",
                    "value": 0.9,
                    "mode": "multiply"
                }
            ]
        }))
    
    def apply_phase_effects(self):
        """Применение эффектов текущей фазы"""
        # Удаляем эффекты предыдущих фаз
        for phase in [1, 2, 3]:
            if phase != self.phase:
                effect_id = f"boss_phase{phase}"
                if effect_id in self.active_effects:
                    self.remove_effect(effect_id)
        
        # Применяем эффекты текущей фазы
        phase_effect_id = f"boss_phase{self.phase}"
        if phase_effect_id in self.effects_db:
            self.add_effect(phase_effect_id, self.effects_db[phase_effect_id])
    
    def update(self, delta_time: float):
        """Обновление состояния босса"""
        if not self.alive:
            return
        
        # Обновление эффектов
        self.update_effects(delta_time)
        
        # Обновление ИИ контроллера
        self.ai_controller.update(delta_time)
        
        # Обновление таймеров
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown -= delta_time
        
        # Проверка смены фазы
        self.check_phase_transition()
        
        # Автоматическое использование способностей
        self._use_abilities(delta_time)
    
    def check_phase_transition(self):
        """Проверка условий для смены фазы боя"""
        current_time = time.time()
        health_percent = self.health / self.max_health
        
        # Проверяем, можно ли сменить фазу (не чаще чем раз в 10 секунд)
        if current_time - self.last_phase_transition < 10.0:
            return
        
        # Определяем, нужно ли переходить на следующую фазу
        if self.phase == 1 and health_percent <= self.phase_transition_health[0]:
            self.set_phase(2)
        elif self.phase == 2 and health_percent <= self.phase_transition_health[1]:
            self.set_phase(3)
        elif self.phase == 3 and health_percent <= self.phase_transition_health[2]:
            self.set_phase(4)
    
    def set_phase(self, new_phase: int):
        """Установка новой фазы боя"""
        if new_phase <= self.phase:
            return
            
        self.phase = new_phase
        self.last_phase_transition = time.time()
        print(f"{self.title} переходит в фазу {self.phase}!")
        
        # Применяем эффекты новой фазы
        self.apply_phase_effects()
        
        # Бонусы при переходе на новую фазу
        if new_phase == 2:
            self.attributes["strength"].value += 10
            self.attributes["vitality"].value += 15
            self.combat_stats["critical_chance"] += 0.1
            self.add_effect("phase2_power", self.effects_db.get("boss_phase2_power", {
                "tags": ["buff", "boss"],
                "modifiers": [
                    {
                        "attribute": "damage_output",
                        "value": 1.3,
                        "mode": "multiply"
                    }
                ],
                "duration": 30.0
            }))
        elif new_phase == 3:
            self.attributes["intelligence"].value += 15
            self.attributes["faith"].value += 10
            self.combat_stats["all_resist"] += 0.1
            self.add_effect("phase3_power", self.effects_db.get("boss_phase3_power", {
                "tags": ["buff", "boss"],
                "modifiers": [
                    {
                        "attribute": "elemental_damage_mod",
                        "value": 1.4,
                        "mode": "multiply"
                    },
                    {
                        "attribute": "mana_regen",
                        "value": "2%/1",
                        "mode": "add",
                        "interval": 1.0
                    }
                ]
            }))
        elif new_phase == 4:
            self.add_effect("final_stand", self.effects_db.get("boss_final_stand", {
                "tags": ["ultimate", "boss"],
                "modifiers": [
                    {
                        "attribute": "damage_output",
                        "value": 2.0,
                        "mode": "multiply"
                    },
                    {
                        "attribute": "attack_speed",
                        "value": 1.5,
                        "mode": "multiply"
                    },
                    {
                        "attribute": "health",
                        "value": "-1%/1",
                        "mode": "add",
                        "interval": 1.0
                    }
                ]
            }))
        
        # Обновляем характеристики после изменений
        self.update_derived_stats()
    
    def _use_abilities(self, delta_time: float):
        """Автоматическое использование способностей босса"""
        # Использование фазовых способностей
        phase_abilities = self.phase_abilities.get(self.phase, [])
        
        for ability_id in phase_abilities:
            if ability_id in self.skills:
                skill_data = self.skills[ability_id]
                
                # Проверка перезарядки
                current_time = time.time()
                last_used = self.skill_cooldowns.get(ability_id, 0)
                cooldown = skill_data.get("cooldown", 10.0)
                
                if current_time - last_used >= cooldown:
                    # Шанс использования способности
                    use_chance = 0.3 * delta_time
                    
                    # Увеличиваем шанс в зависимости от фазы
                    use_chance *= (self.phase * 0.5)
                    
                    if random.random() < use_chance:
                        # Используем способность (упрощенная логика)
                        self.use_skill(ability_id)
                        self.skill_cooldowns[ability_id] = current_time
                        return

    def use_skill(self, ability_id: str):
        """Применение способности босса (упрощенная версия).
        Сейчас просто выводит действие и может накладывать эффект на себя/цель.
        """
        if ability_id not in self.skills:
            return
        skill_data = self.skills[ability_id]
        # Если у босса есть ссылка на игрока, нанесем урон
        target = getattr(self, "player_ref", None)
        if target and getattr(target, "alive", False):
            damage = float(skill_data.get("damage", 0))
            if damage > 0:
                target.take_damage({
                    "total": damage,
                    "boss": damage,
                    "source": self,
                })
        # Наложение эффектов из способности (если есть)
        effect_id = skill_data.get("apply_effect")
        if effect_id and effect_id in self.effects_db:
            self.add_effect(effect_id, self.effects_db[effect_id])
    
    def take_damage(self, damage_report: dict):
        """Переопределение метода получения урона"""
        super().take_damage(damage_report)
        
        # Босс становится агрессивнее при потере здоровья
        health_percent = self.health / self.max_health
        
        if health_percent < 0.7 and self.phase == 1:
            self.emotion = "AGGRESSIVE"
        elif health_percent < 0.4 and self.phase == 2:
            self.emotion = "ENRAGED"
        elif health_percent < 0.2:
            self.emotion = "DESPERATE"
    
    def die(self):
        """Переопределение метода смерти босса"""
        super().die()
        print(f"{self.title} повержен!")
        
        # Генерация награды за победу над боссом
        self._generate_reward()
    
    def _generate_reward(self):
        """Генерация награды за победу над боссом"""
        # Большое количество золота
        base_gold = random.randint(100, 500) * self.level
        gold_amount = self.calculate_gold_amount(base_gold)
        
        # Несколько высококачественных предметов
        num_items = 3 + int(self.attributes["luck"] * 0.1)
        items = []
        
        for _ in range(num_items):
            item_quality = self.calculate_loot_quality(1.0 + self.level * 0.1)
            
            # 50% шанс на редкий предмет
            if random.random() < 0.5:
                rarity = "RARE"
            else:
                # 10% шанс на легендарный предмет
                if random.random() < 0.1 * self.attributes["luck"] * 0.01:
                    rarity = "LEGENDARY"
                else:
                    rarity = "EPIC"
            
            items.append({
                "quality": item_quality,
                "rarity": rarity,
                "value": random.randint(50, 200) * self.level
            })
        
        return {
            "gold": gold_amount,
            "items": items,
            "experience": self.level * 500
        }

    def calculate_gold_amount(self, base_gold: int) -> int:
        """Расчет итогового количества золота (простая формула)."""
        bonus = 1.0 + min(1.0, self.level * 0.05)
        return int(base_gold * bonus)

    def calculate_loot_quality(self, base_quality: float) -> float:
        """Расчет качества добычи (простая формула)."""
        return round(base_quality * (1.0 + self.level * 0.02), 2)
    
    def player_died(self):
        """Усиление босса после смерти игрока"""
        self.level += 1
        self.title = f"{self.title} (Усиленный)"
        
        # Улучшение характеристик
        for attr in self.attributes:
            self.attributes[attr].value = int(self.attributes[attr].value * 1.2)
        
        # Улучшение здоровья и урона
        self.combat_stats["max_health"] = int(self.combat_stats["max_health"] * 1.3)
        self.health = self.max_health
        self.combat_stats["damage_output"] *= 1.25
        
        # Добавление нового навыка
        new_ability_id = f"enhanced_{self.boss_type}_ability"
        if new_ability_id in self.abilities_db:
            self.skills[new_ability_id] = self.abilities_db[new_ability_id]
        
        # Обновление характеристик
        self.update_derived_stats()
        
        print(f"{self.title} достигает уровня {self.level} после смерти игрока!")

# Генератор боссов
class BossGenerator:
    @staticmethod
    def generate_boss(level: int = 10, position: Tuple[float, float] = None):
        """Создание случайного босса"""
        if not position:
            position = (random.randint(0, 1000), random.randint(0, 1000))
        
        boss_type = random.choice(Boss.BOSS_TYPES)
        return Boss(boss_type, level, position)
    
    @staticmethod
    def generate_area_boss(area_level: int, area_type: str):
        """Создание босса для конкретной области"""
        # Подбор типа босса в зависимости от типа области
        type_mapping = {
            "dungeon": ["lich_king", "demon_lord"],
            "forest": ["dragon", "behemoth"],
            "mountain": ["titan", "dragon"],
            "ocean": ["leviathan", "kraken"],
            "desert": ["phoenix", "sphinx"]
        }
        
        # Выбираем тип босса
        if area_type in type_mapping:
            boss_type = random.choice(type_mapping[area_type])
        else:
            boss_type = random.choice(Boss.BOSS_TYPES)
        
        # Уровень босса на основе уровня области
        boss_level = max(10, area_level + 2)
        
        # Позиция босса (центр области)
        position = (500, 500)  # В реальной игре будет зависеть от области
        
        # Создаем босса
        boss = Boss(boss_type, boss_level, position)
        
        # Настройка уникальных характеристик для босса области
        boss.title = f"Страж {area_type.capitalize()}"
        boss.combat_stats["movement_speed"] *= 0.8  # Боссы области медленнее
        boss.combat_stats["all_resist"] += 0.1  # Дополнительное сопротивление
        
        # Добавляем область-специфичные способности
        area_ability = f"{area_type}_boss_ability"
        if area_ability in boss.abilities_db:
            boss.skills[area_ability] = boss.abilities_db[area_ability]
        
        return boss