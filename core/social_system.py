#!/usr/bin/env python3
"""
Система социального взаимодействия и фракций для эволюционной адаптации.
Управляет отношениями, фракциями, дипломатией и социальными событиями.
"""

import random
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FactionType(Enum):
    """Типы фракций"""
    EVOLUTIONISTS = "evolutionists"
    TRADITIONALISTS = "traditionalists"
    TECHNOCRATS = "technocrats"
    MYSTICS = "mystics"
    OUTLAWS = "outlaws"
    NEUTRALS = "neutrals"


class RelationshipType(Enum):
    """Типы отношений"""
    ALLY = "ally"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    ENEMY = "enemy"


class SocialAction(Enum):
    """Социальные действия"""
    GREET = "greet"
    TRADE = "trade"
    HELP = "help"
    ATTACK = "attack"
    GIFT = "gift"
    DIPLOMACY = "diplomacy"
    ESPIONAGE = "espionage"
    ALLIANCE = "alliance"


class NPCPersonality(Enum):
    """Типы личности NPC"""
    AGGRESSIVE = "aggressive"
    FRIENDLY = "friendly"
    CAUTIOUS = "cautious"
    GREEDY = "greedy"
    HELPFUL = "helpful"
    SUSPICIOUS = "suspicious"
    NEUTRAL = "neutral"


@dataclass
class Faction:
    """Фракция"""
    faction_id: str
    name: str
    faction_type: FactionType
    description: str
    leader: str
    population: int
    territory: List[str]  # список локаций
    resources: Dict[str, int]
    military_strength: int
    technology_level: int
    influence: float = 50.0
    reputation: float = 50.0
    goals: List[str] = field(default_factory=list)
    enemies: Set[str] = field(default_factory=set)
    allies: Set[str] = field(default_factory=set)
    
    def get_power_level(self) -> float:
        """Получение уровня силы фракции"""
        return (self.military_strength * 0.4 + 
                self.technology_level * 0.3 + 
                self.influence * 0.2 + 
                self.population * 0.1)
    
    def can_afford_action(self, action_cost: Dict[str, int]) -> bool:
        """Проверка возможности выполнения действия"""
        for resource, amount in action_cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True
    
    def spend_resources(self, cost: Dict[str, int]):
        """Трата ресурсов"""
        for resource, amount in cost.items():
            if resource in self.resources:
                self.resources[resource] = max(0, self.resources[resource] - amount)


@dataclass
class NPC:
    """NPC персонаж"""
    npc_id: str
    name: str
    faction_id: str
    role: str
    personality: Dict[str, float]  # черты характера
    skills: Dict[str, int]
    relationships: Dict[str, float]  # npc_id -> отношение
    current_location: str
    schedule: Dict[str, str]  # время -> локация
    is_alive: bool = True
    influence: float = 10.0
    
    def get_relationship_with(self, other_npc_id: str) -> float:
        """Получение отношения к другому NPC"""
        return self.relationships.get(other_npc_id, 0.0)
    
    def update_relationship(self, other_npc_id: str, change: float):
        """Обновление отношения"""
        current = self.relationships.get(other_npc_id, 0.0)
        self.relationships[other_npc_id] = max(-100.0, min(100.0, current + change))
    
    def get_personality_trait(self, trait: str) -> float:
        """Получение черты характера"""
        return self.personality.get(trait, 0.5)


@dataclass
class SocialEvent:
    """Социальное событие"""
    event_id: str
    event_type: str
    title: str
    description: str
    participants: List[str]  # npc_ids
    location: str
    start_time: float
    duration: float
    requirements: Dict[str, Any]
    consequences: Dict[str, Any]
    is_active: bool = True
    
    def is_ongoing(self) -> bool:
        """Проверка активности события"""
        current_time = time.time()
        return (self.is_active and 
                current_time >= self.start_time and 
                current_time <= self.start_time + self.duration)


@dataclass
class DiplomaticAction:
    """Дипломатическое действие"""
    action_id: str
    action_type: SocialAction
    initiator_id: str
    target_id: str
    parameters: Dict[str, Any]
    success_chance: float
    consequences: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    is_completed: bool = False
    result: Optional[Dict[str, Any]] = None


