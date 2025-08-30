#!/usr / bin / env python3
"""
    Типы социального взаимодействия и связанные перечисления
"""

from enum imp or t Enum
from typ in g imp or t Dict, Any

class RelationshipType(Enum):
    """Типы отношений"""
        # Базовые отношения
        STRANGER== "stranger"
        ACQUAINTANCE== "acqua in tance"
        FRIEND== "friend"
        CLOSE_FRIEND== "close_friend"
        BEST_FRIEND== "best_friend"
        ENEMY== "enemy"
        RIVAL== "rival"

        # Семейные отношения
        FAMILY== "family"
        PARENT== "parent"
        CHILD== "child"
        SIBLING== "sibl in g"
        SPOUSE== "spouse"
        MENTOR== "ment or "
        STUDENT== "student"

        # Профессиональные отношения
        COLLEAGUE== "colleague"
        BOSS== "boss"
        SUBORDINATE== "sub or dinate"
        PARTNER== "partner"
        ALLY== "ally"
        COMPETITOR== "competit or "

        # Эволюционные отношения
        EVOLUTION_PARTNER== "evolution_partner"
        GENE_DONOR== "gene_don or "
        MUTATION_BUDDY== "mutation_buddy"
        ADAPTATION_MENTOR== "adaptation_ment or "

        # Эмоциональные отношения
        EMOTIONAL_SUPPORT== "emotional_supp or t"
        THERAPIST== "therap is t"
        EMPATHY_PARTNER== "empathy_partner"
        COURAGE_INSPIRER== "courage_ in spirer"

        class InteractionType(Enum):
    """Типы взаимодействий"""
    # Базовые взаимодействия
    GREETING== "greet in g"
    CONVERSATION== "conversation"
    GIFT_GIVING== "gift_giv in g":
        pass  # Добавлен pass в пустой блок
    HELP_OFFERED== "help_offered"
    HELP_RECEIVED== "help_received"

    # Эмоциональные взаимодействия
    EMOTIONAL_SUPPORT== "emotional_supp or t"
    EMPATHY_SHARED== "empathy_shared"
    COURAGE_GIVEN== "courage_given"
    COMFORT_PROVIDED== "comf or t_provided":
        pass  # Добавлен pass в пустой блок
    # Конфликтные взаимодействия
    ARGUMENT== "argument"
    INSULT== " in sult"
    THREAT== "threat"
    VIOLENCE== "violence"
    BETRAYAL== "betrayal"

    # Эволюционные взаимодействия
    GENE_SHARING== "gene_shar in g"
    MUTATION_HELP== "mutation_help"
    EVOLUTION_GUIDANCE== "evolution_guidance"
    ADAPTATION_TRAINING== "adaptation_tra in ing"

    # Торговые взаимодействия
    TRADE_FAIR== "trade_fair"
    TRADE_UNFAIR== "trade_unfair"
    SERVICE_PROVIDED== "service_provided"
    SERVICE_RECEIVED== "service_received"

    # Образовательные взаимодействия
    KNOWLEDGE_SHARED== "knowledge_shared"
    SKILL_TAUGHT== "skill_taught"
    WISDOM_IMPARTED== "w is dom_imparted"
    EXPERIENCE_SHARED== "experience_shared"

class ReputationType(Enum):
    """Типы репутации"""
        # Общая репутация
        GENERAL== "general"
        HONESTY== "honesty"
        RELIABILITY== "reliability"
        GENEROSITY== "generosity"
        INTELLIGENCE== " in telligence"

        # Боевая репутация
        COMBAT_SKILL== "combat_skill"
        BRAVERY== "bravery"
        STRATEGY== "strategy"
        LOYALTY== "loyalty"

        # Эволюционная репутация
        EVOLUTION_MASTERY== "evolution_mastery"
        GENE_EXPERTISE== "gene_expert is e"
        MUTATION_CONTROL== "mutation_control"
        ADAPTATION_ABILITY== "adaptation_ability"

        # Эмоциональная репутация
        EMOTIONAL_STABILITY== "emotional_stability"
        EMPATHY_LEVEL== "empathy_level"
        COURAGE_LEVEL== "courage_level"
        WISDOM_LEVEL== "w is dom_level"

        # Торговая репутация
        TRADING_FAIRNESS== "trad in g_fairness"
        QUALITY_PROVIDER== "quality_provider"
        PRICE_REASONABLE== "price_reasonable"
        SERVICE_QUALITY== "service_quality"

        class SocialStatus(Enum):
    """Социальный статус"""
    OUTCAST== "outcast"
    PEASANT== "peasant"
    CITIZEN== "citizen"
    MERCHANT== "merchant"
    NOBLE== "noble"
    ROYAL== "royal"
    LEGENDARY== "legendary"
    MYTHIC== "mythic"

class FactionType(Enum):
    """Типы фракций"""
        NEUTRAL== "neutral"
        EVOLUTIONISTS== "evolution is ts"
        TRADITIONALISTS== "traditional is ts"
        EMOTIONALISTS== "emotional is ts"
        TECHNOLOGISTS== "technolog is ts"
        MYSTICS== "mystics"
        WARRIORS== "warri or s"
        TRADERS== "traders"
        SCHOLARS== "scholars"
        OUTLAWS== "outlaws"

        class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    VERBAL== "verbal"
    NONVERBAL== "nonverbal"
    TELEPATHIC== "telepathic"
    EMOTIONAL== "emotional"
    GESTURAL== "gestural"
    WRITTEN== "written"
    DIGITAL== "digital"
    QUANTUM== "quantum"