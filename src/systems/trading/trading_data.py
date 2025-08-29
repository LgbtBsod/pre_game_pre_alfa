#!/usr/bin/env python3
"""
Структуры данных для системы торговли
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from .trading_types import TradeType, TradeStatus, CurrencyType, TradeCategory, TradeRarity, TradeLocation

@dataclass
class TradeItem:
    """Торговый предмет"""
    item_id: str
    name: str
    description: str
    category: TradeCategory
    rarity: TradeRarity
    quantity: int = 1
    quality: float = 1.0
    base_price: float = 0.0
    current_price: float = 0.0
    currency_type: CurrencyType = CurrencyType.GOLD
    seller_id: Optional[str] = None
    buyer_id: Optional[str] = None
    trade_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def calculate_price(self, market_conditions: Dict[str, float] = None) -> float:
        """Рассчитать текущую цену предмета"""
        if market_conditions is None:
            market_conditions = {}
        
        price = self.base_price * self.quality * self.quantity
        
        # Применение рыночных условий
        rarity_multiplier = {
            TradeRarity.COMMON: 1.0,
            TradeRarity.UNCOMMON: 1.5,
            TradeRarity.RARE: 3.0,
            TradeRarity.EPIC: 7.0,
            TradeRarity.LEGENDARY: 15.0,
            TradeRarity.MYTHIC: 30.0,
            TradeRarity.DIVINE: 100.0
        }
        
        price *= rarity_multiplier.get(self.rarity, 1.0)
        
        # Применение рыночных модификаторов
        for condition, multiplier in market_conditions.items():
            if condition in str(self.category.value):
                price *= multiplier
        
        self.current_price = price
        return price

@dataclass
class TradeOffer:
    """Торговое предложение"""
    offer_id: str
    trade_type: TradeType
    seller_id: str
    buyer_id: Optional[str] = None
    items: List[TradeItem] = field(default_factory=list)
    price: float = 0.0
    currency_type: CurrencyType = CurrencyType.GOLD
    status: TradeStatus = TradeStatus.PENDING
    location: TradeLocation = TradeLocation.MARKETPLACE
    
    # Временные ограничения
    creation_time: float = field(default_factory=time.time)
    expiration_time: Optional[float] = None
    completion_time: Optional[float] = None
    
    # Дополнительные параметры
    is_negotiable: bool = True
    minimum_quantity: int = 1
    maximum_quantity: Optional[int] = None
    bulk_discount: float = 0.0
    reputation_requirement: float = 0.0
    
    def is_expired(self) -> bool:
        """Проверить, истек ли срок предложения"""
        if self.expiration_time:
            return time.time() > self.expiration_time
        return False
    
    def get_remaining_time(self) -> Optional[float]:
        """Получить оставшееся время"""
        if self.expiration_time:
            remaining = self.expiration_time - time.time()
            return max(0, remaining)
        return None
    
    def accept_offer(self, buyer_id: str, quantity: int = None) -> bool:
        """Принять предложение"""
        if self.status != TradeStatus.PENDING:
            return False
        
        if self.is_expired():
            self.status = TradeStatus.EXPIRED
            return False
        
        if quantity is None:
            quantity = self.minimum_quantity
        
        if quantity < self.minimum_quantity:
            return False
        
        if self.maximum_quantity and quantity > self.maximum_quantity:
            return False
        
        self.buyer_id = buyer_id
        self.status = TradeStatus.ACTIVE
        return True
    
    def complete_trade(self) -> bool:
        """Завершить торговую сделку"""
        if self.status != TradeStatus.ACTIVE:
            return False
        
        self.status = TradeStatus.COMPLETED
        self.completion_time = time.time()
        return True
    
    def cancel_offer(self) -> bool:
        """Отменить предложение"""
        if self.status in [TradeStatus.PENDING, TradeStatus.ACTIVE]:
            self.status = TradeStatus.CANCELLED
            return True
        return False

@dataclass
class TradeHistory:
    """История торговли"""
    trade_id: str
    seller_id: str
    buyer_id: str
    items: List[TradeItem] = field(default_factory=list)
    price: float = 0.0
    currency_type: CurrencyType = CurrencyType.GOLD
    trade_type: TradeType = TradeType.EXCHANGE
    location: TradeLocation = TradeLocation.MARKETPLACE
    completion_time: float = field(default_factory=time.time)
    
    # Дополнительная информация
    seller_reputation_change: float = 0.0
    buyer_reputation_change: float = 0.0
    market_impact: float = 0.0
    taxes_paid: float = 0.0
    fees_paid: float = 0.0

@dataclass
class MarketData:
    """Рыночные данные"""
    item_id: str
    category: TradeCategory
    current_price: float = 0.0
    average_price: float = 0.0
    price_volatility: float = 0.0
    supply: int = 0
    demand: int = 0
    last_update: float = field(default_factory=time.time)
    
    # Статистика торговли
    total_trades: int = 0
    total_volume: float = 0.0
    price_history: List[float] = field(default_factory=list)
    
    def update_price(self, new_price: float):
        """Обновить цену и статистику"""
        self.price_history.append(self.current_price)
        if len(self.price_history) > 100:  # Ограничиваем историю
            self.price_history.pop(0)
        
        self.current_price = new_price
        self.last_update = time.time()
        
        # Обновление средней цены
        if self.price_history:
            self.average_price = sum(self.price_history) / len(self.price_history)
        
        # Обновление волатильности
        if len(self.price_history) > 1:
            prices = self.price_history[-10:]  # Последние 10 цен
            if len(prices) > 1:
                mean_price = sum(prices) / len(prices)
                variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                self.price_volatility = variance ** 0.5

@dataclass
class TradeContract:
    """Торговый контракт"""
    contract_id: str
    seller_id: str
    buyer_id: str
    items: List[TradeItem] = field(default_factory=list)
    total_price: float = 0.0
    currency_type: CurrencyType = CurrencyType.GOLD
    delivery_time: Optional[float] = None
    payment_terms: str = "immediate"
    
    # Условия контракта
    quality_guarantee: bool = True
    return_policy: bool = False
    warranty_period: float = 0.0  # в секундах
    
    # Статус контракта
    status: TradeStatus = TradeStatus.PENDING
    creation_time: float = field(default_factory=time.time)
    completion_time: Optional[float] = None
    
    def is_delivery_overdue(self) -> bool:
        """Проверить, просрочена ли доставка"""
        if self.delivery_time and self.status == TradeStatus.ACTIVE:
            return time.time() > self.delivery_time
        return False
    
    def complete_contract(self) -> bool:
        """Завершить контракт"""
        if self.status == TradeStatus.ACTIVE:
            self.status = TradeStatus.COMPLETED
            self.completion_time = time.time()
            return True
        return False
