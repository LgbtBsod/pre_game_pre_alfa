#!/usr/bin/env python3
"""
System Manager - Менеджер систем
Централизованное управление всеми игровыми системами
"""

import logging
from typing import Dict, Optional, Any, List
from .interfaces import ISystem, ISystemManager
from .event_system import EventSystem

logger = logging.getLogger(__name__)

class SystemManager(ISystemManager):
    """
    Менеджер систем
    Координирует работу всех игровых систем
    """
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        
        # Системы
        self.systems: Dict[str, ISystem] = {}
        self.system_dependencies: Dict[str, List[str]] = {}
        self.system_order: List[str] = []
        
        # Состояние
        self.is_initialized = False
        self.initialization_order: List[str] = []
        
        logger.info("Менеджер систем инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера систем"""
        try:
            logger.info("Инициализация менеджера систем...")
            
            # Подписываемся на события
            from .event_system import EventPriority
            self.event_system.subscribe("system_ready", self._handle_system_ready, "system_manager", EventPriority.HIGH)
            self.event_system.subscribe("system_error", self._handle_system_error, "system_manager", EventPriority.CRITICAL)
            
            # Определяем порядок инициализации систем
            self._determine_initialization_order()
            
            # Инициализируем системы в правильном порядке
            for system_name in self.initialization_order:
                if system_name in self.systems:
                    system = self.systems[system_name]
                    if not system.initialize():
                        logger.error(f"Не удалось инициализировать систему {system_name}")
                        return False
                    logger.info(f"Система {system_name} инициализирована")
            
            self.is_initialized = True
            logger.info("Менеджер систем успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера систем: {e}")
            return False
    
    def add_system(self, name: str, system: ISystem, dependencies: List[str] = None) -> bool:
        """Добавление системы"""
        try:
            if name in self.systems:
                logger.warning(f"Система {name} уже существует")
                return False
            
            # Проверяем зависимости
            if dependencies:
                for dep in dependencies:
                    if dep not in self.systems:
                        logger.warning(f"Зависимость {dep} для системы {name} не найдена")
            
            # Добавляем систему
            self.systems[name] = system
            self.system_dependencies[name] = dependencies or []
            
            logger.info(f"Система {name} добавлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления системы {name}: {e}")
            return False
    
    def remove_system(self, name: str) -> bool:
        """Удаление системы"""
        try:
            if name not in self.systems:
                return False
            
            # Проверяем, не зависит ли от этой системы другая система
            for system_name, deps in self.system_dependencies.items():
                if name in deps:
                    logger.warning(f"Нельзя удалить систему {name}, от неё зависит {system_name}")
                    return False
            
            # Очищаем систему
            system = self.systems[name]
            system.cleanup()
            
            # Удаляем из менеджера
            del self.systems[name]
            del self.system_dependencies[name]
            
            # Пересчитываем порядок инициализации
            self._determine_initialization_order()
            
            logger.info(f"Система {name} удалена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления системы {name}: {e}")
            return False
    
    def get_system(self, name: str) -> Optional[ISystem]:
        """Получение системы"""
        return self.systems.get(name)
    
    def has_system(self, name: str) -> bool:
        """Проверка наличия системы"""
        return name in self.systems
    
    def get_system_names(self) -> List[str]:
        """Получение списка имен систем"""
        return list(self.systems.keys())
    
    def get_system_count(self) -> int:
        """Получение количества систем"""
        return len(self.systems)
    
    def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        if not self.is_initialized:
            return
        
        try:
            # Обновляем системы в порядке инициализации
            for system_name in self.initialization_order:
                if system_name in self.systems:
                    system = self.systems[system_name]
                    try:
                        system.update(delta_time)
                    except Exception as e:
                        logger.error(f"Ошибка обновления системы {system_name}: {e}")
                        # Эмитим событие об ошибке
                        self.event_system.emit_event(
                            "system_error",
                            {"system": system_name, "error": str(e)},
                            "system_manager",
                            priority=3
                        )
            
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    def _determine_initialization_order(self) -> None:
        """Определение порядка инициализации систем"""
        try:
            # Используем топологическую сортировку для определения порядка
            self.initialization_order = self._topological_sort()
            
            logger.debug(f"Порядок инициализации систем: {self.initialization_order}")
            
        except Exception as e:
            logger.error(f"Ошибка определения порядка инициализации: {e}")
            # Используем порядок добавления как fallback
            self.initialization_order = list(self.systems.keys())
    
    def _topological_sort(self) -> List[str]:
        """Топологическая сортировка систем по зависимостям"""
        try:
            # Создаем граф зависимостей
            graph = {}
            in_degree = {}
            
            for system_name in self.systems:
                graph[system_name] = []
                in_degree[system_name] = 0
            
            # Добавляем ребра
            for system_name, dependencies in self.system_dependencies.items():
                for dep in dependencies:
                    if dep in graph:
                        graph[dep].append(system_name)
                        in_degree[system_name] += 1
            
            # Топологическая сортировка
            result = []
            queue = [name for name, degree in in_degree.items() if degree == 0]
            
            while queue:
                current = queue.pop(0)
                result.append(current)
                
                for neighbor in graph[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # Проверяем, что все системы включены
            if len(result) != len(self.systems):
                logger.warning("Обнаружен цикл в зависимостях систем")
                # Добавляем недостающие системы в конец
                for system_name in self.systems:
                    if system_name not in result:
                        result.append(system_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка топологической сортировки: {e}")
            return list(self.systems.keys())
    
    def get_system_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о системе"""
        if name not in self.systems:
            return None
        
        system = self.systems[name]
        dependencies = self.system_dependencies.get(name, [])
        
        return {
            "name": name,
            "type": type(system).__name__,
            "dependencies": dependencies,
            "initialized": hasattr(system, 'is_initialized') and system.is_initialized,
            "active": hasattr(system, 'is_active') and system.is_active
        }
    
    def get_all_systems_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех системах"""
        return {name: self.get_system_info(name) for name in self.systems}
    
    def restart_system(self, name: str) -> bool:
        """Перезапуск системы"""
        try:
            if name not in self.systems:
                return False
            
            system = self.systems[name]
            
            # Очищаем систему
            system.cleanup()
            
            # Переинициализируем
            if system.initialize():
                logger.info(f"Система {name} перезапущена")
                return True
            else:
                logger.error(f"Не удалось перезапустить систему {name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка перезапуска системы {name}: {e}")
            return False
    
    def _handle_system_ready(self, event_data: Any) -> None:
        """Обработка события готовности системы"""
        try:
            system_name = event_data.get('system', 'unknown')
            logger.debug(f"Система {system_name} готова")
        except Exception as e:
            logger.error(f"Ошибка обработки события готовности системы: {e}")
    
    def _handle_system_error(self, event_data: Any) -> None:
        """Обработка события ошибки системы"""
        try:
            system_name = event_data.get('system', 'unknown')
            error_msg = event_data.get('error', 'unknown error')
            logger.error(f"Ошибка в системе {system_name}: {error_msg}")
        except Exception as e:
            logger.error(f"Ошибка обработки события ошибки системы: {e}")
    
    def on_event(self, event) -> None:
        """Обработка событий (для обратной совместимости)"""
        if event.event_type == "system_ready":
            self._handle_system_ready(event.data)
        elif event.event_type == "system_error":
            self._handle_system_error(event.data)
    
    def update(self, delta_time: float) -> None:
        """Обновление менеджера систем"""
        try:
            # Обновляем все системы в правильном порядке
            for system_name in self.system_order:
                if system_name in self.systems:
                    system = self.systems[system_name]
                    try:
                        system.update(delta_time)
                    except Exception as e:
                        logger.error(f"Ошибка обновления системы {system_name}: {e}")
        except Exception as e:
            logger.error(f"Ошибка обновления менеджера систем: {e}")
    
    def cleanup(self) -> None:
        """Очистка менеджера систем"""
        logger.info("Очистка менеджера систем...")
        
        try:
            # Очищаем все системы
            for name, system in self.systems.items():
                try:
                    system.cleanup()
                    logger.debug(f"Система {name} очищена")
                except Exception as e:
                    logger.error(f"Ошибка очистки системы {name}: {e}")
            
            # Очищаем менеджер
            self.systems.clear()
            self.system_dependencies.clear()
            self.system_order.clear()
            self.initialization_order.clear()
            self.is_initialized = False
            
            # Очищаем подписчика
            if hasattr(self, 'event_system'):
                # Отписываемся от событий
                pass
            
            logger.info("Менеджер систем очищен")
            
        except Exception as e:
            logger.error(f"Ошибка очистки менеджера систем: {e}")

# Глобальный экземпляр менеджера систем
_global_system_manager: Optional[SystemManager] = None

def get_global_system_manager() -> SystemManager:
    """Получение глобального экземпляра менеджера систем"""
    global _global_system_manager
    if _global_system_manager is None:
        from .event_system import get_global_event_system
        event_system = get_global_event_system()
        _global_system_manager = SystemManager(event_system)
    return _global_system_manager

def set_global_system_manager(system_manager: SystemManager) -> None:
    """Установка глобального экземпляра менеджера систем"""
    global _global_system_manager
    _global_system_manager = system_manager
