"""Менеджер плагинов: обнаружение, загрузка, жизненный цикл"""

from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import sys
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List

from .plugin_interfaces import (
    IPlugin,
    ISystemExtension,
    PluginMetadata,
    PluginLoadType,
)


logger = logging.getLogger(__name__)


class PluginManager:
    """Управление плагинами проекта"""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self._discovered: Dict[str, Path] = {}
        self._loaded: Dict[str, IPlugin] = {}
        self._contexts: Dict[str, Dict[str, Any]] = {}
        self._watcher_thread: Optional[threading.Thread] = None
        self._watching: bool = False
        self._mtimes: Dict[str, float] = {}

    def discover(self) -> List[str]:
        """Поиск плагинов в каталоге"""
        try:
            if not self.plugins_dir.exists():
                return []
            plugin_ids: List[str] = []
            for entry in self.plugins_dir.iterdir():
                if entry.is_dir() and (entry / "__init__.py").exists():
                    pid = entry.name
                    self._discovered[pid] = entry
                    plugin_ids.append(pid)
            logger.info(f"Обнаружено плагинов: {len(plugin_ids)}")
            return plugin_ids
        except Exception as e:
            logger.error(f"Ошибка обнаружения плагинов: {e}")
            return []

    def _load_metadata(self, plugin_path: Path) -> Optional[PluginMetadata]:
        meta_path = plugin_path / "plugin.json"
        try:
            if not meta_path.exists():
                return None
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return PluginMetadata(
                plugin_id=data.get("plugin_id", plugin_path.name),
                name=data.get("name", plugin_path.name),
                version=data.get("version", "0.0.0"),
                author=data.get("author", ""),
                description=data.get("description", ""),
                load_type=PluginLoadType(data.get("load_type", "eager")),
                scope=data.get("scope", "global"),  # kept for forward-compat; not validated here
                depends_on=data.get("depends_on"),
                engine_version=data.get("engine_version"),
                requires_systems=data.get("requires_systems"),
            )
        except Exception as e:
            logger.error(f"Ошибка чтения/валидации метаданных для {plugin_path.name}: {e}")
            return None

    def _import_module(self, plugin_path: Path):
        try:
            module_name = f"plugins.{plugin_path.name}"
            if module_name in sys.modules:
                return sys.modules[module_name]
            spec = importlib.util.spec_from_file_location(
                module_name, plugin_path / "__init__.py"
            )
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
            return module
        except Exception as e:
            logger.error(f"Ошибка импорта модуля плагина {plugin_path}: {e}")
            return None

    def load(self, plugin_id: str, context: Dict[str, Any]) -> bool:
        """Загрузка и инициализация плагина по id папки"""
        try:
            if plugin_id not in self._discovered:
                logger.error(f"Плагин {plugin_id} не обнаружен")
                return False
            plugin_path = self._discovered[plugin_id]
            module = self._import_module(plugin_path)
            if module is None:
                return False

            plugin: Optional[IPlugin] = None
            if hasattr(module, "create_plugin"):
                plugin = module.create_plugin()  # type: ignore[attr-defined]
            elif hasattr(module, "Plugin"):
                plugin = getattr(module, "Plugin")()  # type: ignore[call-arg]
            else:
                logger.error(
                    f"Плагин {plugin_id} не содержит фабрики create_plugin() или класса Plugin"
                )
                return False

            if not plugin.initialize(context):
                logger.error(f"Не удалось инициализировать плагин {plugin_id}")
                return False

            self._loaded[plugin_id] = plugin
            self._contexts[plugin_id] = context
            logger.info(f"Плагин {plugin_id} загружен")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки плагина {plugin_id}: {e}")
            return False

    def start_all(self) -> None:
        for pid, plugin in self._loaded.items():
            try:
                plugin.start()
            except Exception as e:
                logger.error(f"Ошибка запуска плагина {pid}: {e}")

    def stop_all(self) -> None:
        for pid, plugin in self._loaded.items():
            try:
                plugin.stop()
            except Exception as e:
                logger.error(f"Ошибка остановки плагина {pid}: {e}")

    def destroy_all(self) -> None:
        for pid, plugin in list(self._loaded.items()):
            try:
                plugin.destroy()
            except Exception as e:
                logger.error(f"Ошибка уничтожения плагина {pid}: {e}")
        self._loaded.clear()
        self._contexts.clear()

    def _make_sandbox_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Создать упрощенный sandbox-контекст для плагина (белый список)"""
        allowed_keys = {
            "event_system",
            "config_manager",
            "scene_manager",
            "system_factory",
            "system_manager",
        }
        return {k: v for k, v in base_context.items() if k in allowed_keys}

    def _check_requirements(self, md: PluginMetadata, base_context: Dict[str, Any]) -> bool:
        try:
            # Минимальные проверки: требуемые системы присутствуют
            req = md.requires_systems or {}
            systems = base_context.get("system_manager")
            if req and not systems:
                return False
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки требований плагина {md.plugin_id}: {e}")
            return False

    def auto_load(self, base_context: Dict[str, Any]) -> List[str]:
        """Автозагрузка EAGER плагинов, возврат LAZY"""
        lazy: List[str] = []
        for pid, path in self._discovered.items():
            md = self._load_metadata(path)
            if not md:
                continue
            if not self._check_requirements(md, base_context):
                continue
            ctx = self._make_sandbox_context(base_context)
            ctx["metadata"] = md
            if md.load_type == PluginLoadType.EAGER:
                self.load(pid, ctx)
            else:
                lazy.append(pid)
        return lazy

    def bind_system_extensions(self, systems: Dict[str, Any]) -> None:
        """Подключить расширения плагинов к системам по target_system"""
        for pid, plugin in self._loaded.items():
            try:
                module = sys.modules.get(f"plugins.{pid}")
                if not module:
                    continue
                for attr_name in dir(module):
                    obj = getattr(module, attr_name)
                    if isinstance(obj, type):
                        try:
                            candidate = obj()
                        except Exception:
                            continue
                        if isinstance(candidate, ISystemExtension):
                            target = getattr(candidate, "target_system", None)
                            if target and target in systems:
                                candidate.attach(systems[target])
                                logger.info(
                                    f"Плагин {pid}: расширение {attr_name} подключено к {target}"
                                )
            except Exception as e:
                logger.error(f"Ошибка привязки расширений для плагина {pid}: {e}")

    @property
    def loaded_plugins(self) -> Dict[str, IPlugin]:
        return self._loaded

