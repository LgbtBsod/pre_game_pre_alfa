"""
Декларация типов игровых событий для минимизации строк-литералов.
"""

from enum import Enum


class EventType(Enum):
    ENTITY_CREATED = 'entity_created'
    ENTITY_DESTROYED = 'entity_destroyed'
    WORLD_CHANGED = 'world_changed'

"""
Centralized event types and payload contracts.
"""

from enum import Enum
from typing import Any, Dict


class EventType(str, Enum):
    ENTITY_CREATED = 'entity_created'
    ENTITY_DESTROYED = 'entity_destroyed'
    WORLD_CHANGED = 'world_changed'


def make_event(event_type: EventType, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'type': event_type.value,
        'data': data,
    }


