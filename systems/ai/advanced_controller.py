from .behavior_tree import BehaviorTree, generate_tree_for_personality
from .memory import AIMemory, LearningController
from .cooperation import AICoordinator, GroupTactics
from .emotion_genetics import EmotionGeneticSynthesizer
import random

class AdvancedAIController:
    def __init__(self, entity):
        self.entity = entity
        self.memory = AIMemory()
        self.learning = LearningController(entity)
        self.coordinator = AICoordinator()
        self.emotion_genetics = EmotionGeneticSynthesizer(entity)
        self.behavior_tree = self._create_behavior_tree()
        self.personality = self._generate_personality()
        self.threat_level = 0
        self.current_strategy = "EXPLORE"
        self.last_update_time = 0
        self.decision_priority = [
            "SURVIVAL", 
            "GROUP_ORDER", 
            "PERSONAL_GOAL"
        ]
    
    def _create_behavior_tree(self):
        return BehaviorTree(generate_tree_for_personality(self.personality))
    
    def _generate_personality(self):
        return {
            "aggression": random.uniform(0.3, 0.9),
            "caution": random.uniform(0.1, 0.7),
            "intelligence": random.uniform(0.4, 1.0),
            "loyalty": random.uniform(0.2, 0.95)
        }
    
    def update(self, delta_time):
        current_time = self.last_update_time + delta_time
        
        # Режимы обновления для оптимизации
        update_mode = self._determine_update_mode()
        
        if update_mode == "FULL":
            self._full_update(delta_time, current_time)
        elif update_mode == "LIGHT":
            self._light_update(delta_time, current_time)
        elif update_mode == "MINIMAL":
            self._minimal_update(delta_time, current_time)
        
        self.last_update_time = current_time
    
    def light_update(self, delta_time):
        self._light_update(delta_time, self.last_update_time + delta_time)
    
    def minimal_update(self, delta_time):
        self._minimal_update(delta_time, self.last_update_time + delta_time)
    
    def _determine_update_mode(self):
        if self.entity.is_player or self.entity.is_boss:
            return "FULL"
        
        if self.entity.distance_to_player < 1000:  # В поле зрения
            return "LIGHT"
        
        return "MINIMAL"  # Далеко от игрока
    
    def _full_update(self, delta_time, current_time):
        # Обновление сенсоров
        self._update_threat_level()
        
        # Обновление памяти и обучения
        self.memory.record_event("AI_UPDATE", {"time": current_time})
        self.learning.update(delta_time)
        
        # Кооперативное поведение
        if hasattr(self.entity, 'group_id'):
            self.coordinator.register_entity(self.entity, self.entity.group_id)
            group_action = self.coordinator.get_group_action(self.entity)
            if self._should_follow_group_order():
                GroupTactics.execute_action(group_action, self.entity)
        
        # Обновление эмоционально-генетической системы
        self.emotion_genetics.update(delta_time)
        
        # Выполнение поведения
        self.behavior_tree.execute(self.entity)
        
        # Адаптация на основе опыта
        self._adapt_based_on_experience()
    
    def _should_follow_group_order(self):
        if "GROUP_ORDER" not in self.decision_priority:
            return False
        
        # Интеллект влияет на дисциплину
        if random.random() > self.personality["intelligence"] * 0.7:
            return False
        
        return True
    
    def _light_update(self, delta_time, current_time):
        self._update_threat_level()
        self.emotion_genetics.update(delta_time)
        self.behavior_tree.execute(self.entity)
    
    def _minimal_update(self, delta_time, current_time):
        if self.entity.health < 0.3:
            self._healing_behavior()
        elif random.random() < 0.05:
            self._random_movement()
    
    def _update_threat_level(self):
        self.threat_level = 0
        nearby_enemies = self.entity.get_nearby_entities(radius=15.0, enemy_only=True)
        
        for enemy in nearby_enemies:
            threat_score = enemy.combat_level * (1.0 + enemy.damage_output / 100)
            
            if enemy.emotion == "RAGE":
                threat_score *= 1.5
            elif enemy.emotion == "CONFIDENCE":
                threat_score *= 1.2
            
            self.threat_level += threat_score
        
        self.memory.record_event("THREAT_ASSESSMENT", {
            "level": self.threat_level, 
            "enemies": len(nearby_enemies)
        })
    
    def _adapt_based_on_experience(self):
        # Уменьшение агрессии после неудач
        if self.memory.count_failures("ATTACK") > 3:
            self.personality["aggression"] = max(0.1, self.personality["aggression"] - 0.15)
        
        # Увеличение агрессии после успехов
        if self.memory.count_successes("ATTACK") > 5:
            self.personality["aggression"] = min(0.9, self.personality["aggression"] + 0.1)
        
        # Увеличение осторожности при низком здоровье
        if self.entity.health < 0.4:
            self.personality["caution"] = min(0.9, self.personality["caution"] + 0.2)
        
        # Пересборка дерева поведения при изменении личности
        self.behavior_tree = self._create_behavior_tree()
    
    def _healing_behavior(self):
        if self.entity.inventory.has_consumable("HEAL"):
            self.entity.use_item("HEAL")
        elif self.entity.has_ability("SELF_HEAL"):
            self.entity.use_ability("SELF_HEAL")
    
    def _random_movement(self):
        random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.entity.move_in_direction(random_direction)