#!/usr/bin/env python3
"""
Типы торговли и связанные перечисления
"""

from enum import Enum
from typing import Dict, Any

class TradeType(Enum):
    """Типы торговли"""
    # Основные типы
    BUY = "buy"
    SELL = "sell"
    EXCHANGE = "exchange"
    AUCTION = "auction"
    BARTER = "barter"
    
    # Специализированные типы
    BULK_TRADE = "bulk_trade"
    CONTRACT_TRADE = "contract_trade"
    FUTURES_TRADE = "futures_trade"
    OPTIONS_TRADE = "options_trade"
    
    # Эволюционные типы
    GENE_TRADE = "gene_trade"
    EVOLUTION_TRADE = "evolution_trade"
    MUTATION_TRADE = "mutation_trade"
    ADAPTATION_TRADE = "adaptation_trade"
    
    # Эмоциональные типы
    EMOTION_TRADE = "emotion_trade"
    EXPERIENCE_TRADE = "experience_trade"
    MEMORY_TRADE = "memory_trade"
    WISDOM_TRADE = "wisdom_trade"

class TradeStatus(Enum):
    """Статусы торговли"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class CurrencyType(Enum):
    """Типы валют"""
    # Основные валюты
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    PLATINUM = "platinum"
    
    # Специальные валюты
    CREDITS = "credits"
    TOKENS = "tokens"
    POINTS = "points"
    FRAGMENTS = "fragments"
    
    # Эволюционные валюты
    EVOLUTION_POINTS = "evolution_points"
    GENE_FRAGMENTS = "gene_fragments"
    MUTATION_CHANCES = "mutation_chances"
    ADAPTATION_BONUS = "adaptation_bonus"
    
    # Эмоциональные валюты
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY_POINTS = "empathy_points"
    COURAGE_POINTS = "courage_points"
    WISDOM_POINTS = "wisdom_points"

class TradeCategory(Enum):
    """Категории торговли"""
    WEAPONS = "weapons"
    ARMOR = "armor"
    CONSUMABLES = "consumables"
    MATERIALS = "materials"
    CURRENCY = "currency"
    SERVICES = "services"
    INFORMATION = "information"
    SKILLS = "skills"
    GENES = "genes"
    EMOTIONS = "emotions"

class TradeRarity(Enum):
    """Редкость торговых предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

class TradeLocation(Enum):
    """Места торговли"""
    MARKETPLACE = "marketplace"
    SHOP = "shop"
    AUCTION_HOUSE = "auction_house"
    BLACK_MARKET = "black_market"
    TRADING_POST = "trading_post"
    CARAVAN = "caravan"
    PORT = "port"
    GUILD_HALL = "guild_hall"
    TEMPLE = "temple"
    ACADEMY = "academy"
