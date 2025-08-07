import random
import json
import os
import time
from .behavior_tree import BehaviorTree, generate_tree_for_personality
from .memory import AIMemory, LearningController
from .cooperation import AICoordinator, GroupTactics
from .emotion_genetics import EmotionGeneticSynthesizer

class AdvancedAIController:
    # Уровни приоритета для оптимизации
    ENTITY_PRIORITY = {
        "PLAYER": 0,
        "BOSS": 1,
        "MINIBOSS": 2,
        "ELITE": 3,
        "NORMAL": 4
    }
    
    GENETIC_PROFILES_PATH = "data/genetic_profiles.json"
    ABILITIES_PATH = "data/abilities.json"
    EFFECTS_PATH = "data/effects.json"
    
    def __init__(self, entity):
        self.entity = entity
        self.memory = AIMemory()
        self.learning = LearningController(entity)
        self.coordinator = AICoordinator()
        self.personality = self._generate_personality()
        self.behavior_tree = self._create_behavior_tree()
        self.threat_level = 0
        self.current_strategy = "EXPLORE"
        self.last_update_time = time.time()
        self.decision_priority = [
            "SURVIVAL", 
            "GROUP_ORDER", 
            "PERSONAL_GOAL"
        ]
        
        # Загрузка внешних данных
        self.genetic_profiles = self._load_data(self.GENETIC_PROFILES_PATH)
        self.abilities = self._load_data(self.ABILITIES_PATH)
        self.effects = self._load_data(self.EFFECTS_PATH)
        
        # Инициализация подсистем
        self.emotion_genetics = EmotionGeneticSynthesizer(
            self.entity, 
            self.genetic_profiles,
            self.abilities,
            self.effects
        )
    
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
    
    def _create_behavior_tree(self):
        return BehaviorTree(generate_tree_for_personality(self.personality))
    
    def _generate_personality(self):
        """Генерация личности на основе характеристик сущности"""
        aggression = 0.5
        caution = 0.5
        intelligence = 0.5
        loyalty = random.uniform(0.2, 0.95)
        
        # Настройка агрессии
        if hasattr(self.entity, 'damage_output'):
            aggression = min(0.9, max(0.3, self.entity.damage_output / 100))
        
        # Настройка осторожности
        if hasattr(self.entity, 'max_health') and self.entity.max_health > 0:
            health_percent = self.entity.health / self.entity.max_health
            caution = min(0.9, max(0.1, 1.0 - health_percent))
        
        # Настройка интеллекта
        if hasattr(self.entity, 'skills'):
            intelligence = min(1.0, max(0.4, self.entity.skills.get('magic', 0.5)))
        
        # Учет эффектов
        if self.entity.has_effect_tag("berserk"):
            aggression = min(0.95, aggression + 0.3)
            caution = max(0.05, caution - 0.2)
        
        if self.entity.has_effect_tag("fear"):
            aggression = max(0.1, aggression - 0.2)
            caution = min(0.95, caution + 0.3)
        
        return {
            "aggression": aggression,
            "caution": caution,
            "intelligence": intelligence,
            "loyalty": loyalty
        }
    
    def _determine_update_mode(self):
        """Определение режима обновления для оптимизации"""
        # Определяем тип сущности по приоритету
        entity_type = "NORMAL"
        if self.entity.is_player:
            entity_type = "PLAYER"
        elif self.entity.is_boss:
            entity_type = "BOSS"
        elif self.entity.priority <= 2:
            entity_type = "MINIBOSS"
        elif self.entity.priority <= 3:
            entity_type = "ELITE"
        
        # Режимы обновления в зависимости от типа и расстояния
        if entity_type in ["PLAYER", "BOSS"]:
            return "FULL"
        
        if hasattr(self.entity, 'distance_to_player') and self.entity.distance_to_player < 1000:
            if entity_type in ["MINIBOSS", "ELITE"]:
                return "FULL"
            return "LIGHT"
        
        return "MINIMAL"
    
    def update(self, delta_time: float):
        current_time = time.time()
        time_since_last_update = current_time - self.last_update_time
        
        # Режимы обновления для оптимизации
        update_mode = self._determine_update_mode()
        
        if update_mode == "FULL":
            self._full_update(time_since_last_update, current_time)
        elif update_mode == "LIGHT":
            self._light_update(time_since_last_update, current_time)
        elif update_mode == "MINIMAL":
            self._minimal_update(time_since_last_update, current_time)
        
        self.last_update_time = current_time
    
    def light_update(self, delta_time: float):
        self._light_update(delta_time, time.time())
    
    def minimal_update(self, delta_time: float):
        self._minimal_update(delta_time, time.time())
    
    def _full_update(self, delta_time: float, current_time: float):
        """Полное обновление ИИ (для важных сущностей)"""
        # Обновление сенсоров и оценки угроз
        self._update_threat_level()
        
        # Обновление памяти и обучения
        self.memory.record_event("AI_UPDATE", {"time": current_time})
        self.learning.update(delta_time)
        
        # Кооперативное поведение (без вызова сложных действий — сущности не реализуют эти методы)
        if hasattr(self.entity, 'group_id'):
            self.coordinator.register_entity(self.entity, self.entity.group_id)
        
        # Обновление эмоционально-генетической системы
        self.emotion_genetics.update(delta_time)
        
        # Пересборка дерева поведения при изменении личности
        if random.random() < 0.1:
            self.behavior_tree = self._create_behavior_tree()
        
        # Выполнение поведения
        behavior_status = self.behavior_tree.execute(self.entity)
        
        # Запись результата поведения
        self.memory.record_event("BEHAVIOR_EXECUTION", {
            "status": behavior_status.name,
            "strategy": self.current_strategy
        })
        
        # Адаптация на основе опыта
        self._adapt_based_on_experience()
        
        # Тактическое использование способностей
        self._use_tactical_abilities(delta_time)
    
    def _light_update(self, delta_time: float, current_time: float):
        """Облегченное обновление ИИ"""
        self._update_threat_level()
        self.emotion_genetics.update(delta_time)
        
        # Упрощенное выполнение поведения
        self.behavior_tree.execute(self.entity)
        
        # Проверка необходимости лечения
        if self.entity.health < self.entity.max_health * 0.4:
            self._healing_behavior()
    
    def _minimal_update(self, delta_time: float, current_time: float):
        """Минимальное обновление ИИ"""
        if self.entity.health < 0.3:
            self._healing_behavior()
        elif random.random() < 0.05:
            self._random_movement()
    
    def _should_follow_group_order(self) -> bool:
        """Следует ли выполнять групповые приказы"""
        if "GROUP_ORDER" not in self.decision_priority:
            return False
        
        # Интеллект влияет на дисциплину
        if random.random() > self.personality["intelligence"] * 0.7:
            return False
        
        # Эффекты могут влиять на лояльность
        if self.entity.has_effect_tag("disobedience"):
            return False
        
        return True
    
    def _update_threat_level(self):
        """Обновление уровня угрозы"""
        self.threat_level = 0
        
        if not hasattr(self.entity, 'get_nearby_entities'):
            return
        
        nearby_enemies = self.entity.get_nearby_entities(radius=15.0, enemy_only=True)
        
        for enemy in nearby_enemies:
            # Базовый уровень угрозы
            threat_score = enemy.combat_level * (1.0 + enemy.damage_output / 100)
            
            # Модификаторы эмоций
            if enemy.emotion == "RAGE":
                threat_score *= 1.5
            elif enemy.emotion == "CONFIDENCE":
                threat_score *= 1.2
            elif enemy.emotion == "FEAR":
                threat_score *= 0.8
            
            # Учет эффектов
            if enemy.has_effect_tag("stealth"):
                threat_score *= 0.5
            if enemy.has_effect_tag("taunt"):
                threat_score *= 1.8
            
            self.threat_level += threat_score
        
        # Запись в память
        self.memory.record_event("THREAT_ASSESSMENT", {
            "level": self.threat_level, 
            "enemies": len(nearby_enemies),
            "position": tuple(self.entity.position)
        })
    
    def _adapt_based_on_experience(self):
        """Адаптация поведения на основе накопленного опыта"""
        # Уменьшение агрессии после неудач
        if self.memory.count_failures("ATTACK") > 3:
            self.personality["aggression"] = max(0.1, self.personality["aggression"] - 0.15)
            self.memory.record_event("PERSONALITY_CHANGE", {
                "trait": "aggression",
                "change": -0.15,
                "reason": "repeated_failures"
            })
        
        # Увеличение агрессии после успехов
        if self.memory.count_successes("ATTACK") > 5:
            self.personality["aggression"] = min(0.9, self.personality["aggression"] + 0.1)
            self.memory.record_event("PERSONALITY_CHANGE", {
                "trait": "aggression",
                "change": +0.1,
                "reason": "successful_attacks"
            })
        
        # Увеличение осторожности при низком здоровье
        if self.entity.health < 0.4:
            self.personality["caution"] = min(0.9, self.personality["caution"] + 0.2)
            self.memory.record_event("PERSONALITY_CHANGE", {
                "trait": "caution",
                "change": +0.2,
                "reason": "low_health"
            })
        
        # Пересборка дерева поведения при значительных изменениях
        if random.random() < 0.3:
            self.behavior_tree = self._create_behavior_tree()
    
    def _healing_behavior(self):
        """Поведение при лечении"""
        if self.entity.inventory.has_consumable("HEAL"):
            self.entity.use_item("HEAL")
        elif self.entity.has_ability("SELF_HEAL"):
            self.entity.use_ability("SELF_HEAL")
        elif hasattr(self.entity, 'ai_controller'):
            # Запрос помощи у союзников
            self.coordinator.request_help(self.entity, "HEALING")
    
    def _random_movement(self):
        """Случайное перемещение"""
        random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.entity.move_in_direction(random_direction)
    
    def _use_tactical_abilities(self, delta_time: float):
        """Тактическое использование способностей"""
        if not hasattr(self.entity, 'skills') or not self.entity.skills:
            return
        
        # Вероятность использования способности
        use_chance = 0.2 * delta_time
        
        # Увеличение шанса в зависимости от интеллекта
        use_chance *= (0.5 + self.personality["intelligence"])
        
        if random.random() < use_chance:
            self._select_and_use_ability()
    
    def _select_and_use_ability(self):
        """Выбор и использование наиболее подходящей способности"""
        # Приоритет 1: Лечение при низком здоровье
        if self.entity.health < self.entity.max_health * 0.4:
            healing_skills = self._find_skills_by_tags(["heal", "restore", "regeneration"])
            if healing_skills:
                self.entity.use_skill(random.choice(healing_skills))
                return
        
        # Приоритет 2: Защита при высокой угрозе
        if self.threat_level > 15:
            defense_skills = self._find_skills_by_tags(["defense", "shield", "barrier", "evasion"])
            if defense_skills:
                self.entity.use_skill(random.choice(defense_skills))
                return
        
        # Приоритет 3: Усиление перед атакой
        if self.threat_level < 5 and self.entity.health > self.entity.max_health * 0.7:
            buff_skills = self._find_skills_by_tags(["buff", "enhance", "damage_boost"])
            if buff_skills:
                self.entity.use_skill(random.choice(buff_skills))
                return
        
        # Приоритет 4: Атакующие способности
        attack_skills = self._find_skills_by_tags(["attack", "damage", "aoe"])
        if attack_skills:
            self.entity.use_skill(random.choice(attack_skills))
            return
    
    def _find_skills_by_tags(self, tags: list) -> list:
        """Найти способности по тегам"""
        valid_skills = []
        
        for skill_id, skill_data in self.entity.skills.items():
            skill_tags = skill_data.get('tags', [])
            ability_tags = self.abilities.get(skill_id, {}).get('tags', [])
            all_tags = set(skill_tags + ability_tags)
            
            if any(tag in all_tags for tag in tags):
                # Проверка доступности
                if self._is_skill_available(skill_id, skill_data):
                    valid_skills.append(skill_id)
        
        return valid_skills
    
    def _is_skill_available(self, skill_id: str, skill_data: dict) -> bool:
        """Доступна ли способность для использования"""
        # Проверка ресурсов
        if self.entity.mana < skill_data.get('mana_cost', 0):
            return False
        
        if self.entity.stamina < skill_data.get('stamina_cost', 0):
            return False
        
        # Проверка перезарядки
        current_time = time.time()
        last_used = self.entity.skill_cooldowns.get(skill_id, 0)
        cooldown = skill_data.get('cooldown', 0)
        
        if current_time - last_used < cooldown:
            return False
        
        # Проверка специальных условий
        if "requires_target" in skill_data.get('conditions', []) and not self.entity.target:
            return False
        
        return True