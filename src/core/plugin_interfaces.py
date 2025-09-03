from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Dict, Any, Optional, List, Callable, runtime_checkable

"""Плагинная система: интерфейсы и типы метаданных"""


class PluginLoadType(Enum):
    EAGER = "eager"
    LAZY = "lazy"


class PluginScope(Enum):
    GLOBAL = "global"
    SYSTEM = "system"
    SCENE = "scene"


@dataclass(frozen=True)
class PluginMetadata:
    plugin_id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    load_type: PluginLoadType = PluginLoadType.EAGER
    scope: PluginScope = PluginScope.GLOBAL
    depends_on: Optional[List[str]] = None
    engine_version: Optional[str] = None
    requires_systems: Optional[Dict[str, str]] = None  # {system_name: min_version}


@runtime_checkable
class IPlugin(Protocol):
    """Базовый протокол плагина"""

    metadata: PluginMetadata

    def initialize(self, context: Dict[str, Any]) -> bool: ...

    def start(self) -> bool: ...

    def stop(self) -> bool: ...

    def destroy(self) -> bool: ...


@runtime_checkable
class IEventAwarePlugin(IPlugin, Protocol):
    """Плагин, умеющий подписываться на события"""

    def register_event_handlers(self, subscribe: Callable[[str, Callable], None]) -> None: ...


@runtime_checkable
class ISystemExtension(Protocol):
    """Расширение для конкретной системы по id"""

    target_system: str

    def attach(self, system: Any) -> None: ...

    def detach(self, system: Any) -> None: ...

