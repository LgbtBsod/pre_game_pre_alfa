#!/usr/bin/env python3
"""
System Factory - Фабрика систем
Централизованное создание и управление всеми игровыми системами
"""

import logging
from typing import Dict, Any, Optional, Type
from .interfaces import ISystem
from .event_system import EventSystem
try:
    from ..systems.rendering import RenderSystem
    from ..systems.ui import UISystem
    from ..systems.ai import AISystem, PyTorchAISystem
    from ..systems.combat import CombatSystem
    from ..systems.content import ContentDatabase, ContentGenerator
    from ..systems.ai import AIIntegrationSystem
    from ..systems.entity import EntityStatsSystem
except ImportError:
    # Fallback для случаев, когда относительные импорты не работают
    RenderSystem = None
    UISystem = None
    AISystem = None
    PyTorchAISystem = None
    CombatSystem = None
    ContentDatabase = None
    ContentGenerator = None
    AIIntegrationSystem = None
    EntityStatsSystem = None

logger = logging.getLogger(__name__)

class SystemFactory:
    """
    Фабрика систем
    Создает и настраивает все игровые системы
    """
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.system_registry: Dict[str, Type[ISystem]] = {}
        self.system_instances: Dict[str, ISystem] = {}
        
        # Регистрируем доступные системы
        self._register_systems()
        
        logger.info("Фабрика систем инициализирована")
    
    def _register_systems(self):
        """Регистрация доступных систем"""
        systems_to_register = {}
        
        if RenderSystem:
            systems_to_register["render"] = RenderSystem
        if UISystem:
            systems_to_register["ui"] = UISystem
        if AISystem:
            systems_to_register["ai"] = AISystem
        if PyTorchAISystem:
            systems_to_register["pytorch_ai"] = PyTorchAISystem
        if CombatSystem:
            systems_to_register["combat"] = CombatSystem
        if ContentDatabase:
            systems_to_register["content_database"] = ContentDatabase
        if ContentGenerator:
            systems_to_register["content_generator"] = ContentGenerator
        if AIIntegrationSystem:
            systems_to_register["ai_integration"] = AIIntegrationSystem
        if EntityStatsSystem:
            systems_to_register["entity_stats"] = EntityStatsSystem
        
        self.system_registry.update(systems_to_register)
        
        logger.debug(f"Зарегистрировано {len(self.system_registry)} систем")
        logger.info(f"Доступные системы: {list(self.system_registry.keys())}")
    
    def create_system(self, system_name: str, **kwargs) -> Optional[ISystem]:
        """Создание системы по имени"""
        try:
            if system_name not in self.system_registry:
                logger.error(f"Система {system_name} не зарегистрирована")
                return None
            
            system_class = self.system_registry[system_name]
            
            # Создаем экземпляр системы
            if system_name == "render":
                # RenderSystem требует render_node и window
                if "render_node" not in kwargs or "window" not in kwargs:
                    logger.error("RenderSystem требует render_node и window")
                    return None
                system = system_class(kwargs["render_node"], kwargs["window"])
            
            elif system_name == "ai":
                # Базовая AI система
                system = system_class()
            
            elif system_name == "pytorch_ai":
                # PyTorch AI система
                system = system_class()
            
            elif system_name == "content_database":
                # База данных контента
                system = system_class()
            
            elif system_name == "content_generator":
                # Генератор контента
                system = system_class()
            
            elif system_name == "ai_integration":
                # Система интеграции AI
                system = system_class()
            
            elif system_name == "entity_stats":
                # Система характеристик сущностей
                system = system_class()
            
            else:
                # Остальные системы
                system = system_class()
            
            # Инициализируем систему
            if system.initialize():
                self.system_instances[system_name] = system
                logger.info(f"Система {system_name} успешно создана и инициализирована")
                return system
            else:
                logger.error(f"Не удалось инициализировать систему {system_name}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка создания системы {system_name}: {e}")
            return None
    
    def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение системы по имени"""
        return self.system_instances.get(system_name)
    
    def has_system(self, system_name: str) -> bool:
        """Проверка наличия системы"""
        return system_name in self.system_instances
    
    def get_all_systems(self) -> Dict[str, ISystem]:
        """Получение всех созданных систем"""
        return self.system_instances.copy()
    
    def destroy_system(self, system_name: str) -> bool:
        """Уничтожение системы"""
        try:
            if system_name not in self.system_instances:
                return False
            
            system = self.system_instances[system_name]
            system.cleanup()
            
            del self.system_instances[system_name]
            logger.info(f"Система {system_name} уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы {system_name}: {e}")
            return False
    
    def destroy_all_systems(self):
        """Уничтожение всех систем"""
        logger.info("Уничтожение всех систем...")
        
        for system_name in list(self.system_instances.keys()):
            self.destroy_system(system_name)
        
        logger.info("Все системы уничтожены")
    
    def get_system_info(self, system_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о системе"""
        if system_name not in self.system_instances:
            return None
        
        system = self.system_instances[system_name]
        return {
            "name": system_name,
            "type": type(system).__name__,
            "initialized": hasattr(system, 'is_initialized') and system.is_initialized,
            "active": hasattr(system, 'is_active') and system.is_active
        }
    
    def get_all_systems_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех системах"""
        return {name: self.get_system_info(name) for name in self.system_instances}
    
    def create_default_systems(self, render_node, window) -> Dict[str, ISystem]:
        """Создание стандартного набора систем"""
        logger.info("Создание стандартного набора систем...")
        
        created_systems = {}
        
        try:
            # Система рендеринга
            render_system = self.create_system("render", render_node=render_node, window=window)
            if render_system:
                created_systems["render"] = render_system
            
            # Система UI
            ui_system = self.create_system("ui")
            if ui_system:
                created_systems["ui"] = ui_system
            
            # Система AI (пробуем PyTorch, если не получится - базовая)
            ai_system = self.create_system("pytorch_ai")
            if ai_system:
                created_systems["ai"] = ai_system
            else:
                # Fallback на базовую AI систему
                ai_system = self.create_system("ai")
                if ai_system:
                    created_systems["ai"] = ai_system
            
            # Система боя
            combat_system = self.create_system("combat")
            if combat_system:
                created_systems["combat"] = combat_system
            
            # База данных контента
            content_db = self.create_system("content_database")
            if content_db:
                created_systems["content_database"] = content_db
            
            # Генератор контента
            content_gen = self.create_system("content_generator")
            if content_gen:
                created_systems["content_generator"] = content_gen
            
            # Система интеграции AI
            ai_integration = self.create_system("ai_integration")
            if ai_integration:
                created_systems["ai_integration"] = ai_integration
            
            # Система характеристик сущностей
            entity_stats = self.create_system("entity_stats")
            if entity_stats:
                created_systems["entity_stats"] = entity_stats
            
            logger.info(f"Создано {len(created_systems)} систем")
            return created_systems
            
        except Exception as e:
            logger.error(f"Ошибка создания стандартного набора систем: {e}")
            return created_systems
    
    def cleanup(self):
        """Очистка фабрики систем"""
        logger.info("Очистка фабрики систем...")
        self.destroy_all_systems()
        self.system_instances.clear()
        logger.info("Фабрика систем очищена")
