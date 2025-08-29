#!/usr/bin/env python3
"""
Система торговли - управление торговлей между сущностями
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from core.system_interfaces import BaseGameSystem
from core.architecture import Priority, LifecycleState
from core.state_manager import StateManager, StateType, StateScope
from core.repository import RepositoryManager, DataType, StorageType
from core.constants import (
    TradeType, TradeStatus, CurrencyType, TradeCategory, TradeRarity, TradeLocation,
    PROBABILITY_CONSTANTS, SYSTEM_LIMITS,
    TIME_CONSTANTS_RO, get_float
)

from .trading_data import TradeOffer, TradeItem, TradeHistory, MarketData, TradeContract

logger = logging.getLogger(__name__)

@dataclass
class TradeSession:
    """Торговая сессия"""
    session_id: str
    participants: List[str] = field(default_factory=list)
    offers: List[TradeOffer] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    location: TradeLocation = TradeLocation.MARKETPLACE
    status: TradeStatus = TradeStatus.PENDING

class TradingSystem(BaseGameSystem):
    """Система управления торговлей - интегрирована с новой архитектурой"""
    
    def __init__(self, state_manager: Optional[StateManager] = None, repository_manager: Optional[RepositoryManager] = None, event_bus=None):
        super().__init__("trading", Priority.NORMAL)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = state_manager
        self.repository_manager: Optional[RepositoryManager] = repository_manager
        self.event_bus = event_bus
        
        # Торговые предложения (теперь управляются через RepositoryManager)
        self.active_offers: Dict[str, TradeOffer] = {}
        self.completed_trades: List[TradeHistory] = []
        self.trade_sessions: Dict[str, TradeSession] = {}
        
        # Рыночные данные (теперь управляются через RepositoryManager)
        self.market_data: Dict[str, MarketData] = {}
        self.price_history: Dict[str, List[float]] = {}
        
        # Контракты (теперь управляются через RepositoryManager)
        self.active_contracts: Dict[str, TradeContract] = {}
        self.completed_contracts: List[TradeContract] = []
        
        # Настройки системы (теперь управляются через StateManager)
        self.system_settings = {
            'max_active_offers': SYSTEM_LIMITS["max_active_offers"],
            'transaction_fee': PROBABILITY_CONSTANTS["transaction_fee"],
            'tax_rate': PROBABILITY_CONSTANTS["tax_rate"],
            'reputation_impact': PROBABILITY_CONSTANTS["reputation_impact"],
            'price_volatility': PROBABILITY_CONSTANTS["price_volatility"],
            'market_update_interval': get_float(TIME_CONSTANTS_RO, "market_update_interval", 3600.0),
            'offer_expiration_time': get_float(TIME_CONSTANTS_RO, "offer_expiration_time", 604800.0)
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'total_trades': 0,
            'total_volume': 0.0,
            'active_offers_count': 0,
            'completed_contracts': 0,
            'average_trade_value': 0.0,
            'update_time': 0.0
        }
        
        logger.info("Система торговли инициализирована с новой архитектурой")
    
    def initialize(self, state_manager: StateManager = None, repository_manager: RepositoryManager = None, event_bus=None) -> bool:
        """Инициализация системы"""
        try:
            if state_manager is not None:
                self.state_manager = state_manager
            if repository_manager is not None:
                self.repository_manager = repository_manager
            if event_bus is not None:
                self.event_bus = event_bus
            
            if not self.state_manager or not self.repository_manager:
                logger.error("Не заданы зависимости state_manager или repository_manager")
                return False
            
            # Регистрация состояний системы
            self._register_system_states()
            
            # Регистрация репозиториев
            self._register_system_repositories()
            
            # Инициализация рыночных данных
            self._initialize_market_data()
            
            self.state = LifecycleState.INITIALIZED
            logger.info("Система торговли успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы торговли: {e}")
            return False
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.register_state(
                "trading_system_settings",
                self.system_settings,
                StateType.CONFIGURATION,
                StateScope.SYSTEM
            )
            self.state_manager.register_state(
                "trading_system_stats",
                self.system_stats,
                StateType.DYNAMIC_DATA,
                StateScope.SYSTEM
            )
    
    def _register_system_repositories(self):
        """Регистрация репозиториев системы"""
        if self.repository_manager:
            self.repository_manager.create_repository(
                "trade_offers",
                DataType.ENTITY_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "trade_history",
                DataType.HISTORY,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "market_data",
                DataType.DYNAMIC_DATA,
                StorageType.MEMORY
            )
            self.repository_manager.create_repository(
                "trade_contracts",
                DataType.ENTITY_DATA,
                StorageType.MEMORY
            )
    
    def _initialize_market_data(self):
        """Инициализация рыночных данных"""
        # Создание базовых рыночных данных для основных категорий
        for category in TradeCategory:
            market_data = MarketData(
                item_id=f"market_{category.value}",
                category=category,
                current_price=100.0,
                average_price=100.0,
                supply=100,
                demand=100
            )
            self.market_data[market_data.item_id] = market_data
    
    def create_trade_offer(self, seller_id: str, items: List[TradeItem], price: float, 
                          currency_type: CurrencyType = CurrencyType.GOLD,
                          trade_type: TradeType = TradeType.SELL) -> Optional[str]:
        """Создание торгового предложения"""
        try:
            # Проверка ограничений
            if len(self.active_offers) >= self.system_settings['max_active_offers']:
                logger.warning("Достигнут лимит активных предложений")
                return None
            
            offer_id = f"offer_{seller_id}_{int(time.time())}"
            
            offer = TradeOffer(
                offer_id=offer_id,
                trade_type=trade_type,
                seller_id=seller_id,
                items=items,
                price=price,
                currency_type=currency_type,
                expiration_time=time.time() + self.system_settings['offer_expiration_time']
            )
            
            self.active_offers[offer_id] = offer
            self.system_stats['active_offers_count'] += 1
            
            logger.info(f"Создано торговое предложение {offer_id}")
            return offer_id
            
        except Exception as e:
            logger.error(f"Ошибка создания торгового предложения: {e}")
            return None
    
    def accept_trade_offer(self, offer_id: str, buyer_id: str, quantity: int = None) -> bool:
        """Принятие торгового предложения"""
        try:
            if offer_id not in self.active_offers:
                logger.warning(f"Предложение {offer_id} не найдено")
                return False
            
            offer = self.active_offers[offer_id]
            
            if not offer.accept_offer(buyer_id, quantity):
                logger.warning(f"Не удалось принять предложение {offer_id}")
                return False
            
            # Создание истории торговли
            trade_history = TradeHistory(
                trade_id=f"trade_{offer_id}_{int(time.time())}",
                seller_id=offer.seller_id,
                buyer_id=buyer_id,
                items=offer.items,
                price=offer.price,
                currency_type=offer.currency_type,
                trade_type=offer.trade_type,
                location=offer.location
            )
            
            self.completed_trades.append(trade_history)
            
            # Обновление статистики
            self.system_stats['total_trades'] += 1
            self.system_stats['total_volume'] += offer.price
            self.system_stats['average_trade_value'] = (
                self.system_stats['total_volume'] / self.system_stats['total_trades']
            )
            
            # Удаление предложения из активных
            del self.active_offers[offer_id]
            self.system_stats['active_offers_count'] -= 1
            
            # Обновление рыночных данных
            self._update_market_data(offer.items, offer.price)
            
            logger.info(f"Предложение {offer_id} принято покупателем {buyer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка принятия торгового предложения: {e}")
            return False
    
    def _update_market_data(self, items: List[TradeItem], price: float):
        """Обновление рыночных данных"""
        try:
            for item in items:
                market_id = f"market_{item.category.value}"
                if market_id in self.market_data:
                    market_data = self.market_data[market_id]
                    market_data.update_price(price)
                    market_data.total_trades += 1
                    market_data.total_volume += price
                    
                    # Обновление спроса и предложения
                    if item.quantity > 0:
                        market_data.supply += item.quantity
                    market_data.demand += 1
                    
        except Exception as e:
            logger.error(f"Ошибка обновления рыночных данных: {e}")
    
    def get_market_data(self, category: TradeCategory) -> Optional[MarketData]:
        """Получение рыночных данных для категории"""
        market_id = f"market_{category.value}"
        return self.market_data.get(market_id)
    
    def get_active_offers(self, category: Optional[TradeCategory] = None) -> List[TradeOffer]:
        """Получение активных предложений"""
        offers = list(self.active_offers.values())
        
        if category:
            offers = [offer for offer in offers 
                     if any(item.category == category for item in offer.items)]
        
        return offers
    
    def get_trade_history(self, entity_id: str) -> List[TradeHistory]:
        """Получение истории торговли для сущности"""
        return [trade for trade in self.completed_trades 
                if trade.seller_id == entity_id or trade.buyer_id == entity_id]
    
    def create_contract(self, seller_id: str, buyer_id: str, items: List[TradeItem], 
                       total_price: float, delivery_time: Optional[float] = None) -> Optional[str]:
        """Создание торгового контракта"""
        try:
            contract_id = f"contract_{seller_id}_{buyer_id}_{int(time.time())}"
            
            contract = TradeContract(
                contract_id=contract_id,
                seller_id=seller_id,
                buyer_id=buyer_id,
                items=items,
                total_price=total_price,
                delivery_time=delivery_time,
                status=TradeStatus.PENDING
            )
            
            self.active_contracts[contract_id] = contract
            
            logger.info(f"Создан торговый контракт {contract_id}")
            return contract_id
            
        except Exception as e:
            logger.error(f"Ошибка создания торгового контракта: {e}")
            return None
    
    def complete_contract(self, contract_id: str) -> bool:
        """Завершение торгового контракта"""
        try:
            if contract_id not in self.active_contracts:
                logger.warning(f"Контракт {contract_id} не найден")
                return False
            
            contract = self.active_contracts[contract_id]
            
            if not contract.complete_contract():
                logger.warning(f"Не удалось завершить контракт {contract_id}")
                return False
            
            # Перемещение в завершенные контракты
            self.completed_contracts.append(contract)
            del self.active_contracts[contract_id]
            
            self.system_stats['completed_contracts'] += 1
            
            logger.info(f"Контракт {contract_id} завершен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения контракта: {e}")
            return False
    
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        try:
            current_time = time.time()
            
            # Проверка истечения предложений
            self._check_expired_offers(current_time)
            
            # Обновление рыночных данных
            self._update_market_prices(delta_time)
            
            # Проверка просроченных контрактов
            self._check_overdue_contracts(current_time)
            
            # Обновление статистики
            self.system_stats['update_time'] = current_time
            
            # Обновление состояний в StateManager
            if self.state_manager:
                self.state_manager.update_state("trading_system_stats", self.system_stats)
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы торговли: {e}")
    
    def _check_expired_offers(self, current_time: float):
        """Проверка истечения предложений"""
        expired_offers = []
        
        for offer_id, offer in self.active_offers.items():
            if offer.is_expired():
                expired_offers.append(offer_id)
        
        # Удаление истекших предложений
        for offer_id in expired_offers:
            del self.active_offers[offer_id]
            self.system_stats['active_offers_count'] -= 1
            logger.info(f"Предложение {offer_id} истекло")
    
    def _update_market_prices(self, delta_time: float):
        """Обновление рыночных цен"""
        try:
            for market_data in self.market_data.values():
                # Простая модель изменения цен на основе спроса и предложения
                if market_data.supply > 0 and market_data.demand > 0:
                    supply_demand_ratio = market_data.demand / market_data.supply
                    price_change = (supply_demand_ratio - 1.0) * self.system_settings['price_volatility'] * delta_time
                    
                    new_price = market_data.current_price * (1 + price_change)
                    market_data.update_price(new_price)
                    
        except Exception as e:
            logger.error(f"Ошибка обновления рыночных цен: {e}")
    
    def _check_overdue_contracts(self, current_time: float):
        """Проверка просроченных контрактов"""
        overdue_contracts = []
        
        for contract_id, contract in self.active_contracts.items():
            if contract.is_delivery_overdue():
                overdue_contracts.append(contract_id)
        
        # Обработка просроченных контрактов
        for contract_id in overdue_contracts:
            contract = self.active_contracts[contract_id]
            contract.status = TradeStatus.FAILED
            logger.warning(f"Контракт {contract_id} просрочен")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получить информацию о системе"""
        return {
            "system_name": "TradingSystem",
            "state": self.state.value,
            "settings": self.system_settings,
            "stats": self.system_stats,
            "active_offers_count": len(self.active_offers),
            "market_categories": len(self.market_data),
            "active_contracts_count": len(self.active_contracts),
            "completed_trades_count": len(self.completed_trades)
        }
