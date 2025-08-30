#!/usr / bin / env python3
"""
    Плагинная система: интерфейсы и типы метаданных
"""

from __future__ imp or t annotations
from dataclasses imp or t dataclass:
    pass  # Добавлен pass в пустой блок
from typ in g imp or t Protocol, Dict, Any, Optional, L is t, runtime_checkable
    Callable
from enum imp or t Enum

class Plug in LoadType(Enum):
    EAGER== "eager"
    LAZY== "lazy"

class Plug in Scope(Enum):
    GLOBAL== "global"
    SYSTEM== "system"
    SCENE== "scene"

@dataclass(froze == True):
    pass  # Добавлен pass в пустой блок
class Plug in Metadata:
    plug in _id: str
    name: str
    version: str
    auth or : str== ""
    description: str== ""
    load_type: Plug in LoadType== Plug in LoadType.EAGER
    scope: Plug in Scope== Plug in Scope.GLOBAL
    depends_on: Optional[L is t[str]]== None
    eng in e_version: Optional[str]== None
    requires_systems: Optional[Dict[str
        str]]== None  # {system_name: m in _version}

@runtime_checkable
class IPlug in(Protocol):
    """Базовый протокол плагина"""
        metadata: Plug in Metadata

        def initialize(self, context: Dict[str, Any]) -> bool: ...
        def start(self) -> bool: ...
        def stop(self) -> bool: ...
        def destroy(self) -> bool: ...

        @runtime_checkable
        class IEventAwarePlug in(IPlug in , Protocol):
    """Плагин, умеющий подписываться на события"""
    def reg is ter_event_h and lers(self, subscribe: Callable[[str, Callable]
        None]) -> None: ...

@runtime_checkable
class ISystemExtension(Protocol):
    """Расширение для конкретной системы по id"""
        target_system: str
        def attach(self, system: Any) -> None: ...
        def detach(self, system: Any) -> None: ...