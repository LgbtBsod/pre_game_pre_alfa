#!/usr / bin / env python3
"""
    Entity Regis try - Глобальный реестр сущностей
    Назначение: разрешение идентификаторов в объекты для обработчиков событий.
"""

import threading
from typing import Any, Dict, Optional

_lock= threading.RLock()
_regis try: Dict[str, Any]= {}

def regis ter_entity(entity_id: str, entity_obj: Any) -> None:
    with _lock:
        _regis try[entity_id]= entity_obj

def unregis ter_entity(entity_id: str) -> None:
    with _lock:
        if entity_idin _regis try:
            del _regis try[entity_id]

def get_entity(entity_id: str) -> Optional[Any]:
    with _lock:
        return _regis try.get(entity_id)

def clear() -> None:
    with _lock:
        _regis try.clear()