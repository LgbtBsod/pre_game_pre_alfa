#!/usr/bin/env python3
"""
AI Integration System - Система интеграции AI агентов с геномом, эмоциями и скиллами
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem
from .ai_system import AISystem, EmotionType, PersonalityType
from .ai_entity import AIEntity, EntityType, MemoryType
from ..genome.genome_system import Genome, genome_manager
from ..emotion.emotion_system import EmotionSystem, emotion_manager
from ..skills.skill_system import Skill, SkillTree, SkillType
from ..content.content_database import ContentDatabase, ContentType
from ..combat.combat_system import CombatSystem
from ..entity.entity_stats_system import EntityStats, StatType, EntityType as GameEntityType
from ..items.item_system import BaseItem, Weapon, Armor, Accessory
from ..inventory.inventory_system import InventorySystem

logger = logging.getLogger(__name__)

@dataclass
class AIAgentState:
    """Состояние AI агента"""
    entity_id: str
    current_emotion: EmotionType
    emotion_intensity: float
    personality: PersonalityType
    genome: Genome
    skill_tree: SkillTree
    current_health: float
    max_health: float
    current_mana: float
    max_mana: float
    level: int
    experience: float
    position: tuple
    target: Optional[str] = None
    last_action: Optional[str] = None
    action_cooldown: float = 0.0
    inventory_items: List[str] = field(default_factory=list)  # UUID предметов в инвентаре
    equipped_items: Dict[str, str] = field(default_factory=dict)  # Слот -> UUID предмета
    available_skills: List[str] = field(default_factory=list)  # UUID доступных скиллов
    learning_progress: Dict[str, float] = field(default_factory=dict)  # Прогресс обучения по навыкам

class AIIntegrationSystem:
    """Система интеграции AI агентов с игровыми системами"""
    
    def __init__(self, event_system=None, ai_system: AISystem = None, combat_system: CombatSystem = None, 
                 content_db: ContentDatabase = None, inventory_system = None):
        self.event_system = event_system
        self.ai_system = ai_system
        self.combat_system = combat_system
        self.content_db = content_db
        self.inventory_system = inventory_system
        
        # Зарегистрированные AI агенты
        self.ai_agents: Dict[str, AIAgentState] = {}
        
        # Системы характеристик для сущностей
        self.entity_stats: Dict[str, EntityStats] = {}
        
        # Подписка на события
        if self.event_system:
            self._subscribe_to_events()
        
        logger.info("AI Integration System инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы"""
        try:
            # Проверяем доступность зависимостей
            if not self.event_system:
                logger.warning("EventSystem недоступен, некоторые функции будут ограничены")
            
            if not self.ai_system:
                logger.warning("AISystem недоступен, некоторые функции будут ограничены")
            
            if not self.combat_system:
                logger.warning("CombatSystem недоступен, некоторые функции будут ограничены")
            
            if not self.content_db:
                logger.warning("ContentDatabase недоступен, некоторые функции будут ограничены")
            
            if not self.inventory_system:
                logger.warning("InventorySystem недоступен, некоторые функции будут ограничены")
            
            logger.info("AI Integration System успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации AI Integration System: {e}")
            return False
    
    def update(self, delta_time: float):
        """Обновление системы"""
        try:
            # Обновляем AI агентов
            for entity_id, agent_state in self.ai_agents.items():
                self.update_ai_agent(entity_id, delta_time)
            
            # Обновляем характеристики сущностей
            for entity_id, stats in self.entity_stats.items():
                stats.update(delta_time)
                
        except Exception as e:
            logger.error(f"Ошибка обновления AI Integration System: {e}")
    
    def cleanup(self):
        """Очистка системы"""
        try:
            # Очищаем AI агентов
            self.ai_agents.clear()
            
            # Очищаем характеристики сущностей
            self.entity_stats.clear()
            
            logger.info("AI Integration System очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки AI Integration System: {e}")
    
    def _subscribe_to_events(self):
        """Подписка на игровые события"""
        self.event_system.subscribe("entity_damaged", self._on_entity_damaged)
        self.event_system.subscribe("entity_healed", self._on_entity_healed)
        self.event_system.subscribe("item_acquired", self._on_item_acquired)
        self.event_system.subscribe("skill_learned", self._on_skill_learned)
        self.event_system.subscribe("level_up", self._on_level_up)
        self.event_system.subscribe("combat_started", self._on_combat_started)
        self.event_system.subscribe("combat_ended", self._on_combat_ended)
    
    def register_ai_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Регистрация AI сущности в системе интеграции"""
        try:
            # Создаем AI Entity
            ai_entity = AIEntity(entity_id, EntityType.PLAYER if entity_data.get('type') == 'player' else EntityType.ENEMY)
            
            # Создаем систему характеристик
            entity_type = GameEntityType.PLAYER if entity_data.get('type') == 'player' else GameEntityType.ENEMY
            if entity_data.get('type') == 'boss':
                entity_type = GameEntityType.BOSS
            
            stats = EntityStats(
                entity_id=entity_id,
                entity_type=entity_type,
                level=entity_data.get('level', 1),
                experience=entity_data.get('experience', 0)
            )
            
            # Применяем базовые характеристики из entity_data
            if 'stats' in entity_data:
                for stat_name, stat_value in entity_data['stats'].items():
                    if hasattr(stats.base_stats, stat_name):
                        setattr(stats.base_stats, stat_name, stat_value)
                
                # Пересчитываем производные характеристики
                stats._calculate_derived_stats()
                stats._update_current_values()
            
            # Создаем состояние AI агента
            ai_state = AIAgentState(
                entity_id=entity_id,
                current_emotion=EmotionType.NEUTRAL,
                emotion_intensity=0.5,
                personality=PersonalityType.BALANCED,
                genome=entity_data.get('genome', genome_manager.create_genome(entity_id)),
                skill_tree=entity_data.get('skill_tree', SkillTree(entity_id)),
                current_health=stats.current_health,
                max_health=stats.base_stats.health,
                current_mana=stats.current_mana,
                max_mana=stats.base_stats.mana,
                level=stats.level,
                experience=stats.experience,
                position=entity_data.get('position', (0, 0, 0)),
                inventory_items=entity_data.get('inventory', []),
                equipped_items=entity_data.get('equipment', {}),
                available_skills=entity_data.get('skills', [])
            )
            
            # Регистрируем в системах
            self.ai_agents[entity_id] = ai_state
            self.entity_stats[entity_id] = stats
            
            # Регистрируем в AI системе
            self.ai_system.register_entity(entity_id, {
                'type': entity_data.get('type', 'npc'),
                'personality': ai_state.personality.value,
                'learning_rate': ai_entity.learning_rate,
                'memory_capacity': ai_entity.memory_capacity
            })
            
            # Регистрируем в системе боя
            self.combat_system.register_entity(entity_id, {
                'attack': stats.get_stat_value(StatType.ATTACK),
                'defense': stats.get_stat_value(StatType.DEFENSE),
                'health': stats.current_health,
                'max_health': stats.base_stats.health
            })
            
            logger.info(f"AI сущность {entity_id} зарегистрирована в системе интеграции")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации AI сущности {entity_id}: {e}")
            return False
    
    def update_ai_agent(self, entity_id: str, delta_time: float):
        """Обновление AI агента"""
        if entity_id not in self.ai_agents:
            return
        
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        try:
            # Обновляем характеристики
            stats.update(delta_time)
            
            # Обновляем состояние AI агента
            ai_state.current_health = stats.current_health
            ai_state.current_mana = stats.current_mana
            ai_state.level = stats.level
            ai_state.experience = stats.experience
            
            # Обновляем эмоции на основе состояния
            self._update_entity_emotions(entity_id, delta_time)
            
            # Принимаем решения
            self._make_entity_decision(entity_id, delta_time)
            
            # Обновляем AI Entity
            if hasattr(self.ai_system, 'update_entity'):
                self.ai_system.update_entity(entity_id, {
                    'health_percentage': stats.get_health_percentage(),
                    'mana_percentage': stats.get_mana_percentage(),
                    'level': stats.level,
                    'experience': stats.experience,
                    'position': ai_state.position,
                    'target': ai_state.target
                }, delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI агента {entity_id}: {e}")
    
    def _update_entity_emotions(self, entity_id: str, delta_time: float):
        """Обновление эмоций сущности на основе состояния"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        # Эмоции на основе здоровья
        health_percentage = stats.get_health_percentage()
        if health_percentage < 20:
            ai_state.current_emotion = EmotionType.FEAR
            ai_state.emotion_intensity = 0.9
        elif health_percentage < 50:
            ai_state.current_emotion = EmotionType.ANXIETY
            ai_state.emotion_intensity = 0.7
        elif health_percentage > 80:
            ai_state.current_emotion = EmotionType.CONFIDENCE
            ai_state.emotion_intensity = 0.6
        
        # Эмоции на основе маны
        mana_percentage = stats.get_mana_percentage()
        if mana_percentage < 30:
            ai_state.current_emotion = EmotionType.FRUSTRATION
            ai_state.emotion_intensity = 0.5
        
        # Эмоции на основе опыта
        if stats.available_stat_points > 0:
            ai_state.current_emotion = EmotionType.EXCITEMENT
            ai_state.emotion_intensity = 0.4
    
    def _make_entity_decision(self, entity_id: str, delta_time: float):
        """Принятие решений AI сущностью"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        # Проверяем кулдаун действий
        if ai_state.action_cooldown > 0:
            ai_state.action_cooldown -= delta_time
            return
        
        # Анализируем ситуацию
        situation = self._analyze_situation(entity_id)
        
        # Принимаем решение на основе ситуации
        decision = self._evaluate_options(entity_id, situation)
        
        # Выполняем решение
        if decision:
            self._execute_decision(entity_id, decision)
            ai_state.last_action = decision['action_type']
            ai_state.action_cooldown = decision.get('cooldown', 1.0)
    
    def _analyze_situation(self, entity_id: str) -> Dict[str, Any]:
        """Анализ текущей ситуации для AI сущности"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        situation = {
            'health_percentage': stats.get_health_percentage(),
            'mana_percentage': stats.get_mana_percentage(),
            'level': stats.level,
            'available_stat_points': stats.available_stat_points,
            'inventory_count': len(ai_state.inventory_items),
            'equipped_count': len(ai_state.equipped_items),
            'available_skills': len(ai_state.available_skills),
            'target_exists': ai_state.target is not None,
            'emotion': ai_state.current_emotion,
            'emotion_intensity': ai_state.emotion_intensity
        }
        
        # Анализ инвентаря
        if ai_state.inventory_items:
            inventory_analysis = self._analyze_inventory(entity_id)
            situation.update(inventory_analysis)
        
        # Анализ скиллов
        if ai_state.available_skills:
            skills_analysis = self._analyze_skills(entity_id)
            situation.update(skills_analysis)
        
        return situation
    
    def _analyze_inventory(self, entity_id: str) -> Dict[str, Any]:
        """Анализ инвентаря AI сущности"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        analysis = {
            'has_weapon': False,
            'has_armor': False,
            'has_consumables': False,
            'best_weapon_damage': 0,
            'best_armor_value': 0,
            'healing_items': 0,
            'mana_items': 0
        }
        
        for item_uuid in ai_state.inventory_items:
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if not item_data:
                continue
            
            if item_data['content_type'] == ContentType.WEAPON:
                analysis['has_weapon'] = True
                damage = item_data['data'].get('damage', 0)
                if damage > analysis['best_weapon_damage']:
                    analysis['best_weapon_damage'] = damage
            
            elif item_data['content_type'] == ContentType.ARMOR:
                analysis['has_armor'] = True
                armor_value = item_data['data'].get('armor', 0)
                if armor_value > analysis['best_armor_value']:
                    analysis['best_armor_value'] = armor_value
            
            elif item_data['content_type'] == ContentType.CONSUMABLE:
                analysis['has_consumables'] = True
                item_type = item_data['data'].get('type', '')
                if 'здоров' in item_type.lower():
                    analysis['healing_items'] += 1
                elif 'мана' in item_type.lower():
                    analysis['mana_items'] += 1
        
        return analysis
    
    def _analyze_skills(self, entity_id: str) -> Dict[str, Any]:
        """Анализ доступных скиллов AI сущности"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        analysis = {
            'combat_skills': 0,
            'utility_skills': 0,
            'healing_skills': 0,
            'damage_skills': 0,
            'skill_cooldowns': {},
            'mana_costs': {}
        }
        
        for skill_uuid in ai_state.available_skills:
            skill_data = self.content_db.get_content_by_uuid(skill_uuid)
            if not skill_data:
                continue
            
            skill_type = skill_data['data'].get('skill_type', '')
            if 'combat' in skill_type.lower():
                analysis['combat_skills'] += 1
            elif 'utility' in skill_type.lower():
                analysis['utility_skills'] += 1
            
            # Анализируем целевое назначение
            target_type = skill_data['data'].get('target_type', '')
            if 'ally' in target_type.lower() and 'heal' in skill_data['name'].lower():
                analysis['healing_skills'] += 1
            elif 'enemy' in target_type.lower():
                analysis['damage_skills'] += 1
            
            # Запоминаем кулдауны и стоимость маны
            analysis['skill_cooldowns'][skill_uuid] = skill_data['data'].get('cooldown', 1.0)
            analysis['mana_costs'][skill_uuid] = skill_data['data'].get('mana_cost', 0)
        
        return analysis
    
    def _evaluate_options(self, entity_id: str, situation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Оценка доступных опций и выбор лучшего действия"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        options = []
        
        # Опция 1: Распределение очков характеристик
        if situation['available_stat_points'] > 0:
            options.append({
                'action_type': 'distribute_stats',
                'priority': 0.8,
                'description': 'Распределить очки характеристик',
                'cooldown': 0.0
            })
        
        # Опция 2: Экипировка лучшего оружия
        if situation['has_weapon'] and not situation.get('best_weapon_equipped', False):
            options.append({
                'action_type': 'equip_best_weapon',
                'priority': 0.7,
                'description': 'Экипировать лучшее оружие',
                'cooldown': 1.0
            })
        
        # Опция 3: Экипировка лучшей брони
        if situation['has_armor'] and not situation.get('best_armor_equipped', False):
            options.append({
                'action_type': 'equip_best_armor',
                'priority': 0.6,
                'description': 'Экипировать лучшую броню',
                'cooldown': 1.0
            })
        
        # Опция 4: Использование зелья здоровья
        if situation['health_percentage'] < 50 and situation['healing_items'] > 0:
            options.append({
                'action_type': 'use_healing_potion',
                'priority': 0.9,
                'description': 'Использовать зелье здоровья',
                'cooldown': 2.0
            })
        
        # Опция 5: Использование зелья маны
        if situation['mana_percentage'] < 30 and situation['mana_items'] > 0:
            options.append({
                'action_type': 'use_mana_potion',
                'priority': 0.7,
                'description': 'Использовать зелье маны',
                'cooldown': 2.0
            })
        
        # Опция 6: Изучение новых скиллов
        if situation['level'] > 1 and len(situation['available_skills']) < 5:
            options.append({
                'action_type': 'learn_new_skill',
                'priority': 0.5,
                'description': 'Изучить новый скилл',
                'cooldown': 5.0
            })
        
        # Выбираем лучшую опцию
        if not options:
            return None
        
        # Сортируем по приоритету
        options.sort(key=lambda x: x['priority'], reverse=True)
        
        # Применяем эмоциональные модификаторы
        best_option = options[0]
        if ai_state.current_emotion == EmotionType.FEAR:
            # В страхе предпочитаем защитные действия
            if 'healing' in best_option['description'].lower() or 'armor' in best_option['description'].lower():
                best_option['priority'] += 0.2
        elif ai_state.current_emotion == EmotionType.CONFIDENCE:
            # В уверенности предпочитаем атакующие действия
            if 'weapon' in best_option['description'].lower() or 'skill' in best_option['description'].lower():
                best_option['priority'] += 0.2
        
        return best_option
    
    def _execute_decision(self, entity_id: str, decision: Dict[str, Any]):
        """Выполнение принятого решения"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        action_type = decision['action_type']
        
        try:
            if action_type == 'distribute_stats':
                self._execute_distribute_stats(entity_id)
            
            elif action_type == 'equip_best_weapon':
                self._execute_equip_best_weapon(entity_id)
            
            elif action_type == 'equip_best_armor':
                self._execute_equip_best_armor(entity_id)
            
            elif action_type == 'use_healing_potion':
                self._execute_use_healing_potion(entity_id)
            
            elif action_type == 'use_mana_potion':
                self._execute_use_mana_potion(entity_id)
            
            elif action_type == 'learn_new_skill':
                self._execute_learn_new_skill(entity_id)
            
            logger.info(f"AI сущность {entity_id} выполнила действие: {decision['description']}")
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия {action_type} для {entity_id}: {e}")
    
    def _execute_distribute_stats(self, entity_id: str):
        """Выполнение распределения очков характеристик"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        if stats.available_stat_points <= 0:
            return
        
        # AI анализирует свои характеристики и выбирает лучшие для улучшения
        current_stats = {
            'strength': stats.base_stats.strength,
            'agility': stats.base_stats.agility,
            'intelligence': stats.base_stats.intelligence,
            'vitality': stats.base_stats.vitality,
            'wisdom': stats.base_stats.wisdom,
            'charisma': stats.base_stats.charisma
        }
        
        # Определяем приоритеты на основе типа сущности и текущего состояния
        if ai_state.personality == PersonalityType.AGGRESSIVE:
            # Агрессивные предпочитают силу и ловкость
            priority_stats = ['strength', 'agility', 'vitality']
        elif ai_state.personality == PersonalityType.CAUTIOUS:
            # Осторожные предпочитают защиту и ману
            priority_stats = ['vitality', 'wisdom', 'intelligence']
        elif ai_state.personality == PersonalityType.INTELLECTUAL:
            # Интеллектуальные предпочитают ману и интеллект
            priority_stats = ['intelligence', 'wisdom', 'charisma']
        else:
            # Сбалансированные улучшают все понемногу
            priority_stats = ['vitality', 'strength', 'agility', 'intelligence', 'wisdom', 'charisma']
        
        # Распределяем очки по приоритету
        for stat_name in priority_stats:
            if stats.available_stat_points <= 0:
                break
            
            if stats.distribute_stat_point(StatType(stat_name)):
                logger.info(f"{entity_id} улучшил {stat_name} до {getattr(stats.base_stats, stat_name)}")
    
    def _execute_equip_best_weapon(self, entity_id: str):
        """Выполнение экипировки лучшего оружия"""
        ai_state = self.ai_agents[entity_id]
        
        # Находим лучшее оружие в инвентаре
        best_weapon = None
        best_damage = 0
        
        for item_uuid in ai_state.inventory_items:
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if not item_data or item_data['content_type'] != ContentType.WEAPON:
                continue
            
            damage = item_data['data'].get('damage', 0)
            if damage > best_damage:
                best_damage = damage
                best_weapon = item_uuid
        
        if best_weapon:
            # Экипируем оружие
            self.inventory_system.equip_item(entity_id, best_weapon, 'weapon')
            ai_state.equipped_items['weapon'] = best_weapon
            logger.info(f"{entity_id} экипировал оружие с уроном {best_damage}")
    
    def _execute_equip_best_armor(self, entity_id: str):
        """Выполнение экипировки лучшей брони"""
        ai_state = self.ai_agents[entity_id]
        
        # Находим лучшую броню в инвентаре
        best_armor = None
        best_armor_value = 0
        
        for item_uuid in ai_state.inventory_items:
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if not item_data or item_data['content_type'] != ContentType.ARMOR:
                continue
            
            armor_value = item_data['data'].get('armor', 0)
            if armor_value > best_armor_value:
                best_armor_value = armor_value
                best_armor = item_uuid
        
        if best_armor:
            # Экипируем броню
            self.inventory_system.equip_item(entity_id, best_armor, 'armor')
            ai_state.equipped_items['armor'] = best_armor
            logger.info(f"{entity_id} экипировал броню с защитой {best_armor_value}")
    
    def _execute_use_healing_potion(self, entity_id: str):
        """Выполнение использования зелья здоровья"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        # Находим зелье здоровья
        healing_potion = None
        for item_uuid in ai_state.inventory_items:
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if not item_data or item_data['content_type'] != ContentType.CONSUMABLE:
                continue
            
            if 'здоров' in item_data['data'].get('type', '').lower():
                healing_potion = item_uuid
                break
        
        if healing_potion:
            # Используем зелье
            potion_data = self.content_db.get_content_by_uuid(healing_potion)
            potency = potion_data['data'].get('potency', 1.0)
            heal_amount = int(50 * potency)  # Базовое восстановление
            
            old_health = stats.current_health
            stats.heal(heal_amount)
            actual_heal = stats.current_health - old_health
            
            # Удаляем использованное зелье
            ai_state.inventory_items.remove(healing_potion)
            
            logger.info(f"{entity_id} использовал зелье здоровья, восстановил {actual_heal} HP")
    
    def _execute_use_mana_potion(self, entity_id: str):
        """Выполнение использования зелья маны"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        # Находим зелье маны
        mana_potion = None
        for item_uuid in ai_state.inventory_items:
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if not item_data or item_data['content_type'] != ContentType.CONSUMABLE:
                continue
            
            if 'мана' in item_data['data'].get('type', '').lower():
                mana_potion = item_uuid
                break
        
        if mana_potion:
            # Используем зелье
            potion_data = self.content_db.get_content_by_uuid(mana_potion)
            potency = potion_data['data'].get('potency', 1.0)
            restore_amount = int(30 * potency)  # Базовое восстановление
            
            old_mana = stats.current_mana
            stats.restore_mana(restore_amount)
            actual_restore = stats.current_mana - old_mana
            
            # Удаляем использованное зелье
            ai_state.inventory_items.remove(mana_potion)
            
            logger.info(f"{entity_id} использовал зелье маны, восстановил {actual_restore} MP")
    
    def _execute_learn_new_skill(self, entity_id: str):
        """Выполнение изучения нового скилла"""
        ai_state = self.ai_agents[entity_id]
        stats = self.entity_stats[entity_id]
        
        # Проверяем, есть ли доступные скиллы для изучения
        available_skills = self.content_db.get_content_by_type(
            ai_state.session_id if hasattr(ai_state, 'session_id') else 'default',
            ContentType.SKILL
        )
        
        if available_skills:
            # Выбираем подходящий скилл на основе личности
            suitable_skill = None
            
            if ai_state.personality == PersonalityType.AGGRESSIVE:
                # Агрессивные предпочитают боевые скиллы
                for skill in available_skills:
                    if skill['data'].get('skill_type') == 'combat':
                        suitable_skill = skill
                        break
            
            elif ai_state.personality == PersonalityType.CAUTIOUS:
                # Осторожные предпочитают защитные скиллы
                for skill in available_skills:
                    if 'defense' in skill['data'].get('target_type', '').lower():
                        suitable_skill = skill
                        break
            
            elif ai_state.personality == PersonalityType.INTELLECTUAL:
                # Интеллектуальные предпочитают магические скиллы
                for skill in available_skills:
                    if 'magic' in skill['name'].lower() or 'utility' in skill['data'].get('skill_type', '').lower():
                        suitable_skill = skill
                        break
            
            if suitable_skill:
                # Изучаем скилл
                ai_state.available_skills.append(suitable_skill['uuid'])
                ai_state.learning_progress[suitable_skill['uuid']] = 1.0  # Полностью изучен
                
                logger.info(f"{entity_id} изучил новый скилл: {suitable_skill['name']}")
    
    def _on_entity_damaged(self, event_data: Dict[str, Any]):
        """Обработка события получения урона"""
        entity_id = event_data.get('entity_id')
        if entity_id in self.ai_agents:
            # Обновляем эмоции
            ai_state = self.ai_agents[entity_id]
            ai_state.current_emotion = EmotionType.FEAR
            ai_state.emotion_intensity = 0.8
            
            # Записываем в память AI Entity
            if hasattr(self.ai_system, 'add_memory'):
                self.ai_system.add_memory(entity_id, {
                    'type': 'combat',
                    'event': 'damaged',
                    'damage': event_data.get('damage', 0),
                    'source': event_data.get('source', 'unknown'),
                    'timestamp': time.time()
                })
    
    def _on_entity_healed(self, event_data: Dict[str, Any]):
        """Обработка события восстановления здоровья"""
        entity_id = event_data.get('entity_id')
        if entity_id in self.ai_agents:
            # Обновляем эмоции
            ai_state = self.ai_agents[entity_id]
            ai_state.current_emotion = EmotionType.RELIEF
            ai_state.emotion_intensity = 0.6
    
    def _on_item_acquired(self, event_data: Dict[str, Any]):
        """Обработка события получения предмета"""
        entity_id = event_data.get('entity_id')
        item_uuid = event_data.get('item_uuid')
        
        if entity_id in self.ai_agents and item_uuid:
            ai_state = self.ai_agents[entity_id]
            ai_state.inventory_items.append(item_uuid)
            
            # Анализируем предмет для принятия решений
            item_data = self.content_db.get_content_by_uuid(item_uuid)
            if item_data:
                logger.info(f"{entity_id} получил предмет: {item_data['name']}")
    
    def _on_skill_learned(self, event_data: Dict[str, Any]):
        """Обработка события изучения скилла"""
        entity_id = event_data.get('entity_id')
        skill_uuid = event_data.get('skill_uuid')
        
        if entity_id in self.ai_agents and skill_uuid:
            ai_state = self.ai_agents[entity_id]
            if skill_uuid not in ai_state.available_skills:
                ai_state.available_skills.append(skill_uuid)
                ai_state.learning_progress[skill_uuid] = 1.0
    
    def _on_level_up(self, event_data: Dict[str, Any]):
        """Обработка события повышения уровня"""
        entity_id = event_data.get('entity_id')
        if entity_id in self.ai_agents:
            ai_state = self.ai_agents[entity_id]
            ai_state.current_emotion = EmotionType.EXCITEMENT
            ai_state.emotion_intensity = 0.8
            
            # Обновляем характеристики
            if entity_id in self.entity_stats:
                stats = self.entity_stats[entity_id]
                ai_state.level = stats.level
                ai_state.experience = stats.experience
    
    def _on_combat_started(self, event_data: Dict[str, Any]):
        """Обработка события начала боя"""
        entity_id = event_data.get('entity_id')
        if entity_id in self.ai_agents:
            ai_state = self.ai_agents[entity_id]
            ai_state.current_emotion = EmotionType.ALERTNESS
            ai_state.emotion_intensity = 0.7
    
    def _on_combat_ended(self, event_data: Dict[str, Any]):
        """Обработка события окончания боя"""
        entity_id = event_data.get('entity_id')
        if entity_id in self.ai_agents:
            ai_state = self.ai_agents[entity_id]
            
            # Определяем результат боя
            if event_data.get('victory', False):
                ai_state.current_emotion = EmotionType.JOY
                ai_state.emotion_intensity = 0.8
            else:
                ai_state.current_emotion = EmotionType.FRUSTRATION
                ai_state.emotion_intensity = 0.6
    
    def get_ai_agent_state(self, entity_id: str) -> Optional[AIAgentState]:
        """Получение состояния AI агента"""
        return self.ai_agents.get(entity_id)
    
    def get_entity_stats(self, entity_id: str) -> Optional[EntityStats]:
        """Получение характеристик сущности"""
        return self.entity_stats.get(entity_id)
    
    def get_all_ai_agents(self) -> List[str]:
        """Получение списка всех AI агентов"""
        return list(self.ai_agents.keys())
    
    def cleanup(self):
        """Очистка системы интеграции"""
        self.ai_agents.clear()
        self.entity_stats.clear()
        logger.info("AI Integration System очищена")
