#!/usr/bin/env python3
"""ИИ агент для управления персонажем
Принимает решения на основе памяти, эмоций, экипировки и генетических факторов"""

import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time

class EmotionType(Enum):
    """Типы эмоций"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    EXCITED = "excited"
    CALM = "calm"
    STRESSED = "stressed"
    CONFIDENT = "confident"

class DecisionType(Enum):
    """Типы решений"""
    MOVE = "move"
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    EQUIP_ITEM = "equip_item"
    FLEE = "flee"
    EXPLORE = "explore"
    REST = "rest"

@dataclass
class Emotion:
    """Эмоция"""
    emotion_type: EmotionType
    intensity: float  # 0.0 - 1.0
    duration: float
    start_time: float
    source: str  # Источник эмоции

@dataclass
class Decision:
    """Решение ИИ"""
    decision_type: DecisionType
    priority: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    parameters: Dict[str, Any]
    reasoning: str

class AIAgent:
    """ИИ агент для управления персонажем"""
    
    def __init__(self, character):
        self.character = character
        self.emotions: List[Emotion] = []
        self.current_emotion = EmotionType.CALM
        self.personality_traits = self._generate_personality()
        self.decision_history: List[Decision] = []
        self.last_decision_time = time.time()
        self.decision_cooldown = 0.1  # Минимальное время между решениями
        
    def _generate_personality(self) -> Dict[str, float]:
        """Генерация личности на основе генетических факторов"""
        return {
            'aggression': random.uniform(0.1, 0.9),
            'caution': random.uniform(0.1, 0.9),
            'curiosity': random.uniform(0.1, 0.9),
            'social': random.uniform(0.1, 0.9),
            'intelligence': random.uniform(0.1, 0.9),
            'adaptability': random.uniform(0.1, 0.9)
        }
    
    def add_emotion(self, emotion_type: EmotionType, intensity: float, duration: float, source: str):
        """Добавление эмоции"""
        emotion = Emotion(
            emotion_type=emotion_type,
            intensity=intensity,
            duration=duration,
            start_time=time.time(),
            source=source
        )
        self.emotions.append(emotion)
        self._update_current_emotion()
    
    def _update_current_emotion(self):
        """Обновление текущей эмоции на основе всех активных эмоций"""
        if not self.emotions:
            self.current_emotion = EmotionType.CALM
            return
        
        # Удаляем истекшие эмоции
        current_time = time.time()
        self.emotions = [e for e in self.emotions if current_time - e.start_time < e.duration]
        
        if not self.emotions:
            self.current_emotion = EmotionType.CALM
            return
        
        # Определяем доминирующую эмоцию
        emotion_scores = {}
        for emotion in self.emotions:
            if emotion.emotion_type not in emotion_scores:
                emotion_scores[emotion.emotion_type] = 0
            emotion_scores[emotion.emotion_type] += emotion.intensity
        
        self.current_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """Получение текущего эмоционального состояния"""
        return {
            'current_emotion': self.current_emotion.value,
            'emotions': [e.emotion_type.value for e in self.emotions],
            'personality': self.personality_traits
        }
    
    def analyze_situation(self) -> Dict[str, Any]:
        """Анализ текущей ситуации"""
        # Получаем информацию о персонаже
        health_ratio = self.character.health / self.character.max_health
        mana_ratio = self.character.mana / self.character.max_mana
        stamina_ratio = self.character.stamina / self.character.max_stamina
        
        # Анализируем окружение
        enemies = self._get_nearby_enemies()
        items = self._get_nearby_items()
        threats = self._assess_threats()
        
        # Анализируем инвентарь
        inventory = self.character.get_inventory_contents()
        equipment = self.character.get_equipment()
        
        # Анализируем навыки
        skills = self.character.skill_system.get_entity_skills(self.character.entity_id)
        available_skills = [skill_id for skill_id, skill in skills.items() 
                          if self.character.mana >= skill.mana_cost and 
                          self.character.stamina >= skill.stamina_cost]
        
        return {
            'health_ratio': health_ratio,
            'mana_ratio': mana_ratio,
            'stamina_ratio': stamina_ratio,
            'enemies': enemies,
            'items': items,
            'threats': threats,
            'inventory': inventory,
            'equipment': equipment,
            'available_skills': available_skills,
            'emotional_state': self.get_emotional_state()
        }
    
    def _get_nearby_enemies(self) -> List[Dict[str, Any]]:
        """Получение информации о ближайших врагах"""
        # Это упрощенная реализация - в реальной игре нужно получать из game_manager
        return []
    
    def _get_nearby_items(self) -> List[Dict[str, Any]]:
        """Получение информации о ближайших предметах"""
        # Это упрощенная реализация
        return []
    
    def _assess_threats(self) -> Dict[str, float]:
        """Оценка угроз"""
        threats = {
            'health_low': 0.0,
            'enemies_nearby': 0.0,
            'resources_low': 0.0
        }
        
        # Оценка угрозы по здоровью
        if self.character.health / self.character.max_health < 0.3:
            threats['health_low'] = 1.0 - (self.character.health / self.character.max_health)
        
        # Оценка угрозы по ресурсам
        if self.character.mana / self.character.max_mana < 0.2:
            threats['resources_low'] += 0.5
        if self.character.stamina / self.character.max_stamina < 0.2:
            threats['resources_low'] += 0.5
        
        return threats
    
    def make_decision(self) -> Decision:
        """Принятие решения на основе анализа ситуации"""
        if time.time() - self.last_decision_time < self.decision_cooldown:
            return None
        
        situation = self.analyze_situation()
        decisions = self._generate_decisions(situation)
        
        if not decisions:
            return None
        
        # Выбираем лучшее решение
        best_decision = max(decisions, key=lambda d: d.priority * d.confidence)
        
        # Записываем решение в историю
        self.decision_history.append(best_decision)
        self.last_decision_time = time.time()
        
        return best_decision
    
    def _generate_decisions(self, situation: Dict[str, Any]) -> List[Decision]:
        """Генерация возможных решений"""
        decisions = []
        
        # Решение о лечении
        if situation['health_ratio'] < 0.5:
            heal_decision = Decision(
                decision_type=DecisionType.USE_ITEM,
                priority=0.9,
                confidence=0.8,
                parameters={'item_type': 'healing'},
                reasoning="Health is low, need to heal"
            )
            decisions.append(heal_decision)
        
        # Решение о восстановлении ресурсов
        if situation.get('threats', {}).get('resources_low', 0.0) > 0.5:
            restore_decision = Decision(
                decision_type=DecisionType.USE_ITEM,
                priority=0.7,
                confidence=0.6,
                parameters={'item_type': 'restoration'},
                reasoning="Resources are low, need to restore"
            )
            decisions.append(restore_decision)
        
        # Решение об атаке
        if situation['enemies'] and situation['health_ratio'] > 0.3:
            attack_decision = Decision(
                decision_type=DecisionType.ATTACK,
                priority=0.8,
                confidence=0.7,
                parameters={'target': 'nearest_enemy'},
                reasoning="Enemy detected, engaging in combat"
            )
            decisions.append(attack_decision)
        
        # Решение об использовании навыка
        if situation['available_skills'] and situation['mana_ratio'] > 0.4:
            skill_decision = Decision(
                decision_type=DecisionType.USE_SKILL,
                priority=0.6,
                confidence=0.5,
                parameters={'skill_id': situation['available_skills'][0]},
                reasoning="Skill available and resources sufficient"
            )
            decisions.append(skill_decision)
        
        # Решение о бегстве
        if situation['threats']['health_low'] > 0.8:
            flee_decision = Decision(
                decision_type=DecisionType.FLEE,
                priority=0.95,
                confidence=0.9,
                parameters={'direction': 'away_from_threat'},
                reasoning="Health critically low, fleeing for safety"
            )
            decisions.append(flee_decision)
        
        # Решение об исследовании
        if situation['items'] and situation['threats']['health_low'] < 0.3:
            explore_decision = Decision(
                decision_type=DecisionType.EXPLORE,
                priority=0.4,
                confidence=0.6,
                parameters={'target': 'nearest_item'},
                reasoning="Safe to explore for items"
            )
            decisions.append(explore_decision)
        
        return decisions
    
    def execute_decision(self, decision: Decision) -> bool:
        """Выполнение принятого решения"""
        if not decision:
            return False
        
        try:
            if decision.decision_type == DecisionType.USE_ITEM:
                return self._execute_use_item(decision.parameters)
            elif decision.decision_type == DecisionType.ATTACK:
                return self._execute_attack(decision.parameters)
            elif decision.decision_type == DecisionType.USE_SKILL:
                return self._execute_use_skill(decision.parameters)
            elif decision.decision_type == DecisionType.EQUIP_ITEM:
                return self._execute_equip_item(decision.parameters)
            elif decision.decision_type == DecisionType.FLEE:
                return self._execute_flee(decision.parameters)
            elif decision.decision_type == DecisionType.EXPLORE:
                return self._execute_explore(decision.parameters)
            elif decision.decision_type == DecisionType.MOVE:
                return self._execute_move(decision.parameters)
            elif decision.decision_type == DecisionType.REST:
                return self._execute_rest(decision.parameters)
            
        except Exception as e:
            print(f"Error executing decision: {e}")
            return False
        
        return True
    
    def _execute_use_item(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об использовании предмета"""
        item_type = parameters.get('item_type')
        
        # Ищем подходящий предмет в инвентаре
        inventory = self.character.get_inventory_contents()
        for item_data in inventory:
            item = item_data['item']
            slot_index = item_data.get('slot_index')
            if slot_index is None:
                continue
            if item_type == 'healing' and 'heal' in item.get('effects', []):
                return self.character.use_item_from_inventory(slot_index)
            elif item_type == 'restoration' and any(effect in item.get('effects', []) 
                                                   for effect in ['mana', 'stamina']):
                return self.character.use_item_from_inventory(slot_index)
        
        return False
    
    def _execute_attack(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об атаке"""
        # В упрощенной реализации просто атакуем ближайшего врага
        # В реальной игре нужно найти цель из game_manager
        return False
    
    def _execute_use_skill(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об использовании навыка"""
        skill_id = parameters.get('skill_id')
        if skill_id:
            return self.character.use_skill(skill_id)
        return False
    
    def _execute_equip_item(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об экипировке предмета"""
        item_id = parameters.get('item_id')
        if item_id:
            return self.character.equip_item(item_id)
        return False
    
    def _execute_flee(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения о бегстве"""
        direction = parameters.get('direction', 'away_from_threat')
        # В упрощенной реализации просто двигаемся в противоположном направлении
        if direction == 'away_from_threat':
            # Двигаемся в случайном направлении
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.character.move_by(dx, dy, 0, 0.016)
        return True
    
    def _execute_explore(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об исследовании"""
        target = parameters.get('target')
        if target == 'nearest_item':
            # Двигаемся к ближайшему предмету
            # В упрощенной реализации просто двигаемся случайно
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.character.move_by(dx, dy, 0, 0.016)
        return True
    
    def _execute_move(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения о движении"""
        dx = parameters.get('dx', 0)
        dy = parameters.get('dy', 0)
        self.character.move_by(dx, dy, 0, 0.016)
        return True
    
    def _execute_rest(self, parameters: Dict[str, Any]) -> bool:
        """Выполнение решения об отдыхе"""
        # В упрощенной реализации просто не двигаемся
        return True
    
    def update(self, dt: float):
        """Обновление ИИ агента"""
        # Обновляем эмоции
        self._update_current_emotion()
        
        # Принимаем решение
        decision = self.make_decision()
        if decision:
            self.execute_decision(decision)
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Получение статистики ИИ агента"""
        return {
            'personality': self.personality_traits,
            'current_emotion': self.current_emotion.value,
            'active_emotions': len(self.emotions),
            'decision_count': len(self.decision_history),
            'last_decision': self.decision_history[-1].decision_type.value if self.decision_history else None
        }
