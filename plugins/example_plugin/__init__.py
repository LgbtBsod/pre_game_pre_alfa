#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Any
from src.core.plugin_interfaces import IPlugin, PluginMetadata, PluginLoadType, PluginScope

metadata = PluginMetadata(
    plugin_id="example_plugin",
    name="Example Plugin",
    version="0.1.0",
    author="AI",
    description="Пример плагина для демонстрации",
    load_type=PluginLoadType.EAGER,
    scope=PluginScope.GLOBAL,
)

class Plugin(IPlugin):
    metadata = metadata

    def initialize(self, context: Dict[str, Any]) -> bool:
        print("[ExamplePlugin] initialize with context keys:", list(context.keys()))
        self._ctx = context
        return True

    def start(self) -> bool:
        print("[ExamplePlugin] start")
        return True

    def stop(self) -> bool:
        print("[ExamplePlugin] stop")
        return True

    def destroy(self) -> bool:
        print("[ExamplePlugin] destroy")
        return True


def create_plugin() -> IPlugin:
    return Plugin()
