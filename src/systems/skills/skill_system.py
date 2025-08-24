#!/usr/bin/env python3
"""
Система навыков - управление навыками и их применением
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    SkillType, SkillCategory, DamageType, StatType, TriggerType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class SkillRequirements:
    """Требования для навыка"""
    level: int = 1
    stats: Dict[StatType, int] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    experience: int = 0

@dataclass
class SkillCooldown:
    """Перезарядка навыка"""
    base_cooldown: float = 0.0
    current_cooldown: float = 0.0
    cooldown_reduction: float = 0.0
    last_used: float = 0.0

@dataclass
class Skill:
    """Игровой навык"""
    skill_id: str
    name: str
    description: str
    skill_type: SkillType
    category: SkillCategory
    level: int = 1
    max_level: int = 10
    requirements: SkillRequirements = field(default_factory=SkillRequirements)
    cooldown: SkillCooldown = field(default_factory=SkillCooldown)
    mana_cost: int = 0
    health_cost: int = 0
    damage: int = 0
    damage_type: Optional[DamageType] = None
    range: float = 1.0
    area_effect: float = 0.0
    effects: List[str] = field(default_factory=list)
    icon: str = ""
    sound: str = ""
    animation: str = ""
    
    def can_use(self, entity: Dict[str, Any]) -> bool:
        """Проверка возможности использования навыка"""
        try:
            # Проверяем перезарядку
            if self.cooldown.current_cooldown > 0:
                return False
            
            # Проверяем ману
            if self.mana_cost > 0:
                entity_mana = entity.get('mana', 0)
                if entity_mana < self.mana_cost:
                    return False
            
            # Проверяем здоровье
            if self.health_cost > 0:
                entity_health = entity.get('health', 0)
                if entity_health <= self.health_cost:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности использования навыка {self.skill_id}: {e}")
            return False

class SkillSystem(ISystem):
    """Система управления навыками"""
    
    def __init__(self):
        self._system_name = "skills"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Зарегистрированные навыки
        self.registered_skills: Dict[str, Skill] = {}
        
        # Навыки сущностей
        self.entity_skills: Dict[str, Dict[str, Skill]] = {}
        
        # Перезарядки навыков
        self.skill_cooldowns: Dict[str, Dict[str, SkillCooldown]] = {}
        
        # История использования навыков
        self.skill_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_skills_per_entity': SYSTEM_LIMITS["max_skills_per_entity"],
            'max_skill_level': 20,
            'cooldown_reduction_cap': 0.8,  # Максимум 80% сокращения
            'skill_combining_enabled': True,
            'auto_skill_upgrade': False
        }
        
        # Статистика системы
        self.system_stats = {
            'registered_skills_count': 0,
            'total_entity_skills': 0,
            'skills_used_today': 0,
            'skills_learned_today': 0,
            'skills_upgraded_today': 0,
            'update_time': 0.0
        }
        
        logger.info("Система навыков инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы навыков"""
        try:
            logger.info("Инициализация системы навыков...")
            
            # Регистрируем базовые навыки
            self._register_base_skills()
            
            self._system_state = SystemState.READY
            logger.info("Система навыков успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы навыков: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы навыков"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем перезарядки навыков
            self._update_skill_cooldowns(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы навыков: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы навыков"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система навыков приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы навыков: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы навыков"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система навыков возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы навыков: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы навыков"""
        try:
            logger.info("Очистка системы навыков...")
            
            # Очищаем все данные
            self.registered_skills.clear()
            self.entity_skills.clear()
            self.skill_cooldowns.clear()
            self.skill_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'registered_skills_count': 0,
                'total_entity_skills': 0,
                'skills_used_today': 0,
                'skills_learned_today': 0,
                'skills_upgraded_today': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система навыков очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы навыков: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'registered_skills': len(self.registered_skills),
            'entities_with_skills': len(self.entity_skills),
            'total_entity_skills': self.system_stats['total_entity_skills'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "skill_learned":
                return self._handle_skill_learned(event_data)
            elif event_type == "skill_used":
                return self._handle_skill_used(event_data)
            elif event_type == "skill_upgraded":
                return self._handle_skill_upgraded(event_data)
            elif event_type == "entity_leveled_up":
                return self._handle_entity_leveled_up(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
   
    def _update_skill_cooldowns(self, delta_time: float) -> None:
        """Обновление перезарядок навыков"""
        try:
            current_time = time.time()
            
            for entity_id, skills in self.skill_cooldowns.items():
                for skill_id, cooldown in skills.items():
                    if cooldown.current_cooldown > 0:
                        cooldown.current_cooldown = max(0, cooldown.current_cooldown - delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления перезарядок навыков: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['registered_skills_count'] = len(self.registered_skills)
            self.system_stats['total_entity_skills'] = sum(len(skills) for skills in self.entity_skills.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_skill_learned(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изучения навыка"""
        try:
            skill_id = event_data.get('skill_id')
            entity_id = event_data.get('entity_id')
            
            if skill_id and entity_id:
                return self.learn_skill(entity_id, skill_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изучения навыка: {e}")
            return False
    
    def _handle_skill_used(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события использования навыка"""
        try:
            skill_id = event_data.get('skill_id')
            entity_id = event_data.get('entity_id')
            target_id = event_data.get('target_id')
            
            if skill_id and entity_id:
                return self.use_skill(entity_id, skill_id, target_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события использования навыка: {e}")
            return False
    
    def _handle_skill_upgraded(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события улучшения навыка"""
        try:
            skill_id = event_data.get('skill_id')
            entity_id = event_data.get('entity_id')
            new_level = event_data.get('new_level')
            
            if skill_id and entity_id and new_level:
                return self.upgrade_skill(entity_id, skill_id, new_level)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события улучшения навыка: {e}")
            return False
    
    def _handle_entity_leveled_up(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события повышения уровня сущности"""
        try:
            entity_id = event_data.get('entity_id')
            new_level = event_data.get('new_level')
            
            if entity_id and new_level:
                # Проверяем, какие навыки стали доступны
                self._check_available_skills(entity_id, new_level)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события повышения уровня сущности: {e}")
            return False
    
    def learn_skill(self, entity_id: str, skill_id: str) -> bool:
        """Изучение навыка сущностью"""
        try:
            if skill_id not in self.registered_skills:
                logger.warning(f"Навык {skill_id} не найден")
                return False
            
            skill = self.registered_skills[skill_id]
            
            # Проверяем требования
            if not self._check_skill_requirements(entity_id, skill):
                logger.warning(f"Сущность {entity_id} не соответствует требованиям для навыка {skill_id}")
                return False
            
            # Проверяем лимит навыков
            if entity_id in self.entity_skills:
                if len(self.entity_skills[entity_id]) >= self.system_settings['max_skills_per_entity']:
                    logger.warning(f"Достигнут лимит навыков для сущности {entity_id}")
                    return False
            
            # Инициализируем навыки сущности, если нужно
            if entity_id not in self.entity_skills:
                self.entity_skills[entity_id] = {}
            
            # Инициализируем перезарядки, если нужно
            if entity_id not in self.skill_cooldowns:
                self.skill_cooldowns[entity_id] = {}
            
            # Добавляем навык
            self.entity_skills[entity_id][skill_id] = skill
            self.skill_cooldowns[entity_id][skill_id] = SkillCooldown(
                base_cooldown=skill.cooldown.base_cooldown
            )
            
            # Записываем в историю
            current_time = time.time()
            self.skill_history.append({
                'timestamp': current_time,
                'action': 'learned',
                'skill_id': skill_id,
                'entity_id': entity_id,
                'skill_level': skill.level
            })
            
            self.system_stats['skills_learned_today'] += 1
            logger.info(f"Сущность {entity_id} изучила навык {skill_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изучения навыка {skill_id} сущностью {entity_id}: {e}")
            return False
    
    def use_skill(self, entity_id: str, skill_id: str, target_id: Optional[str] = None) -> bool:
        """Использование навыка"""
        try:
            if entity_id not in self.entity_skills or skill_id not in self.entity_skills[entity_id]:
                logger.warning(f"Сущность {entity_id} не знает навык {skill_id}")
                return False
            
            skill = self.entity_skills[entity_id][skill_id]
            cooldown = self.skill_cooldowns[entity_id][skill_id]
            
            # Проверяем перезарядку
            if cooldown.current_cooldown > 0:
                logger.warning(f"Навык {skill_id} на перезарядке для {entity_id}")
                return False
            
            # Проверяем стоимость
            if not self._check_skill_cost(entity_id, skill):
                logger.warning(f"Недостаточно ресурсов для использования навыка {skill_id}")
                return False
            
            # Применяем навык
            if self._apply_skill_effects(entity_id, skill, target_id):
                # Устанавливаем перезарядку
                cooldown.current_cooldown = cooldown.base_cooldown * (1 - cooldown.cooldown_reduction)
                cooldown.last_used = time.time()
                
                # Записываем в историю
                current_time = time.time()
                self.skill_history.append({
                    'timestamp': current_time,
                    'action': 'used',
                    'skill_id': skill_id,
                    'entity_id': entity_id,
                    'target_id': target_id,
                    'skill_level': skill.level
                })
                
                self.system_stats['skills_used_today'] += 1
                logger.info(f"Сущность {entity_id} использовала навык {skill_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка использования навыка {skill_id} сущностью {entity_id}: {e}")
            return False
    
    def upgrade_skill(self, entity_id: str, skill_id: str, new_level: int) -> bool:
        """Улучшение навыка"""
        try:
            if entity_id not in self.entity_skills or skill_id not in self.entity_skills[entity_id]:
                logger.warning(f"Сущность {entity_id} не знает навык {skill_id}")
                return False
            
            skill = self.entity_skills[entity_id][skill_id]
            
            if new_level <= skill.level:
                logger.warning(f"Новый уровень {new_level} должен быть больше текущего {skill.level}")
                return False
            
            if new_level > skill.max_level:
                logger.warning(f"Новый уровень {new_level} превышает максимальный {skill.max_level}")
                return False
            
            # Проверяем требования для нового уровня
            if not self._check_skill_requirements(entity_id, skill, new_level):
                logger.warning(f"Сущность {entity_id} не соответствует требованиям для уровня {new_level}")
                return False
            
            # Улучшаем навык
            skill.level = new_level
            
            # Улучшаем характеристики навыка
            self._upgrade_skill_stats(skill)
            
            # Записываем в историю
            current_time = time.time()
            self.skill_history.append({
                'timestamp': current_time,
                'action': 'upgraded',
                'skill_id': skill_id,
                'entity_id': entity_id,
                'old_level': skill.level - 1,
                'new_level': skill.level
            })
            
            self.system_stats['skills_upgraded_today'] += 1
            logger.info(f"Навык {skill_id} сущности {entity_id} улучшен до уровня {new_level}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка улучшения навыка {skill_id} сущности {entity_id}: {e}")
            return False
    
    def _check_skill_requirements(self, entity_id: str, skill: Skill, level: Optional[int] = None) -> bool:
        """Проверка требований для навыка"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто проверяем базовые требования
            
            if level is None:
                level = skill.level
            
            if skill.requirements.level > level:
                return False
            
            # Другие проверки (статы, предметы, навыки) будут добавлены позже
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований для навыка {skill.skill_id}: {e}")
            return False
    
    def _check_skill_cost(self, entity_id: str, skill: Skill) -> bool:
        """Проверка стоимости навыка"""
        try:
            # Здесь должна быть интеграция с системой характеристик
            # Пока просто возвращаем True
            
            # Проверки маны, здоровья и других ресурсов будут добавлены позже
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки стоимости навыка {skill.skill_id}: {e}")
            return False
    
    def _apply_skill_effects(self, entity_id: str, skill: Skill, target_id: Optional[str]) -> bool:
        """Применение эффектов навыка"""
        try:
            # Здесь должна быть интеграция с другими системами
            # Пока просто логируем
            
            if skill.skill_type == SkillType.ATTACK:
                logger.debug(f"Применена атака {skill.skill_id} от {entity_id} к {target_id}")
            elif skill.skill_type == SkillType.MAGIC:
                logger.debug(f"Применена магия {skill.skill_id} от {entity_id} к {target_id}")
            elif skill.skill_type == SkillType.DEFENSE:
                logger.debug(f"Применена защита {skill.skill_id} от {entity_id}")
            elif skill.skill_type == SkillType.SUPPORT:
                logger.debug(f"Применена поддержка {skill.skill_id} от {entity_id} к {target_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов навыка {skill.skill_id}: {e}")
            return False
    
    def _upgrade_skill_stats(self, skill: Skill) -> None:
        """Улучшение характеристик навыка"""
        try:
            # Улучшаем характеристики на основе уровня
            level_multiplier = 1 + (skill.level - 1) * 0.2  # 20% за уровень
            
            if skill.damage > 0:
                skill.damage = int(skill.damage * level_multiplier)
            
            if skill.mana_cost > 0:
                skill.mana_cost = int(skill.mana_cost * level_multiplier)
            
            if skill.health_cost > 0:
                skill.health_cost = int(skill.health_cost * level_multiplier)
            
            if skill.range > 0:
                skill.range = skill.range * level_multiplier
            
            if skill.area_effect > 0:
                skill.area_effect = skill.area_effect * level_multiplier
            
        except Exception as e:
            logger.error(f"Ошибка улучшения характеристик навыка {skill.skill_id}: {e}")
    
    def _check_available_skills(self, entity_id: str, level: int) -> None:
        """Проверка доступных навыков для нового уровня"""
        try:
            # Проверяем все зарегистрированные навыки
            for skill_id, skill in self.registered_skills.items():
                if skill_id not in self.entity_skills.get(entity_id, {}):
                    if skill.requirements.level <= level:
                        # Навык стал доступен
                        logger.debug(f"Навык {skill_id} стал доступен для {entity_id} на уровне {level}")
                        
                        # Автоматически изучаем, если включено
                        if self.system_settings['auto_skill_upgrade']:
                            self.learn_skill(entity_id, skill_id)
                
        except Exception as e:
            logger.error(f"Ошибка проверки доступных навыков для {entity_id}: {e}")
    
    def get_entity_skills(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение навыков сущности"""
        try:
            if entity_id not in self.entity_skills:
                return []
            
            skills_info = []
            
            for skill_id, skill in self.entity_skills[entity_id].items():
                cooldown = self.skill_cooldowns[entity_id].get(skill_id)
                
                skills_info.append({
                    'skill_id': skill_id,
                    'name': skill.name,
                    'description': skill.description,
                    'skill_type': skill.skill_type.value,
                    'category': skill.category.value,
                    'level': skill.level,
                    'max_level': skill.max_level,
                    'mana_cost': skill.mana_cost,
                    'health_cost': skill.health_cost,
                    'damage': skill.damage,
                    'damage_type': skill.damage_type.value if skill.damage_type else None,
                    'range': skill.range,
                    'area_effect': skill.area_effect,
                    'cooldown_remaining': cooldown.current_cooldown if cooldown else 0.0,
                    'icon': skill.icon
                })
            
            return skills_info
            
        except Exception as e:
            logger.error(f"Ошибка получения навыков сущности {entity_id}: {e}")
            return []
    
    def get_skill_info(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о навыке"""
        try:
            if skill_id not in self.registered_skills:
                return None
            
            skill = self.registered_skills[skill_id]
            
            return {
                'skill_id': skill.skill_id,
                'name': skill.name,
                'description': skill.description,
                'skill_type': skill.skill_type.value,
                'category': skill.category.value,
                'level': skill.level,
                'max_level': skill.max_level,
                'mana_cost': skill.mana_cost,
                'health_cost': skill.health_cost,
                'damage': skill.damage,
                'damage_type': skill.damage_type.value if skill.damage_type else None,
                'range': skill.range,
                'area_effect': skill.area_effect,
                'icon': skill.icon,
                'sound': skill.sound,
                'animation': skill.animation
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о навыке {skill_id}: {e}")
            return None
    
    def register_custom_skill(self, skill: Skill) -> bool:
        """Регистрация пользовательского навыка"""
        try:
            if skill.skill_id in self.registered_skills:
                logger.warning(f"Навык {skill.skill_id} уже зарегистрирован")
                return False
            
            self.registered_skills[skill.skill_id] = skill
            logger.info(f"Зарегистрирован пользовательский навык {skill.skill_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользовательского навыка {skill.skill_id}: {e}")
            return False
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Dict[str, Any]]:
        """Получение навыков по категории"""
        try:
            skills = []
            
            for skill in self.registered_skills.values():
                if skill.category == category:
                    skills.append({
                        'skill_id': skill.skill_id,
                        'name': skill.name,
                        'description': skill.description,
                        'skill_type': skill.skill_type.value,
                        'level': skill.level,
                        'max_level': skill.max_level,
                        'icon': skill.icon
                    })
            
            return skills
            
        except Exception as e:
            logger.error(f"Ошибка получения навыков по категории {category.value}: {e}")
            return []
    
    def get_skills_by_type(self, skill_type: SkillType) -> List[Dict[str, Any]]:
        """Получение навыков по типу"""
        try:
            skills = []
            
            for skill in self.registered_skills.values():
                if skill.skill_type == skill_type:
                    skills.append({
                        'skill_id': skill.skill_id,
                        'name': skill.name,
                        'description': skill.description,
                        'category': skill.category.value,
                        'level': skill.level,
                        'max_level': skill.max_level,
                        'icon': skill.icon
                    })
            
            return skills
            
        except Exception as e:
            logger.error(f"Ошибка получения навыков по типу {skill_type.value}: {e}")
            return []
    
    def get_skill_cooldown(self, entity_id: str, skill_id: str) -> Optional[float]:
        """Получение оставшейся перезарядки навыка"""
        try:
            if entity_id not in self.skill_cooldowns or skill_id not in self.skill_cooldowns[entity_id]:
                return None
            
            return self.skill_cooldowns[entity_id][skill_id].current_cooldown
            
        except Exception as e:
            logger.error(f"Ошибка получения перезарядки навыка {skill_id} для {entity_id}: {e}")
            return None
    
    def reset_skill_cooldown(self, entity_id: str, skill_id: str) -> bool:
        """Сброс перезарядки навыка"""
        try:
            if entity_id not in self.skill_cooldowns or skill_id not in self.skill_cooldowns[entity_id]:
                return False
            
            self.skill_cooldowns[entity_id][skill_id].current_cooldown = 0.0
            logger.debug(f"Перезарядка навыка {skill_id} для {entity_id} сброшена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сброса перезарядки навыка {skill_id} для {entity_id}: {e}")
            return False

class SkillTree:
    """Дерево навыков для сущности"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.skills: Dict[str, Skill] = {}
        self.skill_points = 0
        self.max_skill_points = 100
        self.learned_skills: List[str] = []
        self.available_skills: List[str] = []
        
        # Настройки дерева навыков
        self.settings = {
            'max_skills': 20,
            'skill_point_cost': 1,
            'prerequisite_skills_required': True,
            'level_requirements_enabled': True
        }
        
        logger.debug(f"Создано дерево навыков для сущности {entity_id}")
    
    def add_skill(self, skill: Skill) -> bool:
        """Добавление навыка в дерево"""
        try:
            if skill.skill_id in self.skills:
                logger.warning(f"Навык {skill.skill_id} уже добавлен в дерево навыков")
                return False
            
            if len(self.skills) >= self.settings['max_skills']:
                logger.warning(f"Достигнут лимит навыков в дереве навыков")
                return False
            
            self.skills[skill.skill_id] = skill
            self.available_skills.append(skill.skill_id)
            
            logger.debug(f"Навык {skill.skill_id} добавлен в дерево навыков для {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления навыка {skill.skill_id} в дерево навыков: {e}")
            return False
    
    def learn_skill(self, skill_name: str, entity: Dict[str, Any]) -> bool:
        """Изучение навыка"""
        try:
            # Находим навык по имени
            skill_to_learn = None
            for skill in self.skills.values():
                if skill.name == skill_name:
                    skill_to_learn = skill
                    break
            
            if not skill_to_learn:
                logger.warning(f"Навык {skill_name} не найден в дереве навыков")
                return False
            
            # Проверяем требования
            if not self._check_skill_requirements(skill_to_learn, entity):
                logger.warning(f"Не выполнены требования для изучения навыка {skill_name}")
                return False
            
            # Проверяем очки навыков
            if self.skill_points < self.settings['skill_point_cost']:
                logger.warning(f"Недостаточно очков навыков для изучения {skill_name}")
                return False
            
            # Изучаем навык
            self.skill_points -= self.settings['skill_point_cost']
            self.learned_skills.append(skill_to_learn.skill_id)
            
            logger.info(f"Сущность {self.entity_id} изучила навык {skill_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изучения навыка {skill_name}: {e}")
            return False
    
    def _check_skill_requirements(self, skill: Skill, entity: Dict[str, Any]) -> bool:
        """Проверка требований для изучения навыка"""
        try:
            requirements = skill.requirements
            
            # Проверяем уровень
            if self.settings['level_requirements_enabled']:
                entity_level = entity.get('level', 1)
                if entity_level < requirements.level:
                    return False
            
            # Проверяем характеристики
            entity_stats = entity.get('stats', {})
            for stat, required_value in requirements.stats.items():
                if entity_stats.get(stat.value, 0) < required_value:
                    return False
            
            # Проверяем предметы
            entity_inventory = entity.get('inventory', [])
            for required_item in requirements.items:
                if not any(item.get('name') == required_item for item in entity_inventory):
                    return False
            
            # Проверяем предварительные навыки
            if self.settings['prerequisite_skills_required']:
                for required_skill in requirements.skills:
                    if required_skill not in self.learned_skills:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований навыка: {e}")
            return False
    
    def get_ai_recommended_skill(self, entity: Dict[str, Any], context: Dict[str, Any]) -> Optional[Skill]:
        """Получение рекомендуемого навыка для AI"""
        try:
            target = context.get('target')
            if not target:
                return None
            
            # Простая логика выбора навыка
            for skill_id in self.learned_skills:
                skill = self.skills.get(skill_id)
                if not skill:
                    continue
                
                # Проверяем, подходит ли навык для ситуации
                if skill.skill_type.value in ['combat', 'attack']:
                    # Проверяем дистанцию
                    dx = target.get('x', 0) - entity.get('x', 0)
                    dy = target.get('y', 0) - entity.get('y', 0)
                    distance = (dx*dx + dy*dy) ** 0.5
                    
                    if distance <= skill.range:
                        return skill
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендуемого навыка для AI: {e}")
            return None
    
    def update(self, delta_time: float):
        """Обновление дерева навыков"""
        try:
            # Обновляем перезарядки навыков
            for skill in self.skills.values():
                if skill.cooldown.current_cooldown > 0:
                    skill.cooldown.current_cooldown -= delta_time
                    if skill.cooldown.current_cooldown < 0:
                        skill.cooldown.current_cooldown = 0
            
        except Exception as e:
            logger.error(f"Ошибка обновления дерева навыков: {e}")
    
    def can_use_skill(self, skill: Skill, entity: Dict[str, Any]) -> bool:
        """Проверка возможности использования навыка"""
        try:
            # Проверяем, изучен ли навык
            if skill.skill_id not in self.learned_skills:
                return False
            
            # Проверяем перезарядку
            if skill.cooldown.current_cooldown > 0:
                return False
            
            # Проверяем ману
            if skill.mana_cost > 0:
                entity_mana = entity.get('mana', 0)
                if entity_mana < skill.mana_cost:
                    return False
            
            # Проверяем здоровье
            if skill.health_cost > 0:
                entity_health = entity.get('health', 0)
                if entity_health <= skill.health_cost:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности использования навыка: {e}")
            return False
