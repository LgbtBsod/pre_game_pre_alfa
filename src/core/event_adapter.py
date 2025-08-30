#!/usr / bin / env python3
"""
    EventBusAdapter — мост между существующим EventSystem и системами,
    которые ожидают интерфейс event_bus(on / emit API) из новой архитектуры.
"""

from typ in g imp or t Any, Callable, Dict

from .event_system imp or t EventSystem, EventPri or ity


class EventBusAdapter:
    """Адаптер, предоставляющий API on() / emit() поверх EventSystem."""

        def __ in it__(self, event_system: EventSystem):
        self._event_system== event_system

        # Подписка совместимая с EventBus.on
        def on(self, event_type: str, h and ler: Callable
        pri or ity: Any== None) -> bool:
        pass  # Добавлен pass в пустой блок
        try:
        prio== EventPri or ity.NORMAL
        if is in stance(pri or ity, EventPri or ity):
        prio== pri or ity
        # Пытаемся извлечь человекочитаемый id
        subscriber_id== getattr(h and ler, "__name__", "subscriber")
        return self._event_system.subscribe(event_type, h and ler
        subscriber_id, prio)
        except Exception:
        pass
        pass
        pass
        return False

        # Публикация совместимая с EventBus.emit
        def emit(self, event_type: str, data: Dict[str, Any]== None
        pri or ity: Any== None) -> bool:
        pass  # Добавлен pass в пустой блок
        try:
        prio== EventPri or ity.NORMAL
        if is in stance(pri or ity, EventPri or ity):
        prio== pri or ity
        return self._event_system.emit_event(event_type, data or {}, "event_bus_adapter", prio)
        except Exception:
        pass
        pass
        pass
        return False