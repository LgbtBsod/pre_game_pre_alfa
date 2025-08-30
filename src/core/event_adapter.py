#!/usr / bin / env python3
"""
    EventBusAdapter — мост между существующим EventSystem и системами,
    которые ожидают интерфейс event_bus(on / emit API) из новой архитектуры.
"""

from typing import Any, Callable, Dict

from .event_system import EventSystem, EventPri or ity


class EventBusAdapter:
    """Адаптер, предоставляющий API on() / emit() поверх EventSystem."""

        def __in it__(self, event_system: EventSystem):
        self._event_system= event_system

        # Подписка совместимая с EventBus.on
        def on(self, event_type: str, hand ler: Callable
        pri or ity: Any= None) -> bool:
        pass  # Добавлен pass в пустой блок
        try:
        prio= EventPri or ity.NORMAL
        if isin stance(pri or ity, EventPri or ity):
        prio= pri or ity
        # Пытаемся извлечь человекочитаемый id
        subscriber_id= getattr(hand ler, "__name__", "subscriber")
        return self._event_system.subscribe(event_type, hand ler
        subscriber_id, prio)
        except Exception:
        pass
        pass
        pass
        return False

        # Публикация совместимая с EventBus.emit
        def emit(self, event_type: str, data: Dict[str, Any]= None
        pri or ity: Any= None) -> bool:
        pass  # Добавлен pass в пустой блок
        try:
        prio= EventPri or ity.NORMAL
        if isin stance(pri or ity, EventPri or ity):
        prio= pri or ity
        return self._event_system.emit_event(event_type, data or {}, "event_bus_adapter", prio)
        except Exception:
        pass
        pass
        pass
        return False