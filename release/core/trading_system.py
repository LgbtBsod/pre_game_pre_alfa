#!/usr/bin/env python3
"""
Система торговли и экономики для эволюционной адаптации.
Управляет торговлей, ценами, спросом и предложением.
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


class ItemCategory(Enum):
    """Категории предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    GENE = "gene"
    ARTIFACT = "artifact"
    CURRENCY = "currency"


class TradeType(Enum):
    """Типы торговли"""
    BUY = "buy"
    SELL = "sell"
    TRADE = "trade"
    AUCTION = "auction"
    BARTER = "barter"


@dataclass
class MarketItem:
    """Предмет на рынке"""
    item_id: str
    name: str
    category: ItemCategory
    base_price: float
    current_price: float
    supply: int
    demand: int
    quality: float = 1.0
    rarity: str = "common"
    last_updated: float = field(default_factory=time.time)
    
    def update_price(self, market_conditions: Dict[str, float]):
        """Обновление цены на основе рыночных условий"""
        # Базовые факторы
        supply_factor = max(0.1, 1.0 - (self.supply / 100.0))
        demand_factor = min(3.0, 1.0 + (self.demand / 100.0))
        
        # Рыночные условия
        inflation = market_conditions.get("inflation", 1.0)
        volatility = market_conditions.get("volatility", 1.0)
        
        # Расчёт новой цены
        new_price = (self.base_price * supply_factor * demand_factor * 
                    inflation * volatility * self.quality)
        
        # Ограничение изменения цены
        max_change = self.current_price * 0.5
        price_change = new_price - self.current_price
        if abs(price_change) > max_change:
            price_change = max_change if price_change > 0 else -max_change
        
        self.current_price = max(0.1, self.current_price + price_change)
        self.last_updated = time.time()