class RelationshipManager:
    """Менеджер отношений"""
    
    def __init__(self):
        self.faction_relationships: Dict[Tuple[str, str], float] = {}
        self.npc_relationships: Dict[Tuple[str, str], float] = {}
        self.player_relationships: Dict[str, float] = {}
        
    def get_faction_relationship(self, faction1_id: str, faction2_id: str) -> float:
        """Получение отношения между фракциями"""
        key = tuple(sorted([faction1_id, faction2_id]))
        return self.faction_relationships.get(key, 0.0)
    
    def update_faction_relationship(self, faction1_id: str, faction2_id: str, change: float):
        """Обновление отношения между фракциями"""
        key = tuple(sorted([faction1_id, faction2_id]))
        current = self.faction_relationships.get(key, 0.0)
        self.faction_relationships[key] = max(-100.0, min(100.0, current + change))
    
    def get_npc_relationship(self, npc1_id: str, npc2_id: str) -> float:
        """Получение отношения между NPC"""
        key = tuple(sorted([npc1_id, npc2_id]))
        return self.npc_relationships.get(key, 0.0)
    
    def update_npc_relationship(self, npc1_id: str, npc2_id: str, change: float):
        """Обновление отношения между NPC"""
        key = tuple(sorted([npc1_id, npc2_id]))
        current = self.npc_relationships.get(key, 0.0)
        self.npc_relationships[key] = max(-100.0, min(100.0, current + change))
    
    def get_player_relationship(self, target_id: str) -> float:
        """Получение отношения игрока к цели"""
        return self.player_relationships.get(target_id, 0.0)
    
    def update_player_relationship(self, target_id: str, change: float):
        """Обновление отношения игрока к цели"""
        current = self.player_relationships.get(target_id, 0.0)
        self.player_relationships[target_id] = max(-100.0, min(100.0, current + change))


class SocialEventGenerator:
    """Генератор социальных событий"""
    
    def __init__(self):
        self.event_templates = self._load_event_templates()
    
    def _load_event_templates(self) -> Dict[str, Dict]:
        """Загрузка шаблонов событий"""
        return {
            "faction_meeting": {
                "title": "Встреча фракций",
                "description": "Представители фракций собираются для обсуждения важных вопросов",
                "duration": 3600.0,  # 1 час
                "min_participants": 2,
                "max_participants": 5
            },
            "trade_agreement": {
                "title": "Торговое соглашение",
                "description": "Фракции заключают торговое соглашение",
                "duration": 1800.0,  # 30 минут
                "min_participants": 2,
                "max_participants": 3
            },
            "alliance_formation": {
                "title": "Образование альянса",
                "description": "Фракции объединяются в альянс",
                "duration": 7200.0,  # 2 часа
                "min_participants": 2,
                "max_participants": 4
            },
            "conflict_resolution": {
                "title": "Разрешение конфликта",
                "description": "Попытка мирного разрешения конфликта",
                "duration": 5400.0,  # 1.5 часа
                "min_participants": 2,
                "max_participants": 6
            }
        }
    
    def generate_event(self, event_type: str, participants: List[str], 
                      location: str, start_time: float = None) -> SocialEvent:
        """Генерация социального события"""
        if event_type not in self.event_templates:
            raise ValueError(f"Неизвестный тип события: {event_type}")
        
        template = self.event_templates[event_type]
        
        if start_time is None:
            start_time = time.time()
        
        event_id = f"event_{event_type}_{int(start_time)}_{random.randint(1000, 9999)}"
        
        return SocialEvent(
            event_id=event_id,
            event_type=event_type,
            title=template["title"],
            description=template["description"],
            participants=participants,
            location=location,
            start_time=start_time,
            duration=template["duration"],
            requirements={},
            consequences={}
        )


