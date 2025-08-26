#!/usr/bin/env python3
"""
System Factory - Фабрика систем
Централизованное создание и управление всеми игровыми системами
"""

import logging
from typing import Dict, Any, Optional, Type
from .interfaces import ISystem, IEventSystem
from .event_system import EventSystem
from .config_manager import ConfigManager
from .system_manager import SystemManager

logger = logging.getLogger(__name__)

class SystemFactory:
    """Фабрика для создания игровых систем"""
    
    def __init__(self, config_manager: ConfigManager, event_system: EventSystem, system_manager: Optional[SystemManager] = None):
        self.config_manager = config_manager
        self.event_system = event_system
        self.system_manager = system_manager or SystemManager(event_system)
        
        # Реестр систем
        self.system_registry: Dict[str, Type[ISystem]] = {}
        
        # Созданные системы
        self.created_systems: Dict[str, ISystem] = {}
        
        # Зависимости систем
        self.system_dependencies = {
            'ai_system': ['event_system', 'config_manager'],
            'combat_system': ['event_system', 'ai_system'],
            'content_generator': ['event_system', 'config_manager'],
            'emotion_system': ['event_system', 'ai_system'],
            'evolution_system': ['event_system', 'ai_system'],
            'inventory_system': ['event_system'],
            'item_system': ['event_system', 'content_generator'],
            'skill_system': ['event_system', 'content_generator'],
            'ui_system': ['event_system', 'config_manager'],
            'render_system': ['event_system', 'config_manager']
        }
        
        logger.info("Фабрика систем инициализирована")
    
    def register_system(self, system_name: str, system_class: Type[ISystem]) -> bool:
        """Регистрация системы в фабрике"""
        try:
            self.system_registry[system_name] = system_class
            logger.debug(f"Система {system_name} зарегистрирована в фабрике")
            return True
        except Exception as e:
            logger.error(f"Ошибка регистрации системы {system_name}: {e}")
            return False
    
    def create_system(self, system_name: str, **kwargs) -> Optional[ISystem]:
        """Создание системы"""
        try:
            if system_name not in self.system_registry:
                logger.error(f"Система {system_name} не зарегистрирована")
                return None
            
            # Проверяем зависимости (контекстные зависимости считаются удовлетворенными)
            if not self._check_dependencies(system_name):
                logger.error(f"Не выполнены зависимости для системы {system_name}")
                return None
            
            # Создаем систему
            system_class = self.system_registry[system_name]
            # Внедряем известные зависимости, если система ожидает их через kwargs
            init_kwargs = dict(kwargs)
            if 'config_manager' in system_class.__init__.__code__.co_varnames:
                init_kwargs.setdefault('config_manager', self.config_manager)
            if 'event_system' in system_class.__init__.__code__.co_varnames:
                init_kwargs.setdefault('event_system', self.event_system)
            system = system_class(**init_kwargs)
            
            # Добавляем в менеджер систем
            dependencies = self.system_dependencies.get(system_name, [])
            self.system_manager.add_system(system_name, system, dependencies)
            
            # Сохраняем созданную систему
            self.created_systems[system_name] = system
            
            logger.info(f"Система {system_name} создана и добавлена в менеджер")
            return system
            
        except Exception as e:
            logger.error(f"Ошибка создания системы {system_name}: {e}")
            return None
    
    def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение созданной системы"""
        return self.created_systems.get(system_name)
    
    def initialize_all_systems(self) -> bool:
        """Инициализация всех систем"""
        try:
            logger.info("Инициализация всех систем...")
            
            # Определяем порядок инициализации на основе зависимостей
            init_order = self._determine_initialization_order()
            
            for system_name in init_order:
                if system_name in self.created_systems:
                    system = self.created_systems[system_name]
                    if not system.initialize():
                        logger.error(f"Не удалось инициализировать систему {system_name}")
                        return False
                    logger.info(f"Система {system_name} инициализирована")
            
            # Инициализируем менеджер систем
            if not self.system_manager.initialize():
                logger.error("Не удалось инициализировать менеджер систем")
                return False
            
            logger.info("Все системы успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации систем: {e}")
            return False
    
    def _check_dependencies(self, system_name: str) -> bool:
        """Проверка зависимостей системы"""
        dependencies = self.system_dependencies.get(system_name, [])
        
        for dep in dependencies:
            if dep not in self.created_systems:
                logger.warning(f"Зависимость {dep} для системы {system_name} не создана")
                return False
        
        return True
    
    def _determine_initialization_order(self) -> list:
        """Определение порядка инициализации систем"""
        # Простая топологическая сортировка
        order = []
        visited = set()
        temp_visited = set()
        
        def visit(system_name):
            if system_name in temp_visited:
                raise ValueError(f"Циклическая зависимость обнаружена: {system_name}")
            
            if system_name in visited:
                return
            
            temp_visited.add(system_name)
            
            dependencies = self.system_dependencies.get(system_name, [])
            for dep in dependencies:
                if dep in self.created_systems:
                    visit(dep)
            
            temp_visited.remove(system_name)
            visited.add(system_name)
            order.append(system_name)
        
        for system_name in self.created_systems:
            if system_name not in visited:
                visit(system_name)
        
        return order
    
    def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        try:
            for system_name, system in self.created_systems.items():
                try:
                    system.update(delta_time)
                except Exception as e:
                    logger.error(f"Ошибка обновления системы {system_name}: {e}")
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    def cleanup_all_systems(self) -> None:
        """Очистка всех систем"""
        try:
            logger.info("Очистка всех систем...")
            
            # Очищаем в обратном порядке инициализации
            for system_name in reversed(list(self.created_systems.keys())):
                try:
                    system = self.created_systems[system_name]
                    system.cleanup()
                    logger.info(f"Система {system_name} очищена")
                except Exception as e:
                    logger.error(f"Ошибка очистки системы {system_name}: {e}")
            
            # Очищаем менеджер систем
            self.system_manager.cleanup()
            
            self.created_systems.clear()
            logger.info("Все системы очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки систем: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о всех системах"""
        info = {
            'registered_systems': list(self.system_registry.keys()),
            'created_systems': list(self.created_systems.keys()),
            'system_details': {}
        }
        
        for system_name, system in self.created_systems.items():
            try:
                info['system_details'][system_name] = system.get_system_info()
            except Exception as e:
                logger.error(f"Ошибка получения информации о системе {system_name}: {e}")
        
        return info