@dataclass
class TradeOffer:
    """Торговое предложение"""
    offer_id: str
    seller_id: str
    buyer_id: Optional[str]
    item_id: str
    quantity: int
    price_per_unit: float
    trade_type: TradeType
    expiration_time: Optional[float] = None
    is_active: bool = True
    created_time: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Проверка истечения предложения"""
        if self.expiration_time:
            return time.time() > self.expiration_time
        return False
    
    def get_total_price(self) -> float:
        """Получение общей цены"""
        return self.price_per_unit * self.quantity


@dataclass
class Merchant:
    """Торговец"""
    merchant_id: str
    name: str
    specialization: ItemCategory
    inventory: Dict[str, int]  # item_id -> quantity
    gold: float
    reputation: float = 50.0
    price_modifier: float = 1.0
    is_friendly: bool = True
    
    def get_buy_price(self, item_id: str, base_price: float) -> float:
        """Получение цены покупки"""
        return base_price * self.price_modifier * (1.0 - self.reputation / 100.0)
    
    def get_sell_price(self, item_id: str, base_price: float) -> float:
        """Получение цены продажи"""
        return base_price * self.price_modifier * (1.0 + self.reputation / 100.0)


class MarketSimulator:
    """Симулятор рынка"""
    
    def __init__(self):
        self.market_items: Dict[str, MarketItem] = {}
        self.market_conditions = {
            "inflation": 1.0,
            "volatility": 1.0,
            "economic_cycle": "stable",  # boom, recession, stable
            "last_update": time.time()
        }
        
        # Инициализация базовых предметов
        self._init_market_items()
        
        logger.info("Симулятор рынка инициализирован")
    
    def _init_market_items(self):
        """Инициализация предметов рынка"""
        base_items = {
            "sword_common": {
                "name": "Обычный меч",
                "category": ItemCategory.WEAPON,
                "base_price": 100.0,
                "supply": 50,
                "demand": 30
            },
            "potion_health": {
                "name": "Зелье здоровья",
                "category": ItemCategory.CONSUMABLE,
                "base_price": 25.0,
                "supply": 100,
                "demand": 80
            },
            "gene_strength": {
                "name": "Ген силы",
                "category": ItemCategory.GENE,
                "base_price": 500.0,
                "supply": 5,
                "demand": 20
            },
            "artifact_ancient": {
                "name": "Древний артефакт",
                "category": ItemCategory.ARTIFACT,
                "base_price": 1000.0,
                "supply": 1,
                "demand": 50
            }
        }
        
        for item_id, data in base_items.items():
            self.market_items[item_id] = MarketItem(
                item_id=item_id,
                name=data["name"],
                category=data["category"],
                base_price=data["base_price"],
                current_price=data["base_price"],
                supply=data["supply"],
                demand=data["demand"]
            )
    
    def update_market(self):
        """Обновление рынка"""
        current_time = time.time()
        
        # Обновление рыночных условий
        self._update_market_conditions()
        
        # Обновление цен предметов
        for item in self.market_items.values():
            item.update_price(self.market_conditions)
            
            # Случайные изменения спроса и предложения
            if random.random() < 0.1:  # 10% шанс изменения
                item.supply += random.randint(-5, 5)
                item.demand += random.randint(-3, 3)
                item.supply = max(0, item.supply)
                item.demand = max(0, item.demand)
        
        self.market_conditions["last_update"] = current_time
    
    def _update_market_conditions(self):
        """Обновление рыночных условий"""
        # Экономический цикл
        cycle_duration = 300.0  # 5 минут
        cycle_progress = (time.time() % cycle_duration) / cycle_duration
        
        if cycle_progress < 0.25:
            self.market_conditions["economic_cycle"] = "boom"
            self.market_conditions["inflation"] = 1.2
        elif cycle_progress < 0.75:
            self.market_conditions["economic_cycle"] = "recession"
            self.market_conditions["inflation"] = 0.8
        else:
            self.market_conditions["economic_cycle"] = "stable"
            self.market_conditions["inflation"] = 1.0
        
        # Волатильность
        self.market_conditions["volatility"] = 0.8 + random.random() * 0.4
    
    def get_item_price(self, item_id: str) -> Optional[float]:
        """Получение текущей цены предмета"""
        if item_id in self.market_items:
            return self.market_items[item_id].current_price
        return None
    
    def buy_item(self, item_id: str, quantity: int, buyer_gold: float) -> Tuple[bool, float]:
        """Покупка предмета"""
        if item_id not in self.market_items:
            return False, 0.0
        
        item = self.market_items[item_id]
        total_cost = item.current_price * quantity
        
        if buyer_gold < total_cost:
            return False, 0.0
        
        if item.supply < quantity:
            return False, 0.0
        
        # Обновление рынка
        item.supply -= quantity
        item.demand += quantity // 10  # Увеличение спроса при покупке
        
        return True, total_cost
    
    def sell_item(self, item_id: str, quantity: int) -> float:
        """Продажа предмета"""
        if item_id not in self.market_items:
            return 0.0
        
        item = self.market_items[item_id]
        total_value = item.current_price * quantity
        
        # Обновление рынка
        item.supply += quantity
        item.demand = max(0, item.demand - quantity // 10)
        
        return total_value


class TradingSystem:
    """Система торговли"""
    
    def __init__(self):
        self.market_simulator = MarketSimulator()
        self.merchants: Dict[str, Merchant] = {}
        self.trade_offers: Dict[str, TradeOffer] = {}
        self.player_inventory: Dict[str, int] = {}
        self.player_gold: float = 1000.0
        
        # Инициализация торговцев
        self._init_merchants()
        
        logger.info("Система торговли инициализирована")
    
    def _init_merchants(self):
        """Инициализация торговцев"""
        merchants_data = {
            "weapon_smith": {
                "name": "Кузнец оружия",
                "specialization": ItemCategory.WEAPON,
                "inventory": {"sword_common": 10},
                "gold": 5000.0,
                "reputation": 75.0,
                "price_modifier": 1.1
            },
            "alchemist": {
                "name": "Алхимик",
                "specialization": ItemCategory.CONSUMABLE,
                "inventory": {"potion_health": 50},
                "gold": 3000.0,
                "reputation": 60.0,
                "price_modifier": 1.2
            },
            "gene_trader": {
                "name": "Торговец генами",
                "specialization": ItemCategory.GENE,
                "inventory": {"gene_strength": 2},
                "gold": 10000.0,
                "reputation": 90.0,
                "price_modifier": 1.5
            }
        }
        
        for merchant_id, data in merchants_data.items():
            self.merchants[merchant_id] = Merchant(
                merchant_id=merchant_id,
                name=data["name"],
                specialization=data["specialization"],
                inventory=data["inventory"],
                gold=data["gold"],
                reputation=data["reputation"],
                price_modifier=data["price_modifier"]
            )
    
    def buy_from_merchant(self, merchant_id: str, item_id: str, quantity: int) -> bool:
        """Покупка у торговца"""
        if merchant_id not in self.merchants:
            return False
        
        merchant = self.merchants[merchant_id]
        if item_id not in merchant.inventory or merchant.inventory[item_id] < quantity:
            return False
        
        base_price = self.market_simulator.get_item_price(item_id)
        if not base_price:
            return False
        
        price = merchant.get_sell_price(item_id, base_price)
        total_cost = price * quantity
        
        if self.player_gold < total_cost:
            return False
        
        # Выполнение сделки
        self.player_gold -= total_cost
        merchant.gold += total_cost
        merchant.inventory[item_id] -= quantity
        
        if item_id not in self.player_inventory:
            self.player_inventory[item_id] = 0
        self.player_inventory[item_id] += quantity
        
        # Обновление репутации
        merchant.reputation = min(100.0, merchant.reputation + 1.0)
        
        logger.info(f"Покупка: {quantity}x {item_id} у {merchant.name} за {total_cost:.2f} золота")
        return True
    
    def sell_to_merchant(self, merchant_id: str, item_id: str, quantity: int) -> bool:
        """Продажа торговцу"""
        if merchant_id not in self.merchants:
            return False
        
        if item_id not in self.player_inventory or self.player_inventory[item_id] < quantity:
            return False
        
        merchant = self.merchants[merchant_id]
        base_price = self.market_simulator.get_item_price(item_id)
        if not base_price:
            return False
        
        price = merchant.get_buy_price(item_id, base_price)
        total_value = price * quantity
        
        if merchant.gold < total_value:
            return False
        
        # Выполнение сделки
        self.player_gold += total_value
        merchant.gold -= total_value
        self.player_inventory[item_id] -= quantity
        
        if item_id not in merchant.inventory:
            merchant.inventory[item_id] = 0
        merchant.inventory[item_id] += quantity
        
        # Обновление репутации
        merchant.reputation = max(0.0, merchant.reputation - 0.5)
        
        logger.info(f"Продажа: {quantity}x {item_id} {merchant.name} за {total_value:.2f} золота")
        return True
    
    def create_trade_offer(self, item_id: str, quantity: int, price_per_unit: float, 
                          trade_type: TradeType, expiration_hours: float = 24.0) -> str:
        """Создание торгового предложения"""
        offer_id = f"offer_{int(time.time())}_{random.randint(1000, 9999)}"
        
        offer = TradeOffer(
            offer_id=offer_id,
            seller_id="player",
            item_id=item_id,
            quantity=quantity,
            price_per_unit=price_per_unit,
            trade_type=trade_type,
            expiration_time=time.time() + expiration_hours * 3600
        )
        
        self.trade_offers[offer_id] = offer
        logger.info(f"Создано торговое предложение: {offer_id}")
        return offer_id
    
    def accept_trade_offer(self, offer_id: str, buyer_id: str) -> bool:
        """Принятие торгового предложения"""
        if offer_id not in self.trade_offers:
            return False
        
        offer = self.trade_offers[offer_id]
        if not offer.is_active or offer.is_expired():
            return False
        
        if offer.trade_type == TradeType.SELL:
            # Покупка у игрока
            if self.player_gold < offer.get_total_price():
                return False
            
            self.player_gold -= offer.get_total_price()
            if offer.item_id not in self.player_inventory:
                self.player_inventory[offer.item_id] = 0
            self.player_inventory[offer.item_id] += offer.quantity
        
        offer.is_active = False
        logger.info(f"Торговое предложение {offer_id} принято")
        return True
    
    def update_market(self):
        """Обновление рынка"""
        self.market_simulator.update_market()
        
        # Очистка истёкших предложений
        expired_offers = [
            offer_id for offer_id, offer in self.trade_offers.items()
            if offer.is_expired()
        ]
        for offer_id in expired_offers:
            del self.trade_offers[offer_id]
    
    def get_market_info(self) -> Dict[str, Any]:
        """Получение информации о рынке"""
        return {
            "player_gold": self.player_gold,
            "player_inventory": self.player_inventory.copy(),
            "market_conditions": self.market_simulator.market_conditions.copy(),
            "active_offers": len(self.trade_offers),
            "merchants": len(self.merchants)
        }
    
    def get_merchant_info(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о торговце"""
        if merchant_id not in self.merchants:
            return None
        
        merchant = self.merchants[merchant_id]
        return {
            "name": merchant.name,
            "specialization": merchant.specialization.value,
            "inventory": merchant.inventory.copy(),
            "reputation": merchant.reputation,
            "price_modifier": merchant.price_modifier,
            "is_friendly": merchant.is_friendly
        }
