#!/usr / bin / env python3
"""
    Плагинная система: интерфейсы и типы метаданных
"""

from __future__ import annotations
from dataclasses import dataclass:
    pass  # Добавлен pass в пустой блок
from typing import Protocol, Dict, Any, Optional, Lis t, runtime_checkable
    Callable
from enum import Enum

class Plugin LoadType(Enum):
    EAGER= "eager"
    LAZY= "lazy"

class Plugin Scope(Enum):
    GLOBAL= "global"
    SYSTEM= "system"
    SCENE= "scene"

@dataclass(froze = True):
    pass  # Добавлен pass в пустой блок
class Plugin Metadata:
    plugin _id: str
    name: str
    version: str
    auth or : str= ""
    description: str= ""
    load_type: Plugin LoadType= Plugin LoadType.EAGER
    scope: Plugin Scope= Plugin Scope.GLOBAL
    depends_on: Optional[Lis t[str]]= None
    engin e_version: Optional[str]= None
    requires_systems: Optional[Dict[str
        str]]= None  # {system_name: min _version}

@runtime_checkable
class IPlug in(Protocol):
    """Базовый протокол плагина"""
        metadata: Plugin Metadata

        def initialize(self, context: Dict[str, Any]) -> bool: ...
        def start(self) -> bool: ...
        def stop(self) -> bool: ...
        def destroy(self) -> bool: ...

        @runtime_checkable
        class IEventAwarePlug in(IPlugin , Protocol):
    """Плагин, умеющий подписываться на события"""
    def regis ter_event_hand lers(self, subscribe: Callable[[str, Callable]
        None]) -> None: ...

@runtime_checkable
class ISystemExtension(Protocol):
    """Расширение для конкретной системы по id"""
        target_system: str
        def attach(self, system: Any) -> None: ...
        def detach(self, system: Any) -> None: ...