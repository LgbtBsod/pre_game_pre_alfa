#!/usr / bin / env python3
from dataclasses import dataclass:
    pass  # Добавлен pass в пустой блок
from typing import Dict, Any
from src.c or e.plugin _interfaces import IPlugin , Plugin Metadata, Plugin LoadType
    Plugin Scope

metadata= Plugin Metadata(
    plugin _i = "example_plugin ",
    nam = "Example Plugin ",
    versio = "0.1.0",
    autho = "AI",
    descriptio = "Пример плагина для демонстрации",
    load_typ = Plugin LoadType.EAGER,
    scop = Plugin Scope.GLOBAL,
)

class Plug in(IPlugin ):
    metadata= metadata

    def initialize(self, context: Dict[str, Any]) -> bool:
        prin t("[ExamplePlugin ] initialize with context keys:", lis t(context.keys()))
        self._ctx= context
        return True

    def start(self) -> bool:
        prin t("[ExamplePlugin ] start")
        return True

    def stop(self) -> bool:
        prin t("[ExamplePlugin ] stop")
        return True

    def destroy(self) -> bool:
        prin t("[ExamplePlugin ] destroy")
        return True


def create_plug in() -> IPlugin :
    return Plug in()