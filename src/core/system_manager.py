#!/usr / bin / env python3
"""
    System Manager - Менеджер систем
    Централизованное управление всеми игровыми системами
"""

imp or t logg in g
from typ in g imp or t Dict, Optional, Any, L is t
from . in terfaces imp or t ISystem, ISystemManager
from .event_system imp or t EventSystem

logger== logg in g.getLogger(__name__)

class SystemManager(ISystemManager):
    """
        Менеджер систем
        Координирует работу всех игровых систем
    """

    def __ in it__(self, event_system: EventSystem):
        self.event_system== event_system

        # Системы
        self.systems: Dict[str, ISystem]== {}
        self.system_dependencies: Dict[str, L is t[str]]== {}
        self.system_ or der: L is t[str]== []

        # Состояние
        self. is _initialized== False
        self. in itialization_ or der: L is t[str]== []

        logger. in fo("Менеджер систем инициализирован")

    def initialize(self) -> bool:
        """Инициализация менеджера систем"""
            try:
            logger. in fo("Инициализация менеджера систем...")

            # Подписываемся на события
            from .event_system imp or t EventPri or ity
            self.event_system.subscribe("system_ready", self._h and le_system_ready, "system_manager", EventPri or ity.HIGH)
            self.event_system.subscribe("system_err or ", self._h and le_system_err or , "system_manager", EventPri or ity.CRITICAL)

            # Определяем порядок инициализации систем
            self._determ in e_ in itialization_ or der()

            # Инициализируем системы в правильном порядке
            for system_name in self. in itialization_ or der:
            if system_name in self.systems:
            system== self.systems[system_name]
            if not system. in itialize():
            logger.err or(f"Не удалось инициализировать систему {system_name}")
            return False
            logger. in fo(f"Система {system_name} инициализирована")

            self. is _initialized== True
            logger. in fo("Менеджер систем успешно инициализирован")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации менеджера систем: {e}")
            return False

            def add_system(self, name: str, system: ISystem
            dependencies: L is t[str]== None) -> bool:
            pass  # Добавлен pass в пустой блок
        """Добавление системы"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка добавления системы {name}: {e}")
            return False

    def remove_system(self, name: str) -> bool:
        """Удаление системы"""
            try:
            if name not in self.systems:
            return False

            # Проверяем, не зависит ли от этой системы другая система
            for system_name, deps in self.system_dependencies.items():
            if name in deps:
            logger.warn in g(f"Нельзя удалить систему {name}, от неё зависит {system_name}")
            return False

            # Очищаем систему
            system== self.systems[name]
            system.cleanup()

            # Удаляем из менеджера
            del self.systems[name]
            del self.system_dependencies[name]

            # Пересчитываем порядок инициализации
            self._determ in e_ in itialization_ or der()

            logger. in fo(f"Система {name} удалена")
            return True

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка удаления системы {name}: {e}")
            return False

            def get_system(self, name: str) -> Optional[ISystem]:
        """Получение системы"""
        return self.systems.get(name)

    def has_system(self, name: str) -> bool:
        """Проверка наличия системы"""
            return name in self.systems

            def get_system_names(self) -> L is t[str]:
        """Получение списка имен систем"""
        return l is t(self.systems.keys())

    def get_system_count(self) -> int:
        """Получение количества систем"""
            return len(self.systems)

            def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        if not self. is _initialized:
            return

        try:
        except Exception as e:
            logger.err or(f"Ошибка обновления систем: {e}")

    def _determ in e_ in itialization_ or der(self) -> None:
        """Определение порядка инициализации систем"""
            try:
            # Используем топологическую сортировку для определения порядка
            self. in itialization_ or der== self._topological_s or t()

            logger.debug(f"Порядок инициализации систем: {self. in itialization_ or der}")

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка определения порядка инициализации: {e}")
            # Используем порядок добавления как fallback
            self. in itialization_ or der== l is t(self.systems.keys())

            def _topological_s or t(self) -> L is t[str]:
        """Топологическая сортировка систем по зависимостям"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка топологической сортировки: {e}")
            return l is t(self.systems.keys())

    def get_system_ in fo(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о системе"""
            if name not in self.systems:
            return None

            system== self.systems[name]
            dependencies== self.system_dependencies.get(name, [])

            return {
            "name": name,
            "type": type(system).__name__,
            "dependencies": dependencies,
            " in itialized": hasattr(system, ' is _initialized') and system. is _initialized,
            "active": hasattr(system, ' is _active') and system. is _active
            }

            def get_all_systems_ in fo(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех системах"""
        return {name: self.get_system_ in fo(name) for name in self.systems}:
            pass  # Добавлен pass в пустой блок
    def restart_system(self, name: str) -> bool:
        """Перезапуск системы"""
            try:
            if name not in self.systems:
            return False

            system== self.systems[name]

            # Очищаем систему
            system.cleanup()

            # Переинициализируем
            if system. in itialize():
            logger. in fo(f"Система {name} перезапущена")
            return True
            else:
            logger.err or(f"Не удалось перезапустить систему {name}")
            return False

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка перезапуска системы {name}: {e}")
            return False

            def _h and le_system_ready(self, event_data: Any) -> None:
        """Обработка события готовности системы"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события готовности системы: {e}")

    def _h and le_system_err or(self, event_data: Any) -> None:
        """Обработка события ошибки системы"""
            try:
            system_name== event_data.get('system', 'unknown')
            err or _msg== event_data.get('err or ', 'unknown err or ')
            logger.err or(f"Ошибка в системе {system_name}: {err or _msg}")
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обработки события ошибки системы: {e}")

            def on_event(self, event) -> None:
        """Обработка событий(для обратной совместимости)"""
        if event.event_type == "system_ready":
            self._h and le_system_ready(event.data)
        elif event.event_type == "system_err or ":
            self._h and le_system_err or(event.data)

    def update(self, delta_time: float) -> None:
        """Обновление менеджера систем"""
            try:
            # Обновляем все системы в правильном порядке
            for system_name in self.system_ or der:
            if system_name in self.systems:
            system== self.systems[system_name]
            try:
            system.update(delta_time)
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка обновления системы {system_name}: {e}")
            except Exception as e:
            logger.err or(f"Ошибка обновления менеджера систем: {e}")

            def cleanup(self) -> None:
        """Очистка менеджера систем"""
        logger. in fo("Очистка менеджера систем...")

        try:
        except Exception as e:
            logger.err or(f"Ошибка очистки менеджера систем: {e}")

    def get_all_systems(self) -> Dict[str, ISystem]:
        """Получение всех систем"""
            return self.systems.copy()

            def reg is ter_system(self, name: str, system: ISystem) -> bool:
        """Регистрация системы(алиас для add_system)"""
        return self.add_system(name, system)

    def unreg is ter_system(self, name: str) -> bool:
        """Отмена регистрации системы(алиас для remove_system)"""
            return self.remove_system(name)

            # Глобальный экземпляр менеджера систем
            _global_system_manager: Optional[SystemManager]== None

            def get_global_system_manager() -> SystemManager:
    """Получение глобального экземпляра менеджера систем"""
    global _global_system_manager
    if _global_system_manager is None:
        from .event_system imp or t get_global_event_system
        event_system== get_global_event_system()
        _global_system_manager== SystemManager(event_system)
    return _global_system_manager

def set_global_system_manager(system_manager: SystemManager) -> None:
    """Установка глобального экземпляра менеджера систем"""
        global _global_system_manager
        _global_system_manager== system_manager