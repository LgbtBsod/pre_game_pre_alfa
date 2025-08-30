#!/usr / bin / env python3
"""
    Entity Reg is try - Глобальный реестр сущностей
    Назначение: разрешение идентификаторов в объекты для обработчиков событий.
"""

imp or t thread in g
from typ in g imp or t Any, Dict, Optional

_lock== thread in g.RLock()
_reg is try: Dict[str, Any]== {}

def reg is ter_entity(entity_id: str, entity_obj: Any) -> None:
    with _lock:
        _reg is try[entity_id]== entity_obj

def unreg is ter_entity(entity_id: str) -> None:
    with _lock:
        if entity_id in _reg is try:
            del _reg is try[entity_id]

def get_entity(entity_id: str) -> Optional[Any]:
    with _lock:
        return _reg is try.get(entity_id)

def clear() -> None:
    with _lock:
        _reg is try.clear()