class SocialSystem:
    """Система социального взаимодействия"""
    
    def __init__(self):
        self.factions: Dict[str, Faction] = {}
        self.npcs: Dict[str, NPC] = {}
        self.social_events: Dict[str, SocialEvent] = {}
        self.diplomatic_actions: List[DiplomaticAction] = []
        self.relationship_manager = RelationshipManager()
        self.event_generator = SocialEventGenerator()
        
        # Инициализация фракций
        self._init_factions()
        
        # Инициализация NPC
        self._init_npcs()
        
        logger.info("Система социального взаимодействия инициализирована")
    
    def _init_factions(self):
        """Инициализация фракций"""
        factions_data = {
            "evolutionists": {
                "name": "Эволюционисты",
                "faction_type": FactionType.EVOLUTIONISTS,
                "description": "Сторонники быстрой эволюции и генетических экспериментов",
                "leader": "Доктор Эволюция",
                "population": 1000,
                "territory": ["genetic_lab", "research_center"],
                "resources": {"genetic_material": 100, "technology": 50},
                "military_strength": 200,
                "technology_level": 8,
                "goals": ["genetic_perfection", "evolution_acceleration"]
            },
            "traditionalists": {
                "name": "Традиционалисты",
                "faction_type": FactionType.TRADITIONALISTS,
                "description": "Защитники традиционных ценностей и медленной эволюции",
                "leader": "Страж Традиций",
                "population": 1500,
                "territory": ["temple", "library"],
                "resources": {"knowledge": 200, "artifacts": 30},
                "military_strength": 150,
                "technology_level": 4,
                "goals": ["preserve_traditions", "slow_evolution"]
            },
            "technocrats": {
                "name": "Технократы",
                "faction_type": FactionType.TECHNOCRATS,
                "description": "Поклонники технологического прогресса",
                "leader": "Инженер Прогресс",
                "population": 800,
                "territory": ["tech_lab", "factory"],
                "resources": {"technology": 150, "materials": 100},
                "military_strength": 300,
                "technology_level": 9,
                "goals": ["technological_dominance", "automation"]
            }
        }
        
        for faction_id, data in factions_data.items():
            faction = Faction(
                faction_id=faction_id,
                name=data["name"],
                faction_type=data["faction_type"],
                description=data["description"],
                leader=data["leader"],
                population=data["population"],
                territory=data["territory"],
                resources=data["resources"],
                military_strength=data["military_strength"],
                technology_level=data["technology_level"],
                goals=data["goals"]
            )
            self.factions[faction_id] = faction
    
    def _init_npcs(self):
        """Инициализация NPC"""
        npcs_data = {
            "dr_evolution": {
                "name": "Доктор Эволюция",
                "faction_id": "evolutionists",
                "role": "leader",
                "personality": {"ambition": 0.9, "intelligence": 0.8, "ruthlessness": 0.7},
                "skills": {"genetics": 10, "leadership": 8, "science": 9},
                "current_location": "genetic_lab",
                "schedule": {"morning": "genetic_lab", "afternoon": "research_center", "evening": "genetic_lab"}
            },
            "guardian_traditions": {
                "name": "Страж Традиций",
                "faction_id": "traditionalists",
                "role": "leader",
                "personality": {"wisdom": 0.9, "patience": 0.8, "conservatism": 0.9},
                "skills": {"diplomacy": 9, "knowledge": 10, "defense": 7},
                "current_location": "temple",
                "schedule": {"morning": "temple", "afternoon": "library", "evening": "temple"}
            },
            "engineer_progress": {
                "name": "Инженер Прогресс",
                "faction_id": "technocrats",
                "role": "leader",
                "personality": {"innovation": 0.9, "efficiency": 0.8, "pragmatism": 0.7},
                "skills": {"engineering": 10, "technology": 9, "management": 8},
                "current_location": "tech_lab",
                "schedule": {"morning": "tech_lab", "afternoon": "factory", "evening": "tech_lab"}
            }
        }
        
        for npc_id, data in npcs_data.items():
            npc = NPC(
                npc_id=npc_id,
                name=data["name"],
                faction_id=data["faction_id"],
                role=data["role"],
                personality=data["personality"],
                skills=data["skills"],
                relationships={},
                current_location=data["current_location"],
                schedule=data["schedule"]
            )
            self.npcs[npc_id] = npc
    
    def perform_social_action(self, action_type: SocialAction, initiator_id: str, 
                            target_id: str, parameters: Dict[str, Any] = None) -> bool:
        """Выполнение социального действия"""
        if parameters is None:
            parameters = {}
        
        # Создание дипломатического действия
        action = DiplomaticAction(
            action_id=f"action_{int(time.time())}_{random.randint(1000, 9999)}",
            action_type=action_type,
            initiator_id=initiator_id,
            target_id=target_id,
            parameters=parameters,
            success_chance=self._calculate_success_chance(action_type, initiator_id, target_id),
            consequences=self._get_action_consequences(action_type, parameters)
        )
        
        # Выполнение действия
        success = random.random() < action.success_chance
        action.is_completed = True
        action.result = {
            "success": success,
            "relationship_change": self._calculate_relationship_change(action_type, success, parameters)
        }
        
        # Применение последствий
        self._apply_action_consequences(action)
        
        self.diplomatic_actions.append(action)
        logger.info(f"Социальное действие: {action_type.value} - {'успех' if success else 'неудача'}")
        
        return success
    
    def _calculate_success_chance(self, action_type: SocialAction, initiator_id: str, 
                                 target_id: str) -> float:
        """Расчёт шанса успеха действия"""
        base_chance = 0.5
        
        # Модификаторы на основе отношений
        relationship = self.relationship_manager.get_faction_relationship(initiator_id, target_id)
        relationship_modifier = relationship / 100.0
        
        # Модификаторы на основе типа действия
        action_modifiers = {
            SocialAction.GREET: 0.9,
            SocialAction.TRADE: 0.7,
            SocialAction.HELP: 0.8,
            SocialAction.ATTACK: 0.6,
            SocialAction.GIFT: 0.8,
            SocialAction.DIPLOMACY: 0.6,
            SocialAction.ESPIONAGE: 0.4,
            SocialAction.ALLIANCE: 0.3
        }
        
        action_modifier = action_modifiers.get(action_type, 0.5)
        
        return min(0.95, max(0.05, base_chance + relationship_modifier + action_modifier))
    
    def _calculate_relationship_change(self, action_type: SocialAction, success: bool, 
                                     parameters: Dict[str, Any]) -> float:
        """Расчёт изменения отношений"""
        base_change = 0.0
        
        if success:
            if action_type == SocialAction.GREET:
                base_change = 5.0
            elif action_type == SocialAction.TRADE:
                base_change = 10.0
            elif action_type == SocialAction.HELP:
                base_change = 15.0
            elif action_type == SocialAction.GIFT:
                base_change = 20.0
            elif action_type == SocialAction.DIPLOMACY:
                base_change = 25.0
            elif action_type == SocialAction.ALLIANCE:
                base_change = 50.0
        else:
            if action_type == SocialAction.ATTACK:
                base_change = -30.0
            elif action_type == SocialAction.ESPIONAGE:
                base_change = -20.0
            else:
                base_change = -5.0
        
        # Модификаторы на основе параметров
        if "gift_value" in parameters:
            base_change *= (parameters["gift_value"] / 100.0)
        
        return base_change
    
    def _get_action_consequences(self, action_type: SocialAction, 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Получение последствий действия"""
        consequences = {}
        
        if action_type == SocialAction.TRADE:
            consequences["resource_exchange"] = parameters.get("resources", {})
        elif action_type == SocialAction.ALLIANCE:
            consequences["alliance_formation"] = True
        elif action_type == SocialAction.ATTACK:
            consequences["military_conflict"] = True
        
        return consequences
    
    def _apply_action_consequences(self, action: DiplomaticAction):
        """Применение последствий действия"""
        if not action.is_completed or not action.result:
            return
        
        # Обновление отношений
        relationship_change = action.result["relationship_change"]
        self.relationship_manager.update_faction_relationship(
            action.initiator_id, action.target_id, relationship_change
        )
        
        # Применение специфических последствий
        if "alliance_formation" in action.consequences and action.result["success"]:
            self._form_alliance(action.initiator_id, action.target_id)
        elif "military_conflict" in action.consequences:
            self._start_conflict(action.initiator_id, action.target_id)
    
    def _form_alliance(self, faction1_id: str, faction2_id: str):
        """Образование альянса"""
        if faction1_id in self.factions and faction2_id in self.factions:
            faction1 = self.factions[faction1_id]
            faction2 = self.factions[faction2_id]
            
            faction1.allies.add(faction2_id)
            faction2.allies.add(faction1_id)
            
            logger.info(f"Образован альянс между {faction1.name} и {faction2.name}")
    
    def _start_conflict(self, faction1_id: str, faction2_id: str):
        """Начало конфликта"""
        if faction1_id in self.factions and faction2_id in self.factions:
            faction1 = self.factions[faction1_id]
            faction2 = self.factions[faction2_id]
            
            faction1.enemies.add(faction2_id)
            faction2.enemies.add(faction1_id)
            
            logger.info(f"Начался конфликт между {faction1.name} и {faction2.name}")
    
    def create_social_event(self, event_type: str, participants: List[str], 
                           location: str, start_time: float = None) -> str:
        """Создание социального события"""
        try:
            event = self.event_generator.generate_event(event_type, participants, location, start_time)
            self.social_events[event.event_id] = event
            logger.info(f"Создано социальное событие: {event.title}")
            return event.event_id
        except Exception as e:
            logger.error(f"Ошибка создания события: {e}")
            return None
    
    def get_active_events(self) -> List[SocialEvent]:
        """Получение активных событий"""
        return [event for event in self.social_events.values() if event.is_ongoing()]
    
    def get_faction_info(self, faction_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о фракции"""
        if faction_id not in self.factions:
            return None
        
        faction = self.factions[faction_id]
        return {
            "name": faction.name,
            "type": faction.faction_type.value,
            "description": faction.description,
            "leader": faction.leader,
            "population": faction.population,
            "power_level": faction.get_power_level(),
            "influence": faction.influence,
            "reputation": faction.reputation,
            "allies": list(faction.allies),
            "enemies": list(faction.enemies),
            "goals": faction.goals
        }
    
    def get_npc_info(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о NPC"""
        if npc_id not in self.npcs:
            return None
        
        npc = self.npcs[npc_id]
        return {
            "name": npc.name,
            "faction": npc.faction_id,
            "role": npc.role,
            "personality": npc.personality,
            "skills": npc.skills,
            "current_location": npc.current_location,
            "influence": npc.influence,
            "is_alive": npc.is_alive
        }
    
    def get_social_statistics(self) -> Dict[str, Any]:
        """Получение социальной статистики"""
        return {
            "total_factions": len(self.factions),
            "total_npcs": len(self.npcs),
            "active_events": len(self.get_active_events()),
            "total_relationships": len(self.relationship_manager.faction_relationships),
            "diplomatic_actions": len(self.diplomatic_actions)
        }
