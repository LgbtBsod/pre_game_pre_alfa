import logging
from typing import Dict, Any

from src.core.plugin_interfaces import IPlugin, PluginMetadata, PluginLoadType, IEventAwarePlugin

logger = logging.getLogger(__name__)


class ExamplePlugin(IPlugin):
    metadata: PluginMetadata = PluginMetadata(
        plugin_id="example_plugin",
        name="Example Plugin",
        version="1.0.0",
        author="AI-EVOLVE",
        description="Demo plugin that logs lifecycle events.",
        load_type=PluginLoadType.EAGER,
        depends_on=[],
        requires_systems={},
    )

    def __init__(self) -> None:
        self._initialized = False
        self._started = False
        self._context: Dict[str, Any] = {}

    def initialize(self, context: Dict[str, Any]) -> bool:
        self._context = context
        logger.info("[ExamplePlugin] initialize with context keys: %s", list(context.keys()))
        self._initialized = True
        return True

    def start(self) -> bool:
        if not self._initialized:
            return False
        self._started = True
        logger.info("[ExamplePlugin] start")
        return True

    def stop(self) -> bool:
        if not self._started:
            return True
        logger.info("[ExamplePlugin] stop")
        self._started = False
        return True

    def destroy(self) -> bool:
        logger.info("[ExamplePlugin] destroy")
        self._initialized = False
        self._context.clear()
        return True


def create_plugin() -> IPlugin:
    return ExamplePlugin()
