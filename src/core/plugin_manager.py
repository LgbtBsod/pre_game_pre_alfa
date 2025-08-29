#!/usr/bin/env python3
"""
Менеджер плагинов: обнаружение, загрузка, жизненный цикл
"""

import importlib
import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import threading
import time
import re

from .plugin_interfaces import IPlugin, PluginMetadata, PluginLoadType, ISystemExtension

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
                logger.info(f"Каталог плагинов отсутствует: {self.plugins_dir}")
                return []

            for child in self.plugins_dir.iterdir():
                if child.is_dir():
                    init_file = child / "__init__.py"
                    meta_file = child / "plugin.json"
                    if init_file.exists() or meta_file.exists():
                        self._discovered[child.name] = child
            return list(self._discovered.keys())
        except Exception as e:
            logger.error(f"Ошибка обнаружения плагинов: {e}")
            return []

    def _load_metadata(self, plugin_path: Path) -> Optional[PluginMetadata]:
        meta_path = plugin_path / "plugin.json"
        try:
            if meta_path.exists():
                with meta_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                # минимальная валидация
                required = ["plugin_id", "name", "version"]
                for key in required:
                    if key not in data:
                        raise ValueError(f"Отсутствует поле {key} в plugin.json")
                if not re.match(r"^[a-zA-Z0-9_\-\.]+$", data["plugin_id"]):
                    raise ValueError("Некорректный plugin_id")
                return PluginMetadata(**data)
            # Fallback: try import module attribute `metadata`
            module = self._import_module(plugin_path)
            if module and hasattr(module, "metadata"):
                md = getattr(module, "metadata")
                # проверка полей
                assert md.plugin_id and md.name and md.version
                return md
        except Exception as e:
            logger.error(f"Ошибка чтения/валидации метаданных для {plugin_path.name}: {e}")
        return None

    def _import_module(self, plugin_path: Path):
        try:
            module_name = f"plugins.{plugin_path.name}"
            if str(self.plugins_dir.parent) not in sys.path:
                sys.path.insert(0, str(self.plugins_dir.parent))
            return importlib.import_module(module_name)
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
            # ищем factory: create_plugin()
            if hasattr(module, "create_plugin"):
                plugin: IPlugin = module.create_plugin()
            elif hasattr(module, "Plugin"):
                plugin = getattr(module, "Plugin")()  # type: ignore
            else:
                logger.error(f"Плагин {plugin_id} не содержит фабрики или класса Plugin")
                return False
            # initialize
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
            "event_system", "config_manager", "scene_manager",
            "system_factory", "system_manager"
        }
        ctx = {k: v for k, v in base_context.items() if k in allowed_keys}
        return ctx

    def _check_requirements(self, md: PluginMetadata, base_context: Dict[str, Any]) -> bool:
        try:
            engine_version = str(base_context.get("engine_version", "0.0.0"))
            # simple check; real versioning can use packaging.version
            if md.engine_version and md.engine_version > engine_version:
                logger.warning(f"Плагин {md.plugin_id} требует engine {md.engine_version}+ (есть {engine_version})")
                return False
            if md.requires_systems and base_context.get("system_manager"):
                sm = base_context["system_manager"]
                for sys_name, min_ver in md.requires_systems.items():
                    # assume systems can expose version via get_version() or attribute
                    sys_obj = getattr(sm, 'get_system', lambda n: None)(sys_name)
                    if not sys_obj:
                        logger.warning(f"Плагин {md.plugin_id}: отсутствует требуемая система {sys_name}")
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

    def start_watching(self, interval: float = 1.0) -> None:
        """Запустить примитивный hot-reload наблюдатель (dev)"""
        if self._watching:
            return
        self._watching = True
        def _watch():
            while self._watching:
                try:
                    for pid, path in list(self._discovered.items()):
                        for py in path.rglob('*.py'):
                            mtime = py.stat().st_mtime
                            key = f"{pid}:{py}"
                            old = self._mtimes.get(key, 0)
                            if mtime > old:
                                self._mtimes[key] = mtime
                                # naive approach: stop/destroy and reload plugin
                                if pid in self._loaded:
                                    try:
                                        self._loaded[pid].stop()
                                        self._loaded[pid].destroy()
                                        del self._loaded[pid]
                                    except Exception:
                                        pass
                                ctx = self._contexts.get(pid, {})
                                self.load(pid, ctx)
                                logger.info(f"Плагин {pid} перезагружен (dev)")
                except Exception:
                    pass
                time.sleep(interval)
        self._watcher_thread = threading.Thread(target=_watch, daemon=True)
        self._watcher_thread.start()

    def stop_watching(self) -> None:
        self._watching = False
        if self._watcher_thread and self._watcher_thread.is_alive():
            try:
                self._watcher_thread.join(timeout=1.0)
            except Exception:
                pass

    def bind_system_extensions(self, systems: Dict[str, Any]) -> None:
        """Подключить расширения плагинов к системам по target_system"""
        for pid, plugin in self._loaded.items():
            try:
                # Собираем все объекты расширений из модуля, если есть
                module = sys.modules.get(f"plugins.{pid}")
                if not module:
                    continue
                for attr_name in dir(module):
                    obj = getattr(module, attr_name)
                    if isinstance(obj, type):
                        # классы расширений
                        try:
                            candidate = obj()
                        except Exception:
                            continue
                        if isinstance(candidate, ISystemExtension):
                            target = getattr(candidate, 'target_system', None)
                            if target and target in systems:
                                candidate.attach(systems[target])
                                logger.info(f"Плагин {pid}: расширение {attr_name} подключено к {target}")
            except Exception as e:
                logger.error(f"Ошибка привязки расширений для плагина {pid}: {e}")

    @property
    def loaded_plugins(self) -> Dict[str, IPlugin]:
        return self._loaded
