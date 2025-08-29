#!/usr/bin/env python3
"""
Система социального взаимодействия - управление отношениями между сущностями
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem
from ...core.architecture import Priority, LifecycleState
from ...core.state_manager import StateManager, StateType, StateScope
from ...core.repository import RepositoryManager, DataType, StorageType
from ...core.constants import (
    RelationshipType, InteractionType, ReputationType, SocialStatus, FactionType, CommunicationChannel,
    PROBABILITY_CONSTANTS, SYSTEM_LIMITS,
    TIME_CONSTANTS_RO, get_float
)

from .social_data import Relationship, Interaction, Reputation

logger = logging.getLogger(__name__)

@dataclass
class SocialProfile:
    """Социальный профиль сущности"""
    entity_id: str
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    reputation: Dict[ReputationType, float] = field(default_factory=dict)
    social_status: SocialStatus = SocialStatus.CITIZEN
    faction: Optional[FactionType] = None
    faction_standing: float = 0.0
    last_interaction: float = field(default_factory=time.time)
    interaction_count: int = 0

@dataclass
class SocialEvent:
    """Социальное событие"""
    event_id: str
    event_type: str
    participants: List[str] = field(default_factory=list)
    location: str = ""
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

class SocialSystem(BaseGameSystem):
    """Система управления социальным взаимодействием - интегрирована с новой архитектурой"""
    
    def __init__(self, state_manager: Optional[StateManager] = None, repository_manager: Optional[RepositoryManager] = None, event_bus=None):
        super().__init__("social", Priority.NORMAL)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = state_manager
        self.repository_manager: Optional[RepositoryManager] = repository_manager
        self.event_bus = event_bus
        
        # Социальные профили (теперь управляются через RepositoryManager)
        self.social_profiles: Dict[str, SocialProfile] = {}
        self.interactions: List[Interaction] = []
        self.social_events: List[SocialEvent] = []
        
        # Фракции (теперь управляются через RepositoryManager)
        self.factions: Dict[FactionType, Dict[str, Any]] = {}
        self.faction_members: Dict[FactionType, List[str]] = {}
        
        # Настройки системы (теперь управляются через StateManager)
        self.system_settings = {
            'max_relationships': SYSTEM_LIMITS["max_relationships"],
            'relationship_decay_rate': PROBABILITY_CONSTANTS["relationship_decay_rate"],
            'interaction_cooldown': get_float(TIME_CONSTANTS_RO, "interaction_cooldown", 300.0),
            'reputation_decay_rate': PROBABILITY_CONSTANTS["reputation_decay_rate"],
            'faction_influence': PROBABILITY_CONSTANTS["faction_influence"],
            'interaction_success_rate': PROBABILITY_CONSTANTS["interaction_success_rate"]
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'total_interactions': 0,
            'total_relationships': 0,
            'active_factions': 0,
            'social_events_count': 0,
            'average_reputation': 0.0,
            'update_time': 0.0
        }
        
        logger.info("Система социального взаимодействия инициализирована с новой архитектурой")
    
    def initialize(self, state_manager: StateManager = None, repository_manager: RepositoryManager = None, event_bus=None) -> bool:
        """Инициализация системы"""
        try:
            if state_manager is not None:
                self.state_manager = state_manager
            if repository_manager is not None:
                self.repository_manager = repository_manager
            if event_bus is not None:
                self.event_bus = event_bus
            
            # Допускаем работу в деградированном режиме без внешних менеджеров
            if not self.state_manager or not self.repository_manager:
                logger.warning("SocialSystem: отсутствуют state_manager или repository_manager — работаем в локальном режиме")
            
            # Регистрация состояний системы
            self._register_system_states()
            
            # Регистрация репозиториев
            self._register_system_repositories()
            
            # Инициализация фракций
            self._initialize_factions()
            
            self.state = LifecycleState.INITIALIZED
            logger.info("Система социального взаимодействия успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы социального взаимодействия: {e}")
            return False
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.register_state(
                "social_system_settings",
                self.system_settings,
                StateType.CONFIGURATION,
                StateScope.SYSTEM
            )
            self.state_manager.register_state(
                "social_system_stats",
                self.system_stats,
                StateType.DYNAMIC_DATA,
                StateScope.SYSTEM
            )
    
    def _register_system_repositories(self):
        """Регистрация репозиториев системы"""
        if self.repository_manager:
            self.repository_manager.create_repository(
                "social_profiles",
                DataType.ENTITY_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "interactions",
                DataType.HISTORY,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "factions",
                DataType.SYSTEM_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "social_events",
                DataType.HISTORY,
                StorageType.MEMORY
            )
    
    def _initialize_factions(self):
        """Инициализация фракций"""
        for faction_type in FactionType:
            self.factions[faction_type] = {
                'name': faction_type.value,
                'description': f"Фракция {faction_type.value}",
                'members_count': 0,
                'influence': 0.0,
                'created_time': time.time()
            }
            self.faction_members[faction_type] = []
    
    def create_social_profile(self, entity_id: str) -> bool:
        """Создание социального профиля для сущности"""
        try:
            if entity_id in self.social_profiles:
                logger.warning(f"Социальный профиль для {entity_id} уже существует")
                return False
            
            profile = SocialProfile(entity_id=entity_id)
            self.social_profiles[entity_id] = profile
            
            logger.info(f"Создан социальный профиль для {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания социального профиля: {e}")
            return False
    
    def create_relationship(self, entity_id: str, target_id: str, relationship_type: RelationshipType, 
                          strength: float = 0.0) -> bool:
        """Создание отношения между сущностями"""
        try:
            # Проверка лимитов
            if entity_id not in self.social_profiles:
                self.create_social_profile(entity_id)
            
            profile = self.social_profiles[entity_id]
            
            if len(profile.relationships) >= self.system_settings['max_relationships']:
                logger.warning(f"Достигнут лимит отношений для {entity_id}")
                return False
            
            # Создание отношения
            relationship = Relationship(
                relationship_id=f"rel_{entity_id}_{target_id}",
                entity_id=entity_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength
            )
            
            profile.relationships[target_id] = relationship
            self.system_stats['total_relationships'] += 1
            
            logger.info(f"Создано отношение {relationship_type.value} между {entity_id} и {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания отношения: {e}")
            return False
    
    def perform_interaction(self, initiator_id: str, target_id: str, interaction_type: InteractionType,
                          success: bool = True, data: Dict[str, Any] = None) -> bool:
        """Выполнение взаимодействия между сущностями"""
        try:
            if data is None:
                data = {}
            
            # Создание профилей если не существуют
            if initiator_id not in self.social_profiles:
                self.create_social_profile(initiator_id)
            if target_id not in self.social_profiles:
                self.create_social_profile(target_id)
            
            # Создание взаимодействия
            interaction = Interaction(
                interaction_id=f"int_{initiator_id}_{target_id}_{int(time.time())}",
                initiator_id=initiator_id,
                target_id=target_id,
                interaction_type=interaction_type,
                success=success,
                data=data,
                timestamp=time.time()
            )
            
            self.interactions.append(interaction)
            
            # Обновление отношений
            self._update_relationships_from_interaction(interaction)
            
            # Обновление репутации
            self._update_reputation_from_interaction(interaction)
            
            # Обновление статистики
            self.system_stats['total_interactions'] += 1
            
            # Создание социального события
            self._create_social_event(interaction)
            
            logger.info(f"Выполнено взаимодействие {interaction_type.value} между {initiator_id} и {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выполнения взаимодействия: {e}")
            return False
    
    def _update_relationships_from_interaction(self, interaction: Interaction):
        """Обновление отношений на основе взаимодействия"""
        try:
            initiator_id = interaction.initiator_id
            target_id = interaction.target_id
            
            # Определение изменения силы отношения
            relationship_change = 0.0
            
            if interaction.success:
                if interaction.interaction_type in [InteractionType.GREETING, InteractionType.CONVERSATION]:
                    relationship_change = 1.0
                elif interaction.interaction_type in [InteractionType.GIFT_GIVING, InteractionType.HELP_OFFERED]:
                    relationship_change = 5.0
                elif interaction.interaction_type in [InteractionType.EMOTIONAL_SUPPORT, InteractionType.EMPATHY_SHARED]:
                    relationship_change = 3.0
                elif interaction.interaction_type in [InteractionType.ARGUMENT, InteractionType.INSULT]:
                    relationship_change = -2.0
                elif interaction.interaction_type in [InteractionType.VIOLENCE, InteractionType.BETRAYAL]:
                    relationship_change = -10.0
            else:
                relationship_change = -1.0
            
            # Обновление отношений
            if initiator_id in self.social_profiles:
                profile = self.social_profiles[initiator_id]
                if target_id in profile.relationships:
                    relationship = profile.relationships[target_id]
                    relationship.strength = max(-100.0, min(100.0, relationship.strength + relationship_change))
                    relationship.last_interaction = interaction.timestamp
                else:
                    # Создание нового отношения
                    relationship_type = RelationshipType.STRANGER
                    if relationship_change > 0:
                        relationship_type = RelationshipType.ACQUAINTANCE
                    elif relationship_change < -5:
                        relationship_type = RelationshipType.ENEMY
                    
                    self.create_relationship(initiator_id, target_id, relationship_type, relationship_change)
            
        except Exception as e:
            logger.error(f"Ошибка обновления отношений: {e}")
    
    def _update_reputation_from_interaction(self, interaction: Interaction):
        """Обновление репутации на основе взаимодействия"""
        try:
            initiator_id = interaction.initiator_id
            
            if initiator_id not in self.social_profiles:
                return
            
            profile = self.social_profiles[initiator_id]
            
            # Определение изменения репутации
            reputation_change = 0.0
            
            if interaction.success:
                if interaction.interaction_type in [InteractionType.HELP_OFFERED, InteractionType.GIFT_GIVING]:
                    reputation_change = 2.0
                elif interaction.interaction_type in [InteractionType.EMOTIONAL_SUPPORT, InteractionType.EMPATHY_SHARED]:
                    reputation_change = 1.5
                elif interaction.interaction_type in [InteractionType.KNOWLEDGE_SHARED, InteractionType.SKILL_TAUGHT]:
                    reputation_change = 3.0
                elif interaction.interaction_type in [InteractionType.VIOLENCE, InteractionType.BETRAYAL]:
                    reputation_change = -5.0
            else:
                reputation_change = -1.0
            
            # Обновление общей репутации
            current_reputation = profile.reputation.get(ReputationType.GENERAL, 0.0)
            profile.reputation[ReputationType.GENERAL] = max(-100.0, min(100.0, current_reputation + reputation_change))
            
            # Обновление специализированной репутации
            if interaction.interaction_type in [InteractionType.COMBAT_SKILL, InteractionType.BRAVERY]:
                current_combat_rep = profile.reputation.get(ReputationType.COMBAT_SKILL, 0.0)
                profile.reputation[ReputationType.COMBAT_SKILL] = max(-100.0, min(100.0, current_combat_rep + reputation_change))
            
        except Exception as e:
            logger.error(f"Ошибка обновления репутации: {e}")
    
    def _create_social_event(self, interaction: Interaction):
        """Создание социального события"""
        try:
            event = SocialEvent(
                event_id=f"event_{interaction.interaction_id}",
                event_type=interaction.interaction_type.value,
                participants=[interaction.initiator_id, interaction.target_id],
                timestamp=interaction.timestamp,
                data=interaction.data
            )
            
            self.social_events.append(event)
            self.system_stats['social_events_count'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка создания социального события: {e}")
    
    def join_faction(self, entity_id: str, faction_type: FactionType) -> bool:
        """Вступление в фракцию"""
        try:
            if entity_id not in self.social_profiles:
                self.create_social_profile(entity_id)
            
            profile = self.social_profiles[entity_id]
            
            # Проверка, не состоит ли уже в другой фракции
            if profile.faction and profile.faction != faction_type:
                logger.warning(f"{entity_id} уже состоит в фракции {profile.faction.value}")
                return False
            
            # Вступление в фракцию
            profile.faction = faction_type
            profile.faction_standing = 0.0
            
            if faction_type not in self.faction_members:
                self.faction_members[faction_type] = []
            
            if entity_id not in self.faction_members[faction_type]:
                self.faction_members[faction_type].append(entity_id)
                self.factions[faction_type]['members_count'] += 1
            
            logger.info(f"{entity_id} вступил в фракцию {faction_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка вступления в фракцию: {e}")
            return False
    
    def leave_faction(self, entity_id: str) -> bool:
        """Выход из фракции"""
        try:
            if entity_id not in self.social_profiles:
                return False
            
            profile = self.social_profiles[entity_id]
            
            if not profile.faction:
                logger.warning(f"{entity_id} не состоит ни в одной фракции")
                return False
            
            faction_type = profile.faction
            
            # Выход из фракции
            if entity_id in self.faction_members[faction_type]:
                self.faction_members[faction_type].remove(entity_id)
                self.factions[faction_type]['members_count'] -= 1
            
            profile.faction = None
            profile.faction_standing = 0.0
            
            logger.info(f"{entity_id} покинул фракцию {faction_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выхода из фракции: {e}")
            return False
    
    def get_relationship(self, entity_id: str, target_id: str) -> Optional[Relationship]:
        """Получение отношения между сущностями"""
        if entity_id in self.social_profiles:
            profile = self.social_profiles[entity_id]
            return profile.relationships.get(target_id)
        return None
    
    def get_reputation(self, entity_id: str, reputation_type: ReputationType = ReputationType.GENERAL) -> float:
        """Получение репутации сущности"""
        if entity_id in self.social_profiles:
            profile = self.social_profiles[entity_id]
            return profile.reputation.get(reputation_type, 0.0)
        return 0.0
    
    def get_faction_members(self, faction_type: FactionType) -> List[str]:
        """Получение членов фракции"""
        return self.faction_members.get(faction_type, [])
    
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        try:
            current_time = time.time()
            
            # Обновление отношений (затухание)
            self._update_relationships_decay(delta_time)
            
            # Обновление репутации (затухание)
            self._update_reputation_decay(delta_time)
            
            # Обновление влияния фракций
            self._update_faction_influence(delta_time)
            
            # Обновление статистики
            self.system_stats['update_time'] = current_time
            self.system_stats['total_relationships'] = sum(
                len(profile.relationships) for profile in self.social_profiles.values()
            )
            self.system_stats['active_factions'] = sum(
                1 for faction in self.factions.values() if faction['members_count'] > 0
            )
            
            # Расчет средней репутации
            total_reputation = 0.0
            reputation_count = 0
            for profile in self.social_profiles.values():
                for reputation in profile.reputation.values():
                    total_reputation += reputation
                    reputation_count += 1
            
            if reputation_count > 0:
                self.system_stats['average_reputation'] = total_reputation / reputation_count
            
            # Обновление состояний в StateManager
            if self.state_manager:
                self.state_manager.update_state("social_system_stats", self.system_stats)
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы социального взаимодействия: {e}")
    
    def _update_relationships_decay(self, delta_time: float):
        """Обновление затухания отношений"""
        try:
            decay_rate = self.system_settings['relationship_decay_rate'] * delta_time
            
            for profile in self.social_profiles.values():
                for relationship in profile.relationships.values():
                    # Затухание только для старых отношений
                    time_since_last = time.time() - relationship.last_interaction
                    if time_since_last > get_float(TIME_CONSTANTS_RO, "relationship_update_interval", 3600.0):
                        relationship.strength *= (1.0 - decay_rate)
                        
        except Exception as e:
            logger.error(f"Ошибка обновления затухания отношений: {e}")
    
    def _update_reputation_decay(self, delta_time: float):
        """Обновление затухания репутации"""
        try:
            decay_rate = self.system_settings['reputation_decay_rate'] * delta_time
            
            for profile in self.social_profiles.values():
                for reputation_type, reputation_value in profile.reputation.items():
                    if reputation_type != ReputationType.GENERAL:  # Общая репутация не затухает
                        profile.reputation[reputation_type] = reputation_value * (1.0 - decay_rate)
                        
        except Exception as e:
            logger.error(f"Ошибка обновления затухания репутации: {e}")
    
    def _update_faction_influence(self, delta_time: float):
        """Обновление влияния фракций"""
        try:
            for faction_type, faction_data in self.factions.items():
                members_count = faction_data['members_count']
                if members_count > 0:
                    # Влияние фракции зависит от количества членов
                    faction_data['influence'] = min(100.0, members_count * self.system_settings['faction_influence'])
                    
        except Exception as e:
            logger.error(f"Ошибка обновления влияния фракций: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получить информацию о системе"""
        return {
            "system_name": "SocialSystem",
            "state": self.state.value,
            "settings": self.system_settings,
            "stats": self.system_stats,
            "social_profiles_count": len(self.social_profiles),
            "interactions_count": len(self.interactions),
            "factions_count": len(self.factions),
            "social_events_count": len(self.social_events)
        }
