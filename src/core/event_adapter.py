#!/usr/bin/env python3
"""
EventBusAdapter — мост между существующим EventSystem и системами,
которые ожидают интерфейс event_bus (on/emit API) из новой архитектуры.
"""

from typing import Any, Callable, Dict

from .event_system import EventSystem, EventPriority


class EventBusAdapter:
    """Адаптер, предоставляющий API on()/emit() поверх EventSystem."""

    def __init__(self, event_system: EventSystem):
        self._event_system = event_system

    # Подписка совместимая с EventBus.on
    def on(self, event_type: str, handler: Callable, priority: Any = None) -> bool:
        try:
            prio = EventPriority.NORMAL
            if isinstance(priority, EventPriority):
                prio = priority
            # Пытаемся извлечь человекочитаемый id
            subscriber_id = getattr(handler, "__name__", "subscriber")
            return self._event_system.subscribe(event_type, handler, subscriber_id, prio)
        except Exception:
            return False

    # Публикация совместимая с EventBus.emit
    def emit(self, event_type: str, data: Dict[str, Any] = None, priority: Any = None) -> bool:
        try:
            prio = EventPriority.NORMAL
            if isinstance(priority, EventPriority):
                prio = priority
            return self._event_system.emit_event(event_type, data or {}, "event_bus_adapter", prio)
        except Exception:
            return False


