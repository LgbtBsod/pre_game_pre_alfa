from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from src.core.architecture import BaseComponent, ComponentType, Priority
from typing import *
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
import logging
import os
import random
import sys
import time

#!/usr/bin/env python3
"""Система социального взаимодействия - управление отношениями между сущностями"""

logger = logging.getLogger(__name__)

# = ОСНОВНЫЕ ТИПЫ И ПЕРЕЧИСЛЕНИЯ

class RelationshipType(Enum):
    """Типы отношений"""
    STRANGER = "stranger"        # Незнакомец
    ACQUAINTANCE = "acquaintance"  # Знакомый
    FRIEND = "friend"            # Друг
    CLOSE_FRIEND = "close_friend"  # Близкий друг
    LOVER = "lover"              # Возлюбленный
    ENEMY = "enemy"              # Враг
    RIVAL = "rival"              # Соперник
    MENTOR = "mentor"            # Наставник
    STUDENT = "student"          # Ученик

class InteractionType(Enum):
    """Типы взаимодействий"""
    GREETING = "greeting"        # Приветствие
    CONVERSATION = "conversation"  # Разговор
    GIFT = "gift"                # Подарок
    HELP = "help"                # Помощь
    TRADE = "trade"              # Торговля
    COMBAT = "combat"            # Бой
    COOPERATION = "cooperation"  # Сотрудничество
    COMPETITION = "competition"  # Соревнование

class ReputationType(Enum):
    """Типы репутации"""
    HONOR = "honor"              # Честь
    TRUST = "trust"              # Доверие
    INFLUENCE = "influence"      # Влияние
    WEALTH = "wealth"            # Богатство
    SKILL = "skill"              # Навыки
    VIOLENCE = "violence"        # Насилие

class SocialStatus(Enum):
    """Социальный статус"""
    OUTCAST = "outcast"          # Изгой
    CITIZEN = "citizen"          # Гражданин
    MERCHANT = "merchant"        # Торговец
    WARRIOR = "warrior"          # Воин
    NOBLE = "noble"              # Дворянин
    LEADER = "leader"            # Лидер

class FactionType(Enum):
    """Типы фракций"""
    NEUTRAL = "neutral"          # Нейтральная
    FRIENDLY = "friendly"        # Дружественная
    HOSTILE = "hostile"          # Враждебная
    ALLIED = "allied"            # Союзная
    RIVAL = "rival"              # Соперничающая

class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    VERBAL = "verbal"            # Устная речь
    GESTURE = "gesture"          # Жесты
    WRITTEN = "written"          # Письменность
    TELEPATHIC = "telepathic"    # Телепатия
    MAGICAL = "magical"          # Магическая связь

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class Relationship:
    """Отношения между сущностями"""
    entity_id: str
    target_id: str
    relationship_type: RelationshipType
    trust_level: float = 0.0  # -1.0 до 1.0
    respect_level: float = 0.0  # -1.0 до 1.0
    affection_level: float = 0.0  # -1.0 до 1.0
    fear_level: float = 0.0  # 0.0 до 1.0
    last_interaction: float = field(default_factory=time.time)
    interaction_count: int = 0
    shared_experiences: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

@dataclass
class Interaction:
    """Социальное взаимодействие"""
    interaction_id: str
    initiator_id: str
    target_id: str
    interaction_type: InteractionType
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    success: bool = True
    impact: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    communication_channel: CommunicationChannel = CommunicationChannel.VERBAL

@dataclass
class Reputation:
    """Репутация сущности"""
    entity_id: str
    reputation_type: ReputationType
    value: float = 0.0
    max_value: float = 100.0
    min_value: float = -100.0
    decay_rate: float = 0.1
    last_update: float = field(default_factory=time.time)
    history: List[Tuple[float, float]] = field(default_factory=list)

@dataclass
class SocialProfile:
    """Социальный профиль сущности"""
    entity_id: str
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    reputation: Dict[ReputationType, Reputation] = field(default_factory=dict)
    social_status: SocialStatus = SocialStatus.CITIZEN
    faction: Optional[FactionType] = None
    faction_standing: float = 0.0
    last_interaction: float = field(default_factory=time.time)
    interaction_count: int = 0
    personality_traits: Dict[str, float] = field(default_factory=dict)
    social_skills: Dict[str, float] = field(default_factory=dict)

@dataclass
class SocialEvent:
    """Социальное событие"""
    event_id: str
    event_type: str
    participants: List[str] = field(default_factory=list)
    location: str = ""
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    impact: Dict[str, float] = field(default_factory=dict)

# = СИСТЕМА СОЦИАЛЬНОГО ВЗАИМОДЕЙСТВИЯ

