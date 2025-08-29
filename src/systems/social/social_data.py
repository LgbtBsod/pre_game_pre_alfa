#!/usr/bin/env python3
"""
Структуры данных для системы социального взаимодействия
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ...core.constants import RelationshipType, InteractionType, ReputationType

@dataclass
class Relationship:
    """Отношение между двумя сущностями"""
    relationship_id: str
    entity_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float = 0.0
    trust_level: float = 0.0
    last_interaction: float = field(default_factory=time.time)
    interaction_count: int = 0
    shared_experiences: List[str] = field(default_factory=list)
    notes: str = ""
    
    def update_strength(self, change: float):
        """Обновление силы отношения"""
        self.strength = max(-100.0, min(100.0, self.strength + change))
    
    def update_trust(self, change: float):
        """Обновление уровня доверия"""
        self.trust_level = max(0.0, min(100.0, self.trust_level + change))
    
    def add_experience(self, experience_id: str):
        """Добавление общего опыта"""
        if experience_id not in self.shared_experiences:
            self.shared_experiences.append(experience_id)
    
    def get_relationship_status(self) -> str:
        """Получение статуса отношения"""
        if self.strength >= 80:
            return "excellent"
        elif self.strength >= 60:
            return "good"
        elif self.strength >= 40:
            return "neutral"
        elif self.strength >= 20:
            return "poor"
        else:
            return "hostile"

@dataclass
class Interaction:
    """Взаимодействие между сущностями"""
    interaction_id: str
    initiator_id: str
    target_id: str
    interaction_type: InteractionType
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    location: str = ""
    witnesses: List[str] = field(default_factory=list)
    
    def add_witness(self, witness_id: str):
        """Добавление свидетеля взаимодействия"""
        if witness_id not in self.witnesses:
            self.witnesses.append(witness_id)
    
    def get_interaction_summary(self) -> Dict[str, Any]:
        """Получение краткого описания взаимодействия"""
        return {
            "type": self.interaction_type.value,
            "success": self.success,
            "duration": self.duration,
            "location": self.location,
            "witnesses_count": len(self.witnesses)
        }

@dataclass
class Reputation:
    """Репутация сущности"""
    entity_id: str
    reputation_type: ReputationType
    value: float = 0.0
    max_value: float = 100.0
    min_value: float = -100.0
    decay_rate: float = 0.01
    last_update: float = field(default_factory=time.time)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_value(self, change: float, reason: str = ""):
        """Обновление значения репутации"""
        old_value = self.value
        self.value = max(self.min_value, min(self.max_value, self.value + change))
        
        # Запись в историю
        self.history.append({
            "timestamp": time.time(),
            "old_value": old_value,
            "new_value": self.value,
            "change": change,
            "reason": reason
        })
        
        # Ограничение истории
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def apply_decay(self, delta_time: float):
        """Применение затухания репутации"""
        if self.value != 0:
            decay_amount = self.decay_rate * delta_time
            if self.value > 0:
                self.value = max(0, self.value - decay_amount)
            else:
                self.value = min(0, self.value + decay_amount)
    
    def get_reputation_level(self) -> str:
        """Получение уровня репутации"""
        if self.value >= 80:
            return "excellent"
        elif self.value >= 60:
            return "good"
        elif self.value >= 40:
            return "neutral"
        elif self.value >= 20:
            return "poor"
        else:
            return "terrible"

@dataclass
class SocialNetwork:
    """Социальная сеть сущности"""
    entity_id: str
    connections: Dict[str, Relationship] = field(default_factory=dict)
    influence_radius: float = 10.0
    max_connections: int = 50
    network_strength: float = 0.0
    
    def add_connection(self, relationship: Relationship):
        """Добавление связи в сеть"""
        if len(self.connections) < self.max_connections:
            self.connections[relationship.target_id] = relationship
            self._update_network_strength()
    
    def remove_connection(self, target_id: str):
        """Удаление связи из сети"""
        if target_id in self.connections:
            del self.connections[target_id]
            self._update_network_strength()
    
    def _update_network_strength(self):
        """Обновление силы сети"""
        total_strength = sum(rel.strength for rel in self.connections.values())
        self.network_strength = total_strength / max(1, len(self.connections))
    
    def get_influential_connections(self, min_strength: float = 50.0) -> List[Relationship]:
        """Получение влиятельных связей"""
        return [rel for rel in self.connections.values() if rel.strength >= min_strength]
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Получение статистики сети"""
        return {
            "total_connections": len(self.connections),
            "network_strength": self.network_strength,
            "average_relationship_strength": sum(rel.strength for rel in self.connections.values()) / max(1, len(self.connections)),
            "influential_connections": len(self.get_influential_connections())
        }

@dataclass
class SocialEvent:
    """Социальное событие"""
    event_id: str
    event_type: str
    participants: List[str] = field(default_factory=list)
    location: str = ""
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    impact_radius: float = 5.0
    witnesses: List[str] = field(default_factory=list)
    
    def add_participant(self, participant_id: str):
        """Добавление участника события"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)
    
    def add_witness(self, witness_id: str):
        """Добавление свидетеля события"""
        if witness_id not in self.witnesses:
            self.witnesses.append(witness_id)
    
    def get_event_summary(self) -> Dict[str, Any]:
        """Получение краткого описания события"""
        return {
            "type": self.event_type,
            "participants_count": len(self.participants),
            "witnesses_count": len(self.witnesses),
            "duration": self.duration,
            "location": self.location,
            "impact_radius": self.impact_radius
        }

@dataclass
class FactionData:
    """Данные фракции"""
    faction_id: str
    name: str
    description: str = ""
    members: List[str] = field(default_factory=list)
    leader_id: Optional[str] = None
    influence: float = 0.0
    max_influence: float = 100.0
    created_time: float = field(default_factory=time.time)
    policies: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, float] = field(default_factory=dict)  # Отношения с другими фракциями
    
    def add_member(self, member_id: str):
        """Добавление члена фракции"""
        if member_id not in self.members:
            self.members.append(member_id)
    
    def remove_member(self, member_id: str):
        """Удаление члена фракции"""
        if member_id in self.members:
            self.members.remove(member_id)
    
    def set_leader(self, leader_id: str):
        """Назначение лидера фракции"""
        if leader_id in self.members:
            self.leader_id = leader_id
    
    def update_influence(self, change: float):
        """Обновление влияния фракции"""
        self.influence = max(0.0, min(self.max_influence, self.influence + change))
    
    def get_faction_stats(self) -> Dict[str, Any]:
        """Получение статистики фракции"""
        return {
            "members_count": len(self.members),
            "influence": self.influence,
            "has_leader": self.leader_id is not None,
            "age_days": (time.time() - self.created_time) / 86400
        }
