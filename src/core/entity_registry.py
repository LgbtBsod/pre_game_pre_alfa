#!/usr/bin/env python3
"""
Entity Registry - Глобальный реестр сущностей
Назначение: разрешение идентификаторов в объекты для обработчиков событий.
"""

import threading
from typing import Any, Dict, Optional

_lock = threading.RLock()
_registry: Dict[str, Any] = {}

def register_entity(entity_id: str, entity_obj: Any) -> None:
    with _lock:
        _registry[entity_id] = entity_obj

def unregister_entity(entity_id: str) -> None:
    with _lock:
        if entity_id in _registry:
            del _registry[entity_id]

def get_entity(entity_id: str) -> Optional[Any]:
    with _lock:
        return _registry.get(entity_id)

def clear() -> None:
    with _lock:
        _registry.clear()


