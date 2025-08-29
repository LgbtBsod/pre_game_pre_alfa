#!/usr/bin/env python3
"""
Типы социального взаимодействия и связанные перечисления
"""

from enum import Enum
from typing import Dict, Any

class RelationshipType(Enum):
    """Типы отношений"""
    # Базовые отношения
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    BEST_FRIEND = "best_friend"
    ENEMY = "enemy"
    RIVAL = "rival"
    
    # Семейные отношения
    FAMILY = "family"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    MENTOR = "mentor"
    STUDENT = "student"
    
    # Профессиональные отношения
    COLLEAGUE = "colleague"
    BOSS = "boss"
    SUBORDINATE = "subordinate"
    PARTNER = "partner"
    ALLY = "ally"
    COMPETITOR = "competitor"
    
    # Эволюционные отношения
    EVOLUTION_PARTNER = "evolution_partner"
    GENE_DONOR = "gene_donor"
    MUTATION_BUDDY = "mutation_buddy"
    ADAPTATION_MENTOR = "adaptation_mentor"
    
    # Эмоциональные отношения
    EMOTIONAL_SUPPORT = "emotional_support"
    THERAPIST = "therapist"
    EMPATHY_PARTNER = "empathy_partner"
    COURAGE_INSPIRER = "courage_inspirer"

class InteractionType(Enum):
    """Типы взаимодействий"""
    # Базовые взаимодействия
    GREETING = "greeting"
    CONVERSATION = "conversation"
    GIFT_GIVING = "gift_giving"
    HELP_OFFERED = "help_offered"
    HELP_RECEIVED = "help_received"
    
    # Эмоциональные взаимодействия
    EMOTIONAL_SUPPORT = "emotional_support"
    EMPATHY_SHARED = "empathy_shared"
    COURAGE_GIVEN = "courage_given"
    COMFORT_PROVIDED = "comfort_provided"
    
    # Конфликтные взаимодействия
    ARGUMENT = "argument"
    INSULT = "insult"
    THREAT = "threat"
    VIOLENCE = "violence"
    BETRAYAL = "betrayal"
    
    # Эволюционные взаимодействия
    GENE_SHARING = "gene_sharing"
    MUTATION_HELP = "mutation_help"
    EVOLUTION_GUIDANCE = "evolution_guidance"
    ADAPTATION_TRAINING = "adaptation_training"
    
    # Торговые взаимодействия
    TRADE_FAIR = "trade_fair"
    TRADE_UNFAIR = "trade_unfair"
    SERVICE_PROVIDED = "service_provided"
    SERVICE_RECEIVED = "service_received"
    
    # Образовательные взаимодействия
    KNOWLEDGE_SHARED = "knowledge_shared"
    SKILL_TAUGHT = "skill_taught"
    WISDOM_IMPARTED = "wisdom_imparted"
    EXPERIENCE_SHARED = "experience_shared"

class ReputationType(Enum):
    """Типы репутации"""
    # Общая репутация
    GENERAL = "general"
    HONESTY = "honesty"
    RELIABILITY = "reliability"
    GENEROSITY = "generosity"
    INTELLIGENCE = "intelligence"
    
    # Боевая репутация
    COMBAT_SKILL = "combat_skill"
    BRAVERY = "bravery"
    STRATEGY = "strategy"
    LOYALTY = "loyalty"
    
    # Эволюционная репутация
    EVOLUTION_MASTERY = "evolution_mastery"
    GENE_EXPERTISE = "gene_expertise"
    MUTATION_CONTROL = "mutation_control"
    ADAPTATION_ABILITY = "adaptation_ability"
    
    # Эмоциональная репутация
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY_LEVEL = "empathy_level"
    COURAGE_LEVEL = "courage_level"
    WISDOM_LEVEL = "wisdom_level"
    
    # Торговая репутация
    TRADING_FAIRNESS = "trading_fairness"
    QUALITY_PROVIDER = "quality_provider"
    PRICE_REASONABLE = "price_reasonable"
    SERVICE_QUALITY = "service_quality"

class SocialStatus(Enum):
    """Социальный статус"""
    OUTCAST = "outcast"
    PEASANT = "peasant"
    CITIZEN = "citizen"
    MERCHANT = "merchant"
    NOBLE = "noble"
    ROYAL = "royal"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class FactionType(Enum):
    """Типы фракций"""
    NEUTRAL = "neutral"
    EVOLUTIONISTS = "evolutionists"
    TRADITIONALISTS = "traditionalists"
    EMOTIONALISTS = "emotionalists"
    TECHNOLOGISTS = "technologists"
    MYSTICS = "mystics"
    WARRIORS = "warriors"
    TRADERS = "traders"
    SCHOLARS = "scholars"
    OUTLAWS = "outlaws"

class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    VERBAL = "verbal"
    NONVERBAL = "nonverbal"
    TELEPATHIC = "telepathic"
    EMOTIONAL = "emotional"
    GESTURAL = "gestural"
    WRITTEN = "written"
    DIGITAL = "digital"
    QUANTUM = "quantum"