class SocialSystem(BaseComponent):
    """Система социального взаимодействия"""
    
    def __init__(self):
        super().__init__(
            component_id="SocialSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.NORMAL
        )
        
        # Логгер системы
        self.logger = logging.getLogger(__name__)

        # Социальные данные
        self.social_profiles: Dict[str, SocialProfile] = {}
        self.interactions: List[Interaction] = []
        self.social_events: List[SocialEvent] = []
        
        # Статистика
        self.stats = {
            "total_interactions": 0,
            "total_relationships": 0,
            "social_events": 0,
            "reputation_changes": 0,
            "relationship_evolutions": 0
        }
        
        # Callbacks
        self.interaction_callbacks: Dict[str, Callable] = {}
        self.relationship_callbacks: List[Callable] = []
        self.reputation_callbacks: List[Callable] = []
        
        # Настройки
        self.settings = {
            "max_relationships": 100,
            "interaction_cooldown": 60.0,  # секунды
            "reputation_decay_rate": 0.1,
            "relationship_evolution_rate": 0.05,
            "social_skill_learning_rate": 0.1,
            "personality_influence": 0.3
        }

    def _on_initialize(self) -> bool:
        """Инициализация системы социального взаимодействия"""
        try:
            self.logger.info("Инициализация системы социального взаимодействия")
            
            # Регистрация callbacks
            self._register_callbacks()
            
            self.logger.info("Система социального взаимодействия инициализирована")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системы социального взаимодействия: {e}")
            return False

    def _register_callbacks(self):
        """Регистрация callbacks"""
        try:
            # Callback для изменения отношений
            self.relationship_callbacks.append(self._on_relationship_changed)
            
            # Callback для изменения репутации
            self.reputation_callbacks.append(self._on_reputation_changed)
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации callbacks: {e}")

    def create_social_profile(self, entity_id: str, social_status: SocialStatus = SocialStatus.CITIZEN,
                            faction: Optional[FactionType] = None) -> bool:
        """Создание социального профиля"""
        try:
            if entity_id in self.social_profiles:
                self.logger.warning(f"Социальный профиль для {entity_id} уже существует")
                return False
            
            # Создание профиля
            profile = SocialProfile(
                entity_id=entity_id,
                social_status=social_status,
                faction=faction
            )
            
            # Инициализация репутации
            for rep_type in ReputationType:
                profile.reputation[rep_type] = Reputation(
                    entity_id=entity_id,
                    reputation_type=rep_type
                )
            
            # Инициализация черт личности
            profile.personality_traits = {
                "openness": random.uniform(0.0, 1.0),
                "conscientiousness": random.uniform(0.0, 1.0),
                "extraversion": random.uniform(0.0, 1.0),
                "agreeableness": random.uniform(0.0, 1.0),
                "neuroticism": random.uniform(0.0, 1.0)
            }
            
            # Инициализация социальных навыков
            profile.social_skills = {
                "persuasion": random.uniform(0.0, 1.0),
                "intimidation": random.uniform(0.0, 1.0),
                "deception": random.uniform(0.0, 1.0),
                "insight": random.uniform(0.0, 1.0),
                "performance": random.uniform(0.0, 1.0)
            }
            
            self.social_profiles[entity_id] = profile
            self.stats["total_relationships"] += 1
            
            self.logger.info(f"Создан социальный профиль для {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания социального профиля: {e}")
            return False

    def initiate_interaction(self, initiator_id: str, target_id: str, 
                           interaction_type: InteractionType, duration: float = 0.0,
                           context: Dict[str, Any] = None) -> Optional[str]:
        """Инициация социального взаимодействия"""
        try:
            # Проверка существования профилей
            if initiator_id not in self.social_profiles:
                self.create_social_profile(initiator_id)
            
            if target_id not in self.social_profiles:
                self.create_social_profile(target_id)
            
            # Проверка кулдауна
            if not self._check_interaction_cooldown(initiator_id, target_id):
                self.logger.warning(f"Кулдаун взаимодействия между {initiator_id} и {target_id}")
                return None
            
            # Создание взаимодействия
            interaction_id = f"interaction_{initiator_id}_{target_id}_{int(time.time())}"
            interaction = Interaction(
                interaction_id=interaction_id,
                initiator_id=initiator_id,
                target_id=target_id,
                interaction_type=interaction_type,
                duration=duration,
                context=context or {}
            )
            
            # Расчет влияния взаимодействия
            impact = self._calculate_interaction_impact(interaction)
            interaction.impact = impact
            
            # Применение влияния
            self._apply_interaction_impact(interaction)
            
            # Обновление профилей
            self._update_profiles_after_interaction(interaction)
            
            # Добавление в историю
            self.interactions.append(interaction)
            self.stats["total_interactions"] += 1
            
            # Уведомление о взаимодействии
            self._notify_interaction_completed(interaction)
            
            self.logger.info(f"Взаимодействие {interaction_id} завершено")
            return interaction_id
            
        except Exception as e:
            self.logger.error(f"Ошибка инициации взаимодействия: {e}")
            return None

    def _calculate_interaction_impact(self, interaction: Interaction) -> Dict[str, float]:
        """Расчет влияния взаимодействия"""
        try:
            initiator_profile = self.social_profiles[interaction.initiator_id]
            target_profile = self.social_profiles[interaction.target_id]
            
            impact = {}
            
            # Базовое влияние в зависимости от типа взаимодействия
            base_impact = {
                InteractionType.GREETING: {"trust": 0.1, "respect": 0.05},
                InteractionType.CONVERSATION: {"trust": 0.2, "respect": 0.1},
                InteractionType.GIFT: {"trust": 0.3, "affection": 0.2},
                InteractionType.HELP: {"trust": 0.4, "respect": 0.3},
                InteractionType.TRADE: {"trust": 0.1, "respect": 0.1},
                InteractionType.COMBAT: {"fear": 0.3, "respect": -0.2},
                InteractionType.COOPERATION: {"trust": 0.3, "respect": 0.2},
                InteractionType.COMPETITION: {"respect": 0.2, "fear": 0.1}
            }
            
            base = base_impact.get(interaction.interaction_type, {})
            
            # Модификаторы на основе личности
            personality_modifier = self._calculate_personality_modifier(initiator_profile, target_profile)
            
            # Модификаторы на основе навыков
            skill_modifier = self._calculate_skill_modifier(initiator_profile, interaction.interaction_type)
            
            # Применение модификаторов
            for key, value in base.items():
                modified_value = value * personality_modifier * skill_modifier
                impact[key] = max(-1.0, min(1.0, modified_value))
            
            return impact
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета влияния взаимодействия: {e}")
            return {}

    def _calculate_personality_modifier(self, initiator: SocialProfile, target: SocialProfile) -> float:
        """Расчет модификатора на основе личности"""
        try:
            # Совместимость личностей
            compatibility = 0.0
            
            # Открытость
            openness_diff = abs(initiator.personality_traits["openness"] - target.personality_traits["openness"])
            compatibility += (1.0 - openness_diff) * 0.2
            
            # Доброжелательность
            agreeableness_diff = abs(initiator.personality_traits["agreeableness"] - target.personality_traits["agreeableness"])
            compatibility += (1.0 - agreeableness_diff) * 0.2
            
            # Экстраверсия
            extraversion_diff = abs(initiator.personality_traits["extraversion"] - target.personality_traits["extraversion"])
            compatibility += (1.0 - extraversion_diff) * 0.2
            
            # Добросовестность
            conscientiousness_diff = abs(initiator.personality_traits["conscientiousness"] - target.personality_traits["conscientiousness"])
            compatibility += (1.0 - conscientiousness_diff) * 0.2
            
            # Невротизм (обратная корреляция)
            neuroticism_diff = abs(initiator.personality_traits["neuroticism"] - target.personality_traits["neuroticism"])
            compatibility += neuroticism_diff * 0.2
            
            return max(0.1, min(2.0, compatibility))
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета модификатора личности: {e}")
            return 1.0

    def _calculate_skill_modifier(self, profile: SocialProfile, interaction_type: InteractionType) -> float:
        """Расчет модификатора на основе навыков"""
        try:
            skill_mapping = {
                InteractionType.CONVERSATION: "persuasion",
                InteractionType.GIFT: "performance",
                InteractionType.HELP: "insight",
                InteractionType.COMBAT: "intimidation",
                InteractionType.COOPERATION: "persuasion"
            }
            
            relevant_skill = skill_mapping.get(interaction_type, "persuasion")
            skill_level = profile.social_skills.get(relevant_skill, 0.5)
            
            # Модификатор от 0.5 до 1.5
            return 0.5 + skill_level
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета модификатора навыков: {e}")
            return 1.0

    def _apply_interaction_impact(self, interaction: Interaction):
        """Применение влияния взаимодействия"""
        try:
            initiator_id = interaction.initiator_id
            target_id = interaction.target_id
            
            # Обновление отношений
            if target_id not in self.social_profiles[initiator_id].relationships:
                self.social_profiles[initiator_id].relationships[target_id] = Relationship(
                    entity_id=initiator_id,
                    target_id=target_id,
                    relationship_type=RelationshipType.STRANGER
                )
            
            if initiator_id not in self.social_profiles[target_id].relationships:
                self.social_profiles[target_id].relationships[initiator_id] = Relationship(
                    entity_id=target_id,
                    target_id=initiator_id,
                    relationship_type=RelationshipType.STRANGER
                )
            
            # Применение влияния к отношениям
            initiator_relationship = self.social_profiles[initiator_id].relationships[target_id]
            target_relationship = self.social_profiles[target_id].relationships[initiator_id]
            
            for key, value in interaction.impact.items():
                if key == "trust":
                    initiator_relationship.trust_level = max(-1.0, min(1.0, initiator_relationship.trust_level + value))
                    target_relationship.trust_level = max(-1.0, min(1.0, target_relationship.trust_level + value * 0.5))
                elif key == "respect":
                    initiator_relationship.respect_level = max(-1.0, min(1.0, initiator_relationship.respect_level + value))
                    target_relationship.respect_level = max(-1.0, min(1.0, target_relationship.respect_level + value * 0.5))
                elif key == "affection":
                    initiator_relationship.affection_level = max(-1.0, min(1.0, initiator_relationship.affection_level + value))
                    target_relationship.affection_level = max(-1.0, min(1.0, target_relationship.affection_level + value * 0.5))
                elif key == "fear":
                    initiator_relationship.fear_level = max(0.0, min(1.0, initiator_relationship.fear_level + value))
                    target_relationship.fear_level = max(0.0, min(1.0, target_relationship.fear_level + value * 0.5))
            
            # Обновление времени последнего взаимодействия
            initiator_relationship.last_interaction = time.time()
            target_relationship.last_interaction = time.time()
            
            # Увеличение счетчика взаимодействий
            initiator_relationship.interaction_count += 1
            target_relationship.interaction_count += 1
            
            # Эволюция типа отношений
            self._evolve_relationship_type(initiator_relationship)
            self._evolve_relationship_type(target_relationship)
            
        except Exception as e:
            self.logger.error(f"Ошибка применения влияния взаимодействия: {e}")

    def _evolve_relationship_type(self, relationship: Relationship):
        """Эволюция типа отношений"""
        try:
            # Определение нового типа отношений на основе уровней
            trust = relationship.trust_level
            respect = relationship.respect_level
            affection = relationship.affection_level
            fear = relationship.fear_level
            
            new_type = RelationshipType.STRANGER
            
            if fear > 0.7:
                new_type = RelationshipType.ENEMY
            elif affection > 0.7 and trust > 0.5:
                new_type = RelationshipType.LOVER
            elif trust > 0.6 and respect > 0.5:
                new_type = RelationshipType.CLOSE_FRIEND
            elif trust > 0.3 and respect > 0.3:
                new_type = RelationshipType.FRIEND
            elif trust > 0.1 or respect > 0.1:
                new_type = RelationshipType.ACQUAINTANCE
            elif fear > 0.3:
                new_type = RelationshipType.RIVAL
            
            if new_type != relationship.relationship_type:
                relationship.relationship_type = new_type
                self.stats["relationship_evolutions"] += 1
                
                # Уведомление об изменении отношений
                self._notify_relationship_changed(relationship)
                
        except Exception as e:
            self.logger.error(f"Ошибка эволюции типа отношений: {e}")

    def _update_profiles_after_interaction(self, interaction: Interaction):
        """Обновление профилей после взаимодействия"""
        try:
            initiator_profile = self.social_profiles[interaction.initiator_id]
            target_profile = self.social_profiles[interaction.target_id]
            
            # Обновление времени последнего взаимодействия
            initiator_profile.last_interaction = time.time()
            target_profile.last_interaction = time.time()
            
            # Увеличение счетчика взаимодействий
            initiator_profile.interaction_count += 1
            target_profile.interaction_count += 1
            
            # Обучение социальным навыкам
            self._learn_social_skills(initiator_profile, interaction)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления профилей: {e}")

    def _learn_social_skills(self, profile: SocialProfile, interaction: Interaction):
        """Обучение социальным навыкам"""
        try:
            skill_mapping = {
                InteractionType.CONVERSATION: "persuasion",
                InteractionType.GIFT: "performance",
                InteractionType.HELP: "insight",
                InteractionType.COMBAT: "intimidation",
                InteractionType.COOPERATION: "persuasion"
            }
            
            relevant_skill = skill_mapping.get(interaction.interaction_type, "persuasion")
            if relevant_skill in profile.social_skills:
                learning_rate = self.settings["social_skill_learning_rate"]
                current_skill = profile.social_skills[relevant_skill]
                
                # Обучение на основе успеха взаимодействия
                if interaction.success:
                    improvement = learning_rate * (1.0 - current_skill)
                    profile.social_skills[relevant_skill] = min(1.0, current_skill + improvement)
                
        except Exception as e:
            self.logger.error(f"Ошибка обучения социальным навыкам: {e}")

    def _check_interaction_cooldown(self, initiator_id: str, target_id: str) -> bool:
        """Проверка кулдауна взаимодействия"""
        try:
            if initiator_id not in self.social_profiles or target_id not in self.social_profiles:
                return True
            
            initiator_profile = self.social_profiles[initiator_id]
            if target_id in initiator_profile.relationships:
                relationship = initiator_profile.relationships[target_id]
                cooldown_time = self.settings["interaction_cooldown"]
                
                return (time.time() - relationship.last_interaction) >= cooldown_time
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки кулдауна: {e}")
            return True

    def get_relationship(self, entity_id: str, target_id: str) -> Optional[Relationship]:
        """Получение отношений между сущностями"""
        try:
            if entity_id in self.social_profiles:
                return self.social_profiles[entity_id].relationships.get(target_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения отношений: {e}")
            return None

    def get_social_profile(self, entity_id: str) -> Optional[SocialProfile]:
        """Получение социального профиля"""
        return self.social_profiles.get(entity_id)

    def update_reputation(self, entity_id: str, reputation_type: ReputationType, 
                         change: float, source: str = "system"):
        """Обновление репутации"""
        try:
            if entity_id not in self.social_profiles:
                self.create_social_profile(entity_id)
            
            profile = self.social_profiles[entity_id]
            reputation = profile.reputation[reputation_type]
            
            # Обновление значения
            old_value = reputation.value
            reputation.value = max(reputation.min_value, 
                                 min(reputation.max_value, reputation.value + change))
            
            # Запись в историю
            reputation.history.append((time.time(), reputation.value))
            
            # Ограничение истории
            if len(reputation.history) > 100:
                reputation.history = reputation.history[-100:]
            
            reputation.last_update = time.time()
            
            # Уведомление об изменении репутации
            if old_value != reputation.value:
                self.stats["reputation_changes"] += 1
                self._notify_reputation_changed(entity_id, reputation_type, old_value, reputation.value)
                
        except Exception as e:
            self.logger.error(f"Ошибка обновления репутации: {e}")

    def _notify_interaction_completed(self, interaction: Interaction):
        """Уведомление о завершении взаимодействия"""
        try:
            for callback in self.interaction_callbacks.get("completed", []):
                callback(interaction)
        except Exception as e:
            self.logger.error(f"Ошибка уведомления о завершении взаимодействия: {e}")

    def _notify_relationship_changed(self, relationship: Relationship):
        """Уведомление об изменении отношений"""
        try:
            for callback in self.relationship_callbacks:
                callback(relationship)
        except Exception as e:
            self.logger.error(f"Ошибка уведомления об изменении отношений: {e}")

    def _notify_reputation_changed(self, entity_id: str, reputation_type: ReputationType, 
                                 old_value: float, new_value: float):
        """Уведомление об изменении репутации"""
        try:
            for callback in self.reputation_callbacks:
                callback(entity_id, reputation_type, old_value, new_value)
        except Exception as e:
            self.logger.error(f"Ошибка уведомления об изменении репутации: {e}")

    def _on_relationship_changed(self, relationship: Relationship):
        """Callback при изменении отношений"""
        self.logger.debug(f"Отношения изменились: {relationship.entity_id} -> {relationship.target_id}: {relationship.relationship_type.value}")

    def _on_reputation_changed(self, entity_id: str, reputation_type: ReputationType, 
                             old_value: float, new_value: float):
        """Callback при изменении репутации"""
        self.logger.debug(f"Репутация изменилась: {entity_id} {reputation_type.value}: {old_value:.2f} -> {new_value:.2f}")

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            "total_profiles": len(self.social_profiles),
            "total_interactions": len(self.interactions),
            "total_events": len(self.social_events),
            "stats": self.stats.copy()
        }

    def update(self, delta_time: float):
        """Обновление системы социального взаимодействия"""
        try:
            # Обновление репутации (затухание)
            for profile in self.social_profiles.values():
                for reputation in profile.reputation.values():
                    decay_rate = reputation.decay_rate * delta_time
                    if reputation.value > 0:
                        reputation.value = max(0, reputation.value - decay_rate)
                    elif reputation.value < 0:
                        reputation.value = min(0, reputation.value + decay_rate)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления системы социального взаимодействия: {e}")
